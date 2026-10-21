import json
import socket
import time
from threading import Thread

from Logic.Player import Player
from Logic.Device import Device
from Utils.Helpers import Helpers
from Protocol.LogicLaserMessageFactory import packets
from Protocol.Messages.Server.LobbyInfoMessage import LobbyInfoMessage
from Protocol.Messages.Server.LoginFailedMessage import LoginFailedMessage


def _(*args):
    for arg in args:
        print(arg, end=' ')
    print()


class ClientThread(Thread):
    HEADER_SIZE = 7
    MAX_PACKET_SIZE = 2 * 1024 * 1024
    SOCKET_TIMEOUT = 10

    def __init__(self, client, address, db):
        super().__init__(daemon=True)
        self.client = client
        self.address = address
        self.db = db
        self.config = json.loads(open('config.json', 'r').read())
        self.device = Device(self.client)
        self.player = Player(self.device)
        self._counted = False

    def recvall(self, length: int):
        data = bytearray()
        while len(data) < length:
            chunk = self.client.recv(length - len(data))
            if not chunk:
                raise ConnectionError('client disconnected while receiving data')
            data.extend(chunk)
        return bytes(data)

    def _cleanup(self):
        player_id = getattr(self.player, 'ID', 0)
        if player_id:
            Helpers.connected_clients['Clients'].pop(str(player_id), None)
        if self._counted:
            Helpers.connected_clients['ClientsCount'] = max(
                0, Helpers.connected_clients['ClientsCount'] - 1
            )
            self._counted = False
        try:
            self.client.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        try:
            self.client.close()
        except OSError:
            pass
        _(f"{Helpers.cyan}[DEBUG] Client disconnected! IP: {self.address[0]}")

    def run(self):
        self.client.settimeout(self.SOCKET_TIMEOUT)
        Helpers.connected_clients['ClientsCount'] += 1
        self._counted = True

        try:
            while True:
                header = self.recvall(self.HEADER_SIZE)
                packet_id = int.from_bytes(header[:2], 'big')
                packet_length = int.from_bytes(header[2:5], 'big')

                if packet_length < 0 or packet_length > self.MAX_PACKET_SIZE:
                    raise ValueError(f'invalid packet length: {packet_length}')

                packet_data = self.recvall(packet_length)

                if self.address[0] in self.config.get('BannedIPs', []):
                    self.player.err_code = 11
                    LoginFailedMessage(self.client, self.player, 'Account banned!').send()
                    break

                LobbyInfoMessage(
                    self.client,
                    self.player,
                    Helpers.connected_clients['ClientsCount']
                ).send()

                message_cls = packets.get(packet_id)
                if message_cls is None:
                    _(f'{Helpers.cyan}[CLIENT] Unhandled Packet! ID: {packet_id}, Length: {packet_length}')
                    continue

                _(f'{Helpers.blue}[CLIENT] PacketID: {packet_id}, Name: {message_cls.__name__} Length: {packet_length}')
                message = message_cls(self.client, self.player, packet_data)
                message.decode()
                message.process(self.db)

                if packet_id == 10101 and getattr(self.player, 'ID', 0):
                    Helpers.connected_clients['Clients'][str(self.player.ID)] = {
                        'SocketInfo': self.client
                    }

        except (ConnectionAbortedError, ConnectionResetError, ConnectionError, socket.timeout):
            pass
        except (EOFError, UnicodeDecodeError, ValueError) as exc:
            _(f'{Helpers.red}[ERROR] Malformed packet from {self.address[0]}: {exc}')
        except Exception as exc:
            _(f'{Helpers.red}[ERROR] Client thread crashed for {self.address[0]}: {exc}')
        finally:
            self._cleanup()
