import json
import socket

from Utils.Helpers import Helpers
from DataBase.MongoDB import MongoDB
from Core.Networking.ClientThread import ClientThread


def _(*args):
    for arg in args:
        print(arg, end=' ')
    print()


class Server:
    def __init__(self, ip: str, port: int):
        with open('config.json', 'r', encoding='utf-8') as config_file:
            self.config = json.load(config_file)
        mongo_url = self.config.get('MongoConnectionURL', '').strip()
        if not mongo_url:
            raise ValueError('MongoConnectionURL is empty in config.json')

        self.db = MongoDB(mongo_url)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.port = port
        self.ip = ip

    def start(self):
        self.server.bind((self.ip, self.port))
        self.server.listen(128)
        _(f'{Helpers.cyan}[DEBUG] Server started! Listening on {self.ip}:{self.port}')

        try:
            while True:
                client, address = self.server.accept()
                _(f'{Helpers.cyan}[DEBUG] Client connected! IP: {address[0]}')
                ClientThread(client, address, self.db).start()
        finally:
            self.server.close()
