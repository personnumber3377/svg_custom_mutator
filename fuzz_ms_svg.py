import zipfile
import shutil
import os
import tempfile
import subprocess
from pathlib import Path
import main
import random
import pyautogui
import time
import pickle

# === CONFIG ===
TEMPLATE_DOCX = "template.docx"
OUTPUT_DOCX   = "fuzzed.docx"
FUZZ_INPUT = "C:\\Users\\elsku\\svg_custom_mutator\\fuzzed.docx"

NUM_SVGS = 220

WORD_MEDIA_DIR = "word/media"

INIT_CORPUS_DIR = "C:\\Users\\elsku\\svg_corpus\\"
INIT_CORPUS_FILES = os.listdir(INIT_CORPUS_DIR)

INTERESTING_DIRECTORY = "C:\\Users\\elsku\\svg_interesting\\"

CRASHES_DIRECTORY = "C:\\Users\\elsku\\svg_crashes\\"

COVERAGE_FILE = "C:\\Users\\elsku\\svg_custom_mutator\\coverage.bin"
STATE_FILE = "C:\\Users\\elsku\\svg_custom_mutator\\state.pkl"

# === COVERAGE CMD (UNCHANGED) ===
COVERAGE_CMD = [
    "C:\\Users\\elsku\\TinyInst\\build\\Release\\litecov.exe",
    "-instrument_module", "MSOSVG.dll",
    "-coverage_file", COVERAGE_FILE,
    "--",
    "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE",
    "/n",
    "/q",
    FUZZ_INPUT
]

# === RUNTIME CONFIG ===
SCROLL_DOWN_AMOUNT = -500
STEPS = 50
TIME_STEP = 0.01
PROC_TIMEOUT = 100.0

# === GLOBAL STATE ===
coverage = set()
interesting_corpus = []
initial_corpus = []

# === LOAD INITIAL CORPUS INTO MEMORY ===
def load_initial_corpus():
    corpus = []
    for f in INIT_CORPUS_FILES:
        try:
            with open(INIT_CORPUS_DIR + f, "rb") as fh:
                corpus.append(fh.read())
        except:
            pass
    print(f"[+] Loaded {len(corpus)} initial SVGs into memory")
    return corpus

# === STATE SAVE / LOAD ===
def save_state():
    with open(STATE_FILE, "wb") as f:
        pickle.dump({
            "coverage": coverage,
            "interesting_corpus": interesting_corpus
        }, f)
    print("[+] State saved")

def load_state():
    global coverage, interesting_corpus

    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "rb") as f:
            data = pickle.load(f)
            coverage = data["coverage"]
            interesting_corpus = data["interesting_corpus"]
        print("[+] Resumed previous session")

# === DOCX UTIL ===
def unzip_docx(docx_path, extract_dir):
    with zipfile.ZipFile(docx_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)

def zip_docx(folder, output_path):
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as docx:
        for root, dirs, files in os.walk(folder):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, folder)
                docx.write(full_path, rel_path)

# === SVG GENERATION ===
def generate_svgs(media_dir):
    generated = []
    svg_group = []

    use_interesting = (
        len(interesting_corpus) > 0 and random.random() < 0.8
    )

    for i in range(NUM_SVGS):
        out_svg = media_dir / f"fuzz{i}.svg"

        if use_interesting:
            base_group = random.choice(interesting_corpus)
            base_svg = random.choice(base_group)
        else:
            base_svg = random.choice(initial_corpus)

        mutated = main.mutate_main(base_svg)

        with open(out_svg, "wb") as fh:
            fh.write(mutated)

        svg_group.append(mutated)
        generated.append(f"media/fuzz{i}.svg")

    return generated, svg_group

# === BUILD DOCX ===
def build_fuzzed_docx():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        unzip_docx(TEMPLATE_DOCX, tmpdir)

        media_dir = tmpdir / WORD_MEDIA_DIR

        _, svg_group = generate_svgs(media_dir)

        zip_docx(tmpdir, OUTPUT_DOCX)

        print(f"[+] Generated {OUTPUT_DOCX}")

        return svg_group

# === POPUP HANDLER (PIXEL BASED, MINIMAL) ===
def handle_popups():
    try:
        # You NEED to calibrate this pixel once
        x, y = 960, 540
        color = pyautogui.screenshot().getpixel((x, y))

        # crude "blue-ish dialog" detection
        if color[2] > 150 and color[0] < 120:
            print("[!] Popup detected, auto-dismiss")
            pyautogui.press("left")
            pyautogui.press("enter")

    except:
        pass

# === RUN TARGET ===
def run_program():
    proc = subprocess.Popen(COVERAGE_CMD)

    try:
        for i in range(STEPS):
            handle_popups()
            pyautogui.scroll(SCROLL_DOWN_AMOUNT)
            time.sleep(TIME_STEP)

        rc = proc.wait(timeout=PROC_TIMEOUT)

        print("return code:", rc)

        if rc != 0:
            print("abnormal exit")
            dst = CRASHES_DIRECTORY + str(random.randrange(10_000_000)) + ".docx"
            shutil.copy(FUZZ_INPUT, dst)
            # exit(1)
            return True # Crash, so skip coverage detection...
    except subprocess.TimeoutExpired:
        proc.kill()
        return False
    return False

# === COVERAGE PARSER ===
def parse_coverage():
    try:
        with open(COVERAGE_FILE, "r") as fh:
            lines = fh.readlines()
    except:
        return set()

    header = "MSOSVG.dll+"
    cov = set()

    for line in lines:
        if line.startswith(header):
            l = line[len(header):].strip()
            try:
                cov.add(int(l, 16))
            except:
                pass

    return cov

# === COVERAGE UPDATE ===
def update_coverage_and_is_interesting():
    global coverage

    current_coverage = parse_coverage()
    new_coverage = current_coverage - coverage

    print("new_coverage:", new_coverage)

    if new_coverage:
        coverage |= new_coverage
        return True

    return False

# === SAVE INTERESTING DOCX ===
def save_docx_copy():
    dst = INTERESTING_DIRECTORY + str(random.randrange(10_000_000)) + ".docx"
    shutil.copy(FUZZ_INPUT, dst)

# === FUZZ LOOP ===
def fuzz():
    iteration = 0

    while True:
        svg_group = build_fuzzed_docx()
        if run_program():
            # Skip coverage detection...
            continue

        print("Checking coverage...")

        if update_coverage_and_is_interesting():
            print("[+] Interesting sample found!")
            print("Coverage size:", len(coverage))

            interesting_corpus.append(svg_group)
            save_docx_copy()

        iteration += 1

        if iteration % 10 == 0:
            save_state()

# === MAIN ===
if __name__ == "__main__":
    initial_corpus = load_initial_corpus()
    load_state()
    fuzz()
