# Boondocks LED Controller

**Intro**
Bluetooth Low Energy (BLE) devices communicate with each other using
"Services" and "Characteristics".  A BLE peripheral advertizes one or
more services and each service contains one or more characteristics.
A central device either searches for peripherals and queries the services
that it  provides or, it can connect to a specific service by UUID once
it has identified the peripheral.  The characteristics are queried from
the service or, if the characteristics UUID are known ahead of time, the
central device can work directly with them.

A central device can either read from a characteristic or write to a 
characteristic on a peripheral.  The common example of reading from a 
characteristic is reading the temperature from a temperature sensor.
The peripheral constantly updates the buffer of the characteristic and
the central device reads from it whenever it desires.  Write characteristics
are used to command a peripheral to do something such as turn on an LED
in our case.

**A note about the UART service**
Every BLE device implements a UART service with two characteristics:
UART_TX and UART_RX. This service was used in the example that Patrick
implemented on the phone app.  It is my belief that you can communicate
with a peripheral either using the UART service or or a service with
specifically designed characteristics, but not both.

**Json messages.txt** - This file describes the service and characteristics
UUIDs and the json messages that will be used to interact with them.

**main_board.py** - This file is the main implementation of the code running
on the pico in the LED controller.  It handles all of the logic of the
characteristics.

**ble_advertising.py** - This code implements the advertising done by the 
peripheral.  It is basically the same as the original exammple.  This file 
must reside on the pico.

**led_peripheral.py** - This file sets up the service and characteristics and
handles the processing of the callbacks for each characteristic.  This file
must reside on the pico.

**ConfigObj.py** - This file implements the class that stores, reads, and 
processes the configuration settings.  This file must reside on the pico.

**example_central.py** - This is basically some test code that emulates the
phone app by sending a few canned json messages to the led controller.  This
file runs on a separate pico from the led controller.  Note that the bluetooth
code in this file differs from the main_board.py in that it uses a higher level
library called aioble. While this library allows the central to negotiage the
maximum transmission unit(MTU - basically the maximum message length) with the 
peripheral, it does not allow you to set the buffer size of the characteristic
which sets the MTU.  This is why the code on the peripheral has to use lower
level bluetooth code.

**LED Controller Documentation (Toms Edits).pptx** - A power point file that
describes how the screens on the phone app should look and operate.

**Other files** - These other files in the repository are for historical reference
and can safely be ignored.
alternate_board.py is an early attempt to implement the LED controller side using 
the higher level library, aioble.
example_peripheral.py - This is the original example that communicates over the
UART service that was modified to use aioble.
LED Controller Documentation.pptx - This is Kevin's original design document.


