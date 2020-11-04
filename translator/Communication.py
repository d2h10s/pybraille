import serial, sys
from serial.tools import list_ports
import translator.kor_to_braille as kor_to_braille
from PyQt5.QtWidgets import *

## communication ascii code
STX = 0x02
ETX = 0x03
COMMA = 0x2C
ACK = b'\x06'
NAK = b'\x15'
CMD_PRINT = 0x01
LINE_COMPLETE = b'\x19'

### Flag
COM_COMPLETE = True
NEXT_PAGE_READY = False

step = 7
page_line = 30

mbed = serial.Serial()

class confirm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Waitting for Next Page')
        self.center()
        self.resize(w=300, h=200)
        self.show()
        self.btn = QPushButton(self)
        self.btn.setText('Next Page')
        self.btn.clicked.connect(self.btnFuntion)

    def center(self):
        qr = self.frameGeometry() # get position and size of window in rect structure
        cp = QDesktopWidget().availableGeometry().center() # get center of monitor in point structure
        qr.moveCenter(cp) # move window to monitor's center
        self.move(qr.topLeft()) # move window to monitor's center

    def btnFunction(self):
        global NEXT_PAGE_READY
        NEXT_PAGE_READY = True
        qApp.quit()




def autoSerial():
    global mbed
    port_lists = list_ports.comports()
    for port in port_lists:
        print(port[0])
        try:
            mbed = serial.Serial(port=port[0], baudrate=115200, timeout=1)
            mbed.write(bytes([STX, 0x03, 0x00, 0xFF, ETX]))
            reply = mbed.read()
            if reply != ACK:
                mbed = serial.Serial()
                print(mbed)
                print('serial not found')
            elif reply == ACK:
                print('serail found')
        except:
            print('2serail not found')
    mbed.timeout=30


def CS(data):
    return (~sum(data)) & 0xFF


def bit2byte(bit_data):
    hex_list = []
    temp = 0; idx = 7
    for bit in bit_data:
        temp |= bit << idx
        idx -= 1
        if idx < 0:
            hex_list.append(temp)
            temp = 0; idx = 7
    if temp:
        hex_list.append(temp)
    return hex_list # [0x21 0x3F 0xFA 0x27]

def dot_debugging(dot_data):
    # for debugging
    # print('dot_data', [hex(x) for x in dot_data])
    # print('dot_data', [bin(x) for x in dot_data])
    for k, i in enumerate(dot_data):
        for j in range(7,-1,-1):
            print(' ', end=' ') if (j+1) % 2 == 0 else 0
            print('●' if i & (1 << j) else '○',end=' ')
        print() if (k+1) % step == 0 else 0

def spread(dot):
    if dot == ' ':
        return [0,0,0,0,0,0]
    s = bin(ord(dot) - 10240)[2:]
    while len(s) < 6:
        s = '0' + s
    bit = ([int(s[i]) for i in range(6)])
    bit.reverse()
    return bit

def Data_Send(string):
    if not mbed.isOpen():
       autoSerial()
       if not mbed.isOpen():
           return 0
    #mbed = serial.Serial(port='COM11', baudrate=115200, timeout=30)
    app = QApplication(sys.argv)
    doubles = [spread(x) for x in kor_to_braille.translate(string)]
    Send_list = [x for double in doubles for x in double]
    Row_Data = [Send_list[i::3] for i in range(3)]  # 1,2,3열의 데이터 생성
    hex_data = [bit2byte(Row_Data[i]) for i in range(3)] # [[227, 132, 244, 99, 250, 228, 55, 198, 163, 91, 174, 24], [236, 124, 112, 223, 54, 27, 8, 65, 147, 167, 97, 11], [16, 113, 140, 16, 136, 33, 8, 134, 48, 136, 130, 69]]
    send_data = []
    for line in Row_Data:
        for i, dot in enumerate(line): # 조심
            print('  ', end='') if (i+2) % 2 == 0 else 0
            print('●' if dot else '○',end=' ')
        print('')
    print(hex_data)

    line = 1
    start = 0
    end = min(step, len(hex_data[0]))
    while start < len(hex_data[0]):     #4b,4b,4b 로 끊어서 데이터 만들기
        temp_data = []
        for i in range(3):
            for j in range(start, end):
                temp_data.append(hex_data[i][j])
            if end - start < step:
                for _ in range(step - end + start):
                    temp_data.append(0x00)
        dot_debugging(temp_data)
        send_data.append([STX, CMD_PRINT, len(temp_data)] + temp_data + [CS(temp_data), ETX]) #보낼 데이터
        start += step
        end = min(end + step, len(hex_data[0]))

    while line < len(send_data):
        mbed.write(bytes(send_data[line]))
        print(line, 'line transmission OK, waiting echo...')
        reply = mbed.read()
        print('reply: ', reply)

        if reply == NAK:
            mbed.write(bytes(send_data[line]))
            print('recieved NAK, transmit again line', line)
        elif reply == ACK:
            print('waitting for complete print a line')
            reply = mbed.read()
            if reply == LINE_COMPLETE:
                print('complete a line')
                line += 1
            else:
                print('print failed')
        else: print('irregular occured, reply:', reply)
        if line % page_line == 0:
            print('reload paper, print next page')
            ex = confirm()
            while not NEXT_PAGE_READY:
                pass
#Data_Send('서울과학기술대학교')