# This example demonstrates a UART periperhal.

import bluetooth
import random
import struct
import time
from ble_advertising import advertising_payload

from micropython import const

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)
_IRQ_GATTS_READ_REQUEST = const(4)

_FLAG_READ = const(0x0002)
_FLAG_WRITE_NO_RESPONSE = const(0x0004)
_FLAG_WRITE = const(0x0008)
_FLAG_NOTIFY = const(0x0010)

_UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX = (
    bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"),
    _FLAG_READ | _FLAG_NOTIFY,
)
_UART_RX = (
    bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"),
#    _FLAG_WRITE | _FLAG_WRITE_NO_RESPONSE,
    _FLAG_WRITE,
)
_UART_SERVICE = (
    _UART_UUID,
    (_UART_TX, _UART_RX),
)

# Define UUIDs for the service and characteristics
SERVICE_UUID = bluetooth.UUID("b00d0c55-1111-2222-3333-0000b00d0c50")
CHAR_UUIDS = [
    bluetooth.UUID("b00d0c55-1111-2222-3333-0000b00d0c51"),
    bluetooth.UUID("b00d0c55-1111-2222-3333-0000b00d0c52"),
    bluetooth.UUID("b00d0c55-1111-2222-3333-0000b00d0c53"),
    bluetooth.UUID("b00d0c55-1111-2222-3333-0000b00d0c54"),
    bluetooth.UUID("b00d0c55-1111-2222-3333-0000b00d0c55"),
    bluetooth.UUID("b00d0c55-1111-2222-3333-0000b00d0c56"),
    bluetooth.UUID("b00d0c55-1111-2222-3333-0000b00d0c57"),
    bluetooth.UUID("b00d0c55-1111-2222-3333-0000b00d0c58"),
]


# Create 4 characteristics; one readable, others writable
config_char = (CHAR_UUIDS[0], _FLAG_READ | _FLAG_NOTIFY)
set_led_char = (CHAR_UUIDS[1], _FLAG_WRITE)
setBright_char = (CHAR_UUIDS[2], _FLAG_WRITE)
allOff_char = (CHAR_UUIDS[3], _FLAG_WRITE)
sceneSelect_char = (CHAR_UUIDS[4], _FLAG_WRITE)
sceneSave_char = (CHAR_UUIDS[5], _FLAG_WRITE)
ctrlType_char = (CHAR_UUIDS[6], _FLAG_WRITE)
setID_char = (CHAR_UUIDS[7], _FLAG_WRITE)

# Create the BLE service
charSet = (config_char, set_led_char, setBright_char, allOff_char, sceneSelect_char, sceneSave_char, ctrlType_char, setID_char)
service2 = (SERVICE_UUID, charSet)
SERVICES = (service2,)



class LEDPeripheral:
    def __init__(self, ble, name="BoonLED"):
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)
        ((self._handle_config, 
          self._handle_setLED, 
          self._handle_setBright, 
          self._handle_allOff, 
          self._handle_sceneSelect, 
          self._handle_sceneSave,
          self._handle_setCtrlType,
          self._handle_setID),) = self._ble.gatts_register_services(SERVICES)
        self._connections = set()
#        self._config_callback = None
        self._setLED_callback = None
        self._setBright_callback = None
        self._allOff_callback = None
        self._sceneSelect_callback = None
        self._sceneSave_callback = None
        self._setCtrlType_callback = None
        self._setID_callback = None
        self._long_string_data = None
        self._payload = advertising_payload(name=name, services=[SERVICE_UUID])
        self._ble.config(mtu=244)
        self._ble.gatts_set_buffer(self._handle_config, 244)
        self._ble.gatts_set_buffer(self._handle_setLED, 244)
        self._ble.gatts_set_buffer(self._handle_setBright, 244)
        self._ble.gatts_set_buffer(self._handle_allOff, 244)
        self._ble.gatts_set_buffer(self._handle_sceneSelect, 244)
        self._ble.gatts_set_buffer(self._handle_sceneSave, 244)
        self._ble.gatts_set_buffer(self._handle_setCtrlType, 244)
        self._ble.gatts_set_buffer(self._handle_setID, 244)
        print("payload:", self._payload)
        print("Length:", len(self._payload))
        self._advertise()

    def _irq(self, event, data):
        # Track connections so we can send notifications.
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            print("New connection", conn_handle)
            self._connections.add(conn_handle)
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            print("Disconnected", conn_handle)
            self._connections.remove(conn_handle)
            # Start advertising again to allow a new connection.
            self._advertise()
        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            value = self._ble.gatts_read(value_handle)
#            print("Write request on handle:", value_handle, "with value:", value)
#            print("setType handle:", self._handle_setCtrlType)
#            print("Callback:", self._setCtrlType_callback)
            if value_handle == self._handle_setLED and self._setLED_callback:
                self._setLED_callback(value)
            elif value_handle == self._handle_setBright and self._setBright_callback:
                self._setBright_callback(value)
            elif value_handle == self._handle_allOff and self._allOff_callback:
                self._allOff_callback(value)
            elif value_handle == self._handle_sceneSelect and self._sceneSelect_callback:
                self._sceneSelect_callback(value)
            elif value_handle == self._handle_sceneSave and self._sceneSave_callback:
                self._sceneSave_callback(value)
            elif value_handle == self._handle_setCtrlType and self._setCtrlType_callback:
                self._setCtrlType_callback(value)
            elif value_handle == self._handle_setID and self._setID_callback:
                self._setID_callback(value)
            else:
                print("Handle without a callback: ", value_handle)
        elif event == _IRQ_GATTS_READ_REQUEST:
            conn_handle, value_handle = data
            # Send long string if config characteristic is being read
            if value_handle == self._handle_config and self._long_string_data:
                self.send_long_string(self._long_string_data, self._handle_config)
            else:
                self.send(b'Missing config')

    def set_local_config(self, config):
        self._ble.gatts_write(self._handle_config, config)
            
    def send(self, data):
        for conn_handle in self._connections:
            self._ble.gatts_notify(conn_handle, self._handle_config, data)

    def is_connected(self):
        return len(self._connections) > 0

    def _advertise(self, interval_us=500000):
        print("Starting advertising")
        self._ble.gap_advertise(interval_us, adv_data=self._payload)

#    def set_config_callback(self, callback):
#        self._config_callback = callback

    def set_setLED_callback(self, callback):
        self._setLED_callback = callback

    def set_setBright_callback(self, callback):
        self._setBright_callback = callback

    def set_allOff_callback(self, callback):
        self._allOff_callback = callback

    def set_sceneSelect_callback(self, callback):
        self._sceneSelect_callback = callback

    def set_sceneSave_callback(self, callback):
        self._sceneSave_callback = callback

    def set_setCtrlType_callback(self, callback):
        self._setCtrlType_callback = callback

    def set_setID_callback(self, callback):
        self._setID_callback = callback

    def set_long_string_data(self, long_string):
        """
        Set the long string data to be sent when the config characteristic is read.
        
        Args:
            long_string: The string to store for transmission (str or bytes)
        """
        self._long_string_data = long_string

    def send_long_string(self, long_string, characteristic_handle, chunk_size=240):
        """
        Send a long string over BLE by chunking it into MTU-sized pieces.
        
        Args:
            long_string: The string to send (will be encoded to bytes)
            characteristic_handle: The characteristic handle to write to
            chunk_size: Maximum bytes per chunk (default 240, leaving room for BLE overhead)
        
        Returns:
            True if all chunks sent successfully, False otherwise
        """
        if isinstance(long_string, str):
            data = long_string.encode('utf-8')
        else:
            data = long_string
        
        total_length = len(data)
        chunks_sent = 0
        
        try:
            for i in range(0, total_length, chunk_size):
                chunk = data[i:i + chunk_size]
                self._ble.gatts_write(characteristic_handle, chunk)
                
                # Notify all connected centrals of the data
                for conn_handle in self._connections:
                    self._ble.gatts_notify(conn_handle, characteristic_handle, chunk)
                
                chunks_sent += 1
                time.sleep(0.01)  # Small delay between chunks to avoid overwhelming the central
            
            print(f"Long string sent successfully in {chunks_sent} chunks ({total_length} bytes)")
            return True
            
        except Exception as e:
            print(f"Error sending long string: {e}")
            return False