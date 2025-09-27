import numpy as np
import pandas as pd
import bitstring
from tqdm import tqdm
from rich import print
from multiprocessing import Pool, cpu_count
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

    @staticmethod
    def decode_element(element):
        cat, length, data = element
        if cat == 48:
            return decode_cat48(cat, length, data)
        return None

    def load(self, file_name, parallel=True):
        with open(file_name, "rb") as f:
            self.data = f.read()
        self.bit_data = bitstring.BitArray(self.data)
        print(f"Loaded {len(self.data)} bytes from {file_name}")
        self.splited_data = self.split_data(self.bit_data)
        decoded_messages = []

        if parallel:
            with Pool(processes=min(cpu_count() - 1, 8)) as pool:
                results = list(
                    tqdm(
                        pool.imap(Decoder.decode_element, self.splited_data),
                        total=len(self.splited_data),
                        desc="Decoding",
                        unit="Msg",
                    )
                )
        else:
            results = list(
                tqdm(
                    map(Decoder.decode_element, self.splited_data),
                    total=len(self.splited_data),
                    desc="Decoding",
                    unit="Msg",
                )
            )
        decoded_messages.extend([msg for msg in results if msg is not None])
        # print(decoded_messages)
