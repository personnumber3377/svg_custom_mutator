import pyautogui
import time

# === CONFIG ===

# Polling interval
POLL_INTERVAL = 0.33

# Delay before clicking after detection
CLICK_DELAY = 1.0

# Pixel checks

# x=1098, y=565    and then click on   x=1026, y=567)

# x=1099, y=568


CHECKS = [
    {
        "name": "Dialog1",
        "check_pos": (810, 513), # x=810, y=513 # (807, 517),
        "click_pos": (1101, 620),
    },
    {
        "name": "Dialog2",
        "check_pos": (972, 592),
        "click_pos": (927, 596),
    },
    {
        "name": "Dialog3",
        "check_pos": (1098, 565),
        "click_pos": (1026, 567),
    }
]

# === HELPER ===

def is_blue(pixel):
    r, g, b = pixel
    # "blue-ish" heuristic (tweak if needed)
    return b > 150 and r < 140 and g < 140

# === MAIN LOOP ===

print("[+] Clicker daemon started")

while True:
    try:
        screenshot = pyautogui.screenshot()

        for check in CHECKS:
            pixel = screenshot.getpixel(check["check_pos"])
            print("pixel: "+str(pixel))
            if is_blue(pixel):
                print(f"[!] Detected {check['name']} at {check['check_pos']} -> {pixel}")

                time.sleep(CLICK_DELAY)

                pyautogui.click(check["click_pos"])
                print(f"[+] Clicked {check['click_pos']}")

                # small cooldown so we don't spam clicks
                time.sleep(1.0)

        time.sleep(POLL_INTERVAL)

    except Exception as e:
        print("Error:", e)
        time.sleep(1)
