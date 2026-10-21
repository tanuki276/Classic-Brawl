from io import BufferedReader, BytesIO


class Reader(BufferedReader):
    MAX_VINT_BYTES = 5

    def __init__(self, initial_bytes, endian: str = 'big'):
        super().__init__(BytesIO(initial_bytes))
        self.buffer = initial_bytes
        self.endian = endian

    def _read_exact(self, length: int) -> bytes:
        if length < 0:
            raise ValueError("length must be non-negative")
        data = self.read(length)
        if len(data) != length:
            raise EOFError(f"expected {length} bytes, got {len(data)}")
        return data

    def remaining(self) -> int:
        return len(self.buffer) - self.tell()

    def readByte(self):
        return int.from_bytes(self._read_exact(1), "big")

    def readVInt(self):
        n = self._read_varint(True)
        return (n >> 1) ^ (-(n & 1))

    def readIntList(self) -> list:
        length = self.readVInt()
        if length < 0:
            raise ValueError("negative list length")
        return [self.readVInt() for _ in range(length)]

    def readShort(self, length=2):
        return int.from_bytes(self._read_exact(length), "big")

    def readInt(self, length=4):
        return int.from_bytes(self._read_exact(length), "big")

    def readLong(self):
        return self.readInt(8)

    def readUInt8(self) -> int:
        return self.readUInteger()

    def readUInteger(self, length: int = 1) -> int:
        return int.from_bytes(self._read_exact(length), self.endian, signed=False)

    def _read_varint(self, rotate: bool = True):
        result = 0
        shift = 0
        for _ in range(self.MAX_VINT_BYTES):
            byte = self.readByte()
            if rotate and shift == 0:
                seventh = (byte & 0x40) >> 6
                msb = (byte & 0x80) >> 7
                n = byte << 1
                n = n & ~0x181
                byte = n | (msb << 7) | seventh
            result |= (byte & 0x7f) << shift
            if not (byte & 0x80):
                return result
            shift += 7
        raise ValueError("VInt is too long")

    def readBool(self) -> bool:
        return self.readUInt8() >= 1

    def readDataReference(self):
        a = self.readVInt()
        if a > 0:
            return a, self.readVInt()
        return [a, 0]

    def readString(self):
        length = self.readInt()
        if length == pow(2, 32) - 1:
            return ""
        if length > self.remaining():
            raise EOFError(f"string length {length} exceeds remaining payload {self.remaining()}")
        return self._read_exact(length).decode('utf-8')

    def peekInt(self, length=4):
        data = self.peek(length)[:length]
        if len(data) != length:
            raise EOFError(f"expected {length} bytes to peek, got {len(data)}")
        return int.from_bytes(data, "big")

    def readLogicLong(self):
        x = self.readVInt()
        y = self.readVInt()
        return [x, y]
