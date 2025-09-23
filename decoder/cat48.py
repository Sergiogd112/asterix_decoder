import numpy as np

import pandas as pd
import bitstring

def decode_DSI(data):
    if len(data) < 8:
        raise ValueError("Data length must be at least 8 bits for DSI")
    SAC = data[0:8]
    SIC = data[8:16]
    next_bits = data[16:]
    dsi = (SAC, SIC)
    return dsi, 16


mapper = [("DSI", decode_DSI)]


def DecodeCat48(cat, len, data:bitstring.BitArray):
    if cat != 48:
        raise ValueError("Category must be 48 for DecodeCat48")
    start = 24
    data=bitstring.BitArray(bin=data)
    fspec_block = data[:24]
    data_items_to_decode = [i for i, bit in enumerate(fspec_block) if bit == True]
    decoded = {}
    for item in data_items_to_decode[:1]:
        result, step = mapper[item][1](data[start:])
        decoded[mapper[item][0]] = result
        start += step
    print(f"Decoded CAT48 Data Items: {decoded}")
    return data_items_to_decode
