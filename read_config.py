#-----------------------------------------------------------------
#--- read_config.py
#--- This implments a program to read the config data from the 
#--- config characteristic on the led_peripheral.
#-----------------------------------------------------------------

import bluetooth
import random
import struct
import time
import micropython

from ble_advertising import decode_services, decode_name

from micropython import const

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)
_IRQ_GATTS_READ_REQUEST = const(4)
_IRQ_SCAN_RESULT = const(5)
_IRQ_SCAN_DONE = const(6)
_IRQ_PERIPHERAL_CONNECT = const(7)
_IRQ_PERIPHERAL_DISCONNECT = const(8)
_IRQ_GATTC_SERVICE_RESULT = const(9)
_IRQ_GATTC_SERVICE_DONE = const(10)
_IRQ_GATTC_CHARACTERISTIC_RESULT = const(11)
_IRQ_GATTC_CHARACTERISTIC_DONE = const(12)
_IRQ_GATTC_DESCRIPTOR_RESULT = const(13)
_IRQ_GATTC_DESCRIPTOR_DONE = const(14)
_IRQ_GATTC_READ_RESULT = const(15)
_IRQ_GATTC_READ_DONE = const(16)
_IRQ_GATTC_WRITE_DONE = const(17)
_IRQ_GATTC_NOTIFY = const(18)
_IRQ_GATTC_INDICATE = const(19)

_ADV_IND = const(0x00)
_ADV_DIRECT_IND = const(0x01)
_ADV_SCAN_IND = const(0x02)
_ADV_NONCONN_IND = const(0x03)

# org.bluetooth.service.environmental_sensing
_ENV_SENSE_UUID = bluetooth.UUID(0x181A)
# org.bluetooth.characteristic.temperature
_TEMP_UUID = bluetooth.UUID(0x2A6E)

#--- Define service and characteristics UUIDs to match peripheral
SERVICE_UUID = bluetooth.UUID("b00d0c55-1111-2222-3333-0000b00d0c50")
CONFIG_CHAR_UUID = bluetooth.UUID("b00d0c55-1111-2222-3333-0000b00d0c51")
SET_LED_CHAR_UUID = bluetooth.UUID("b00d0c55-1111-2222-3333-0000b00d0c52")
SET_BRIGHT_CHAR_UUID = bluetooth.UUID("b00d0c55-1111-2222-3333-0000b00d0c53")
ALL_OFF_CHAR_UUID = bluetooth.UUID("b00d0c55-1111-2222-3333-0000b00d0c54")
SELECT_SCENE_CHAR_UUID = bluetooth.UUID("b00d0c55-1111-2222-3333-0000b00d0c55")
SAVE_SCENE_CHAR_UUID = bluetooth.UUID("b00d0c55-1111-2222-3333-0000b00d0c56")
SET_CTRL_TYPE_CHAR_UUID = bluetooth.UUID("b00d0c55-1111-2222-3333-0000b00d0c57")
SET_BOX_ID_CHAR_UUID = bluetooth.UUID("b00d0c55-1111-2222-3333-0000b00d0c58")

SCAN_DURATION_MS = const(5000)
SCAN_INTERVAL_US = const(30000)
SCAN_WINDOW_US = const(30000)



class BLEConfigReadCentral:
    def __init__(self, ble):
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)

        self._reset()

    def _reset(self):
        # Cached name and address from a successful scan.
        self.chunks = []
        self._name = None
        self._addr_type = None
        self._addr = None

        # Cached value (if we have one)
        self._value = None

        # Callbacks for completion of various operations.
        # These reset back to None after being invoked.
        self._scan_callback = None
        self._conn_callback = None
        self._read_callback = None

        # Persistent callback for when new data is notified from the device.
        self._notify_callback = None

        # Connected device.
        self._conn_handle = None
        self._start_handle = None
        self._end_handle = None
        self._value_handle = None

    def _irq(self, event, data):
        if event == _IRQ_SCAN_RESULT:
            addr_type, addr, adv_type, rssi, adv_data = data
            if adv_type in (_ADV_IND, _ADV_DIRECT_IND) and SERVICE_UUID in decode_services(
                adv_data
            ):
                # Found a potential device, remember it and stop scanning.
                self._addr_type = addr_type
                self._addr = bytes(
                    addr
                )  # Note: addr buffer is owned by caller so need to copy it.
                self._name = decode_name(adv_data) or "?"
                self._ble.gap_scan(None)

        elif event == _IRQ_SCAN_DONE:
            if self._scan_callback:
                if self._addr:
                    # Found a device during the scan (and the scan was explicitly stopped).
                    self._scan_callback(self._addr_type, self._addr, self._name)
                    self._scan_callback = None
                else:
                    # Scan timed out.
                    self._scan_callback(None, None, None)

        elif event == _IRQ_PERIPHERAL_CONNECT:
            # Connect successful.
            conn_handle, addr_type, addr = data
            if addr_type == self._addr_type and addr == self._addr:
                self._conn_handle = conn_handle
                self._ble.gattc_discover_services(self._conn_handle)

        elif event == _IRQ_PERIPHERAL_DISCONNECT:
            # Disconnect (either initiated by us or the remote end).
            conn_handle, _, _ = data
            if conn_handle == self._conn_handle:
                # If it was initiated by us, it'll already be reset.
                self._reset()

        elif event == _IRQ_GATTC_SERVICE_RESULT:
            print("Service result")
            # Connected device returned a service.
            conn_handle, start_handle, end_handle, uuid = data
            print("Service result UUID: ", uuid)
            if conn_handle == self._conn_handle and uuid == SERVICE_UUID:
                self._start_handle, self._end_handle = start_handle, end_handle

        elif event == _IRQ_GATTC_SERVICE_DONE:
            print("Service Done")
            # Service query complete.
            if self._start_handle and self._end_handle:
                self._ble.gattc_discover_characteristics(
                    self._conn_handle, self._start_handle, self._end_handle
                )
            else:
                print("Failed to find Boondocks service.")

        elif event == _IRQ_GATTC_CHARACTERISTIC_RESULT:
            print("Characteristic Result")
            # Connected device returned a characteristic.
            conn_handle, def_handle, value_handle, properties, uuid = data
            if conn_handle == self._conn_handle and uuid == CONFIG_CHAR_UUID:
                self._value_handle = value_handle

        elif event == _IRQ_GATTC_CHARACTERISTIC_DONE:
            print("Characteristic Done")
            # Characteristic query complete.
            if self._value_handle:
                # We've finished connecting and discovering device, fire the connect callback.
                if self._conn_callback:
                    self._conn_callback()
            else:
                print("Failed to find config characteristic.")

        elif event == _IRQ_GATTC_READ_RESULT:
            print("Read Result")
            # A read completed successfully.
            conn_handle, value_handle, char_data = data
            if conn_handle == self._conn_handle and value_handle == self._value_handle:
                self._update_value(char_data)
                if self._read_callback:
                    self._read_callback(self._value)
                    self._read_callback = None

        elif event == _IRQ_GATTC_READ_DONE:
            print("Read Done")
            # Read completed (no-op).
            conn_handle, value_handle, status = data

        elif event == _IRQ_GATTC_NOTIFY:
            print("Notify")
            # The ble_temperature.py demo periodically notifies its value.
            conn_handle, value_handle, notify_data = data
            if conn_handle == self._conn_handle and value_handle == self._value_handle:
                self._update_value(notify_data)
                if self._notify_callback:
                    self._notify_callback(self._value)

    # Returns true if we've successfully connected and discovered characteristics.
    def is_connected(self):
        return self._conn_handle is not None and self._value_handle is not None

    # Find a device advertising the environmental sensor service.
    def scan(self, callback=None):
        self._addr_type = None
        self._addr = None
        self._scan_callback = callback
        self._ble.gap_scan(2000, 30000, 30000)

    # Connect to the specified device (otherwise use cached address from a scan).
    def connect(self, addr_type=None, addr=None, callback=None):
        self._addr_type = addr_type or self._addr_type
        self._addr = addr or self._addr
        self._conn_callback = callback
        if self._addr_type is None or self._addr is None:
            return False
        self._ble.gap_connect(self._addr_type, self._addr)
        return True

    # Disconnect from current device.
    def disconnect(self):
        if self._conn_handle is None:
            return
        self._ble.gap_disconnect(self._conn_handle)
        self._reset()

    # Issues an (asynchronous) read, will invoke callback with data.
    def read(self, callback):
        if not self.is_connected():
            return
        self._read_callback = callback
        self._ble.gattc_read(self._conn_handle, self._value_handle)

    # Sets a callback to be invoked when the device notifies us.
    def on_notify(self, callback):
        self._notify_callback = callback

    def _update_value(self, data):
        # Data is sint16 in degrees Celsius with a resolution of 0.01 degrees Celsius.
        self._value = struct.unpack("<h", data)[0] / 100
        return self._value

    def value(self):
        return self._value


def demo():
    ble = bluetooth.BLE()
    central = BLEConfigReadCentral(ble)

    not_found = False

    def on_scan(addr_type, addr, name):
        if addr_type is not None:
            print("Found sensor:", addr_type, addr, name)
            central.connect()
        else:
            nonlocal not_found
            not_found = True
            print("No led_peripheral found.")

    central.scan(callback=on_scan)

    # Wait for connection...
    while not central.is_connected():
        time.sleep_ms(100)
        if not_found:
            return

    print("Connected")

    # Explicitly issue reads, using "print" as the callback.
    while central.is_connected():


        while True:

            idx = int(input("Select Operation: \n" +
                            "20: Read Config \n"  ))

            if 20 == idx:
                central.read(callback=print)

            else:
                print("Invalid selection. Try again.")
                continue

        time.sleep_ms(2000)

    # Alternative to the above, just show the most recently notified value.
    # while central.is_connected():
    #     print(central.value())
    #     time.sleep_ms(2000)

    print("Disconnected")


if __name__ == "__main__":
    demo()