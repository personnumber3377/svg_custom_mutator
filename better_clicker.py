import time
import win32gui
import win32con

# === CONFIG ===
# (dialog_text_substring, button_text_substring)
RULES = [
    ("safe mode", "no"),
    ("microsoft word", "open"),
    # ("warning", "yes"),
    # ("microsoft word", "cancel"),
]

SCAN_INTERVAL = 1.0  # seconds


# === HELPERS ===

def get_window_text(hwnd):
    try:
        return win32gui.GetWindowText(hwnd)
    except:
        return ""


def window_contains_text(hwnd, substring):
    """Check if substring appears in window title OR any child text"""
    substring = substring.lower()

    # Check title
    title = get_window_text(hwnd).lower()
    print(title)
    if substring in title:
        return True

    # Check children
    found = False

    def enum_children(child_hwnd, _):
        nonlocal found
        if found:
            return
        text = get_window_text(child_hwnd).lower()
        # print(text)
        if substring in text:
            found = True

    try:
        win32gui.EnumChildWindows(hwnd, enum_children, None)
    except:
        pass

    return found


def find_and_click_button(hwnd, button_substring):
    """Find a button inside hwnd and click it"""
    button_substring = button_substring.lower()
    clicked = False

    def enum_children(child_hwnd, _):
        nonlocal clicked
        if clicked:
            return

        try:
            cls = win32gui.GetClassName(child_hwnd)
            text = get_window_text(child_hwnd).lower()
        except:
            print("FUCK"*100)
            return
        print("text: "+str(text))
        if cls == "Button" and button_substring in text:
            print(f"[+] Clicking button: '{text}'")
            try:
                win32gui.SendMessage(child_hwnd, win32con.BM_CLICK, 0, 0)
                clicked = True
            except:
                pass
    print("Clicking..."*100)
    try:
        win32gui.EnumChildWindows(hwnd, enum_children, None)
    except:
        pass

    return clicked


# === MAIN LOOP ===

def scan_once():
    def enum_windows(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return

        for dialog_text, button_text in RULES:
            if window_contains_text(hwnd, dialog_text):
                title = get_window_text(hwnd)
                print(f"[+] Found matching window: '{title}'")

                if find_and_click_button(hwnd, button_text):
                    print(f"[+] Action: '{dialog_text}' → '{button_text}'")

    try:
        win32gui.EnumWindows(enum_windows, None)
    except:
        pass


def main():
    print("[+] Popup handler started")
    while True:
        scan_once()
        time.sleep(SCAN_INTERVAL)


if __name__ == "__main__":
    main()