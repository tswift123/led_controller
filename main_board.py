#-----------------------------------------------------------------
#--- LED Controller
#---
#--- Author: Tom Swift
#--- Creation Date: 4/30/2024
#--- Copyright: Boondocks LLC
#---
#--- This app will take input from a phone app over bluetooth and
#--- set the colors on the specified channel(s) of the controller.
#-----------------------------------------------------------------
from machine import Pin,PWM
from utime import sleep, ticks_ms
import bluetooth
from ble_simple_peripheral import BLESimplePeripheral
import ujson
import neopixel
import math


#--- Create a Bluetooth Low Energy (BLE) object
ble = bluetooth.BLE()

#--- Create an instance of the BLESimplePeripheral class with the BLE object
sp = BLESimplePeripheral(ble)


#--- PWM Setup for RGBW ===
PWM_FREQ = 1000  # Hz
rgbw_pins = {
    "R": PWM(Pin(12)),
    "G": PWM(Pin(13)),
    "B": PWM(Pin(14)),
    "W": PWM(Pin(15))
}

#--- Set frequency for all channels
for pwm in rgbw_pins.values():
    pwm.freq(PWM_FREQ)


#------------------------------------------------
#--- set_rgbw
#--- Take in an RGBW value in the range of 0 to 255
#--- convert them to the duty cycle for the LED
#--- channels and set the values into the LED.
#------------------------------------------------
def set_rgbw(r, g, b, w):
    # Convert 0–255 to 0–65535 duty cycle
    rgbw_pins["R"].duty_u16(int(r / 255 * 65535))
    rgbw_pins["G"].duty_u16(int(g / 255 * 65535))
    rgbw_pins["B"].duty_u16(int(b / 255 * 65535))
    rgbw_pins["W"].duty_u16(int(w / 255 * 65535))


#------------------------------------------------
#--- fade_rgbw_to
#--- Get the current RGBW values for the LED and
#--- then fade all channels using the number of 
#--- steps, pausing for duration at each step.
#------------------------------------------------
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


#--- NeoPixel Setup ----
MATRIX_WIDTH = 16
MATRIX_HEIGHT = 16
NUM_PIXELS = MATRIX_WIDTH * MATRIX_HEIGHT
np = neopixel.NeoPixel(Pin(28), NUM_PIXELS)


#--------------------------------------------------
#--- get_index
#--- Helper to get linear index for serpentine wiring
#--------------------------------------------------
def get_index(x, y):
    if y % 2 == 0:
        return y * MATRIX_WIDTH + x
    else:
        return y * MATRIX_WIDTH + (MATRIX_WIDTH - 1 - x)


#---------------------------------------------------
#--- fill_matrix_color
#--- This function loops over the entire LED matrix
#--- setting the specified color in each pixel.
#--- This is primarily used to turn off all LEDs.
#---------------------------------------------------
def fill_matrix_color(r, g, b):
    for y in range(MATRIX_HEIGHT):
        for x in range(MATRIX_WIDTH):
            index = get_index(x, y)
            np[index] = (r, g, b)
    np.write()


#---------------------------------------------------
#--- fade_matrix_to
#--- This function fades the LED matrix to the target
#--- RGBW value over the specified number of steps,
#--- pausing for duration at each step.
#---------------------------------------------------
def fade_matrix_to(r_target, g_target, b_target, duration=1000, steps=50):
    r0, g0, b0 = np[0]  # assuming the matrix is uniform
    for i in range(1, steps + 1):
        r = r0 + (r_target - r0) * i // steps
        g = g0 + (g_target - g0) * i // steps
        b = b0 + (b_target - b0) * i // steps
        fill_matrix_color(r, g, b)
        sleep(duration / steps / 1000)


#----------------------------------------------------------------
#--- on_rx
#--- Define a callback function to handle received data
#---
#--- duty_u16 is ratio of duty_cycle / 65535
#--- So we have to convert 0 to 255 into 0 to 65535
#----------------------------------------------------------------
def on_rx(data):
    print("Data received: ", data)  # Print the received data

    localDict = {}

    localDict = ujson.loads(data)
    print("First object: ", localDict)

#    dataStr = data.decode('utf-8')

#    aSecObj = ujson.loads(dataStr)
#    print("Second object: ", aSecObj)

    if localDict['LEDScene'] == 1:
        set_rgbw(255, 0, 0, 0)
    elif localDict['LEDScene'] == 2:
        set_rgbw(0, 0, 0, 0)
    else:
        set_rgbw(0, 0, 0, 0)


       
    global led_state  # Access the global variable led_state
#    if data == b'toggle\r\n':  # Check if the received data is "toggle"
#        led.value(not led_state)  # Toggle the LED state (on/off)
#        led_state = 1 - led_state  # Update the LED state


def main():

    try:
        print("Setting up")

        while True:
            if sp.is_connected():    # Check of a BLE connection is established
                sp.on_write(on_rx)   # Set the callback function for data reception

        print("Finished.")

    except KeyboardInterrupt:
        print("Inner except")
        set_rgbw(0, 0, 0, 0)
        fill_matrix_color(0, 0, 0)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Outer except")


