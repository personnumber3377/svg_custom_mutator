import os
import random
import zipfile
import tempfile
import shutil
import signal
import sys
import traceback
import faulthandler
import time

# === IMPORT YOUR MUTATOR ===
import main  # must contain mutate_main(bytes) -> bytes

# === CONFIG ===
DOCX_DIR = "/home/oof/svg_corp/"
TIMEOUT = 3  # seconds
OUTPUT_HANG_FILE = "hang.svg"

# Enable automatic traceback dumping
faulthandler.enable()

# Dump traceback every TIMEOUT seconds (useful for hangs)
faulthandler.dump_traceback_later(TIMEOUT, repeat=True)


class TimeoutException(Exception):
    pass


def timeout_handler(signum, frame):
    raise TimeoutException()


# Setup alarm signal (Linux only)
signal.signal(signal.SIGALRM, timeout_handler)


def unzip_docx(docx_path, extract_dir):
    with zipfile.ZipFile(docx_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)


def find_svgs(root_dir):
    svgs = []
    for root, _, files in os.walk(root_dir):
        for f in files:
            if f.lower().endswith(".svg"):
                svgs.append(os.path.join(root, f))
    return svgs


def test_svg(svg_path):
    print(f"[+] Testing SVG: {svg_path}")

    with open(svg_path, "rb") as f:
        data = f.read()

    try:
        signal.alarm(TIMEOUT)
        start = time.time()

        mutated = main.mutate_main(data)

        elapsed = time.time() - start
        signal.alarm(0)

        print(f"[+] Mutation OK ({elapsed:.2f}s)")

    except TimeoutException:
        print("[!!!] HANG DETECTED")

        # Save problematic input
        with open(OUTPUT_HANG_FILE, "wb") as f:
            f.write(data)

        print(f"[!] Saved hanging SVG to {OUTPUT_HANG_FILE}")

        print("\n[!] Dumping traceback:")
        faulthandler.dump_traceback()

        sys.exit(1)

    except Exception as e:
        signal.alarm(0)
        print(f"[!] Mutation error: {e}")
        traceback.print_exc()


def main_loop():
    docx_files = [
        os.path.join(DOCX_DIR, f)
        for f in os.listdir(DOCX_DIR)
        if f.endswith(".docx")
    ]

    if not docx_files:
        print("No DOCX files found.")
        return

    while True:
        docx = random.choice(docx_files)
        print(f"\n[+] Selected DOCX: {docx}")

        with tempfile.TemporaryDirectory() as tmpdir:
            unzip_docx(docx, tmpdir)

            svgs = find_svgs(tmpdir)

            print(f"[+] Found {len(svgs)} SVGs")

            for svg in svgs:
                test_svg(svg)


# === CTRL-C TRACEBACK ===
def handle_sigint(sig, frame):
    print("\n[!] Ctrl-C detected, dumping traceback:\n")
    faulthandler.dump_traceback()
    sys.exit(1)


signal.signal(signal.SIGINT, handle_sigint)


if __name__ == "__main__":
    main_loop()