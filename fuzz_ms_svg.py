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
STEPS = 1000
TIME_STEP = 0.01

def run_program():
    # The file is the current directory and then plus fuzzed.docx...
    # proc = subprocess.Popen(["your_program.exe", "input.file"])
    
    proc = subprocess.Popen(["C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE", "C:\\Users\\elsku\\svg_custom_mutator\\fuzzed.docx"], timeout=5)
    
    '''
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
    '''

    try:
        time.sleep(5.0) # Wait 5 seconds for word to open...
        # Now scroll slowly...
        for _ in range(STEPS):
            pyautogui.scroll(SCROLL_DOWN_AMOUNT)
            time.sleep(TIME_STEP)
        rc = proc.wait()

        print("return code:", rc)

        # On Windows, many crash exits show up as large unsigned values or negative signed values.
        if rc != 0:
            print("abnormal exit")
            exit(1)
    except subprocess.TimeoutExpired: # Timeout???
        # Just kill and return normally...
        proc.kill()
        return

# Main fuzzing loop...

def fuzz():
    while True: # Main fuzzing loop...
        # First construct the fuzzed docx
        build_fuzzed_docx()
        # Then try to run the program
        run_program()

if __name__ == "__main__":
    fuzz()
    exit()
