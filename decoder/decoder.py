import numpy as np
import pandas as pd
import bitstring
from tqdm import tqdm
from .cat48 import DecodeCat48


class Decoder:
    def __init__(self):
        pass

    def split_data(self, bit_data):
        result = []
        current_pos = 0
        total_bits = len(bit_data)

        with tqdm(total=total_bits // 8, desc="Decoding") as pbar:
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
        distinct_data_items =set()
        for element in tqdm(self.splited_data[:100]):
            cat, length, data = element
            if cat == 48:
                data_items_to_decode=DecodeCat48(cat, length, data.bin)
                distinct_data_items.update(data_items_to_decode)
        print(f'Distinct data items in the records: {sorted(distinct_data_items)}')
