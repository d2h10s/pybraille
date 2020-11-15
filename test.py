import serial, sys, glob

STX = 0x02
ETX = 0x03
COMMA = 0x2C
ACK = b'\x06'
NAK = b'\x15'
CMD_PRINT = 0x01
LINE_COMPLETE = b'\x19'
PAGE_COMPLETE = b'\x14'

mbed = serial.Serial()

def autoSerial():
    global mbed
    if sys.platform.startswith('win'):
        ports = ['COM%s' % i for i in range(1,30)] # 1~257
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')
    for port in ports:
        try:
            mbed = serial.Serial(port, baudrate=115200, timeout=0.01, write_timeout=0.01)
            mbed.write(bytes([STX, 0x03, 0x00, 0xFF, ETX]))
            reply = mbed.read()
            if reply != ACK:
                mbed = serial.Serial()
            elif reply == ACK:
                print('serail found')
                mbed.timeout=30
                return 1
        except (OSError, serial.SerialException):
            mbed = serial.Serial()
    return 0

autoSerial()
print(mbed)