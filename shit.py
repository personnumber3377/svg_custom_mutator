import time
import win32gui
import win32con
import win32api

RULES = [
    ("serious error", "open"),  # THIS will catch your popup
    ("safe mode", "no"),
]

SCAN_INTERVAL = 1.0


def get_text(hwnd):
    try:
        return win32gui.GetWindowText(hwnd)
    except:
        return ""


def window_contains_text(hwnd, substring):
    substring = substring.lower()

    # check title
    title_thing = get_text(hwnd).lower()
    if substring in title_thing:
        return True

    # check children
    found = False

    def enum_child(child, _):
        nonlocal found
        if found:
            return
        text = get_text(child).lower()
        print("text: "+str(text))
        if substring in text:
            found = True

    try:
        win32gui.EnumChildWindows(hwnd, enum_child, None)
    except:
        pass

    return found


def click_button(hwnd, button_substring):
    button_substring = button_substring.lower()
    clicked = False

    def enum_child(child, _):
        nonlocal clicked
        if clicked:
            return

        try:
            cls = win32gui.GetClassName(child)
            text = get_text(child).lower()
        except:
            return

        # DEBUG (you should enable this once)
        print(cls, text)

        if cls == "Button" and button_substring in text:
            print(f"[+] Found button: {text}")

            try:
                # Bring window to foreground (important sometimes)
                win32gui.SetForegroundWindow(hwnd)

                # Try normal click
                win32gui.SendMessage(child, win32con.BM_CLICK, 0, 0)

                # Fallback (more aggressive)
                win32api.PostMessage(child, win32con.WM_LBUTTONDOWN, 0, 0)
                win32api.PostMessage(child, win32con.WM_LBUTTONUP, 0, 0)

                clicked = True
            except Exception as e:
                print("click error:", e)

    try:
        win32gui.EnumChildWindows(hwnd, enum_child, None)
    except:
        pass

    return clicked


def scan():
    def enum_windows(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return

        cls = win32gui.GetClassName(hwnd)

        # 🔥 ONLY look at dialog windows
        if cls != "#32770":
            return

        title = get_text(hwnd)
        print(f"[DIALOG] {title}")

        for dialog_text, button_text in RULES:
            if window_contains_text(hwnd, dialog_text):
                print(f"[+] MATCHED WINDOW: {title}")

                if click_button(hwnd, button_text):
                    print(f"[+] CLICKED: {button_text}")

    win32gui.EnumWindows(enum_windows, None)


def main():
    print("[+] Popup killer running...")
    while True:
        scan()
        time.sleep(SCAN_INTERVAL)


if __name__ == "__main__":
    main()