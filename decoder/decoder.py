import numpy as np
import pandas as pd
import bitstring
from multiprocessing import Pool, cpu_count
from rich import print
from tqdm import tqdm
from .cat48 import decode_cat48
from .cat21 import decode_cat21


class Decoder:
    def __init__(self):
        pass

    def split_data(self, bit_data,max_messages=None):
        result = []
        current_pos = 0
        total_bits = len(bit_data)
        i=0
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
                i+=1
                if max_messages is not None and i > max_messages:
                    break

        return result

    @staticmethod
    def decode_element(element):
        cat, length, data = element
        if cat == 48:
            return decode_cat48(cat, length, data)
        elif cat == 21:
            return decode_cat21(cat, length, data)
        return None

    def load(self, file_name, parallel=True, max_messages=None):
        with open(file_name, "rb") as f:
            self.data = f.read()
        self.bit_data = bitstring.BitArray(self.data)
        print(f"Loaded {len(self.data)} bytes from {file_name}")
        self.splited_data = self.split_data(self.bit_data,max_messages)
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
        print(f"Decoded {len(decoded_messages)} messages")
        if max_messages is not None:
            results = results[:max_messages]
        print(f"Returning {len(decoded_messages)} messages")
        print(results)
        return decoded_messages
