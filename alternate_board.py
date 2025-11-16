#---------------------------------------------------
#--- LED Controller
#--- This code implements the LED controller which is
#--- a peripheral device that can be controlled via
#--- Bluetooth LE.  It uses the aioble library to handle
#--- the BLE functionality.
#--- The controller manages 4, 4 channel controllers which
#--- can be configured as RGBW, RGB+1 separate light, or
#--- 4 Channel (4 separate lights).
#---------------------------------------------------


from machine import Pin, PWM, unique_id
from time import sleep, ticks_ms
import neopixel
#import NeoMatrix
import math
from bluetooth import UUID
import aioble
import asyncio
import ujson as json

# Define UUIDs for the service and characteristics
SERVICE_UUID = UUID("b00d0c55-1111-2222-3333-0000b00d0c50")
CHAR_UUIDS = [
    UUID("b00d0c55-1111-2222-3333-0000b00d0c51"),
    UUID("b00d0c55-1111-2222-3333-0000b00d0c52"),
    UUID("b00d0c55-1111-2222-3333-0000b00d0c53"),
    UUID("b00d0c55-1111-2222-3333-0000b00d0c54"),
    UUID("b00d0c55-1111-2222-3333-0000b00d0c55"),
]

# Create the BLE service
service = aioble.Service(SERVICE_UUID)

# Create 7 characteristics; one readable, others writable
config_char = aioble.Characteristic(service, CHAR_UUIDS[0], read=True, notify=True)  # This will return data
set_led_char = aioble.Characteristic(service, CHAR_UUIDS[1], write_no_response=True, capture=True)  # This will accept data
set_bright_char = aioble.Characteristic(service, CHAR_UUIDS[2], write_no_response=True, capture=True)
all_off_char = aioble.Characteristic(service, CHAR_UUIDS[3], write_no_response=True, capture=True)
select_scene_char = aioble.Characteristic(service, CHAR_UUIDS[4], write_no_response=True, capture=True)

#--- Value to return for the readable characteristic
char1_value = b"Hello BLE!"

# Register the service
aioble.register_services(service)
#--- Set initial value for char1
config_char.write(char1_value, send_update=True)
#print("char1 value written:", char1_value)


#--- VSCode suggested all of these constants.  They may not all be needed.
#--- Define constants for BLE configuration
#--- Advertising interval in microseconds
ADV_INTERVAL_MS = 30000  # 30 sec
#--- Connection interval in milliseconds
CONN_INTERVAL_MS = 100  # 100 ms
#--- Slave latency
SLAVE_LATENCY = 0
#--- Supervision timeout in milliseconds
SUPERVISION_TIMEOUT_MS = 4000  # 4 seconds
#--- Task sleep interval in milliseconds
TASK_SLEEP_INTERVAL_MS = 200  # 200 ms


# === PWM Setup for RGBW ===
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

#--- multiplier and divider to set brightness duty cycle
LED_Dimmer_multiply_Array =  (4,  8,  12, 16)
LED_Dimmer_divide_Array =    (16, 16, 16, 16)

Max_RGBW_Array_Index = const(8)
Max_RGB_Array_Index = const(7)
Max_W_Array_Index = const(1)
Max_Dimmer_Index = const(3)

# Set frequency for all channels
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

LEDSceneNames = {
    "LEDScene1": "Scene 1",
    "LEDScene2": "Scene 2",
    "LEDScene3": "Scene 3",
    "LEDScene4": "Scene 4"
}

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

    ctrlStr = str(ctrlNum)

    # Convert 0–255 to 0–65535 duty cycle
    rgbw_pins[ctrlStr+"R"].duty_u16(int(r / 255 * 65535 * mulr / divr))
    rgbw_pins[ctrlStr+"G"].duty_u16(int(g / 255 * 65535 * mulg / divg))
    rgbw_pins[ctrlStr+"B"].duty_u16(int(b / 255 * 65535 * mulb / divb))
    rgbw_pins[ctrlStr+"W"].duty_u16(int(w / 255 * 65535 * mulw / divw))


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



#---------------------------------------------------
#--- scan_for_devices
#--- A simple function to scan for nearby bluetooth
#--- LE devices.  It prints out the name, address (MAC)
#--- and the Received Signal Strength Indication (RSSI)
#---------------------------------------------------
# async def scan_for_devices():
#     async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
#         async for result in scanner:
#             addr = binascii.hexlify(result.device.addr, ':').decode('utf-8')
#             name = result.name() if result.name else "Unknown"
#             print(f"Found Device: {name} ({addr}), RSSI: {result.rssi}")


#---------------------------------------------------------------
#--- parseAndRunData
#---- This function will parse the data received on writable characteristics
#--- and perform actions based on the data.
#---------------------------------------------------------------
def parseAndRunData(data):
    print("Data received on writable characteristic:", data)
    # Add logic to parse and act on the received data
    # For example, if controlling an LED, parse color values and set the LED accordingly
    #--- Decode the json and set the various attributes of the LED controller
    #--- This is a placeholder for actual implementation
    #---------------------------------------------------------------
    dataStr = data.decode('utf-8')

    dataDict = json.loads(dataStr)
    print("Parsed data:", dataDict)
    print("Length of data:", len(dataStr))


#----------------------------------------------------------------
#--- read_scene_file
#--- Use the passed in scene name (e.g. LEDScene1) to read a json
#--- file.  Return the data dictionary represented by the json string
#--- from the file.
#---
#----------------------------------------------------------------
def read_scene_file(sceneName):

    filePath = sceneName + ".json"

    sceneData = {}

    try:
        with open(filePath, "r") as file:
            sceneData = json.load(file)

    except OSError:
        #--- Failed to open file for read so no
        #--- scene data has been saved. Nothing
        #--- to do.
#        print("Failed to open config file for write")
        pass
    finally:
        if 'file' in locals():
            file.close()

    return sceneData


#---------------------------------------------------------
#--- all_off_task
#--- This function will be called when data is written to the 
#--- writable characteristic select_scene_char.  It should parse
#--- the data and perform actions based on the data.  The data
#--- will be a json string with the keyword, 1, and the value 'off'
#--- e.g. {'1:'off'}
#---------------------------------------------------------
async def all_off_task():
    while True:
        try:
            connection, data = await all_off_char.written()
            print("Data written to all_off_char:", data)

            dataStr = data.decode('utf-8')

            dataDict = json.loads(dataStr)
#            print("Parsed data:", dataDict)
#            print("Length of data:", len(dataStr))

            #--- It doesn't matter what the keyword or value is, just the
            #--- fact that something was written to this characteristic means
            #--- to turn all LEDs off.
            all_off()

        except asyncio.CancelledError:
            print("set_bright_task cancelled")
        except Exception as e:
            print("Error in set_bright_task:", e)
        await asyncio.sleep_ms(200)


#---------------------------------------------------------
#--- select_scene_task
#--- This function will be called when data is written to the 
#--- writable characteristic select_scene_char.  It should parse
#--- the data and perform actions based on the data.  The data
#--- will be a json string with the keyword, LEDScene, and the
#--- scene number as the value (1-4) in the format:
#--- {'LEDScene': scene#}
#--- e.g. {'LEDScene: 1}
#---------------------------------------------------------
async def select_scene_task():
    while True:
        try:
            connection, data = await select_scene_char.written()
            print("Data written to select_scene_char:", data)

            dataStr = data.decode('utf-8')

            dataDict = json.loads(dataStr)
#            print("Parsed data:", dataDict)
#            print("Length of data:", len(dataStr))

            #--- Combine the keyword and value to form the key
            #--- into the LEDSceneNames arrays.
            dataDictKeys = dataDict.keys()
            for aKeyword in dataDictKeys:
                sceneNum = dataDict[aKeyword]
                key = f"{aKeyword}{sceneNum}"
                if key in LEDSceneNames:
                    #--- Use the key as a file name and read the
                    #--- file to load the saved scene.  The file
                    #--- will contain the saved_rgbw_values and 
                    #--- brightnesses in a json string.
                    sceneData = read_scene_file(key)
                    print("Scene data read from file:", sceneData)

                    #-----------------------------------------------
                    #--- REMOVE BEFORE FLIGHT ---
                    #--- This is only partially finished.  Need to 
                    #--- read LED values and also brightness values
                    #--- separately from the file, apply them to the
                    #--- save arrays and then set the LEDs.
                    #-----------------------------------------------

                    for ctrlNum in sceneData:
                        chanDict = sceneData[ctrlNum]
                        chanKeys = chanDict.keys()
                        for chan in chanKeys:
                            key = f"{ctrlNum}{chan}"
                            value = chanDict[chan]
                            print("Setting", key, "to", value)
                            if key in saved_rgbw_values:
                                saved_rgbw_values[key] = value
                                #--- Apply brightness dimming
                                dimmer_index = rgbw_brightness[key]
                                dimmed_value = (value * LED_Dimmer_multiply_Array[dimmer_index]) // LED_Dimmer_divide_Array[dimmer_index]
                                rgbw_pins[key].duty_u16(int(dimmed_value / 255 * 65535))
                            else:
                                print("Invalid key:", key)
                else:
                    print("Invalid key:", key)

        except asyncio.CancelledError:
            print("set_bright_task cancelled")
        except Exception as e:
            print("Error in set_bright_task:", e)
        await asyncio.sleep_ms(200)


#---------------------------------------------------------
#--- set_bright_task
#--- This function will be called when data is written to the 
#--- writable characteristic set_bright_char.  It should parse
#--- the data and perform actions based on the data.  The data
#--- will be a json string with the controller number, the
#--- channel (R, G, B, W) and the index value (0-3) in the format:
#--- {Ctrl#: {Chan: Value}}
#--- e.g. {"1": {"R": 3}}
#---------------------------------------------------------
async def set_bright_task():
    while True:
        try:
            connection, data = await set_bright_char.written()
            print("Data written to set_bright_char:", data)

            dataStr = data.decode('utf-8')

            dataDict = json.loads(dataStr)
#            print("Parsed data:", dataDict)
#            print("Length of data:", len(dataStr))

            #--- Combine the controller number and channel to form the key
            #--- into the saved RGBW values and brightness arrays.
            dataDictKeys = dataDict.keys()
            for ctrlNum in dataDictKeys:
                chanDict = dataDict[ctrlNum]
                chanKeys = chanDict.keys()
                for chan in chanKeys:
                    key = f"{ctrlNum}{chan}"
                    value = chanDict[chan]
                    print("Setting", key, "to", value)
                    if key in saved_rgbw_values:
                        ledValue = saved_rgbw_values[key]
                        rgbw_brightness[key] = value
                        #--- Apply brightness dimming
                        dimmer_index = rgbw_brightness[key]
                        dimmed_value = (ledValue * LED_Dimmer_multiply_Array[dimmer_index]) // LED_Dimmer_divide_Array[dimmer_index]
                        rgbw_pins[key].duty_u16(int(dimmed_value / 255 * 65535))
                    else:
                        print("Invalid key:", key)

        except asyncio.CancelledError:
            print("set_bright_task cancelled")
        except Exception as e:
            print("Error in set_bright_task:", e)
        await asyncio.sleep_ms(200)


#---------------------------------------------------------
#--- set_led_task
#--- This function will be called when data is written to the 
#--- writable characteristic set_led_char.  It should parse
#--- the data and perform actions based on the data.  The data
#--- will be a json string with the controller number, the
#--- channel (R, G, B, W) and the value (0-255) in the format:
#--- {Ctrl#: {Chan: Value}}
#--- e.g. {"1": {"R": 255}}
#---------------------------------------------------------
async def set_led_task():
    while True:
        try:
            connection, data = await set_led_char.written()
#            print("Data written to set_led_char:", data)

            dataStr = data.decode('utf-8')

            dataDict = json.loads(dataStr)
#            print("Parsed data:", dataDict)
#            print("Length of data:", len(dataStr))

            #--- Combine the controller number and channel to form the key
            #--- into the saved RGBW values and brihtness arrays.
            dataDictKeys = dataDict.keys()
            for ctrlNum in dataDictKeys:
                chanDict = dataDict[ctrlNum]
                chanKeys = chanDict.keys()
                for chan in chanKeys:
                    key = f"{ctrlNum}{chan}"
                    value = chanDict[chan]
#                    print("Setting", key, "to", value)
                    if key in saved_rgbw_values:
                        saved_rgbw_values[key] = value
                        #--- Apply brightness dimming
                        dimmer_index = rgbw_brightness[key]
                        dimmed_value = (value * LED_Dimmer_multiply_Array[dimmer_index]) // LED_Dimmer_divide_Array[dimmer_index]
                        rgbw_pins[key].duty_u16(int(dimmed_value / 255 * 65535))
                    else:
                        print("Invalid key:", key)

        except asyncio.CancelledError:
            print("set_led_task cancelled")
        except Exception as e:
            print("Error in set_led_task:", e)
        await asyncio.sleep_ms(200)


#-------------------------------------------------------
#--- peripheral_task
#--- This function will be called when the peripheral is connected.
#--- It will handle reading and writing to characteristics.
#--- This is the main loop for the peripheral.
#-------------------------------------------------------
async def peripheral_task():
    while True:
        print("Starting peripheral_task...")
        try:
            # Start advertising
            print("Advertising BLE peripheral...")
            # Wait for a connection
            async with await aioble.advertise(interval_us=ADV_INTERVAL_MS, 
                                                name="BoonLEDCtrl",
                                                services=[SERVICE_UUID]
                                            ) as connection:
                
                print("Device connected:", connection)
                await connection.disconnected()
        except asyncio.CancelledError:
            print("peripheral_task cancelled") 
        except Exception as e:
            print("Error in peripheral_task:", e)
        finally:
            await asyncio.sleep_ms(TASK_SLEEP_INTERVAL_MS)



#------------------------------------
# === Main Program ===
#------------------------------------
async def main():
    all_off()
    t1 = asyncio.create_task(peripheral_task())
    t2 = asyncio.create_task(set_led_task())
    t3 = asyncio.create_task(set_bright_task())
    t4 = asyncio.create_task(all_off_task())
    await asyncio.gather(t1, t2, t3, t4)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        all_off()
        print("Program stopped by user")