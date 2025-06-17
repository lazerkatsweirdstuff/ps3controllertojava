import pygame
import keyboard
import time
import ctypes

SendInput = ctypes.windll.user32.SendInput
PUL = ctypes.POINTER(ctypes.c_ulong)

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("mi", MouseInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

def move_mouse(dx, dy):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.mi = MouseInput(dx, dy, 0, 0x0001, 0, ctypes.pointer(extra))
    command = Input(ctypes.c_ulong(0), ii_)
    SendInput(1, ctypes.pointer(command), ctypes.sizeof(command))

def scroll_mouse(amount):
    ctypes.windll.user32.mouse_event(0x0800, 0, 0, amount, 0)

def mouse_click(down_flag, up_flag, state, pressed):
    if state and not pressed:
        ctypes.windll.user32.mouse_event(down_flag, 0, 0, 0, 0)
        return True
    elif not state and pressed:
        ctypes.windll.user32.mouse_event(up_flag, 0, 0, 0, 0)
        return False
    return pressed

pygame.init()
pygame.joystick.init()

while pygame.joystick.get_count() == 0:
    print("Waiting for controller...")
    time.sleep(1)
    pygame.joystick.quit()
    pygame.joystick.init()

joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"Controller connected: {joystick.get_name()}")

DEADZONE = 0.2
SENSITIVITY = 20
TRIGGER_THRESHOLD = 0.5

l2_pressed = False
r2_pressed = False
t_held = False
esc_held = False
shift_held = False  

while True:
    pygame.event.pump()

    x = joystick.get_axis(0)
    y = joystick.get_axis(1)

    keyboard.press('w') if y < -DEADZONE else keyboard.release('w')
    keyboard.press('s') if y > DEADZONE else keyboard.release('s')
    keyboard.press('a') if x < -DEADZONE else keyboard.release('a')
    keyboard.press('d') if x > DEADZONE else keyboard.release('d')

    rx = joystick.get_axis(2)
    ry = joystick.get_axis(3)

    if abs(rx) > DEADZONE or abs(ry) > DEADZONE:
        move_mouse(int(rx * SENSITIVITY), int(ry * SENSITIVITY))

    l2 = joystick.get_axis(4)
    r2 = joystick.get_axis(5)

    l2_pressed = mouse_click(8, 0x10, l2 > TRIGGER_THRESHOLD, l2_pressed)

    r2_pressed = mouse_click(2, 4, r2 > TRIGGER_THRESHOLD, r2_pressed)

    btn = [joystick.get_button(i) for i in range(joystick.get_numbuttons())]

    keyboard.press('space') if btn[0] else keyboard.release('space')

    if btn[1] and not shift_held:
        keyboard.press('shift')
        shift_held = True
    elif not btn[1] and shift_held:
        keyboard.release('shift')
        shift_held = False

    keyboard.press('e') if btn[2] else keyboard.release('e')

    if btn[7] and not esc_held:
        keyboard.press('esc')
        esc_held = True
    elif not btn[7] and esc_held:
        keyboard.release('esc')
        esc_held = False

    hat = joystick.get_hat(0)
    dpad_x, dpad_y = hat

    keyboard.press('q') if dpad_y == -1 else keyboard.release('q')

    if dpad_x == -1 and not t_held:
        keyboard.press('t')
        t_held = True
    elif dpad_x != -1 and t_held:
        keyboard.release('t')
        t_held = False

    if btn[4]:  
        scroll_mouse(120)
        time.sleep(0.15)
    if btn[5]:  
        scroll_mouse(-120)
        time.sleep(0.15)

    time.sleep(0.01)
