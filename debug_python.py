#!/usr/bin/env python3
"""
Debug Python message structure.
"""


def debug_python_messages():
    """Debug Python message structure."""
    from decoder.decoder import Decoder

    decoder = Decoder()
    file_path = "Test_Data/datos_asterix_radar.ast"

    results = decoder.load(file_path, max_messages=3)
    print(f"Python returned {len(results)} messages")

    for i, msg in enumerate(results[:3]):
        print(f"\nMessage {i + 1}:")
        print(f"  Type: {type(msg)}")
        if isinstance(msg, tuple):
            print(f"  Tuple length: {len(msg)}")
            print(f"  First element type: {type(msg[0])}")
            print(f"  Second element type: {type(msg[1])}")
            if isinstance(msg[1], dict):
                print(f"  Keys: {list(msg[1].keys())[:5]}...")  # First 5 keys
                print(f"  Category: {msg[1].get('Category')}")
        elif isinstance(msg, dict):
            print(f"  Keys: {list(msg.keys())[:5]}...")  # First 5 keys
            print(f"  Category: {msg.get('Category')}")


if __name__ == "__main__":
    debug_python_messages()
