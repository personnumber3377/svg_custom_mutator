import sys
import time
import xml.etree.ElementTree as ET
import faulthandler

faulthandler.enable()

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} file.svg")
        sys.exit(1)

    filename = sys.argv[1]

    print(f"[+] Parsing file: {filename}")

    start = time.time()

    try:
        tree = ET.parse(filename)
        root = tree.getroot()
    except Exception as e:
        print(f"[!] Parse error: {e}")
        return

    print(f"[+] Parsed OK in {time.time() - start:.4f}s")

    print("[+] Iterating nodes...")

    count = 0
    start = time.time()

    try:
        for node in root.iter():
            count += 1

            # Print progress every 1000 nodes
            if count % 1000 == 0:
                print(f"[+] Visited {count} nodes")

    except Exception as e:
        print(f"[!] Iteration error: {e}")
        return

    elapsed = time.time() - start

    print(f"[+] Done. Total nodes: {count}")
    print(f"[+] Iteration took {elapsed:.4f}s")


if __name__ == "__main__":
    main()