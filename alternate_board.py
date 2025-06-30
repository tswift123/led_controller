from machine import Pin, PWM
from time import sleep, ticks_ms
import neopixel
import NeoMatrix
import math

# === PWM Setup for RGBW ===
PWM_FREQ = 1000  # Hz
rgbw_pins = {
    "R": PWM(Pin(0)),
    "G": PWM(Pin(1)),
    "B": PWM(Pin(2)),
    "W": PWM(Pin(3))
    #"R": PWM(Pin(4)),
    #"G": PWM(Pin(5)),
    #"B": PWM(Pin(6)),
    #"W": PWM(Pin(7))
    #"R": PWM(Pin(8)),
    #"G": PWM(Pin(9)),
    #"B": PWM(Pin(10)),
    #"W": PWM(Pin(11))
    #"R": PWM(Pin(12)),
    #"G": PWM(Pin(13)),
    #"B": PWM(Pin(14)),
    #"W": PWM(Pin(15))
}

# Set frequency for all channels
for pwm in rgbw_pins.values():
    pwm.freq(PWM_FREQ)

def set_rgbw(r, g, b, w):
    # Convert 0–255 to 0–65535 duty cycle
    rgbw_pins["R"].duty_u16(int(r / 255 * 65535))
    rgbw_pins["G"].duty_u16(int(g / 255 * 65535))
    rgbw_pins["B"].duty_u16(int(b / 255 * 65535))
    rgbw_pins["W"].duty_u16(int(w / 255 * 65535))

def fade_rgbw_to(r_target, g_target, b_target, w_target, duration=1000, steps=50):
    r_current = rgbw_pins["R"].duty_u16() // 257
    g_current = rgbw_pins["G"].duty_u16() // 257
    b_current = rgbw_pins["B"].duty_u16() // 257
    w_current = rgbw_pins["W"].duty_u16() // 257

    for i in range(1, steps + 1):
        r = r_current + (r_target - r_current) * i // steps
        g = g_current + (g_target - g_current) * i // steps
        b = b_current + (b_target - b_current) * i // steps
        w = w_current + (w_target - w_current) * i // steps
        set_rgbw(r, g, b, w)
        sleep(duration / steps / 1000)


# === NeoPixel Setup ===
MATRIX_WIDTH = 16
MATRIX_HEIGHT = 32
NUM_PIXELS = MATRIX_WIDTH * MATRIX_HEIGHT
STATE_MACHINE = 0
np = neopixel.NeoPixel(Pin(28), NUM_PIXELS)

# Helper to get linear index for serpentine wiring
def get_index(x, y):
    if y % 2 == 0:
        return y * MATRIX_WIDTH + x
    else:
        return y * MATRIX_WIDTH + (MATRIX_WIDTH - 1 - x)

def fill_matrix_color(r, g, b):
    for y in range(MATRIX_HEIGHT):
        for x in range(MATRIX_WIDTH):
            index = get_index(x, y)
            np[index] = (r, g, b)
    np.write()

def matrix_string(r, g, b):
    for i in range(NUM_PIXELS):
        np[i] = (r, g, b)
        if i >= 1:
            np[i-1] = (0,  0, 0)
        np.write()
        sleep (0.1)


def matrix_snake(r, g, b):
    for i in range(5, NUM_PIXELS):
        np[i] = (255, 0, 0)
        np[i-1] = (0, 255, 0)
        np[i-2] = (0, 255, 0)
        np[i-3] = (0, 255, 0)
        np[i-4] = (0, 255, 0)

        if i-5 >= 1:
            np[i-5] = (0,  0, 0)
        np.write()
        sleep (0.1)


def fade_matrix_to(r_target, g_target, b_target, duration=1000, steps=50):
    r0, g0, b0 = np[0]  # assuming the matrix is uniform
    for i in range(1, steps + 1):
        r = r0 + (r_target - r0) * i // steps
        g = g0 + (g_target - g0) * i // steps
        b = b0 + (b_target - b0) * i // steps
        fill_matrix_color(r, g, b)
        sleep(duration / steps / 1000)

# === Main Program ===
def main():
    try:
        colors = [
            (255, 0, 0, 0),     # Red
            (0, 255, 0, 0),     # Green
            (0, 0, 255, 0),     # Blue
            (0, 0, 0, 255),     # White
            (128, 0, 128, 64),  # Purple + White
            (0, 0, 0, 0)        # Off
        ]

        while True:
            for color in colors:
                print("Color: ", color)
                r, g, b, w = color
#                fade_rgbw_to(r, g, b, w, duration=1500)
#                fade_matrix_to(r, g, b, duration=1500)
#                fill_matrix_color(r, g, b)
#                matrix_snake(r, g, b)
                matrix_string(r, g, b)
#                fill_matrix_color(0, 0, 0)

                sleep(1)

    except KeyboardInterrupt:
        print("Exiting. Turning off LEDs.")
        set_rgbw(0, 0, 0, 0)
        fill_matrix_color(0, 0, 0)

# Entry point
if __name__ == "__main__":
    main()
