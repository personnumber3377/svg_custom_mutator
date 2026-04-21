import zipfile
import shutil
import os
import tempfile
import subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import main
import random
import pyautogui
import time


# === CONFIG ===
TEMPLATE_DOCX = "template.docx"
OUTPUT_DOCX   = "fuzzed.docx"

FUZZ_INPUT = "C:\\Users\\elsku\\svg_custom_mutator\\fuzzed.docx"

# SVG_MUTATOR   = ["python3", "main.py"]
# BASE_SVG      = "seed.svg"
NUM_SVGS      = 220

WORD_MEDIA_DIR = "word/media"
RELS_FILE = "word/_rels/document.xml.rels"

# Corpus files...
CORPUS_DIR = "C:\\Users\\elsku\\svg_corpus\\"
CORPUS_FILES = os.listdir(CORPUS_DIR)

# === UTIL ===

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

def mutate_svg(seed_path, output_path):
    # subprocess.run(SVG_MUTATOR + [seed_path, output_path], check=True)
    fh = open(seed_path, "rb")
    data = fh.read()
    fh.close()

    # Now mutate...

    mutated = main.mutate_main(data)

    fh = open(output_path, "wb")
    fh.write(mutated)
    fh.close()
    return

def generate_svgs(media_dir):
    generated = []

    for i in range(NUM_SVGS):
        out_svg = media_dir / f"fuzz{i}.svg"
        # image2.svg
        # out_svg = media_dir / f"image2.svg"

        # Get the base svg file...
        BASE_SVG = random.choice(CORPUS_FILES)
        BASE_SVG = CORPUS_DIR + BASE_SVG # Add the corpus stuff...
        print("base svg: "+str(BASE_SVG))

        mutate_svg(BASE_SVG, str(out_svg))
        generated.append(f"media/fuzz{i}.svg")
        # generated.append(f"media/image2.svg")

    return generated

# === MAIN ===

def build_fuzzed_docx():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # 1. unzip
        unzip_docx(TEMPLATE_DOCX, tmpdir)

        media_dir = tmpdir / WORD_MEDIA_DIR
        rels_path = tmpdir / RELS_FILE

        # 2. generate mutated svgs
        new_svgs = generate_svgs(media_dir)

        # 3. update rels
        # update_relationships(rels_path, new_svgs)

        # 4. zip back
        zip_docx(tmpdir, OUTPUT_DOCX)

        print(f"[+] Generated {OUTPUT_DOCX}")

# Run the program...

SCROLL_DOWN_AMOUNT = -500
STEPS = 50
TIME_STEP = 0.01
PROC_TIMEOUT = 100.0
INITIAL_WAIT_TIME = 100.0

COVERAGE_FILE = "C:\\Users\\elsku\\svg_custom_mutator\\coverage.bin"

COVERAGE_CMD = [
        "C:\\Users\\elsku\\TinyInst\\build\\Release\\litecov.exe",
        "-instrument_module", "MSOSVG.dll",
        "-coverage_file", COVERAGE_FILE, # Coverage output file...
        "--",
        "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE",
        "/n",
        "/q",
        "C:\\Users\\elsku\\svg_custom_mutator\\fuzzed.docx"
    ]

def run_program():
    # The file is the current directory and then plus fuzzed.docx...
    # proc = subprocess.Popen(["your_program.exe", "input.file"])
    
    # proc = subprocess.Popen(["C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE", "C:\\Users\\elsku\\svg_custom_mutator\\fuzzed.docx"])
    
    '''
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
    '''

    '''
    proc = subprocess.Popen([
        "litecov.exe",
        "-instrument_module", "MSOSVG.dll",
        "--",
        "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE",
        "C:\\Users\\elsku\\svg_custom_mutator\\fuzzed.docx"
    ])
    '''

    # Actually get coverage of the process and specifically the MSOSVG.dll file...
    proc = subprocess.Popen(COVERAGE_CMD)

    try:
        # time.sleep(INITIAL_WAIT_TIME) # Wait 5 seconds for word to open...
        # Now scroll slowly...
        for i in range(STEPS):
            print(i)
            pyautogui.scroll(SCROLL_DOWN_AMOUNT)
            time.sleep(TIME_STEP)
        rc = proc.wait(timeout=PROC_TIMEOUT)

        print("return code:", rc)

        # On Windows, many crash exits show up as large unsigned values or negative signed values.
        if rc != 0:
            print("abnormal exit")
            exit(1)
    except subprocess.TimeoutExpired: # Timeout???
        # Just kill and return normally...
        proc.kill()
        return

coverage = set() # Empty set

def parse_coverage():
    fh = open(COVERAGE_FILE, "r")
    lines = fh.readlines()
    fh.close()
    # Now check for "MSOSVG.DLL+"
    # cov = set()
    header = "MSOSVG.DLL+"
    cov = [int(string[len(header):], 16) for string in lines if string.startswith(header)]
    cov = set(cov)
    return cov

# Check if there is new coverage... if there is then this returns True

def update_coverage_and_is_interesting():
    # Check if the coverage file is interesting...
    current_coverage = parse_coverage()

    new_coverage = current_coverage - coverage
    if new_coverage != set(): # Non-empty so new coverage was found...
        global coverage
        coverage = coverage + new_coverage # Add those to the hash map...
        return True
    return False

corpus = []

def add_sample_to_corpus():
    fh = open()

# Main fuzzing loop...
def fuzz():
    while True: # Main fuzzing loop...
        # First construct the fuzzed docx
        build_fuzzed_docx()
        # Then try to run the program
        run_program()
        # Now try to determine whether or not that sample was interesting or not...
        if update_coverage_and_is_interesting():
            # Add the sample to the current corpus...
            # global corpus
            add_sample_to_corpus()
    return

if __name__ == "__main__":
    fuzz()
    exit()
