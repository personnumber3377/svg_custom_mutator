#!/usr/bin/env python3
import time, hashlib, random, copy, os, sys
from pathlib import Path
import main as mn

BASE = Path(os.getenv("HOME", "/tmp")) / "mut_ipc"
SLOT_PREFIX = "mut_input"

def find_slot():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} INDEX")
        sys.exit(1)

    idx = int(sys.argv[1])
    input_slot = BASE / f"mut_input{idx}"
    output_slot = BASE / f"mut_output{idx}"

    print(f"[client] attached to slot #{idx}")
    print(f"[client] input  → {input_slot}")
    print(f"[client] output → {output_slot}")

    return input_slot, output_slot

def wait_for_change(path, last_hash):
    while True:
        if path.exists():
            data = path.read_bytes()
            h = hashlib.sha1(data).hexdigest()
            if h != last_hash:
                return data, h
        time.sleep(0.001)

def main():
    input_slot, output_slot = find_slot()
    last_hash = ""

    mn.init(random.randrange(2**32))

    while True:
        data, last_hash = wait_for_change(input_slot, last_hash)
        orig = data
        mutated = orig

        # Ensure mutation actually changes input
        for _ in range(10):
            mutated = mn.fuzz(bytearray(orig), None, 10_000_000)
            if mutated != orig:
                break

        output_slot.write_bytes(mutated)
        print(f"[client] wrote mutated output ({len(mutated)} bytes)")

if __name__ == "__main__":
    main()