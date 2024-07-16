class BinaryReader:
    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0
    
    @property
    def eof(self) -> bool:
        return self.pos >= len(self.data)
    
    def rewind(self, size: int):
        self.pos -= size
    
    def goto(self, pos: int):
        self.pos = pos
    
    def skip(self, size: int):
        self.pos += size
    
    def skip_current_zero(self):
        if self.readByte() == 0:
            return
        self.rewind(1)
    
    def peek(self, size: int) -> bytes:
        return self.data[self.pos:self.pos + size]
    
    def peek_byte(self) -> int:
        return self.data[self.pos]
    
    def read_byte(self) -> int:
        value = self.data[self.pos]
        self.pos += 1
        return value
    
    def get_byte(self, pos: int) -> int:
        return self.data[pos]
    
    def read_signed_byte(self) -> int:
        value = self.data[self.pos]
        if value > 127:
            value -= 256
        self.pos += 1
        return value
    
    def read_bytes(self, size: int) -> bytes:
        value = self.data[self.pos:self.pos + size]
        self.pos += size
        return value
    
    def read_bytes_into_reader(self, size: int) -> 'BinaryReader':
        value = BinaryReader(self.data[self.pos:self.pos + size])
        self.pos += size
        return value
    
    def read_bool(self) -> bool:
        value = self.readByte()
        if value == 0:
            return False
        elif value == 1:
            return True
        else:
            raise ValueError('Invalid boolean value')
    
    def read_unsigned_int_64(self) -> int:
        value = int.from_bytes(self.data[self.pos:self.pos + 8], 'big')
        self.pos += 8
        return value
    
    def read_unsigned_int_64_le(self) -> int:
        value = int.from_bytes(self.data[self.pos:self.pos + 8], 'little')
        self.pos += 8
        return value
    
    def read_unsigned_int_32(self) -> int:
        value = int.from_bytes(self.data[self.pos:self.pos + 4], 'big')
        self.pos += 4
        return value
    
    def read_unsigned_int_32_le(self) -> int:
        value = int.from_bytes(self.data[self.pos:self.pos + 4], 'little')
        self.pos += 4
        return value
    
    def read_unsigned_int_16(self) -> int:
        value = int.from_bytes(self.data[self.pos:self.pos + 2], 'big')
        self.pos += 2
        return value
    
    def read_unsigned_int_16_le(self) -> int:
        value = int.from_bytes(self.data[self.pos:self.pos + 2], 'little')
        self.pos += 2
        return value
    
    def read_signed_int_64(self) -> int:
        value = int.from_bytes(self.data[self.pos:self.pos + 8], 'big', signed=True)
        self.pos += 8
        return value
    
    def read_signed_int_64_le(self) -> int:
        value = int.from_bytes(self.data[self.pos:self.pos + 8], 'little', signed=True)
        self.pos += 8
        return value
    
    def read_signed_int_32(self) -> int:
        value = int.from_bytes(self.data[self.pos:self.pos + 4], 'big', signed=True)
        self.pos += 4
        return value
    
    def read_signed_int_32_le(self) -> int:
        value = int.from_bytes(self.data[self.pos:self.pos + 4], 'little', signed=True)
        self.pos += 4
        return value
    
    def read_signed_int_16(self) -> int:
        value = int.from_bytes(self.data[self.pos:self.pos + 2], 'big', signed=True)
        self.pos += 2
        return value
    
    def read_signed_int_16_le(self) -> int:
        value = int.from_bytes(self.data[self.pos:self.pos + 2], 'little', signed=True)
        self.pos += 2
        return value
    
    def read_c_string(self, decoding = "utf-8") -> str:
        end = self.data.index(0, self.pos)
        value = self.data[self.pos:end].decode(decoding)
        self.pos = end + 1
        return value
    
    def read_c_string_with_size(self, size: int, decoding = "utf-8") -> str:
        value = self.data[self.pos:self.pos + size].decode(decoding)
        self.pos += size
        return value

