import numpy as np
import pandas as pd
import bitstring
from tqdm import tqdm
from rich import print
from .cat48 import decode_cat48


class Decoder:
    def __init__(self):
        pass

    def split_data(self, bit_data):
        result = []
        current_pos = 0
        total_bits = len(bit_data)

        with tqdm(total=total_bits // 8, desc="Splitting", unit="B") as pbar:
            while current_pos + 24 <= total_bits:  # Need at least 24 bits for header
                cat = bit_data[current_pos : current_pos + 8].uint
                length = bit_data[current_pos + 8 : current_pos + 24].uint
                data_end = current_pos + (length) * 8

                if data_end > total_bits:
                    break

                data = bit_data[current_pos + 24 : data_end]
                result.append((cat, length, data))

                current_pos = data_end
                pbar.update(length)

        return result

    def load(self, file_name):
        with open(file_name, "rb") as f:
            self.data = f.read()
        self.bit_data = bitstring.BitArray(self.data)
        print(f"Loaded {len(self.data)} bytes from {file_name}")
        self.splited_data = self.split_data(self.bit_data)
        decoded_messages=[]
        for element in tqdm(self.splited_data,desc="Decoding", unit="Msg"):
            cat, length, data = element
            if cat == 48:
                decoded_message = decode_cat48(cat, length, data)
                decoded_messages.append(decoded_message)
        # print(decoded_messages)
