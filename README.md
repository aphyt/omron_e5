# Omron E5_C Communications Driver

This project is a Python library that enables communication with the E5GC, E5CC, E5EC, E5AC and E5DC temperature controllers. It uses PySerial which can be installed using `pip install pyserial`.

## Example
This example demonstrates connecting via a USB RS-485 adapter on Linux to a controller at node 1, reading controller attributes and process value, as well as manipulating the set-point. On Windows the port name will change from '/dev/ttyUSB0' to something like 'COM5'.
```python
from omron_e5 import E5

temp_controller = E5()
temp_controller.connect('/dev/ttyUSB0')

print(temp_controller.read_controller_attributes(1))
print(temp_controller.read_process_value(1))
print(temp_controller.read_set_point(1))
# You must first execute a command to write to the E5 controller
temp_controller.enable_com_write(1)
temp_controller.write_set_point(1, 120)
print(temp_controller.read_set_point(1))
temp_controller.write_set_point(1, 60)
print(temp_controller.read_set_point(1))

temp_controller.disconnect()
```