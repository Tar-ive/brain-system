#!/usr/bin/env python3
"""
Decode base64 file to binary.
"""
import base64

# Paste the base64 string here (this is just the beginning as example)
b64_data = """H4sIAAAAAAAAA9Q8XXPbRpJ59q+YiuuKoJekJTtOtnTLraIp2datJPskOZesy4WMgCGJEwgg+KDE
TeW/X/d8zwCg6I3zcHqwiUF3T09PT3dPTw/YlpUheyhoFifZKoxpTStWh9WuqtkmjFmVrLLJJv7m
j/wdwd/333+H/7/84cWx/f/R0fHR0asfXn5z/Oro+xcvvjt+cfTqm6MXR98dv/yGHP2hXg/8a6qa
loR8A/8mW9YP99j7/6d/T8kCNGC8UBpAToUGkGuuASdknm+KlNWMzMpondQsqpuSPXny9KmEIO8B
# ... PUT THE FULL BASE64 STRING HERE ...
"""

# Method 1: Using b64decode (correct way)
try:
    # Decode and save
    decoded_data = base64.b64decode(b64_data)
    with open("eed_system_files.tar.gz", "wb") as f:
        f.write(decoded_data)
    print("Successfully decoded and saved to eed_system_files.tar.gz")
    print(f"File size: {len(decoded_data)} bytes")
except Exception as e:
    print(f"Error: {e}")

# Method 2: Alternative using codecs
import codecs
try:
    with open("eed_system_files_alt.tar.gz", "wb") as f:
        f.write(codecs.decode(b64_data.encode('ascii'), 'base64'))
    print("Alternative method also succeeded")
except Exception as e:
    print(f"Alternative method error: {e}")