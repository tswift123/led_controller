#-------------------------------------------------------------------
#--- Save this code to your MicroPython device (e.g., ble_peripheral.py).
#--- Ensure you have the aioble library installed.
#--- Run the script. The peripheral will advertise a single service with 4 characteristics.
#--- char1 (first characteristic) is readable and will return "Hello BLE!" when read from a BLE central.
#--- The other 3 characteristics are writable (write logic can be expanded as needed).
#--------------------------------------------------------------------

import uasyncio as asyncio
import aioble
from aioble import Service, Characteristic
import bluetooth
from bluetooth import UUID
import json


# Define UUIDs for the service and characteristics
SERVICE_UUID = UUID("b00d0c55-1111-2222-3333-0000b00d0c50")
CHAR_UUIDS = [
    UUID("b00d0c55-1111-2222-3333-0000b00d0c51"),
    UUID("b00d0c55-1111-2222-3333-0000b00d0c52"),
    UUID("b00d0c55-1111-2222-3333-0000b00d0c53"),
    UUID("b00d0c55-1111-2222-3333-0000b00d0c54"),
]

# Create the BLE service
service = Service(SERVICE_UUID)

# Create 4 characteristics; one readable, others writable
config_char = Characteristic(service, CHAR_UUIDS[0], read=True, notify=True)  # This will return data
set_led_char = Characteristic(service, CHAR_UUIDS[1], write=True, capture=True)  # This will accept data
char3 = Characteristic(service, CHAR_UUIDS[2], write=True, capture=True)
char4 = Characteristic(service, CHAR_UUIDS[3], write=True, capture=True)

config_char2 = (CHAR_UUIDS[0], bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY)
set_led_char2 = (CHAR_UUIDS[1], bluetooth.FLAG_WRITE)
char3_2 = (CHAR_UUIDS[2], bluetooth.FLAG_WRITE)
char4_2 = (CHAR_UUIDS[3], bluetooth.FLAG_WRITE)

charSet = (config_char2, set_led_char2, char3_2, char4_2)
service2 = (SERVICE_UUID, charSet)
SERVICES = (service2,)

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
#--- MTU size
MTU_SIZE = 244  # bytes
#--- Write buffer size
WRITE_BUFFER_SIZE = 512  # bytes
#--- Read buffer size
READ_BUFFER_SIZE = 512  # bytes
#--- Connection timeout in milliseconds
CONNECTION_TIMEOUT_MS = 10000  # 10 seconds
#--- Maximum number of connections
MAX_CONNECTIONS = 1
#--- Task delay in milliseconds
TASK_DELAY_MS = 200  # 200 ms
#--- Characteristic read timeout in milliseconds
CHAR_READ_TIMEOUT_MS = 1000  # 1 second
#--- Characteristic write timeout in milliseconds
CHAR_WRITE_TIMEOUT_MS = 1000  # 1 second
#--- Characteristic notify timeout in milliseconds
CHAR_NOTIFY_TIMEOUT_MS = 1000  # 1 second
#--- Characteristic capture timeout in milliseconds
CHAR_CAPTURE_TIMEOUT_MS = 1000  # 1 second
#--- Characteristic read buffer size
CHAR_READ_BUFFER_SIZE = 256  # bytes
#--- Characteristic write buffer size
CHAR_WRITE_BUFFER_SIZE = 256  # bytes
#--- Characteristic notify buffer size
CHAR_NOTIFY_BUFFER_SIZE = 256  # bytes
#--- Characteristic capture buffer size
CHAR_CAPTURE_BUFFER_SIZE = 256  # bytes
#--- Characteristic read interval in milliseconds
CHAR_READ_INTERVAL_MS = 1000  # 1 second
#--- Characteristic write interval in milliseconds
CHAR_WRITE_INTERVAL_MS = 1000  # 1 second
#--- Characteristic notify interval in milliseconds
CHAR_NOTIFY_INTERVAL_MS = 1000  # 1 second
#--- Characteristic capture interval in milliseconds
CHAR_CAPTURE_INTERVAL_MS = 1000  # 1 second
#--- Task sleep interval in milliseconds
TASK_SLEEP_INTERVAL_MS = 200  # 200 ms
#--- Maximum number of retries for characteristic operations
MAX_RETRIES = 3
#--- Delay between retries in milliseconds
RETRY_DELAY_MS = 100  # 100 ms
#--- Timeout for characteristic operations in milliseconds
CHAR_OP_TIMEOUT_MS = 1000  # 1 second
#--- Delay between characteristic operations in milliseconds
CHAR_OP_DELAY_MS = 100  # 100 ms
#--- Maximum number of characteristic operations per connection
MAX_CHAR_OPS_PER_CONN = 10
#--- Delay between characteristic operations in milliseconds
CHAR_OPS_DELAY_MS = 100  # 100 ms
#--- Task delay in milliseconds
TASK_DELAY_MS = 200  # 200 ms
#--- Characteristic read timeout in milliseconds
CHAR_READ_TIMEOUT_MS = 1000  # 1 second
#--- Characteristic write timeout in milliseconds
CHAR_WRITE_TIMEOUT_MS = 1000  # 1 second
#--- Characteristic notify timeout in milliseconds
CHAR_NOTIFY_TIMEOUT_MS = 1000  # 1 second
#--- Characteristic capture timeout in milliseconds
CHAR_CAPTURE_TIMEOUT_MS = 1000  # 1 second
#--- Characteristic read buffer size
CHAR_READ_BUFFER_SIZE = 256  # bytes
#--- Characteristic write buffer size
CHAR_WRITE_BUFFER_SIZE = 256  # bytes
#--- Characteristic notify buffer size
CHAR_NOTIFY_BUFFER_SIZE = 256  # bytes
#--- Characteristic capture buffer size
CHAR_CAPTURE_BUFFER_SIZE = 256  # bytes
#--- Characteristic read interval in milliseconds
CHAR_READ_INTERVAL_MS = 1000  # 1 second
#--- Characteristic write interval in milliseconds
CHAR_WRITE_INTERVAL_MS = 1000  # 1 second
#--- Characteristic notify interval in milliseconds
CHAR_NOTIFY_INTERVAL_MS = 1000  # 1 second
#--- Characteristic capture interval in milliseconds
CHAR_CAPTURE_INTERVAL_MS = 1000  # 1 second
#--- Task sleep interval in milliseconds
TASK_SLEEP_INTERVAL_MS = 200  # 200 ms
#--- Maximum number of retries for characteristic operations
MAX_RETRIES = 3
#--- Delay between retries in milliseconds
RETRY_DELAY_MS = 100  # 100 ms
#--- Timeout for characteristic operations in milliseconds
CHAR_OP_TIMEOUT_MS = 1000  # 1 second

#--- Value to return for the readable characteristic
char1_value = b"Hello BLE!"
char2_value = b"12345678901234567890123456789012345678901234567890"  # 50 bytes

# Register the service
aioble.register_services(service)
aioble.config(mtu=MTU_SIZE)
##--- The below write doesn't work. Gives a value error.
#set_led_char.write(char2_value, send_update=True)  # Pre-allocate write buffer

#--- Create a Bluetooth Low Energy (BLE) object
#ble = bluetooth.BLE()
#--- Register services
#((conn_handle,), (config_handle, setLEDHandle, char3Handle, char4Handle,),) = ble.gatts_register_services(SERVICES)

#--- Set buffer size for writable characteristics
#ble.gatts_write(setLEDHandle, bytes(WRITE_BUFFER_SIZE))

#--- Store value for config characteristic
#ble.gatts_write(config_handle, char1_value)


#--- Set initial value for char1
#config_char.write(char1_value, send_update=True)
#print("char1 value written:", char1_value)

_IRQ_MTU_EXCHANGED = const(21)
_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
#-------------------------------------------------------
#--- _irq
#--- This function will handle BLE events.
#-------------------------------------------------------
def _irq(event, data):
    if event == _IRQ_CENTRAL_CONNECT:
        conn_handle, _, _ = data
        print("New connection", conn_handle)
    elif event == _IRQ_CENTRAL_DISCONNECT:
        conn_handle, _, _ = data
        print("Disconnected", conn_handle)
    elif event == _IRQ_MTU_EXCHANGED:
        conn_handle, mtu = data
        print("MTU exchanged:", conn_handle, mtu)

#aioble.device.ble.irq(_irq)


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


#---------------------------------------------------------
#--- set_led_task
#--- This function will be called when data is written to the 
#--- writable characteristic set_led_char.  It should parse
#--- the data and perform actions based on the data.
#---------------------------------------------------------
async def set_led_task():
    while True:
        try:
            connection, data = await set_led_char.written()
            print("Data written to set_led_char:", data)
            parseAndRunData(data)
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
                connection.ble.gatts_write(set_led_char._value_handle, char2_value)
                mtu = connection.mtu
                print("Connection MTU:", mtu)   
                await connection.disconnected()
        except asyncio.CancelledError:
            print("peripheral_task cancelled") 
        except Exception as e:
            print("Error in peripheral_task:", e)
        finally:
            await asyncio.sleep_ms(TASK_SLEEP_INTERVAL_MS)



async def main():
    t1 = asyncio.create_task(peripheral_task())
    t2 = asyncio.create_task(set_led_task())
    await asyncio.gather(t1, t2)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program stopped by user")