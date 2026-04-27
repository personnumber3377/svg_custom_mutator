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

# Check if x=735, y=543 is blue and then if yes, then click on x=1206, y=733

# x=1171, y=642)   and then x=1066, y=644

# x=955, y=700  and if yes, then x=846, y=685

# Point(x=816, y=522) and then if yes, then   Point(x=1136, y=616)

# Then the recover data stuff is Point(x=984, y=592)   and then Point(x=890, y=600)

CHECKS = [
    {
        "name": "Fuzz machine 1",
        "check_pos": (816, 522), # (810, 513), # x=810, y=513 # (807, 517),
        "click_pos": (1136, 616), # (1101, 620),
    },
    {
        "name": "Fuzz machine 2",
        "check_pos": (984, 592), # (810, 513), # x=810, y=513 # (807, 517),
        "click_pos": (890, 600), # (1101, 620),
    },
    {
        "name": "Haluatko silti avata sen...",
        "check_pos": (1171, 642), # (810, 513), # x=810, y=513 # (807, 517),
        "click_pos": (1066, 644), # (1101, 620),
    },
    {
        "name": "Palauttaa tiedot jne..",
        "check_pos": (955, 700), # (810, 513), # x=810, y=513 # (807, 517),
        "click_pos": (846, 685), # (1101, 620),
    },
    {
        "name": "Dialog1",
        "check_pos": (781, 440), # (810, 513), # x=810, y=513 # (807, 517),
        "click_pos": (1079, 541), # (1101, 620),
    },
    {
        "name": "Dialogpaska",
        "check_pos": (810, 513), # x=810, y=513 # (807, 517),
        "click_pos": (1101, 620),
    },
    {
        "name": "Dialogpaska",
        "check_pos": (810, 513+60), # x=810, y=513 # (807, 517),
        "click_pos": (1101, 620+60),
    },
    {
        "name": "Dialog2",
        "check_pos": (956, 653), # (972, 592),
        "click_pos": (927, 660), # (927, 596),
    },
    {
        "name": "Dialog3",
        "check_pos": (1098, 565),
        "click_pos": (1026, 567),
    },
    {
        "name": "Dialog3",
        "check_pos": (1098, 565+60),
        "click_pos": (1026, 567+60),
    },
    {
        "name": "Dialog3fefeffefe",
        "check_pos": (735, 543),
        "click_pos": (1206, 733),
    },
    {
        "name": "fefefefeefeffe",
        "check_pos": (1167, 643),
        "click_pos": (1170, 642),
    }
]

# x=1167, y=643 blue then click on x=1170, y=642

# 1101, y=628
# 1101, y=628

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
