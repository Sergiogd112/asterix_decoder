import decoderrs
import json

messages = decoderrs.load("Test_Data/datos_asterix_radar.ast")

for i, msg in enumerate(messages[:5]):
    print(f"Message {i}: {json.dumps(msg, indent=2)}")
