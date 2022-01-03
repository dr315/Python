from bluetool import Bluetooth


print('starting')

bluetooth = Bluetooth()
bluetooth.scan()
devices = bluetooth.get_available_devices()
print(devices)