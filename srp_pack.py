import os
import sys
from io import BytesIO
from typing import TypedDict

from rich.progress import track

from binary import BinaryReader, BinaryWriter


class BitTreeEncoder:
    def __init__(self):
        self.output = BytesIO()
        self.current_byte = 0
        self.bit_position = 0
        self.next_node_id = 256

    def write_bit(self, bit: int) -> None:
        self.current_byte = (self.current_byte << 1) | (bit & 1)
        self.bit_position += 1

        if self.bit_position == 8:
            self.output.write(bytes([self.current_byte]))
            self.current_byte = 0
            self.bit_position = 0

    def write_bits(self, value: int, count: int) -> None:
        for i in range(count - 1, -1, -1):
            self.write_bit((value >> i) & 1)

    def flush(self) -> None:
        if self.bit_position > 0:
            self.current_byte <<= 8 - self.bit_position
            self.output.write(bytes([self.current_byte]))
            self.current_byte = 0
            self.bit_position = 0

    def build_tree(self, data: bytes) -> tuple[int, dict]:
        if not data:
            return None, {}

        freq = {}
        for byte in data:
            freq[byte] = freq.get(byte, 0) + 1

        if len(freq) == 1:
            return next(iter(freq)), {}

        nodes = {}

        items = sorted(freq.items(), key=lambda x: x[1], reverse=True)

        left, _ = items[0]
        right, _ = items[1]
        root = self.next_node_id
        self.next_node_id += 1
        nodes[root] = (left, right)

        for byte, _ in items[2:]:
            if self.next_node_id >= 511:
                break
            new_root = self.next_node_id
            self.next_node_id += 1
            nodes[new_root] = (root, byte)
            root = new_root

        return root, nodes

    def encode(self, data: bytes) -> bytes:
        for i in range(4):
            self.output.write(bytes([(len(data) >> (i * 8)) & 0xFF]))

        root, nodes = self.build_tree(data)

        def write_tree(node_id: int):
            if node_id < 256:
                self.write_bit(0)
                self.write_bits(node_id, 8)
                return

            self.write_bit(1)
            left, right = nodes[node_id]
            write_tree(left)
            write_tree(right)

        write_tree(root)
        byte_cache = build_byte_cache(nodes)

        for byte in data:
            current = root
            path = []

            while current >= 256:
                left, right = nodes[current]
                if byte == left or (
                    byte < 256 and find_byte(nodes, left, byte, byte_cache)
                ):
                    path.append(0)
                    current = left
                else:
                    path.append(1)
                    current = right

            for bit in path:
                self.write_bit(bit)

        self.flush()
        return self.output.getvalue()


def build_byte_cache(nodes: dict) -> dict[int, set[int]]:
    cache = {}

    def collect_bytes(node_id: int) -> set[int]:
        if node_id in cache:
            return cache[node_id]

        if node_id < 256:
            result = {node_id}
        else:
            left, right = nodes[node_id]
            result = collect_bytes(left) | collect_bytes(right)

        cache[node_id] = result
        return result

    for node_id in nodes:
        collect_bytes(node_id)

    return cache


def find_byte(
    nodes: dict, node_id: int, target: int, byte_cache: dict[int, set[int]]
) -> bool:
    if node_id < 256:
        return node_id == target
    return target in byte_cache[node_id]


class File(TypedDict):
    name: str
    data: bytes


def split_array(array: list[File], size: int) -> list[list[File]]:
    return [array[i : i + size] for i in range(0, len(array), size)]


def pack_fga(files: list[File]) -> bytes:
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
            data_len = len(file["data"])
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
            fga.write_bytes(file["data"])
        offset += 0x318
    return fga.data


def make_txt_to_srp(file: bytes) -> bytes:
    huff = BitTreeEncoder()
    return huff.encode(file)


def pack_srp(folder_path: str) -> bytes:
    files = []
    print("This may take a while, please wait...")
    for file in track(os.listdir(folder_path), description="Reading files"):
        if file.endswith(".SRP.txt"):
            file_name = file[:-4]
            print(f"Packing {file_name}...")
            with open(os.path.join(folder_path, file), "rb") as f:
                files.append({"name": file_name, "data": make_txt_to_srp(f.read())})
    return pack_fga(files)


if __name__ == "__main__":
    srp = pack_srp(sys.argv[1])
    with open("packed_srp.fga", "wb") as f:
        f.write(srp)
    print("Done! Your packed SRP is saved as packed_srp.fga")
