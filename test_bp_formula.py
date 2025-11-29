#!/usr/bin/env python3

import bitstring

# Let's manually create the exact bit pattern that should give BP = 1013.6
# BP = raw * 0.1 + 800.0
# raw = (1013.6 - 800.0) / 0.1 = 2136

target_raw = 2136
print(f"Target raw value for BP=1013.6: {target_raw}")
print(f"Target raw in binary (12 bits): {target_raw:012b}")

# Now let's see what this looks like in 16 bits with the 4-bit offset
# According to C# code: array3[i] = array2[i+4] for i=0..11
# This means bits 4-15 of the 16-bit value contain our 12-bit value
# So we need to shift left by 4 bits

pressure_16bit = target_raw << 4
print(f"16-bit value (shifted left by 4): {pressure_16bit:016b} ({pressure_16bit})")

# Now let's test the extraction
extracted = (pressure_16bit >> 4) & 0xFFF
print(f"Extracted back: {extracted} (should be {target_raw})")
print(f"Calculated BP: {extracted * 0.1 + 800:.1f}")

# Let's also test what the current Python code would get
print(f"Python extraction result: {extracted * 0.1 + 800:.1f}")

# Now let's check what raw value would give 942.8 (what Python currently gets)
python_bp = 942.8
python_raw = (python_bp - 800.0) / 0.1
print(f"\nPython raw value for BP=942.8: {python_raw}")
print(f"Python raw in binary (12 bits): {int(python_raw):012b}")

python_16bit = int(python_raw) << 4
print(f"Python 16-bit value: {python_16bit:016b} ({python_16bit})")
