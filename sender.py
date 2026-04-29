import time
import smtplib
import matplotlib.pyplot as plt
from email.message import EmailMessage
import sys

LOG_FILE = "coverage_log.csv"
OUTPUT_IMAGE = "coverage.png"

EMAIL = "sontapaa.jokulainen@gmail.com"
if len(sys.argv) != 2: # Must specify app password...
    print("Must specify app password on command line!!!")
    exit(1)

PASSWORD = str(sys.argv[1]) # "your_app_password"  # IMPORTANT (see below)
TO_EMAIL = "sontapaa.jokulainen@gmail.com"

def read_data():
    xs = []
    cov = []
    execs = []

    with open(LOG_FILE, "r") as f:
        for line in f:
            try:
                t, c, e = line.strip().split(",")
                xs.append(int(t))
                cov.append(int(c))
                execs.append(int(e))
            except:
                continue

    # normalize coverage (optional)
    if cov:
        base = cov[0]
        cov = [c - base for c in cov]

    return xs, cov, execs

def plot_graph(xs, cov, execs):
    plt.figure(figsize=(12, 8))

    # --- Coverage subplot ---
    plt.subplot(2, 1, 1)
    plt.plot(xs, cov)
    plt.xlabel("Time (seconds)")
    plt.ylabel("Coverage")
    plt.title("Coverage Over Time")
    plt.grid()

    # --- Execution subplot ---
    plt.subplot(2, 1, 2)
    plt.plot(xs, execs)
    plt.xlabel("Time (seconds)")
    plt.ylabel("Executions")
    plt.title("Executions Over Time")
    plt.grid()

    plt.tight_layout()
    plt.savefig(OUTPUT_IMAGE)
    plt.close()

def send_email():
    msg = EmailMessage()
    msg["Subject"] = "Fuzzing Coverage Update"
    msg["From"] = EMAIL
    msg["To"] = TO_EMAIL

    msg.set_content("See attached coverage graph.")

    with open(OUTPUT_IMAGE, "rb") as f:
        msg.add_attachment(f.read(), maintype="image", subtype="png", filename="coverage.png")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL, PASSWORD)
        smtp.send_message(msg)

def main():
    xs, cov, execs = read_data()
    if not xs:
        return

    plot_graph(xs, cov, execs)
    send_email()
    print("[+] Email sent")

WAIT_AMOUNT = 60*60 # 60*60*3 # Send email every three hours...

if __name__ == "__main__":
    while True:
        main()
        print("[+] Waiting for "+str(WAIT_AMOUNT)+" seconds...")
        time.sleep(WAIT_AMOUNT)

