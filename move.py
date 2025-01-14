from pynput import mouse, keyboard
from threading import Thread
import time

# Track last activity time
last_activity_time = time.time()

# Callback functions for mouse events
def on_mouse_move(x, y):
    global last_activity_time
    last_activity_time = time.time()
    # print(f"Mouse moved to ({x}, {y})")

def on_mouse_click(x, y, button, pressed):
    global last_activity_time
    last_activity_time = time.time()
    if pressed:
        # print(f"Mouse clicked at ({x}, {y}) with {button}")

def on_mouse_scroll(x, y, dx, dy):
    global last_activity_time
    last_activity_time = time.time()
    # print(f"Mouse scrolled at ({x}, {y}) with delta ({dx}, {dy})")

# Callback functions for keyboard events
def on_key_press(key):
    global last_activity_time
    last_activity_time = time.time()
    try:
        # print(f"Key pressed: {key.char}")
    except AttributeError:
        # print(f"Special key pressed: {key}")

def on_key_release(key):
    global last_activity_time
    last_activity_time = time.time()
    # print(f"Key released: {key}")
    if key == keyboard.Key.esc:  # Stop listener on 'Esc' key press
        return False

# Mouse listener thread
def mouse_listener():
    with mouse.Listener(
        on_move=on_mouse_move,
        on_click=on_mouse_click,
        on_scroll=on_mouse_scroll) as listener:
        listener.join()

# Keyboard listener thread
def keyboard_listener():
    with keyboard.Listener(
        on_press=on_key_press,
        on_release=on_key_release) as listener:
        listener.join()

# Activity monitor thread
def activity_monitor():
    global last_activity_time
    while True:
        print(f"last_activity_time ;{ last_activity_time}")
        if time.time() - last_activity_time > 5:  # 5 seconds of inactivity
            print("HHHHHHHHHHHH")
            last_activity_time = time.time()  # Reset last activity time to avoid continuous printing
        time.sleep(1)

# Run mouse, keyboard, and activity monitor in separate threads
if __name__ == "__main__":
    mouse_thread = Thread(target=mouse_listener)
    keyboard_thread = Thread(target=keyboard_listener)
    monitor_thread = Thread(target=activity_monitor)

    mouse_thread.start()
    keyboard_thread.start()
    monitor_thread.start()

    try:
        while True:
            time.sleep(1)  # Keep the main thread running
    except KeyboardInterrupt:
        print("Program stopped.")
