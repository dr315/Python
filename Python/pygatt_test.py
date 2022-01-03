import pygatt

#adapter = pygatt.GATTToolBackend()
adapter = pygatt.BGAPIBackend()

try:
    adapter.start()
    device = adapter.connect('18:04:ed:c7:21:7f')    
    
    value2 = device.char_read("0000fa01-0000-1000-8000-00805f9b34fb")
    print("0xfa01:", value2);

    value3 = device.char_read("0000fa02-0000-1000-8000-00805f9b34fb")
    print("0xfa02:", value3);

    value1 = device.char_read("0000fa00-0000-1000-8000-00805f9b34fb")
    print("0xfa00:", value1);
 
    
finally:
    adapter.stop()