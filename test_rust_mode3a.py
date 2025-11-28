#!/usr/bin/env python3

import decoderrs
import json

# Test with the same file
results = decoderrs.load(
    "Test_Data/datos_asterix_radar.ast", 41.0, 2.0, 100, max_messages=10
)

# Find CAT48 messages with Mode-3/A
cat48_count = 0
for i, result in enumerate(results):
    if result.get("Category") == 48 and "Mode-3/A Code" in result:
        cat48_count += 1
        print(f"CAT48 Message {cat48_count}: {result['Mode-3/A Code']}")
        if cat48_count >= 3:
            break
