import os
import sys
from binary import BinaryReader
from typing import TypedDict

class Huff:
    def __init__(self, data: bytes):
        self.dword_46FAE4 = BinaryReader(data)
        
        self.dword_46FAEC = 256
        self.dword_462468 = 0
        self.dword_46246C = 0
        
        self.dword_46FAF0 = {}
        self.dword_4702EC = {}
        
        self.dword_46FAE8 = bytearray()
    
    def sub_4115C8(self) -> int:
        self.dword_462468 = self.dword_462468 - 1
        if self.dword_462468 < 0:
            self.dword_462468 = 7
            self.dword_46246C = self.dword_46FAE4.read_byte()
            return (self.dword_46246C >> 7) & 1
        else:
            return (self.dword_46246C >> self.dword_462468) & 1
    
    def sub_41160C(self, a1: int) -> int:
        a1_ = a1
        v2 = 0
        while a1_ > self.dword_462468:
            a1_ -= self.dword_462468
            v2 |= (self.dword_46246C & ((1 << self.dword_462468) - 1)) << a1_
            self.dword_46246C = self.dword_46FAE4.read_byte()
            self.dword_462468 = 8
        self.dword_462468 -= a1_
        return v2 | ((1 << a1_) - 1) & (self.dword_46246C >> self.dword_462468)
    
    def sub_411694(self) -> int:
        if self.sub_4115C8() == 0:
            return self.sub_41160C(8)
        v3 = self.dword_46FAEC
        self.dword_46FAEC += 1
        v5 = v3
        if v3 >= 511:
            raise Exception("Huff: sub_411694: v3 >= 511")
        self.dword_46FAF0[v3] = self.sub_411694()
        self.dword_4702EC[v5] = self.sub_411694()
        return v5
    
    def sub_4116FC(self) -> bytes:
        v3 = 0
        for i in range(4):
            v3 |= self.dword_46FAE4.read_byte() << (i * 8)
        
        v5 = self.sub_411694()
        
        for _ in range(v3):
            v6 = v5
            while v6 >= 256:
                if self.sub_4115C8():
                    v6 = self.dword_4702EC[v6]
                else:
                    v6 = self.dword_46FAF0[v6]
            self.dword_46FAE8.append(v6)
        
        return bytes(self.dword_46FAE8)

os.makedirs("srp", exist_ok=True)

class FileMetadata(TypedDict):
    name: str
    offset: int
    size: int

def read_metadata_table(reader: BinaryReader):
    tables: list[FileMetadata] = []
    header_reader = reader.read_bytes_into_reader(0x318)
    while not header_reader.eof:
        name = header_reader.read_bytes(12)
        if name == b'\xff' * 12:
            now = reader.pos
            reader.goto(header_reader.read_unsigned_int_32_le())
            tables.extend(read_metadata_table(reader))
            reader.goto(now + 12)
            continue
        offset = header_reader.read_unsigned_int_32_le()
        size = header_reader.read_unsigned_int_32_le()
        if offset == 0 and size == 0:
            break
        c_name = name.rstrip(b'\0').decode("shift-jis")
        tables.append({"name": c_name, "offset": offset, "size": size})
        header_reader.skip(4)
    return tables

with open(sys.argv[1], "rb") as f:
    reader = BinaryReader(f.read())

metadata = read_metadata_table(reader)

for entry in metadata:
    reader.goto(entry["offset"])
    data = reader.read_bytes(entry["size"])
    with open(f"srp/{entry['name']}", "wb") as f:
        f.write(data)
    huff = Huff(data)
    data = huff.sub_4116FC()
    with open(f"srp/{entry['name']}.txt", "wb") as f:
        f.write(data)
