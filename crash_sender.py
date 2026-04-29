import os
import time
import smtplib
from email.message import EmailMessage
import sys

CRASH_DIR = r"C:\Users\elsku\svg_crashes"

EMAIL = "sontapaa.jokulainen@gmail.com"
TO_EMAIL = "sontapaa.jokulainen@gmail.com"

if len(sys.argv) != 2:
    print("Must specify app password!")
    exit(1)

PASSWORD = sys.argv[1]

CHECK_INTERVAL = 60  # seconds

seen_files = set()


def classify_crash(code: str):
    code = code.lower()

    if code == "0":
        return None
    if code == "ff":
        return None
    if code == "c0000409":
        return None

    # interesting ones
    if code == "c0000005":
        return "Access violation (possible UAF / OOB)"
    if code == "c0000374":
        return "Heap corruption (very interesting)"
    if code == "c000001d":
        return "Illegal instruction (corruption?)"
    if code == "c00000fd":
        return "Stack overflow"
    
    # fallback
    return f"Unknown crash ({code})"


def parse_filename(name: str):
    """
    Format:
    RANDOM_RETURNCODE.docx
    or RANDOM_0_zeroreturn.docx
    """
    base = os.path.basename(name)
    parts = base.split("_")

    if len(parts) < 2:
        return None

    code = parts[1].split(".")[0]
    return code.lower()


def send_email(filepath, description):
    msg = EmailMessage()
    msg["Subject"] = f"[FUZZ] Crash detected: {os.path.basename(filepath)}"
    msg["From"] = EMAIL
    msg["To"] = TO_EMAIL

    msg.set_content(f"Crash detected!\n\nFile: {filepath}\nDescription: {description}")

    with open(filepath, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="octet-stream",
            filename=os.path.basename(filepath)
        )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL, PASSWORD)
        smtp.send_message(msg)

    print(f"[+] Sent crash email: {filepath}")


def scan():
    global seen_files

    for fname in os.listdir(CRASH_DIR):
        path = os.path.join(CRASH_DIR, fname)

        if not os.path.isfile(path):
            continue

        if path in seen_files:
            continue

        code = parse_filename(fname)
        if code is None:
            continue

        desc = classify_crash(code)
        if desc is None:
            continue

        send_email(path, desc)
        seen_files.add(path)


def main():
    print("[+] Monitoring crash directory...")
    while True:
        scan()
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()