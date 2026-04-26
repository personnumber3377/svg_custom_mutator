import pickle
import random
import xml.etree.ElementTree as ET

STATE_FILE = "C:\\Users\\elsku\\svg_custom_mutator\\state.pkl"

def is_valid_svg(data):
    try:
        ET.fromstring(data.decode("utf-8", "ignore"))
        return True
    except:
        return False

def clean_state():
    with open(STATE_FILE, "rb") as f:
        data = pickle.load(f)

    interesting = data["interesting_corpus"]

    total = 0
    fixed = 0

    for group_idx, group in enumerate(interesting):
        valid_svgs = [svg for svg in group if is_valid_svg(svg)]

        if not valid_svgs:
            continue  # nothing we can fix from

        for i in range(len(group)):
            total += 1
            if not is_valid_svg(group[i]):
                fixed += 1
                group[i] = random.choice(valid_svgs)

    print(f"[+] Checked {total} SVGs, fixed {fixed}")

    with open(STATE_FILE, "wb") as f:
        pickle.dump(data, f)

    print("[+] State cleaned and saved")

if __name__ == "__main__":
    clean_state()