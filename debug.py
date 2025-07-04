from pynput import mouse
from pynput import keyboard
import pyautogui

x = 0
y = 0


def on_move(nx, ny):
    global x, y
    x, y = int(nx), int(ny)


def on_press(key):
    try:
        if key.char == "=":
            r, g, b = pyautogui.pixel(x * 2, y * 2)  # type: ignore
            print(f"RGB values at ({x}, {y}): ({r}, {g}, {b})")
    except AttributeError:
        pass


mouse_listener = mouse.Listener(on_move=on_move)
mouse_listener.start()

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
