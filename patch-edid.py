#!/usr/bin/env python3
with open("original.bin", "rb") as f:
    original = bytearray(f.read())

block0 = bytearray(original[0:128])
block1 = bytearray(original[128:256])
block2 = bytearray(original[256:384])

# Update extension count 1 -> 2
assert block0[0x7E] == 0x02
block0[0x7E] = 0x03

# Recalculate Block 0 checksum
block0[0x7F] = 0
block0[0x7F] = (256 - (sum(block0) % 256)) % 256

# Create CTA-861 block with HDR data copied from DisplayID block
cta = bytearray(128)
cta[0:4] = [0x02, 0x03, 0x23, 0x00]  # CTA header

assert original[0x120:0x123] == bytearray([0x73, 0x1a, 0x00])
cta[4:24] = original[0x120:0x120+20]   # AMD VSDB (FreeSync)

assert original[0xEE:0xEE+4] == bytearray([0xe3, 0x05, 0x80, 0x00])
cta[24:28] = original[0xEE:0xEE+4]   # Colorimetry (BT2020RGB)

cta[28:35] = original[0xF2:0xF2+7]   # HDR Static Metadata

# CTA checksum
cta[127] = (256 - (sum(cta) % 256)) % 256

patched = bytes(block0) + bytes(block1) + bytes(block2) + bytes(cta)
with open("edid-patched-hdr.bin", "wb") as f:
    f.write(patched)

print(f"Patched EDID saved: {len(patched)} bytes")
