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
import traceback

# === CONFIG ===

# To gather a corpus or to try to find crashes?
# "crash" / "coverage"
MODE = "coverage"

# MODE = "crash"

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


# This is mainly for actual crash discovery since the coverage mechanism hides a lot of crashes for some reason...
NO_COVERAGE_CMD = [
    "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE",
    "/n",
    "/q",
    FUZZ_INPUT
]

# === RUNTIME CONFIG ===
SCROLL_DOWN_AMOUNT = -500
STEPS = 50
TIME_STEP = 0.01
PROC_TIMEOUT = 40.0 # 30.0

# === GLOBAL STATE ===
coverage = set()
interesting_corpus = []
initial_corpus = []

def log(string):
    # Logs a string to the log file...
    fh = open("C:\\Users\\elsku\\svg_mutator_log_thing.txt", "a+")
    fh.write("[LOG] "+str(string)+"\n")
    fh.close()

def wait_until_unlocked(path, timeout=5.0):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with open(path, "ab"):
                return True
        except PermissionError:
            time.sleep(0.2)
    return False

def safe_copy(src, dst, retries=10, delay=0.5):
    for attempt in range(retries):
        try:
            shutil.copy(src, dst)
            return
        except PermissionError:
            print(f"[!] Copy failed (locked), retry {attempt+1}")
            time.sleep(delay)
    print("[!] Copy failed permanently")

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
'''
def zip_docx(folder, output_path):
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as docx:
        for root, dirs, files in os.walk(folder):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, folder)
                docx.write(full_path, rel_path)
'''

def zip_docx(folder, output_path, retries=10, delay=0.5):
    for attempt in range(retries):
        try:
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as docx:
                for root, dirs, files in os.walk(folder):
                    for file in files:
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, folder)
                        docx.write(full_path, rel_path)
            return  # success

        except PermissionError as e:
            print(f"[!] Permission denied writing {output_path}, retry {attempt+1}/{retries}")
            time.sleep(delay)

    raise RuntimeError(f"Failed to write {output_path} after retries")

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

        success = False
        count = 0

        try:

            # mutated = main.mutate_main(base_svg)

            # Also use crossover too...

            if random.random() < 0.3:
                # --- CROSSOVER ---
                if use_interesting and len(interesting_corpus) > 0:
                    other_group = random.choice(interesting_corpus)
                    other_svg = random.choice(other_group)
                else:
                    other_svg = random.choice(initial_corpus)

                try:
                    mutated = main.crossover_svg(base_svg, other_svg)
                except Exception as e:
                    log(str(e)) # Log the exception...
                    log("Back trace:")
                    tb = traceback.format_exc()
                    log(tb)
                    print("Got this exception here on crossover: "+str(e))
                    mutated = base_svg

            else:
                # --- NORMAL MUTATION ---
                try:
                    mutated = main.mutate_main(base_svg)
                except Exception as e:
                    log(str(e)) # Log the exception...
                    log("Back trace:")
                    tb = traceback.format_exc()
                    log(tb)
                    print("Got this exception here on normal mutation: "+str(e))
                    mutated = base_svg

                success = True
        except:
            # continue
            mutated = base_svg


        with open(out_svg, "wb") as fh:
            fh.write(mutated)

        svg_group.append(mutated)
        generated.append(f"media/fuzz{i}.svg")

    return generated, svg_group

# === BUILD DOCX ===
def build_fuzzed_docx():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        print("[+] Unzipping the template docx...")
        unzip_docx(TEMPLATE_DOCX, tmpdir)

        media_dir = tmpdir / WORD_MEDIA_DIR
        print("[+] Generating the svg files...")
        _, svg_group = generate_svgs(media_dir)
        print("[+] Zipping the docx back...")
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

# This is a helper to just kill all the word processes after a crash such that we start from a clean slate...
'''
def kill_all_word():
    print("[!] Killing all WINWORD processes...")
    
    try:
        subprocess.run(
            ["taskkill", "/IM", "WINWORD.EXE", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception as e:
        print("kill error:", e)

    # small delay to let Windows clean up
    time.sleep(0.5)
'''

def kill_all_word():
    print("[!] Killing all WINWORD processes...")

    try:
        subprocess.run(
            ["taskkill", "/IM", "WINWORD.EXE", "/F", "/T"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception as e:
        print("kill error:", e)

    time.sleep(1.0)  # increase delay
    print("[+] Returned from the kill_all_word function!")

# === RUN TARGET ===

def run_program():
    cmd = COVERAGE_CMD if MODE == "coverage" else NO_COVERAGE_CMD

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    crash_detected = False
    crash_info = []

    try:
        start_time = time.time()

        while True:
            # === READ OUTPUT (if available) ===
            if proc.stdout and MODE == "coverage": # Check for coverage mode here...
                line = proc.stdout.readline()
                if line:
                    print(line.strip())

                    if (
                        "Process crashed" in line or
                        "Exception at address" in line or
                        "Access address" in line
                    ):
                        crash_detected = True
                        crash_info.append(line.strip())

            # === UI INTERACTION ===
            handle_popups()
            pyautogui.scroll(SCROLL_DOWN_AMOUNT)

            # === TIMEOUT (CRITICAL IN CRASH MODE) ===
            if time.time() - start_time > PROC_TIMEOUT:
                print("[!] Timeout hit -> killing process")
                proc.kill()
                proc.wait(timeout=2)
                kill_all_word()

                # Timeout = interesting in crash mode
                '''
                if MODE == "crash":
                    dst = (
                        CRASHES_DIRECTORY +
                        str(random.randrange(10_000_000)) +
                        "_timeout.docx"
                    )
                    safe_copy(FUZZ_INPUT, dst)
                '''
                return True

            # === PROCESS EXIT CHECK ===
            if proc.poll() is not None:
                break

            time.sleep(TIME_STEP)

        rc = proc.wait()
        print("return code:", rc)

        # === CRASH DETECTION ===
        if crash_detected:
            print("[!!!] CRASH DETECTED")

            suffix = "_".join(crash_info).replace(" ", "_")[:100]

            dst = (
                CRASHES_DIRECTORY +
                str(random.randrange(10_000_000)) +
                "_" + suffix +
                ".docx"
            )

            safe_copy(FUZZ_INPUT, dst)
            kill_all_word()
            return True

        # === NON-ZERO EXIT ===
        if rc != 0:
            print("[!] abnormal exit")

            dst = (
                CRASHES_DIRECTORY +
                str(random.randrange(10_000_000)) +
                "_" + str(hex(rc))[2:] +
                ".docx"
            )

            safe_copy(FUZZ_INPUT, dst)
            kill_all_word()
            return True

        # If the file returns with zero, but without timing out, then it may also be an indicative of a problem...
        if MODE == "crash": # Only check in the crash mode...
            print("[!] exited even though shouldn't")

            dst = (
                CRASHES_DIRECTORY +
                str(random.randrange(10_000_000)) +
                "_" + str(hex(rc))[2:] + "_zeroreturn" +
                ".docx"
            )

            safe_copy(FUZZ_INPUT, dst)
            kill_all_word()
            return True
        return False

    except Exception as e:
        print("run error:", e)
        proc.kill()
        proc.wait(timeout=2)
        kill_all_word()
        return True

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
    safe_copy(FUZZ_INPUT, dst)

# === FUZZ LOOP ===
def fuzz():
    iteration = 0

    while True:
        print("[+] Killing word")
        kill_all_word()
        print("[+] Waiting for unlocked...")
        wait_until_unlocked(OUTPUT_DOCX)
        print("[+] Building word document...")
        svg_group = build_fuzzed_docx()
        print("[+] Running the microsoft word program...")
        crashed = run_program()
        print("Crashed: "+str(crashed))
        if MODE == "coverage":
            if crashed:
                continue

            print("Checking coverage...")

            if update_coverage_and_is_interesting():
                print("[+] Interesting sample found!")
                print("Coverage size:", len(coverage))

                interesting_corpus.append(svg_group)
                save_docx_copy()

        else:  # CRASH MODE
            # No coverage logic
            pass

        iteration += 1

        if iteration % 10 == 0:
            save_state()

# === MAIN ===
if __name__ == "__main__":
    initial_corpus = load_initial_corpus()
    load_state()
    fuzz()


# This stuff is for the clicker...
# Check if x=735, y=543 is blue and then if yes, then click on x=1206, y=733
