import serial
mbed = serial.Serial(port='COM4', baudrate=115200)

STX = 0x02
ETX = 0x03
COMMA = 0x2C

data = [0x1C, 0x3D, 0xF3, 0x8D]
def CS(data) -> bytearray:
    return (~sum(data))&0xFF

#                 STX    CMD   LEN  DATA+0   DATA+1   DATA+2   DATA+3      CS     ETX
data = bytearray([0x02, 0x01, 0x04, data[0], data[1], data[2], data[3], CS(data), ETX])

mbed.write(data)