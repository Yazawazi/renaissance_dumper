import os
import sys
from typing import TypedDict

from rich.progress import track

from binary import BinaryReader, BinaryWriter


class File(TypedDict):
    name: str
    data: BinaryReader


def split_array(array: list[File], size: int) -> list[list[File]]:
    return [array[i : i + size] for i in range(0, len(array), size)]


def pack_fga(files: list[File]) -> BinaryWriter:
    fga = BinaryWriter()
    offset = 0x318
    splited_files = split_array(files, 32)
    for grouped_files_index, grouped_files in track(
        enumerate(splited_files), description="Packing files", total=len(splited_files)
    ):
        for file in grouped_files:
            name = file["name"].encode("shift-jis")
            if len(name) > 12:
                raise ValueError(f"File name {file['name']} is too long")
            fga.write_bytes(name)
            if len(name) < 12:
                fga.write_bytes(b"\0" * (12 - len(name)))
            data_len = len(file["data"].data)
            fga.write_unsigned_int_32_le(offset)
            fga.write_unsigned_int_32_le(data_len)
            fga.write_bytes(b"\0" * 4)
            offset += data_len
        if len(grouped_files) < 32:
            for _ in range(32 - len(grouped_files)):
                fga.write_bytes(b"\x00" * 12)
                fga.write_unsigned_int_32_le(0)
                fga.write_unsigned_int_32_le(0)
                fga.write_bytes(b"\0" * 4)
        if grouped_files_index == len(splited_files) - 1:
            fga.write_bytes(b"\xff" * 12)
            fga.write_unsigned_int_32_le(0)
            fga.write_unsigned_int_32_le(0)
            fga.write_bytes(b"\0" * 4)
        else:
            fga.write_bytes(b"\xff" * 12)
            fga.write_unsigned_int_32_le(offset)
            fga.write_unsigned_int_32_le(0)
            fga.write_bytes(b"\0" * 4)
        for file in grouped_files:
            fga.write_bytes(file["data"].data)
        offset += 0x318
    return fga


def make_bmp_to_ebp(file: BinaryReader) -> BinaryWriter:
    ebp = BinaryWriter()
    ebp.write_unsigned_int_32_le(len(file.data) - 2)
    while not file.eof:
        first_3_bytes = file.read_bytes(3)
        ebp.write_bytes(first_3_bytes)
        ebp.write_byte(1)
    return ebp


def pack_ebp(folder_path: str) -> BinaryWriter:
    files = []
    print("This may take a while, please wait...")
    for file in track(os.listdir(folder_path), description="Reading files"):
        if file.endswith(".EBP.bmp"):
            file_name = file[:-4]
            with open(os.path.join(folder_path, file), "rb") as f:
                files.append(
                    {"name": file_name, "data": make_bmp_to_ebp(BinaryReader(f.read()))}
                )
    return pack_fga(files)


if __name__ == "__main__":
    ebp = pack_ebp(sys.argv[1])
    with open("packed_ebp.fga", "wb") as f:
        f.write(ebp.bytes)
    print("Done! Your packed EBP is saved as packed_ebp.fga")
