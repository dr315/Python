import pygatt
import time
import os
import sys
import zlib
import datetime
import binascii

class DrIoT:
    adapter = None
    address=None
    device=None
    
    def __init__(self, address):
        #self.adapter = pygatt.GATTToolBackend()
        self.adapter = pygatt.BGAPIBackend()
        self.adapter.start()
        self.device = self.adapter.connect(address)

    def __del__(self):
        self.adapter.stop()

    def readchar(self, uuid_16):
        try:
            value = self.device.char_read("0000{}-0000-1000-8000-00805f9b34fb".format(uuid_16))
        except:
            print("Read char {} error...".format(uuid_16))
        return value
    
    def writechar(self, uuid_16, value, size):
        try:
            self.device.char_write("0000{}-0000-1000-8000-00805f9b34fb".format(uuid_16), value )
        except:
            print("Write char {} error...".format(uuid_16))

    def FotaStart(self, address=0x00, size=0x00):
        ba = bytearray()
        ba.extend(address.to_bytes(length=4, byteorder='big'))
        ba.extend(size.to_bytes(length=4, byteorder='big'))
        return self.writechar('fb00', ba, 8)
    
    def FotaTransfer(self, data, size):
        return self.writechar('fb01', data, size)
    
    def FotaFinish(self, crc, version):
        ba = bytearray()
        ba.extend(crc.to_bytes(length=4, byteorder='big'))
        ba.extend(version.to_bytes(length=4, byteorder='big'))
        return self.writechar('fb02', ba, 8)

    def FotaStatus(self):
        try:
            status = self.readchar('fb03')
        except:
            print("Error")
        return status[0]

    def readVersion(self):
        return self.readchar('fa04')
    
    def readBattery(self):
        return self.readchar('faa0')
    
    def writeBuzzer(self, sound):
        return self.writechar('fa09', sound, 1)

class Fota (DrIoT):
    filename=''
    crc = 0
    packet=20
    def __init__(self, address, packet=250):
        self.packet = packet
        DrIoT.__init__(self, address)
    
    def wait(self): 
        print("processing...")
        
        status = self.FotaStatus()
        while (status == 1):
            status = self.FotaStatus()

        print("OK")
        return status
    
    def crc32(self, data):
        self.crc = zlib.crc32(data, self.crc)

    def crcFile(self, filename):
        buf = open(filename,'rb').read()
        buf = (binascii.crc32(buf) & 0xFFFFFFFF)
        return "%08X" % buf       
        
    def LoadFirmware(self, filename, address = 0x00):
        self.filename = filename
        self.crc=0
        size = os.stat(filename).st_size
        try:
            file=open(filename, "rb")
            print("Starting {}, {} bytes".format( address, size))
            t1 = datetime.datetime.now()
            self.FotaStart(address, size)
            self.wait()
            sent=0
            t2 = datetime.datetime.now()
            while(sent < size):
                s = min(size - sent , self.packet)
                print("Sending {} bytes {:.2f}%...".format( s, sent * 100 / size))
                packet = file.read(s)
                self.crc32(packet)
                self.FotaTransfer(packet, s)
                t3 = datetime.datetime.now()
                elapsed = (t3 - t2).total_seconds()
                # self.wait()
                sent = sent + s
                print('{:.02f} kb sent in {:.02f} seconds, {:.02f} kb/s'.format(sent / 1024, elapsed, sent / 1024 / elapsed))
            file.close()
            print("Finishing CRC: ", hex(self.crc))            
            self.FotaFinish(self.crc,  0x01020005)
            self.wait()
        except:
            print ("Cannot open file")

if __name__ == "__main__":
    # iot = DrIoT('18:04:ed:c7:21:7f')
#   print (iot.readBattery())    
    

    fota = Fota('18:04:ed:c7:21:7f', 80)
    fota.LoadFirmware(str(sys.argv[1]), int(sys.argv[2]))
     
    #  crc=zlib.crc32(b'ABCD')
    #  crc=zlib.crc32(b'EFG',crc)
    #  print(hex(crc))