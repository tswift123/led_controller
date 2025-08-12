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

#--- multiplier and divider to set brightness duty cycle
LED_Dimmer_multiply_Array =  (4,  8,  12, 16)
LED_Dimmer_divide_Array =    (16, 16, 16, 16)

Max_RGBW_Array_Index = const(8)
Max_RGB_Array_Index = const(7)
Max_W_Array_Index = const(1)
Max_Dimmer_Index = const(3)

#--- PWM Setup for RGBW ===
PWM_FREQ = 1000  # Hz
rgbw_pins = {
    "1R": PWM(Pin(0)),
    "1G": PWM(Pin(1)),
    "1B": PWM(Pin(2)),
    "1W": PWM(Pin(3)),
    "2R": PWM(Pin(4)),
    "2G": PWM(Pin(5)),
    "2B": PWM(Pin(6)),
    "2W": PWM(Pin(7)),
    "3R": PWM(Pin(8)),
    "3G": PWM(Pin(9)),
    "3B": PWM(Pin(10)),
    "3W": PWM(Pin(11)),
    "4R": PWM(Pin(12)),
    "4G": PWM(Pin(13)),
    "4B": PWM(Pin(14)),
    "4W": PWM(Pin(15))
}

#--- Set frequency for all channels
for pwm in rgbw_pins.values():
    pwm.freq(PWM_FREQ)

rgbw_brightness = {
    "1R": 3,
    "1G": 3,
    "1B": 3,
    "1W": 3,
    "2R": 3,
    "2G": 3,
    "2B": 3,
    "2W": 3,
    "3R": 3,
    "3G": 3,
    "3B": 3,
    "3W": 3,
    "4R": 3,
    "4G": 3,
    "4B": 3,
    "4W": 3
}


saved_rgbw_values = {
    "1R": 0,
    "1G": 0,
    "1B": 0,
    "1W": 0,
    "2R": 0,
    "2G": 0,
    "2B": 0,
    "2W": 0,
    "3R": 0,
    "3G": 0,
    "3B": 0,
    "3W": 0,
    "4R": 0,
    "4G": 0,
    "4B": 0,
    "4W": 0
}


#------------------------------------------------
#--- set_rgbw
#--- This function sets the RGBW values for a single
#--- Controller.  It takes in the contoller number, 
#--- and the 4 RGBW values in the range of 0 to 255
#--- and the brightness value of 0 to 4.  
#--- It then converts them to the duty cycle for the 
#--- LED channels and set the values into the LED.
#--- This is used by the JSON parsing routine but is
#--- primarily used by the set brightness to change
#--- an LEDs brightness given saved values.
#------------------------------------------------
def set_rgbw(ctrlNum, r, g, b, w, rb, gb, bb, wb):


    #--- Brightness ratios
    mulr = LED_Dimmer_multiply_Array[rb]
    divr = LED_Dimmer_divide_Array[rb]
    mulg = LED_Dimmer_multiply_Array[gb]
    divg = LED_Dimmer_divide_Array[gb]
    mulb = LED_Dimmer_multiply_Array[bb]
    divb = LED_Dimmer_divide_Array[bb]
    mulw = LED_Dimmer_multiply_Array[wb]
    divw = LED_Dimmer_divide_Array[wb]
        
    if 1 == ctrlNum:
        # Convert 0–255 to 0–65535 duty cycle
        rgbw_pins["1R"].duty_u16(int(r / 255 * 65535 * mulr / divr))
        rgbw_pins["1G"].duty_u16(int(g / 255 * 65535 * mulg / divg))
        rgbw_pins["1B"].duty_u16(int(b / 255 * 65535 * mulb / divb))
        rgbw_pins["1W"].duty_u16(int(w / 255 * 65535 * mulw / divw))


    if 2 == ctrlNum:
        # Convert 0–255 to 0–65535 duty cycle
        rgbw_pins["2R"].duty_u16(int(r / 255 * 65535 * mulr / divr))
        rgbw_pins["2G"].duty_u16(int(g / 255 * 65535 * mulg / divg))
        rgbw_pins["2B"].duty_u16(int(b / 255 * 65535 * mulb / divb))
        rgbw_pins["2W"].duty_u16(int(w / 255 * 65535 * mulw / divw))

    elif 3 == ctrlNum:
        # Convert 0–255 to 0–65535 duty cycle
        rgbw_pins["3R"].duty_u16(int(r / 255 * 65535 * mulr / divr))
        rgbw_pins["3G"].duty_u16(int(g / 255 * 65535 * mulg / divg))
        rgbw_pins["3B"].duty_u16(int(b / 255 * 65535 * mulb / divb))
        rgbw_pins["3W"].duty_u16(int(w / 255 * 65535 * mulw / divw))
    else:
        # Convert 0–255 to 0–65535 duty cycle
        rgbw_pins["4R"].duty_u16(int(r / 255 * 65535 * mulr / divr))
        rgbw_pins["4G"].duty_u16(int(g / 255 * 65535 * mulg / divg))
        rgbw_pins["4B"].duty_u16(int(b / 255 * 65535 * mulb / divb))
        rgbw_pins["4W"].duty_u16(int(w / 255 * 65535 * mulw / divw))



#------------------------------------------------
#--- set_rgbw_json
#--- Take in a  JSON string which contains the 
#--- contoller number, and the 4 RGBW values in 
#--- the range of 0 to 255.  Save them and then
#--- call the set routine using existing brightness.
#------------------------------------------------
def set_rgbw_json(ledData):
    if 1 in ledData:
        saved_rgbw_values["1R"] = ledData[1]["R"]
        saved_rgbw_values["1G"] = ledData[1]["G"]
        saved_rgbw_values["1B"] = ledData[1]["B"]
        saved_rgbw_values["1W"] = ledData[1]["W"]

        set_rgbw(1,
                 saved_rgbw_values["1R"],
                 saved_rgbw_values["1G"],
                 saved_rgbw_values["1B"],
                 saved_rgbw_values["1W"],
                 rgbw_brightness["1R"],
                 rgbw_brightness["1G"],
                 rgbw_brightness["1B"],
                 rgbw_brightness["1W"]
                )

    elif 2 in ledData:
        saved_rgbw_values["2R"] = ledData[2]["R"]
        saved_rgbw_values["2G"] = ledData[2]["G"]
        saved_rgbw_values["2B"] = ledData[2]["B"]
        saved_rgbw_values["2W"] = ledData[2]["W"]

        set_rgbw(2,
                 saved_rgbw_values["2R"],
                 saved_rgbw_values["2G"],
                 saved_rgbw_values["2B"],
                 saved_rgbw_values["2W"],
                 rgbw_brightness["2R"],
                 rgbw_brightness["2G"],
                 rgbw_brightness["2B"],
                 rgbw_brightness["2W"]
                )

    elif 3 in ledData:
        saved_rgbw_values["3R"] = ledData[3]["R"]
        saved_rgbw_values["3G"] = ledData[3]["G"]
        saved_rgbw_values["3B"] = ledData[3]["B"]
        saved_rgbw_values["3W"] = ledData[3]["W"]

        set_rgbw(3,
                 saved_rgbw_values["3R"],
                 saved_rgbw_values["3G"],
                 saved_rgbw_values["3B"],
                 saved_rgbw_values["3W"],
                 rgbw_brightness["3R"],
                 rgbw_brightness["3G"],
                 rgbw_brightness["3B"],
                 rgbw_brightness["3W"]
                )

    else:
        saved_rgbw_values["4R"] = ledData[4]["R"]
        saved_rgbw_values["4G"] = ledData[4]["G"]
        saved_rgbw_values["4B"] = ledData[4]["B"]
        saved_rgbw_values["4W"] = ledData[4]["W"]

        set_rgbw(4,
                 saved_rgbw_values["4R"],
                 saved_rgbw_values["4G"],
                 saved_rgbw_values["4B"],
                 saved_rgbw_values["4W"],
                 rgbw_brightness["4R"],
                 rgbw_brightness["4G"],
                 rgbw_brightness["4B"],
                 rgbw_brightness["4W"]
                )



#------------------------------------------------
#--- set_brightness
#--- Take in a json string that has 4 indexes that 
#--- correspond to the 4 channels on a given controller, 
#--- and set the value into the array of brightnesses.  
#--- Then set the LED with the new brightness.
#------------------------------------------------
def set_brightness(jsonData):
    if 1 in jsonData:
        rgbw_brightness["1R"] = jsonData[1]["chan1Index"]
        rgbw_brightness["1G"] = jsonData[1]["chan2Index"]
        rgbw_brightness["1B"] = jsonData[1]["chan3Index"]
        rgbw_brightness["1W"] = jsonData[1]["chan4Index"]

        set_rgbw(1,
                 saved_rgbw_values["1R"],
                 saved_rgbw_values["1G"],
                 saved_rgbw_values["1B"],
                 saved_rgbw_values["1W"],
                 rgbw_brightness["1R"],
                 rgbw_brightness["1G"],
                 rgbw_brightness["1B"],
                 rgbw_brightness["1W"]
                )

    if 2 in jsonData:
        rgbw_brightness["2R"] = jsonData[2]["chan1Index"]
        rgbw_brightness["2G"] = jsonData[2]["chan2Index"]
        rgbw_brightness["2B"] = jsonData[2]["chan3Index"]
        rgbw_brightness["2W"] = jsonData[2]["chan4Index"]

        set_rgbw(2,
                 saved_rgbw_values["2R"],
                 saved_rgbw_values["2G"],
                 saved_rgbw_values["2B"],
                 saved_rgbw_values["2W"],
                 rgbw_brightness["2R"],
                 rgbw_brightness["2G"],
                 rgbw_brightness["2B"],
                 rgbw_brightness["2W"]
                )

    if 3 in jsonData:
        rgbw_brightness["3R"] = jsonData[3]["chan1Index"]
        rgbw_brightness["3G"] = jsonData[3]["chan2Index"]
        rgbw_brightness["3B"] = jsonData[3]["chan3Index"]
        rgbw_brightness["3W"] = jsonData[3]["chan4Index"]

        set_rgbw(3,
                 saved_rgbw_values["3R"],
                 saved_rgbw_values["3G"],
                 saved_rgbw_values["3B"],
                 saved_rgbw_values["3W"],
                 rgbw_brightness["3R"],
                 rgbw_brightness["3G"],
                 rgbw_brightness["3B"],
                 rgbw_brightness["3W"]
                )

    else:
        rgbw_brightness["4R"] = jsonData[4]["chan1Index"]
        rgbw_brightness["4G"] = jsonData[4]["chan2Index"]
        rgbw_brightness["4B"] = jsonData[4]["chan3Index"]
        rgbw_brightness["4W"] = jsonData[4]["chan4Index"]

        set_rgbw(4,
                 saved_rgbw_values["4R"],
                 saved_rgbw_values["4G"],
                 saved_rgbw_values["4B"],
                 saved_rgbw_values["4W"],
                 rgbw_brightness["4R"],
                 rgbw_brightness["4G"],
                 rgbw_brightness["4B"],
                 rgbw_brightness["4W"]
                )



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
#        set_rgbw("Ctrl1", r, g, b, w)
        sleep(duration / steps / 1000)


#--- NeoPixel Setup ----
MATRIX_WIDTH = 32
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

#---------------------------------------------------------------
#--- matrix_snake
#--- A function to make a centipede move across the matrix.
#---------------------------------------------------------------
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


#----------------------------------------------------------------
#--- save_config
#--- Take the passed in json string and writes it to a file
#---
#----------------------------------------------------------------
def save_config(data):

    config_file_path = "config.json"

    filePath = config_file_path
    try:
        with open(filePath, "w") as file:
            ujson.dump(data, file)

    except OSError:
        #--- Failed to open file for write
        print("Failed to open config file for write")
    finally:
        if 'file' in locals():
            file.close()


#----------------------------------------------------------------
#--- save_scene_config
#--- Take the passed in id, name and file path and writes
#--- the name and all LED values and LED brightness out to a file.
#---
#----------------------------------------------------------------
def save_scene_config(sceneID, SceneName, filePath):

    localDict = {}
    ledValues = {}
    ledDims = {}

    ledValues["1R"] = saved_rgbw_values["1R"]
    ledValues["1G"] = saved_rgbw_values["1G"]
    ledValues["1B"] = saved_rgbw_values["1B"]
    ledValues["1W"] = saved_rgbw_values["1W"]
    ledValues["2R"] = saved_rgbw_values["2R"]
    ledValues["2G"] = saved_rgbw_values["2G"]
    ledValues["2B"] = saved_rgbw_values["2B"]
    ledValues["2W"] = saved_rgbw_values["2W"]
    ledValues["3R"] = saved_rgbw_values["3R"]
    ledValues["3G"] = saved_rgbw_values["3G"]
    ledValues["3B"] = saved_rgbw_values["3B"]
    ledValues["3W"] = saved_rgbw_values["3W"]
    ledValues["4R"] = saved_rgbw_values["4R"]
    ledValues["4G"] = saved_rgbw_values["4G"]
    ledValues["4B"] = saved_rgbw_values["4B"]
    ledValues["4W"] = saved_rgbw_values["4W"]

    ledDims["1R"] = rgbw_brightness["1R"]
    ledDims["1G"] = rgbw_brightness["1G"]
    ledDims["1B"] = rgbw_brightness["1B"]
    ledDims["1W"] = rgbw_brightness["1W"]
    ledDims["2R"] = rgbw_brightness["2R"]
    ledDims["2G"] = rgbw_brightness["2G"]
    ledDims["2B"] = rgbw_brightness["2B"]
    ledDims["2W"] = rgbw_brightness["2W"]
    ledDims["3R"] = rgbw_brightness["3R"]
    ledDims["3G"] = rgbw_brightness["3G"]
    ledDims["3B"] = rgbw_brightness["3B"]
    ledDims["3W"] = rgbw_brightness["3W"]
    ledDims["4R"] = rgbw_brightness["4R"]
    ledDims["4G"] = rgbw_brightness["4G"]
    ledDims["4B"] = rgbw_brightness["4B"]
    ledDims["4W"] = rgbw_brightness["4W"]

    cfgData = {}
    cfgData["Name"] = SceneName
    cfgData["leds"] = ledValues
    cfgData["dims"] = ledDims

    localDict[sceneID] = cfgData

    try:
        with open(filePath, "w") as file:
            ujson.dump(localDict, file)

    except OSError:
        #--- Failed to open file for write
        print("Failed to open config file for write")
    finally:
        if 'file' in locals():
            file.close()


#----------------------------------------------------------------
#--- save_scene
#--- Take the passed in json string, parses out the scene name
#--- and and scene ID and writes the name and all LED values and
#--- LED brightness out to a file.
#---
#----------------------------------------------------------------
def save_scene(data):
    if "Scene1Cfg" in data:
        print("Found save scene 1")
        config_file_path = "Scene1.json"
        aName = data["Scene1Cfg"]
        save_scene_config("Scene1", aName, config_file_path)

    if "Scene2Cfg" in data:
        config_file_path = "Scene2.json"
        aName = data["Scene2Cfg"]
        save_scene_config("Scene2", aName, config_file_path)

    if "Scene3Cfg" in data:
        config_file_path = "Scene3.json"
        aName = data["Scene3Cfg"]
        save_scene_config("Scene3", aName, config_file_path)

    if "Scene4Cfg" in data:
        config_file_path = "Scene4.json"
        aName = data["Scene4Cfg"]
        save_scene_config("Scene4", aName, config_file_path)





#----------------------------------------------------------------
#--- default_config_data
#--- Build a structure of config data with default names.
#---
#----------------------------------------------------------------
def default_config_data():

    cfgData = {}
    ctrlData = {}
    ctrlDef = {}
    chanNames = {}
    chanNames["Chan1Name"] = "Chan1"
    chanNames["Chan2Name"] = "Chan2"
    chanNames["Chan3Name"] = "Chan3"
    chanNames["Chan4Name"] = "Chan5"

    ctrlDef["Name"] = "Ctrl1"
    ctrlDef["Type"] = "RGBW"
    ctrlDef["ChanNames"] = chanNames
    ctrlData[1] = ctrlDef

    ctrlDef["Name"] = "Ctrl2"
    ctrlDef["Type"] = "RGBW"
    ctrlDef["ChanNames"] = chanNames
    ctrlData[2] = ctrlDef

    ctrlDef["Name"] = "Ctrl3"
    ctrlDef["Type"] = "RGBW"
    ctrlDef["ChanNames"] = chanNames
    ctrlData[3] = ctrlDef

    ctrlDef["Name"] = "Ctrl4"
    ctrlDef["Type"] = "RGBW"
    ctrlDef["ChanNames"] = chanNames
    ctrlData[4] = ctrlDef

    cfgData["ConfigData"] = ctrlData

    return cfgData


#----------------------------------------------------------------
#--- test_SaveConfig
#--- Build a structure of config data with default names to 
#--- emulate the message coming from the phone app.
#---
#----------------------------------------------------------------
def test_SaveConfig():

    cfgData = {}
    ctrlData = {}
    ctrlDef = {}
    chanNames = {}
    chanNames["Chan1Name"] = "myChan1"
    chanNames["Chan2Name"] = "myChan2"
    chanNames["Chan3Name"] = "myChan3"
    chanNames["Chan4Name"] = "myChan5"

    ctrlDef["Name"] = "myCtrl1"
    ctrlDef["Type"] = "RGBW"
    ctrlDef["ChanNames"] = chanNames
    ctrlData[1] = ctrlDef

    ctrlDef["Name"] = "myCtrl2"
    ctrlDef["Type"] = "RGB+1"
    ctrlDef["ChanNames"] = chanNames
    ctrlData[2] = ctrlDef

    ctrlDef["Name"] = "myCtrl3"
    ctrlDef["Type"] = "4Channel"
    ctrlDef["ChanNames"] = chanNames
    ctrlData[3] = ctrlDef

    ctrlDef["Name"] = "myCtrl4"
    ctrlDef["Type"] = "4Channel"
    ctrlDef["ChanNames"] = chanNames
    ctrlData[4] = ctrlDef

    cfgData["SaveConfig"] = ctrlData

    return cfgData


#----------------------------------------------------------------
#--- read_config
#--- Read the names and config settings from the config file and
#--- load into a json string that will get sent to the phone app.
#---
#----------------------------------------------------------------
def read_config():

    config_file_path = "config.json"

    cfgData = {}

    filePath = config_file_path
    try:
        with open(filePath, "r") as file:
            cfgData = ujson.load(file)

    except OSError:
        #--- Failed to open file for read so no
        #--- config data has been saved. Create
        #--- default data to return.
#        print("Failed to open config file for write")
        cfgData = default_config_data()
    finally:
        if 'file' in locals():
            file.close()

    return cfgData


#----------------------------------------------------------------
#--- set_a_scene
#--- Once the scene data has been read from a file, this function
#--- takes the data and sets all of the brightness and LED values.
#---
#----------------------------------------------------------------
def set_a_scene(data):
    dims = {}
    dims = data["dims"]
    rgbw_brightness["1R"] = dims["1R"]
    rgbw_brightness["1G"] = dims["1G"]
    rgbw_brightness["1B"] = dims["1B"]
    rgbw_brightness["1W"] = dims["1W"]
    rgbw_brightness["2R"] = dims["2R"]
    rgbw_brightness["2G"] = dims["2G"]
    rgbw_brightness["2B"] = dims["2B"]
    rgbw_brightness["2W"] = dims["2W"]
    rgbw_brightness["3R"] = dims["3R"]
    rgbw_brightness["3G"] = dims["3G"]
    rgbw_brightness["3B"] = dims["3B"]
    rgbw_brightness["3W"] = dims["3W"]
    rgbw_brightness["4R"] = dims["4R"]
    rgbw_brightness["4G"] = dims["4G"]
    rgbw_brightness["4B"] = dims["4B"]
    rgbw_brightness["4W"] = dims["4W"]

    ledValues = data["ledValues"]
    #--- Save for later brightness adjustment
    saved_rgbw_values["1R"] = ledValues["1R"]
    saved_rgbw_values["1G"] = ledValues["1G"]
    saved_rgbw_values["1B"] = ledValues["1B"]
    saved_rgbw_values["1W"] = ledValues["1W"]
    saved_rgbw_values["2R"] = ledValues["2R"]
    saved_rgbw_values["2G"] = ledValues["2G"]
    saved_rgbw_values["2B"] = ledValues["2B"]
    saved_rgbw_values["2W"] = ledValues["2W"]
    saved_rgbw_values["3R"] = ledValues["3R"]
    saved_rgbw_values["3G"] = ledValues["3G"]
    saved_rgbw_values["3B"] = ledValues["3B"]
    saved_rgbw_values["3W"] = ledValues["3W"]
    saved_rgbw_values["4R"] = ledValues["4R"]
    saved_rgbw_values["4G"] = ledValues["4G"]
    saved_rgbw_values["4B"] = ledValues["4B"]
    saved_rgbw_values["4W"] = ledValues["4W"]

    #--- Set the actual LEDs
    set_rgbw(   1,
                saved_rgbw_values["1R"],
                saved_rgbw_values["1G"],
                saved_rgbw_values["1B"],
                saved_rgbw_values["1W"],
                rgbw_brightness["1R"],
                rgbw_brightness["1G"],
                rgbw_brightness["1B"],
                rgbw_brightness["1W"]
            )
    
    set_rgbw(   2,
                saved_rgbw_values["2R"],
                saved_rgbw_values["2G"],
                saved_rgbw_values["2B"],
                saved_rgbw_values["2W"],
                rgbw_brightness["2R"],
                rgbw_brightness["2G"],
                rgbw_brightness["2B"],
                rgbw_brightness["2W"]
            )

    set_rgbw(   3,
                saved_rgbw_values["3R"],
                saved_rgbw_values["3G"],
                saved_rgbw_values["3B"],
                saved_rgbw_values["3W"],
                rgbw_brightness["3R"],
                rgbw_brightness["3G"],
                rgbw_brightness["3B"],
                rgbw_brightness["3W"]
            )

    set_rgbw(   4,
                saved_rgbw_values["4R"],
                saved_rgbw_values["4G"],
                saved_rgbw_values["4B"],
                saved_rgbw_values["4W"],
                rgbw_brightness["4R"],
                rgbw_brightness["4G"],
                rgbw_brightness["4B"],
                rgbw_brightness["4W"]
            )



#----------------------------------------------------------------
#--- load_scene
#--- Figure out the scene number from the passed in data and then
#--- retrieve that scene from a file and turn on the LEDs.
#---
#----------------------------------------------------------------
def load_scene(sceneNum):

    if sceneNum == 1:
        print("Found save scene 1")
        config_file_path = "Scene1.json"

    if sceneNum == 2:
        config_file_path = "Scene2.json"

    if sceneNum == 3:
        config_file_path = "Scene3.json"

    if sceneNum == 4:
        config_file_path = "Scene4.json"


    sceneData = {}

    filePath = config_file_path
    try:
        with open(filePath, "r") as file:
            sceneData = ujson.load(file)
            set_a_scene(sceneData)

    except OSError:
        #--- Failed to open file for read so no
        #--- scene data has been saved. Nothing
        #--- to do.
#        print("Failed to open config file for write")
        pass
    finally:
        if 'file' in locals():
            file.close()


#----------------------------------------------------------------
#--- all_off
#--- Turn all LEDs off and set brightness to max.
#---
#----------------------------------------------------------------
def all_off():
    saved_rgbw_values["1R"] = 0
    saved_rgbw_values["1G"] = 0
    saved_rgbw_values["1B"] = 0
    saved_rgbw_values["1W"] = 0
    saved_rgbw_values["2R"] = 0
    saved_rgbw_values["2G"] = 0
    saved_rgbw_values["2B"] = 0
    saved_rgbw_values["2W"] = 0
    saved_rgbw_values["3R"] = 0
    saved_rgbw_values["3G"] = 0
    saved_rgbw_values["3B"] = 0
    saved_rgbw_values["3W"] = 0
    saved_rgbw_values["4R"] = 0
    saved_rgbw_values["4G"] = 0
    saved_rgbw_values["4B"] = 0
    saved_rgbw_values["4W"] = 0
    rgbw_brightness["1R"] = 4
    rgbw_brightness["1G"] = 4
    rgbw_brightness["1B"] = 4
    rgbw_brightness["1W"] = 4
    rgbw_brightness["2R"] = 4
    rgbw_brightness["2G"] = 4
    rgbw_brightness["2B"] = 4
    rgbw_brightness["2W"] = 4
    rgbw_brightness["3R"] = 4
    rgbw_brightness["3G"] = 4
    rgbw_brightness["3B"] = 4
    rgbw_brightness["3W"] = 4
    rgbw_brightness["4R"] = 4
    rgbw_brightness["4G"] = 4
    rgbw_brightness["4B"] = 4
    rgbw_brightness["4W"] = 4
    set_rgbw(1, 0, 0, 0, 0, 4, 4, 4, 4)
    set_rgbw(2, 0, 0, 0, 0, 4, 4, 4, 4)
    set_rgbw(3, 0, 0, 0, 0, 4, 4, 4, 4)
    set_rgbw(4, 0, 0, 0, 0, 4, 4, 4, 4)



#----------------------------------------------------------------
#--- test_SetLED
#--- This function build a json string that emulates what will 
#--- come from the phone app.
#---
#----------------------------------------------------------------
def test_SetLED():
    localDict = {}
    ledValues = {}

    ledValues["R"] = 75
    ledValues["G"] = 75
    ledValues["B"] = 75
    ledValues["W"] = 75

    localDict[1] = ledValues

    return localDict


#----------------------------------------------------------------
#--- test_Brightness
#--- This function build a json string that emulates what will 
#--- come from the phone app.
#---
#----------------------------------------------------------------
def test_Brightness():
    localDict = {}
    ledValues = {}

    ledValues["chan1Index"] = 4
    ledValues["chan2Index"] = 3
    ledValues["chan3Index"] = 2
    ledValues["chan4Index"] = 1

    localDict[1] = ledValues

    return localDict


#----------------------------------------------------------------
#--- test_save_scene
#--- This function build a json string that emulates what will 
#--- come from the phone app.
#---
#----------------------------------------------------------------
def test_SaveScene():
    localDict = {}
    ledValues = {}

    ledValues["chan1Index"] = 4
    ledValues["chan2Index"] = 3
    ledValues["chan3Index"] = 2
    ledValues["chan4Index"] = 1

    localDict[1] = ledValues

    return localDict


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

    if "LEDScene" in localDict:
        load_scene(localDict["LEDScene"])
    elif "SetLED" in localDict:
#        localJson = localDict["SetLED"]
        localJson = test_SetLED()
        set_rgbw_json(localJson)
    elif "SendConfig" in localDict:
        pass
    elif "SetBrightness" in localDict:
#        localJson = localDict["SetBrightness"]
        localJson = test_Brightness()
        set_brightness(localJson)
    elif "SaveScene" in localDict:
#        sceneConfigData = localDict["SaveScene"]
        sceneConfigData = test_SaveScene()
        save_scene(sceneConfigData)
    elif "SaveConfig" in localDict:
        configData = localDict["SaveConfig"]
        configData = test_SaveConfig()
        save_config(configData)

    else:
        # AllOff
        all_off()

    # sceneConfig = {}
    # sceneConfig["Scene1Cfg"] = "NewScene"

    # if localDict['LEDScene'] == 1:
    #     set_rgbw("Ctrl1", 255, 0, 0, 0)
    #     curDuty = rgbw_pins["1R"].duty_u16()
    #     print("Current duty: ", curDuty)
    #     set_rgbw("Ctrl2", 0, 255, 0, 0)
    #     set_rgbw("Ctrl3", 0, 0, 255, 0)
    # elif localDict['LEDScene'] == 2:
    #     load_scene("Scene1Cfg")
    # else:
    #     all_off()


       
    global led_state  # Access the global variable led_state
#    if data == b'toggle\r\n':  # Check if the received data is "toggle"
#        led.value(not led_state)  # Toggle the LED state (on/off)
#        led_state = 1 - led_state  # Update the LED state


#----------------------------------------------------------
#--- main
#----------------------------------------------------------
def main():

    try:
        print("Setting up")

        cfgData = default_config_data()
        save_config(cfgData)

        while True:
            if sp.is_connected():    # Check of a BLE connection is established
                sp.on_write(on_rx)   # Set the callback function for data reception


    except KeyboardInterrupt:
        print("Finished.")
        print("Inner except")
        all_off()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Outer except")


