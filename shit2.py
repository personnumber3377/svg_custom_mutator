import time
from pywinauto import Desktop
import psutil

RULES = [
    ("serious error", "open"),
    ("safe mode", "no"),
]

SCAN_INTERVAL = 1.0


def is_word_process(hwnd):
    try:
        import win32process
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        return "WINWORD.EXE" in psutil.Process(pid).name().upper()
    except:
        return False


def scan():
    desktop = Desktop(backend="uia")

    for window in desktop.windows():
        try:
            title = window.window_text().lower()
        except:
            continue

        if not title:
            continue

        # Optional: filter Word only (recommended)
        '''
        try:
            if "word" not in title:
                continue
        except:
            pass
        '''
        
        print("[WINDOW]", title)

        for dialog_text, button_text in RULES:
            if dialog_text in title or dialog_text in window.window_text().lower():
                print(f"[+] MATCHED: {title}")

                try:
                    # Print all buttons (debug)
                    for child in window.descendants():
                        try:
                            ctrl_type = child.element_info.control_type
                            text = child.window_text().lower()
                        except:
                            continue

                        if ctrl_type == "Button":
                            print("   [BUTTON]", text)

                            if button_text in text:
                                print(f"[+] Clicking: {text}")
                                child.click_input()
                                return

                    # 🔥 fallback: click first button
                    print("[!] No matching button text, clicking first button")
                    buttons = window.descendants(control_type="Button")
                    if buttons:
                        buttons[0].click_input()

                except Exception as e:
                    print("click error:", e)


def main():
    print("[+] pywinauto popup killer running...")

    while True:
        scan()
        time.sleep(SCAN_INTERVAL)


if __name__ == "__main__":
    main()