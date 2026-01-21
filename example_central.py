#----------------------------------------------------------------
#--- example_central.py ---
#--- Example of a central device that connects to the peripheral.
#--- It will read from one characteristic and write to another.
#--- The write data is a json string encoded to bytes.
#----------------------------------------------------------------

from micropython import const

import uasyncio as asyncio
import aioble
import bluetooth
import json

import random
import struct

# org.bluetooth.service.environmental_sensing
_ENV_SENSE_UUID = bluetooth.UUID(0x181A)
# org.bluetooth.characteristic.temperature
_ENV_SENSE_TEMP_UUID = bluetooth.UUID(0x2A6E)

#--- Define service and characteristics UUIDs to match peripheral
SERVICE_UUID = bluetooth.UUID("b00d0c55-1111-2222-3333-0000b00d0c50")
CONFIG_CHAR_UUID = bluetooth.UUID("b00d0c55-1111-2222-3333-0000b00d0c51")
SET_LED_CHAR_UUID = bluetooth.UUID("b00d0c55-1111-2222-3333-0000b00d0c52")
SET_BRIGHT_CHAR_UUID = bluetooth.UUID("b00d0c55-1111-2222-3333-0000b00d0c53")
ALL_OFF_CHAR_UUID = bluetooth.UUID("b00d0c55-1111-2222-3333-0000b00d0c54")
SELECT_SCENE_CHAR_UUID = bluetooth.UUID("b00d0c55-1111-2222-3333-0000b00d0c55")
SAVE_SCENE_CHAR_UUID = bluetooth.UUID("b00d0c55-1111-2222-3333-0000b00d0c56")
SET_CTRL_TYPE_CHAR_UUID = bluetooth.UUID("b00d0c55-1111-2222-3333-0000b00d0c57")

SCAN_DURATION_MS = const(5000)
SCAN_INTERVAL_US = const(30000)
SCAN_WINDOW_US = const(30000)

# MAX_MTU = const(100)
# MAX_CHUNK = const(MAX_MTU - 3)
# MAX_CHUNKS = const(10)
# MAX_DATA = const(MAX_CHUNK * MAX_CHUNKS)


#----------------------------------------------------------------
#--- rgbw_brightness_string
#--- Take a controller number and brightness value and build a 
#--- short json string to set an LED.
#----------------------------------------------------------------
def rgbw_brightness_string(ctrlNum, val):
    #--- {'1':{'W':'255'}}
    chanVal = {}
    ctrlStr = {}
    chanVal['R'] = val
    chanVal['G'] = val
    chanVal['B'] = val
    chanVal['W'] = val
    ctrlStr[ctrlNum] = chanVal
    cfgDataStr = json.dumps(ctrlStr)
    bcfgDataStr = cfgDataStr.encode('utf-8')

    return bcfgDataStr


#----------------------------------------------------------------
#--- rgbw_1_brightness_string
#--- Take a controller number and brightness value and build a 
#--- short json string to set the brightness of the RGB LED of
#--- an RGB+1 controller..
#----------------------------------------------------------------
def rgb_1_brightness_string(ctrlNum, val):
    #--- {'1':{'W':'255'}}
    chanVal = {}
    ctrlStr = {}
    chanVal['R'] = val
    chanVal['G'] = val
    chanVal['B'] = val
    ctrlStr[ctrlNum] = chanVal
    cfgDataStr = json.dumps(ctrlStr)
    bcfgDataStr = cfgDataStr.encode('utf-8')

    return bcfgDataStr


#----------------------------------------------------------------
#--- rgbw_1_brightness_string
#--- Take a controller number and brightness value and build a 
#--- short json string to set the brightness of the RGB LED of
#--- an RGB+1 controller. The assumption is that chanNum is a
#--- character.
#----------------------------------------------------------------
def fourChan_brightness_string(ctrlNum, chanNum, val):
    #--- {'1':{'W':'255'}}
    chanVal = {}
    ctrlStr = {}
    chanVal[chanNum] = val
    ctrlStr[ctrlNum] = chanVal
    cfgDataStr = json.dumps(ctrlStr)
    bcfgDataStr = cfgDataStr.encode('utf-8')

    return bcfgDataStr


#----------------------------------------------------------------
#--- one_led_string
#--- Take a controller number, channel, and value and build a 
#--- short json string to set an LED.
#----------------------------------------------------------------
def one_led_string(ctrlNum, chan, val):
    #--- {'1':{'W':'255'}}
    chanVal = {}
    ctrlStr = {}
    chanVal[chan] = val
    ctrlStr[ctrlNum] = chanVal
    cfgDataStr = json.dumps(ctrlStr)
    bcfgDataStr = cfgDataStr.encode('utf-8')

    return bcfgDataStr


#----------------------------------------------------------------
#--- save_scene_string
#--- Build the short json string to save the current state of the LEDs.
#----------------------------------------------------------------
def save_scene_string(sceneNum):
    ctrlStr = {}
    sceneStr = {}
    sceneStr[sceneNum] = "ASceneName"
    cfgDataStr = json.dumps(sceneStr)
    bcfgDataStr = cfgDataStr.encode('utf-8')

    return bcfgDataStr


#----------------------------------------------------------------
#--- select_scene_string
#--- Build the short json string to select a previously stored scene.
#----------------------------------------------------------------
def select_scene_string(sceneNum):
    ctrlStr = {}
    ctrlStr["LEDScene"] = sceneNum
    cfgDataStr = json.dumps(ctrlStr)
    bcfgDataStr = cfgDataStr.encode('utf-8')

    return bcfgDataStr


#----------------------------------------------------------------
#--- all_off_string
#--- Build the short json string to turn off all LEDs.
#----------------------------------------------------------------
def all_off_string():
    #--- {'1':'off'}
    ctrlStr = {}
    ctrlStr[1] = 'off'
    cfgDataStr = json.dumps(ctrlStr)
    bcfgDataStr = cfgDataStr.encode('utf-8')

    return bcfgDataStr


#----------------------------------------------------------------
#--- set_ctrl_type_string
#--- Build the json message to set the controller type, name,
#--- and channel names for a specified controller number.  Four
#--- options are implemented here so that the four controllers
#--- can be set to different types.
#----------------------------------------------------------------
def set_ctrl_type_string(ctrlNum):

    chanNames = {}
    ctrlAttribs = {}
    ctrl_dict = {}

    if (1 == ctrlNum) or (4 == ctrlNum):
        #--- {'1':{'Type: 'RGBW', 'Name': 'CabCtrl', 'ChanNames': chanNames}}
        chanNames['RGBW'] = "Cabinets"
        ctrlAttribs['Name'] = "CabCtrl"
        ctrlAttribs['Type'] = 'RGBW'
        ctrlAttribs['ChanNames'] = chanNames
        ctrl_dict[ctrlNum] = ctrlAttribs
    elif 2 == ctrlNum:
        #--- {'2':{'Type: 'RGB+1', 'Name': 'LeftCtrl', 'ChanNames': {'RGB': Cabinets, 'W': 'LeftSpot'}}}
        chanNames['RGB'] = "Cabinets"
        chanNames['W'] = 'LeftSpot'
        ctrlAttribs['Name'] = "LeftCtrl"
        ctrlAttribs['Type'] = 'RGB+1'
        ctrlAttribs['ChanNames'] = chanNames
        ctrl_dict[2] = ctrlAttribs
    elif 3 == ctrlNum:
        #--- {'3':{'Type: '4Chan', 'Name': 'SpotCtrl', 'ChanNames': {'R': 'Spot1', 'G': 'Spot2', 'B': 'Spot3', 'W': 'Spot4'}}}
        chanNames['R'] = "Spot1"
        chanNames['G'] = 'Spot2'
        chanNames['B'] = 'Spot3'
        chanNames['W'] = 'Spot4'
        ctrlAttribs['Name'] = "SpotCtrl"
        ctrlAttribs['Type'] = '4Chan'
        ctrlAttribs['ChanNames'] = chanNames
        ctrl_dict[3] = ctrlAttribs
    else:
        print("Invalid controller number: ", ctrlNum)

    cfgDataStr = json.dumps(ctrl_dict)
    bcfgDataStr = cfgDataStr.encode('utf-8')

    return bcfgDataStr


#----------------------------------------------------------------
#--- build_short_json_string
#--- Build a short json string to test the write functionality
#--- Set a single LED for a controller.  This assumes that
#--- controller 1 and 4 are RGBW, 2 is RGB+1, and 3 is 4Chan.
#----------------------------------------------------------------
def build_short_json_string(ctrlVal):
    #--- {'1':{'W':'255'}}
    chanVal = {}
    ctrlStr = {}
    if 1 == ctrlVal:
        chanVal["R"] = "255"
        chanVal["G"] = "000"
        chanVal["B"] = "067"
        chanVal["W"] = "000"
    elif 2 == ctrlVal:
        chanVal["R"] = "255"
        chanVal["G"] = "000"
        chanVal["B"] = "038"
#        chanVal["W"] = "000"
    elif 3 == ctrlVal:
        chanVal["R"] = "255"
#        chanVal["G"] = "000"
#        chanVal["B"] = "255"
#        chanVal["W"] = "000"
    else:
        chanVal["R"] = "255"
        chanVal["G"] = "000"
        chanVal["B"] = "041"
        chanVal["W"] = "000"

    ctrlStr[ctrlVal] = chanVal
    cfgDataStr = json.dumps(ctrlStr)
    bcfgDataStr = cfgDataStr.encode('utf-8')

    return bcfgDataStr


#----------------------------------------------------------------
#--- build_json_string
#--- Build a structure of config data with default names to 
#--- emulate the message coming from the phone app.  Convert to
#--- a json string and encoded it to bytes.
#----------------------------------------------------------------
def build_json_string():

    cfgData = {}
    ctrlData = {}
    ctrlDef = {}
    chanNames = {}
    chanNames["Chan1Name"] = "myChan1"
    chanNames["Chan2Name"] = "myChan2"
    chanNames["Chan3Name"] = "myChan3"
    chanNames["Chan4Name"] = "myChan5"

    ctrlDef["Nm"] = "my"
#    ctrlDef["Type"] = "RGBW"
#    ctrlDef["ChanNames"] = chanNames
    ctrlData[1] = ctrlDef

    # ctrlDef["Name"] = "myCtrl2"
    # ctrlDef["Type"] = "RGB+1"
    # ctrlDef["ChanNames"] = chanNames
    # ctrlData[2] = ctrlDef

    # ctrlDef["Name"] = "myCtrl3"
    # ctrlDef["Type"] = "4Channel"
    # ctrlDef["ChanNames"] = chanNames
    # ctrlData[3] = ctrlDef

    # ctrlDef["Name"] = "myCtrl4"
    # ctrlDef["Type"] = "4Channel"
    # ctrlDef["ChanNames"] = chanNames
    # ctrlData[4] = ctrlDef

    cfgData["SaveConfig"] = ctrlData

    cfgDataStr = json.dumps(ctrlData)
    bcfgDataStr = cfgDataStr.encode('utf-8')

    return bcfgDataStr


#-------------------------------------------------------
#--- find_other_board
#--- This function will scan for the pico board with the
#--- correct service UUID and return the device if found.
#--- If not found, it will return None.
#-------------------------------------------------------
#async def find_other_board() -> aioble.Device:
async def find_other_board():
    # Scan for 7 seconds, in active mode, with very low interval/window (to
    # maximise detection rate).
    async with aioble.scan(7000, interval_us=SCAN_INTERVAL_US, window_us=SCAN_WINDOW_US, active=True) as scanner:
        async for result in scanner:
            # See if it matches our name and the environmental sensing service.
            #--- REMOVE BEFORE FLIGHT - To handle the possibility that multiple
            #--- LED Controller boxes are in the same vecinity, each controller 
            #--- will be given a unique number in the center part of the UUID.
            #--- Collect all of the devices with the name "BoonLED", and then
            #--- make sure the SERVICE_UUID ends in 0000b00d0c50. Get the 
            #--- characteristics for each box and handle each box separately.
            if result.name() == "BoonLED" and SERVICE_UUID in result.services():
 #           for aService in result.services():
 #               print("Service: ", aService)
 #           if SERVICE_UUID in result.services():
                print("Found device:", result)
                print("Name:", result.name())
                for aService in result.services():
                    print("Service:", aService)
                return result.device
    return None


#-------------------------------------------------------
#---
#--- MAIN PROGRAM
#---
#-------------------------------------------------------
async def main():
    print("Starting Central")
    
    #--- Loop over user input
    while True:

        #--- First try to find the other board
        aDev = await find_other_board()

        if aDev is not None:
            
            try:            
                connection = await aDev.connect()
    #            print("The connection is: ", connection)
                # Initiate MTU exchange after connecting
                # This starts the negotiation process.
                try:
                    mtu = await connection.exchange_mtu(250)
                    print(f"MTU negotiation complete, final MTU is: {mtu}")
                except Exception as e:
                    print(f"MTU exchange failed: {e}")
            except asyncio.TimeoutError:
                print("Timeout during connection")
                continue
        else:
            print("LED Controller not found.  Waiting 5 seconds...")
            await asyncio.sleep_ms(5000)


        async with connection:
            try:
                led_service = await connection.service(bluetooth.UUID('b00d0c55-1111-2222-3333-0000b00d0c50'))
                print("Discovering characteristics")
                if led_service is None:
                    print("LED service not found")
                    await asyncio.sleep_ms(5000)
                    continue
                print("LED service:", led_service)
                config_char = await led_service.characteristic(CONFIG_CHAR_UUID)
                set_led_char = await led_service.characteristic(SET_LED_CHAR_UUID)
                brightness_char = await led_service.characteristic(SET_BRIGHT_CHAR_UUID)
                all_off_char = await led_service.characteristic(ALL_OFF_CHAR_UUID)
                select_scene_char = await led_service.characteristic(SELECT_SCENE_CHAR_UUID)
                save_scene_char = await led_service.characteristic(SAVE_SCENE_CHAR_UUID)
                set_ctrl_type_char = await led_service.characteristic(SET_CTRL_TYPE_CHAR_UUID)
            except asyncio.TimeoutError:
                print("Timeout discovering services/characteristics")
                await asyncio.sleep_ms(5000)
                continue
            except Exception as e:
                print("Exception discovering services/characteristics: ", e)
                await asyncio.sleep_ms(5000)
                continue

            dimIndex = 1

            while True:

                idx = int(input("Select Operation: \n" +
                                "1: Set CTRL 1 LED (Set RGBW type first!)\n" + 
                                "2: Set CTRL 2 LED (Set RGB+1 type first!)\n" + 
                                "3: Set CTRL 3 LED (Set 4Chan type first!)\n" + 
                                "4: Set CTRL 4 LED (Set RGBW type first!)\n" + 
                                "5: Rotate Brightness \n" + 
                                "6: All Off \n" +
                                "7: Select Scene 1\n" +
                                "8: Save Scene 1\n" +
                                "9: Set Ctrl Type\n" +
                                "10: Rotate Brightness RGB+1\n" +
                                "11: Rotate Brightness 4Chan\n" +
                                "12: Select Scene 2\n" +
                                "13: Save Scene 2\n" +
                                "20: Read Config \n"  ))

                if 1 == idx:
                    #--- Write json byte string to peripheral
                    json_str = build_short_json_string(idx)
#                    print("JSON string: ", json_str)
#                    print("Length: ", len(json_str))
                    await set_led_char.write(json_str)
                    
                elif 2 == idx:
                    #--- Write json byte string to peripheral
                    json_str = build_short_json_string(idx)
                    await set_led_char.write(json_str)
                    
                elif 3 == idx:
                    #--- Write json byte string to peripheral
                    json_str = build_short_json_string(idx)
                    await set_led_char.write(json_str)
                    
                elif 4 == idx:
                    #--- Write json byte string to peripheral
                    json_str = build_short_json_string(idx)
                    await set_led_char.write(json_str)
                    
                elif 5 == idx:
                    if dimIndex >= 100:
                        dimIndex = 1
                    else:
                        dimIndex = dimIndex + 5
                    
                    json_str = rgbw_brightness_string(1, dimIndex)
#                    print("Brightness string: ", json_str)
                    await brightness_char.write(json_str)

                elif 6 == idx:
                    json_str = all_off_string()
#                    print("All Off string: ", json_str)
                    await all_off_char.write(json_str)

                elif 7 == idx:
                    json_str = select_scene_string(1)
#                    print("Select scene string: ", json_str)
                    await select_scene_char.write(json_str)

                elif 8 == idx:
                    json_str = save_scene_string(1)
#                    print("Save scene string: ", json_str)
                    await save_scene_char.write(json_str)

                elif 9 == idx:
                    json_str = set_ctrl_type_string(1)
                    await set_ctrl_type_char.write(json_str)
                    await asyncio.sleep_ms(750)
                    json_str = set_ctrl_type_string(2)
                    await set_ctrl_type_char.write(json_str)
                    await asyncio.sleep_ms(750)
                    json_str = set_ctrl_type_string(3)
                    await set_ctrl_type_char.write(json_str)
                    await asyncio.sleep_ms(750)
                    json_str = set_ctrl_type_string(4)
                    await set_ctrl_type_char.write(json_str)
                    await asyncio.sleep_ms(750)
                    
                elif 10 == idx:
                    if dimIndex >= 100:
                        dimIndex = 1
                    else:
                        dimIndex = dimIndex + 5
                    
                    json_str = rgb_1_brightness_string(2, dimIndex)
#                    print("Brightness string: ", json_str)
                    await brightness_char.write(json_str)

                elif 11 == idx:
                    if dimIndex >= 100:
                        dimIndex = 1
                    else:
                        dimIndex = dimIndex + 5
                    
                    json_str = fourChan_brightness_string(3, 'B', dimIndex)
#                    print("Brightness string: ", json_str)
                    await brightness_char.write(json_str)

                elif 12 == idx:
                    json_str = select_scene_string(2)
#                    print("Select scene string: ", json_str)
                    await select_scene_char.write(json_str)

                elif 13 == idx:
                    json_str = save_scene_string(2)
#                    print("Save scene string: ", json_str)
                    await save_scene_char.write(json_str)

                elif 20 == idx:
                    try:
                        config_str = await config_char.read()

                        if config_str is not None:
                            print("Config data: ", config_str)
                            print("Length: ", len(config_str))
                        else:
                            print("No config data read")
                    except Exception as e:
                        print("Exception reading config char: ", e)
                        await asyncio.sleep_ms(500)
                        continue

                else:
                    print("Unexpected input: ", idx)

                await asyncio.sleep_ms(500)

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("KeyboardInterrupt")