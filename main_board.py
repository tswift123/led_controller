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
from machine import Pin,PWM,unique_id
from utime import sleep, ticks_ms
import ubluetooth as bluetooth
from led_peripheral import LEDPeripheral
import ujson
import neopixel
import math
import ConfigObj

#--- Create a Bluetooth Low Energy (BLE) object
ble = bluetooth.BLE()

#--- Create an instance of the BLESimplePeripheral class with the BLE object
ledPeripheral = LEDPeripheral(ble)

#--- multiplier and divider to set brightness duty cycle
LED_Dimmer_multiply_Array =  (1,  4,  8, 16)
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

#--- Define an object to hold the configuration settings.
global cfgObj
cfgObj = ConfigObj.ConfigObj()

#------------------------------------------------
#--- set_channel_names 
#--- This function is used to set the names of the
#--- channels of the passed in controller number.
#--- jsonData contains only the channel names dictionary.
#--- jsonData is the dictionary of channel names from the 
#--- json string.
#------------------------------------------------
def set_channel_names(ctrlNum, jsonData):
    
    #--- Since the controller number will have already
    #--- been set, we can use that to control how the
    #--- names will be set. For RGBW and RGB+1 types,
    #--- put the name in the "R" channel.
    localCtrlType = cfgObj.get_ctrl_type(ctrlNum)
    if "RGBW" == localCtrlType:
        if "RGBW" in jsonData:
            cfgObj.set_channel_name(ctrlNum, 'R', jsonData["RGBW"])
        else:
            print("Invalid ctrl type and chan names. Type: ", localCtrlType, " Names: ", jsonData)

    if "RGB+1" == localCtrlType:
        if ("RGB" in jsonData) or ("W" in jsonData):
            if "RGB" in jsonData:
                cfgObj.set_channel_name(ctrlNum, 'R', jsonData["RGB"])
            if 'W' in jsonData:
                cfgObj.set_channel_name(ctrlNum, 'W', jsonData["W"])
        else:
            print("Invalid ctrl type and chan names. Type: ", localCtrlType, " Names: ", jsonData)

    if "4Chan" == localCtrlType:
        if ("R" in jsonData) or ("G" in jsonData) or ("B" in jsonData) or ("W" in jsonData):
            if "R" in jsonData:
                cfgObj.set_channel_name(ctrlNum, 'R', jsonData["R"])
            if "G" in jsonData:
                cfgObj.set_channel_name(ctrlNum, 'G', jsonData["G"])
            if "B" in jsonData:
                cfgObj.set_channel_name(ctrlNum, 'B', jsonData["B"])
            if 'W' in jsonData:
                cfgObj.set_channel_name(ctrlNum, 'W', jsonData["W"])
        else:
            print("Invalid ctrl type and chan names. Type: ", localCtrlType, " Names: ", jsonData)


#------------------------------------------------
#--- set_w
#--- This function sets the brightness  values for a 
#--- single controller.  The assumption is that this
#--- is the +1 channel on an RGB+1 controller. It 
#--- takes in the contoller number, the saved RGB
#--- value (which should be 255), and the brightness 
#--- value of 0 to 3.  
#--- It then converts them to the duty cycle for the 
#--- LED channels and set the values into the LED.
#--- This is used by the JSON parsing routine but is
#--- primarily used by the set brightness to change
#--- an LEDs brightness given saved values.
#--- rb, gb, bb, and wb are the brightness indexes.
#------------------------------------------------
def set_w(ctrlNum, w, wb):

    #--- Brightness ratios
    mulw = LED_Dimmer_multiply_Array[wb]
    divw = LED_Dimmer_divide_Array[wb]
        
    if 1 == ctrlNum:
        # Convert 0–255 to 0–65535 duty cycle
        rgbw_pins["1W"].duty_u16(int(w / 255 * 65535 * mulw / divw))


    if 2 == ctrlNum:
        # Convert 0–255 to 0–65535 duty cycle
        rgbw_pins["2W"].duty_u16(int(w / 255 * 65535 * mulw / divw))

    if 3 == ctrlNum:
        # Convert 0–255 to 0–65535 duty cycle
        rgbw_pins["3W"].duty_u16(int(w / 255 * 65535 * mulw / divw))

    if 4 == ctrlNum:
        # Convert 0–255 to 0–65535 duty cycle
        rgbw_pins["4W"].duty_u16(int(w / 255 * 65535 * mulw / divw))



#------------------------------------------------
#--- set_rgb
#--- This function sets the RGB values for a single
#--- Controller.  It takes in the contoller number, 
#--- and the 3 RGB values in the range of 0 to 255
#--- and the brightness value of 0 to 3.  
#--- It then converts them to the duty cycle for the 
#--- LED channels and set the values into the LED.
#--- This is used by the JSON parsing routine but is
#--- primarily used by the set brightness to change
#--- an LEDs brightness given saved values.
#--- rb, gb, bb, and wb are the brightness indexes.
#------------------------------------------------
def set_rgb(ctrlNum, r, g, b, rb, gb, bb):

    #--- Brightness ratios
    mulr = LED_Dimmer_multiply_Array[rb]
    divr = LED_Dimmer_divide_Array[rb]
    mulg = LED_Dimmer_multiply_Array[gb]
    divg = LED_Dimmer_divide_Array[gb]
    mulb = LED_Dimmer_multiply_Array[bb]
    divb = LED_Dimmer_divide_Array[bb]
        
    if 1 == ctrlNum:
        # Convert 0–255 to 0–65535 duty cycle
        rgbw_pins["1R"].duty_u16(int(r / 255 * 65535 * mulr / divr))
        rgbw_pins["1G"].duty_u16(int(g / 255 * 65535 * mulg / divg))
        rgbw_pins["1B"].duty_u16(int(b / 255 * 65535 * mulb / divb))


    if 2 == ctrlNum:
        # Convert 0–255 to 0–65535 duty cycle
        rgbw_pins["2R"].duty_u16(int(r / 255 * 65535 * mulr / divr))
        rgbw_pins["2G"].duty_u16(int(g / 255 * 65535 * mulg / divg))
        rgbw_pins["2B"].duty_u16(int(b / 255 * 65535 * mulb / divb))

    if 3 == ctrlNum:
        # Convert 0–255 to 0–65535 duty cycle
        rgbw_pins["3R"].duty_u16(int(r / 255 * 65535 * mulr / divr))
        rgbw_pins["3G"].duty_u16(int(g / 255 * 65535 * mulg / divg))
        rgbw_pins["3B"].duty_u16(int(b / 255 * 65535 * mulb / divb))

    if 4 == ctrlNum:
        # Convert 0–255 to 0–65535 duty cycle
        rgbw_pins["4R"].duty_u16(int(r / 255 * 65535 * mulr / divr))
        rgbw_pins["4G"].duty_u16(int(g / 255 * 65535 * mulg / divg))
        rgbw_pins["4B"].duty_u16(int(b / 255 * 65535 * mulb / divb))



#------------------------------------------------
#--- set_rgbw
#--- This function sets the RGBW values for a single
#--- Controller.  It takes in the contoller number, 
#--- and the 4 RGBW values in the range of 0 to 255
#--- and the brightness value of 0 to 3.  
#--- It then converts them to the duty cycle for the 
#--- LED channels and set the values into the LED.
#--- This is used by the JSON parsing routine but is
#--- primarily used by the set brightness to change
#--- an LEDs brightness given saved values.
#--- rb, gb, bb, and wb are the brightness indexes.
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

    if 3 == ctrlNum:
        # Convert 0–255 to 0–65535 duty cycle
        rgbw_pins["3R"].duty_u16(int(r / 255 * 65535 * mulr / divr))
        rgbw_pins["3G"].duty_u16(int(g / 255 * 65535 * mulg / divg))
        rgbw_pins["3B"].duty_u16(int(b / 255 * 65535 * mulb / divb))
        rgbw_pins["3W"].duty_u16(int(w / 255 * 65535 * mulw / divw))

    if 4 == ctrlNum:
        # Convert 0–255 to 0–65535 duty cycle
        rgbw_pins["4R"].duty_u16(int(r / 255 * 65535 * mulr / divr))
        rgbw_pins["4G"].duty_u16(int(g / 255 * 65535 * mulg / divg))
        rgbw_pins["4B"].duty_u16(int(b / 255 * 65535 * mulb / divb))
        rgbw_pins["4W"].duty_u16(int(w / 255 * 65535 * mulw / divw))



#------------------------------------------------
#--- set_4Chan_json
#--- Take in a data dictionary that was built from a
#--- json string that has the controller number and 
#--- one index. The index will be for one of the
#--- 4 channel. Set the brightness of the LED.
#--- This expects only one controller message to be 
#--- in the JSON string with only one channel being set.
#------------------------------------------------
def set_4Chan_json(jsonData):

    #--- Pull out the controller number (first key),
    #--- the channel (first key of inner dictionary),
    #--- and the index value (value of channel key).
    #--- Save the index in the rgbw array and then
    #--- set the LED.
    ctrlNum = next(iter(jsonData))
    chanDict = jsonData[ctrlNum]
    chanKey = next(iter(chanDict))
    chanValue = chanDict[chanKey]
    saved_rgbw_values[ctrlNum + chanKey] = chanValue
    chanBright = rgbw_brightness[ctrlNum + chanKey]

    #--- Brightness ratios
    mulVal = LED_Dimmer_multiply_Array[chanValue]
    divVal = LED_Dimmer_divide_Array[chanValue]
        
    # Convert 0–255 to 0–65535 duty cycle and set the actual LED.
    rgbw_pins[ctrlNum + chanKey].duty_u16(int(chanValue / 255 * 65535 * mulVal / mulVal))


#------------------------------------------------
#--- set_rgb_plus_one_json
#--- Take in a data dictionary that was built from
#--- a JSON string which contains the contoller 
#--- number, and either the 3 RGB values or the single
#--- W value, in the range of 0 to 255.  Save them and 
#--- then call the set LED routine using existing 
#--- brightness. This expects only one controller 
#--- message to be in the JSON string.
#------------------------------------------------
def set_rgb_plus_one_json(jsonData):

    #--- First get the controller number
    ctrlNum = next(iter(jsonData))
    #--- Next get the values dictionary
    chanDict = jsonData[ctrlNum]

    #--- It's either setting the RGB channels or the W 
    #--- channel, not both.
    if 'W' in chanDict:
        saved_rgbw_values[ctrlNum + "W"] = int(chanDict["W"])
        #--- Write to the actual LED
        set_w(int(ctrlNum), 
              saved_rgbw_values[ctrlNum + "W"],
              rgbw_brightness[ctrlNum + "W"]) 
    else:
        #--- Get the 3 RGB values
        saved_rgbw_values[ctrlNum + "R"] = int(chanDict["R"])
        saved_rgbw_values[ctrlNum + "G"] = int(chanDict["G"])
        saved_rgbw_values[ctrlNum + "B"] = int(chanDict["B"])

        set_rgb(int(ctrlNum),
                saved_rgbw_values[ctrlNum + "R"],
                saved_rgbw_values[ctrlNum + "G"],
                saved_rgbw_values[ctrlNum + "B"],
                rgbw_brightness[ctrlNum + "R"],
                rgbw_brightness[ctrlNum + "G"],
                rgbw_brightness[ctrlNum + "B"]
                )


#------------------------------------------------
#--- set_rgbw_json
#--- Take in a data dictionary that was built from
#--- a JSON string which contains the contoller 
#--- number, and the 4 RGBW values in the range of 
#--- 0 to 255.  Save them and then call the set LED
#--- routine using existing brightness. This expects
#--- only one controller message to be in the JSON string.
#------------------------------------------------
def set_rgbw_json(ledData):

    if "1" in ledData:
        saved_rgbw_values["1R"] = int(ledData["1"]["R"])
        saved_rgbw_values["1G"] = int(ledData["1"]["G"])
        saved_rgbw_values["1B"] = int(ledData["1"]["B"])
        saved_rgbw_values["1W"] = int(ledData["1"]["W"])
        print("RGBW 1:", saved_rgbw_values["1R"], saved_rgbw_values["1G"], saved_rgbw_values["1B"], saved_rgbw_values["1W"])

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

    if "2" in ledData:
        saved_rgbw_values["2R"] = int(ledData["2"]["R"])
        saved_rgbw_values["2G"] = int(ledData["2"]["G"])
        saved_rgbw_values["2B"] = int(ledData["2"]["B"])
        saved_rgbw_values["2W"] = int(ledData["2"]["W"])

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

    if "3" in ledData:
        saved_rgbw_values["3R"] = int(ledData["3"]["R"])
        saved_rgbw_values["3G"] = int(ledData["3"]["G"])
        saved_rgbw_values["3B"] = int(ledData["3"]["B"])
        saved_rgbw_values["3W"] = int(ledData["3"]["W"])

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

    if "4" in ledData:
        saved_rgbw_values["4R"] = int(ledData["4"]["R"])
        saved_rgbw_values["4G"] = int(ledData["4"]["G"])
        saved_rgbw_values["4B"] = int(ledData["4"]["B"])
        saved_rgbw_values["4W"] = int(ledData["4"]["W"])

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
#--- set_brightness_4Chan
#--- Take in a data dictionary that was built from a
#--- json string that has the controller number and 
#--- one index. The index will be either for one of 
#--- the 4 channel. Set the brightness of the 
#--- appropriate LED.
#--- This expects only one controller message to be 
#--- in the JSON string with only one channel being set.
#------------------------------------------------
def set_brightness_4Chan(jsonData):

    #--- Pull out the controller number (first key),
    #--- the channel (first key of inner dictionary),
    #--- and the index value (value of channel key).
    #--- Save the index in the brightness array and
    #--- then get the saved RGB value for convenience.
    ctrlNum = next(iter(jsonData))
    chanDict = jsonData[ctrlNum]
    chanKey = next(iter(chanDict))
    chanValue = chanDict[chanKey]
    rgbw_brightness[ctrlNum + chanKey] = chanValue
    rgbw_value = saved_rgbw_values[ctrlNum + chanKey]

    #--- Brightness ratios
    mulw = LED_Dimmer_multiply_Array[chanValue]
    divw = LED_Dimmer_divide_Array[chanValue]
        
    # Convert 0–255 to 0–65535 duty cycle and set the actual LED.
    rgbw_pins[ctrlNum + chanKey].duty_u16(int(rgbw_value / 255 * 65535 * mulw / divw))


#------------------------------------------------
#--- set_brightness_rgb_plus_one
#--- Take in a data dictionary that was built from a
#--- json string that has the controller number and 
#--- one index. The index will be either for the RGB
#--- channel or the +1 (w) channel. Set the brightness
#--- of the appropriate LED.
#--- This expects only one controller message to be 
#--- in the JSON string and either 3 channels or the
#--- single W channel.
#------------------------------------------------
def set_brightness_rgb_plus_one(jsonData):

    ctrlNum = next(iter(jsonData))

    if "W" in jsonData[ctrlNum]:
        #--- First check for +1 channel.
        rgbw_brightness[ctrlNum + "W"] = int(jsonData[ctrlNum]["W"])
        #--- Write to the actual LED
        set_w(int(ctrlNum), 
              saved_rgbw_values[ctrlNum + "W"],
              rgbw_brightness[ctrlNum + "W"]) 
    else:
        #--- Else, is the RGB channel
        set_rgb(int(ctrlNum),
                saved_rgbw_values[ctrlNum + "R"],
                saved_rgbw_values[ctrlNum + "G"],
                saved_rgbw_values[ctrlNum + "B"],
                rgbw_brightness[ctrlNum + "R"],
                rgbw_brightness[ctrlNum + "G"],
                rgbw_brightness[ctrlNum + "B"]
                )


#------------------------------------------------
#--- set_brightness_rgbw
#--- Take in a data dictionary that was built from a
#--- json string that has the controller number and 
#--- 4 indexes that correspond to the 4 channels on 
#--- a given controller. Save the value into the 
#--- array of brightnesses, then set the LED with 
#--- the new brightness.
#--- This expects only one controller message to be 
#--- in the JSON string and all four channels in it.
#------------------------------------------------
def set_brightness_rgbw(jsonData):
    if "1" in jsonData:
        rgbw_brightness["1R"] = int(jsonData["1"]["R"])
        rgbw_brightness["1G"] = int(jsonData["1"]["G"])
        rgbw_brightness["1B"] = int(jsonData["1"]["B"])
        rgbw_brightness["1W"] = int(jsonData["1"]["W"])

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

    if "2" in jsonData:
        rgbw_brightness["2R"] = int(jsonData["2"]["R"])
        rgbw_brightness["2G"] = int(jsonData["2"]["G"])
        rgbw_brightness["2B"] = int(jsonData["2"]["B"])
        rgbw_brightness["2W"] = int(jsonData["2"]["W"])

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

    if "3" in jsonData:
        rgbw_brightness["3R"] = int(jsonData["3"]["R"])
        rgbw_brightness["3G"] = int(jsonData["3"]["G"])
        rgbw_brightness["3B"] = int(jsonData["3"]["B"])
        rgbw_brightness["3W"] = int(jsonData["3"]["W"])

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

    if "4" in jsonData:
        rgbw_brightness["4R"] = int(jsonData["4"]["R"])
        rgbw_brightness["4G"] = int(jsonData["4"]["G"])
        rgbw_brightness["4B"] = int(jsonData["4"]["B"])
        rgbw_brightness["4W"] = int(jsonData["4"]["W"])

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
#--- and scene ID and writes the name and all LED values and
#--- LED brightness out to a file.
#---
#----------------------------------------------------------------
def save_scene(data):
    print("In save scene. Got data: ", data)
    if "1" in data:
        print("Found save scene 1")
        config_file_path = "Scene1.json"
        aName = data["1"]
        save_scene_config("1", aName, config_file_path)

    if "2" in data:
        config_file_path = "Scene2.json"
        aName = data["2"]
        save_scene_config("2", aName, config_file_path)

    if "3" in data:
        config_file_path = "Scene3.json"
        aName = data["3"]
        save_scene_config("3", aName, config_file_path)

    if "4" in data:
        config_file_path = "Scene4.json"
        aName = data["4"]
        save_scene_config("4", aName, config_file_path)




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

    ledValues = data["leds"]
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
        print("Found load scene 1")
        config_file_path = "Scene1.json"
        sceneKey = "1"

    if sceneNum == 2:
        config_file_path = "Scene2.json"
        sceneKey = "2"

    if sceneNum == 3:
        config_file_path = "Scene3.json"
        sceneKey = "3"

    if sceneNum == 4:
        config_file_path = "Scene4.json"
        sceneKey = "4"


    sceneData = {}

    filePath = config_file_path
    try:
        with open(filePath, "r") as file:
            sceneData = ujson.load(file)
            set_a_scene(sceneData[sceneKey])

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
    rgbw_brightness["1R"] = 3
    rgbw_brightness["1G"] = 3
    rgbw_brightness["1B"] = 3
    rgbw_brightness["1W"] = 3
    rgbw_brightness["2R"] = 3
    rgbw_brightness["2G"] = 3
    rgbw_brightness["2B"] = 3
    rgbw_brightness["2W"] = 3
    rgbw_brightness["3R"] = 3
    rgbw_brightness["3G"] = 3
    rgbw_brightness["3B"] = 3
    rgbw_brightness["3W"] = 3
    rgbw_brightness["4R"] = 3
    rgbw_brightness["4G"] = 3
    rgbw_brightness["4B"] = 3
    rgbw_brightness["4W"] = 3
    set_rgbw(1, 0, 0, 0, 0, 3, 3, 3, 3)
    set_rgbw(2, 0, 0, 0, 0, 3, 3, 3, 3)
    set_rgbw(3, 0, 0, 0, 0, 3, 3, 3, 3)
    set_rgbw(4, 0, 0, 0, 0, 3, 3, 3, 3)



#----------------------------------------------------------------
#--- on_sceneSelect_rx
#--- Define a callback function to handle a received command
#--- to select a predefined scene.
#---
#----------------------------------------------------------------
def on_sceneSelect_rx(data):
    print("sceneSelect Data received: ", data)  # Print the received data

    #--- The only data is the scene number.
    localDict = {}
    dataStr = data.decode('utf-8')
    localDict = ujson.loads(dataStr)
 
    if "LEDScene" in localDict:
        load_scene(localDict["LEDScene"])



#----------------------------------------------------------------
#--- on_sceneSave_rx
#--- Define a callback function to handle a received command
#--- to save the current state of LEDs to a file.
#---
#----------------------------------------------------------------
def on_sceneSave_rx(data):
    print("sceneSave Data received: ", data)  # Print the received data

    #--- Get the scene data which is a scene number and a name.
    localDict = {}
    dataStr = data.decode('utf-8')
    localDict = ujson.loads(dataStr)
 
    if "SaveScene" in localDict:
        sceneConfigData = localDict["SaveScene"]
        save_scene(sceneConfigData)



#----------------------------------------------------------------
#--- on_setBright_rx
#--- Define a callback function to handle a received command
#--- to set the brightness of the LEDs.
#--- The first key in the json string is the controller number.
#--- Get the controller type and call the appropriate
#--- brightness setting function.
#--- duty_u16 is ratio of duty_cycle / 65535
#--- So we have to convert 0 to 255 into 0 to 65535
#----------------------------------------------------------------
def on_setBright_rx(data):
    print("setBright Data received: ", data)  # Print the received data

    #--- There should only be a message for a single controller
    localDict = {}
    dataStr = data.decode('utf-8')
    localDict = ujson.loads(dataStr)
    ctrlNum = next(iter(localDict))
    print("First key: ", ctrlNum)

    localCtrType = cfgObj.get_ctrl_type(ctrlNum)

    if 'RGBW' == localCtrType:
        set_brightness_rgbw(localDict)
    elif 'RGB+1' == localCtrType:
        set_brightness_rgb_plus_one(localDict)
    else:  # '4Chan' == localCtrType:
        set_brightness_4Chan(localDict)




#----------------------------------------------------------------
#--- on_allOff_rx
#--- Define a callback function to handle a received command
#--- to turn all LEDs off.
#---
#--- duty_u16 is ratio of duty_cycle / 65535
#--- So we have to convert 0 to 255 into 0 to 65535
#----------------------------------------------------------------
def on_allOff_rx(data):
    print("allOff Data received: ", data)  # Print the received data

    #--- It doesn't matter what the message is, we are just
    #--- turning everything off.
    localDict = {}
    dataStr = data.decode('utf-8')
    localDict = ujson.loads(dataStr)
    all_off()



#----------------------------------------------------------------
#--- on_setLED_rx
#--- Define a callback function to handle received data to set an LED.
#--- The first key in the json string is the controller number.
#--- Get the controller type and call the appropriate
#--- LED setting function.
#--- 
#---
#--- duty_u16 is ratio of duty_cycle / 65535
#--- So we have to convert 0 to 255 into 0 to 65535
#----------------------------------------------------------------
def on_setLED_rx(data):
    print("setLED Data received: ", data)  # Print the received data

    #--- There should only be a message for a single controller
    localDict = {}
    dataStr = data.decode('utf-8')
    localDict = ujson.loads(dataStr)
    ctrlNum = next(iter(localDict))
    print("Controller: ", ctrlNum)

    localCtrType = cfgObj.get_ctrl_type(ctrlNum)

    if 'RGBW' == localCtrType:
        set_rgbw_json(localDict)
    elif 'RGB+1' == localCtrType:
        set_rgb_plus_one_json(localDict)
    else:  # '4Chan' == localCtrType:
        set_4Chan_json(localDict)

    return


#----------------------------------------------------------------
#--- on_setCtrlType_rx
#--- Define a callback function to handle the json message to set
#--- the controller type, name, and channel names.
#--- The first key in the json string is the controller number.
#--- Get the controller type and call the appropriate
#--- LED setting function.
#--- 
#----------------------------------------------------------------
def on_setCtrlType_rx(data):
    print("setCtrlType Data received: ", data)  # Print the received data

    #--- There should only be a message for a single controller
    localDict = {}
    dataStr = data.decode('utf-8')
    localDict = ujson.loads(dataStr)
    ctrlNum = next(iter(localDict))
    cfgObj.set_ctrl_type(ctrlNum, localDict[ctrlNum]['Type'])
    cfgObj.set_ctrl_name(ctrlNum, localDict[ctrlNum]['Name'])
    chanNames = localDict[ctrlNum]['ChanNames']
    set_channel_names(ctrlNum, chanNames)


#----------------------------------------------------------
#--- main
#----------------------------------------------------------
def main():

    try:
        print("Setting up")

        unique_id_bytes = unique_id()

        unique_id_hex = ""

        for b in unique_id_bytes:
            unique_id_hex += "{:02X}".format(b) + ":"

    #--- This pico's UUID
        print("Pico Unique ID: ", unique_id_hex)

        #--- Read the config data from the file if it exists.
        #--- If it doesn't, get the default data. Then write the config
        #--- string to the read characteristic so the app can get it.
        cfgStr = cfgObj.to_json()
#        cfgStr = ujson.dumps(cfgDict)
        cfgBytes = cfgStr.encode('utf-8')
        ledPeripheral.set_local_config(cfgBytes)

        while True:
            if ledPeripheral.is_connected():    # Check if a BLE connection is established
                #--- Make sure callbacks are set.
                if ledPeripheral._setLED_callback is None:
                    print("Connection Ready")
                    ledPeripheral.set_setLED_callback(on_setLED_rx)   # Set the callback function for data reception
                    ledPeripheral.set_allOff_callback(on_allOff_rx)
                    ledPeripheral.set_setBright_callback(on_setBright_rx)
                    ledPeripheral.set_sceneSave_callback(on_sceneSave_rx)
                    ledPeripheral.set_sceneSelect_callback(on_sceneSelect_rx)
                    ledPeripheral.set_setCtrlType_callback(on_setCtrlType_rx)
                sleep(1)

    except KeyboardInterrupt:
        print("Finished.")
        print("Inner except")
        all_off()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Outer except")


