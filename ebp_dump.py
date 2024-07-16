import os
import sys
from binary import BinaryReader
from typing import TypedDict


os.makedirs("ebp", exist_ok=True)

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
    with open(f"ebp/{entry['name']}", "wb") as f:
        f.write(data)
    data_reader = BinaryReader(data)
    true_bmp = bytearray()
    while not data_reader.eof:
        first_3_bytes = data_reader.read_bytes(3)
        repeat_count = data_reader.read_byte()
        for _ in range(repeat_count):
            true_bmp.extend(first_3_bytes)
    with open(f"ebp/{entry['name']}.bmp", "wb") as f:
        f.write(true_bmp)
