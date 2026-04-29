from pywinauto import Application
import time

RULES = [
    # ("serious error", "no"),
    # ("serious problem", "open"),
    # ("recover data", "open"),
    ("serious error", "open"),
    ("safe mode", "no"),
    ("the last time you opened", "yes"),
]

SCAN_INTERVAL = 1.0


def scan_word():
    try:
        app = Application(backend="uia").connect(path="WINWORD.EXE")
    except:
        return

    for w in app.windows():
        try:
            title = w.window_text().lower()
        except:
            continue

        print("[WORD WINDOW]", title)

        # 🔥 search ALL descendants (important)
        try:
            elements = w.descendants()
        except:
            continue

        for elem in elements:
            try:
                text = elem.window_text().lower()
                ctrl_type = elem.element_info.control_type
            except:
                continue

            # DEBUG (enable temporarily)
            if text:
                print("   ", ctrl_type, text)

            for dialog_text, button_text in RULES:
                if dialog_text in text:
                    print(f"[+] MATCH FOUND: {text}")

                    # 🔥 find button
                    for btn in elements:
                        try:
                            btn_text = btn.window_text().lower()
                            btn_type = btn.element_info.control_type
                        except:
                            continue

                        if btn_type == "Button" and button_text in btn_text:
                            print(f"[+] Clicking: {btn_text}")
                            btn.click_input()
                            return

    # fallback: click ANY button if dialog detected
    '''
    for w in app.windows():
        try:
            buttons = w.descendants(control_type="Button")
            if buttons:
                print("[!] Fallback click first button")
                buttons[0].click_input()
                return
        except:
            pass
    '''

def main():
    print("[+] Word popup killer (process-bound)...")

    while True:
        scan_word()
        time.sleep(SCAN_INTERVAL)


if __name__ == "__main__":
    main()