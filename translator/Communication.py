import os, serial, sys, glob, ctypes, threading, time
import translator.kor_to_braille as kor_to_braille

# >>> use if you want to debug without serial
FOR_DEBUGGING = False
# <<< use if you want to debug without serial

## communication ascii code

STX = 0x02
ETX = 0x03
COMMA = 0x2C
ACK = b'\x06'
NAK = b'\x15'
CMD_PRINT = 0x01
LINE_COMPLETE = b'\x19'
PAGE_COMPLETE = b'\x14'

### Flag
COM_COMPLETE = True
NEXT_PAGE_READY = False

step = 7
page_line = 20

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
            print(reply)
            if reply != ACK:
                mbed = serial.Serial()
            elif reply == ACK:
                print('serail found')
                mbed.timeout=30
                return 1
        except (OSError, serial.SerialException):
            mbed = serial.Serial()
    return 0


def CS(data):
    return (~sum(data)) & 0xFF


def bit2byte(bit_data):
    hex_list = []
    temp = 0; idx = 7
    for bit in bit_data:
        end_flag = False
        temp |= bit << idx
        idx -= 1
        if idx < 0:
            hex_list.append(temp)
            temp = 0; idx = 7; end_flag = True
    if not end_flag:
        hex_list.append(temp)
    return hex_list # [0x21 0x3F 0xFA 0x27]


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Deubg Function
def debug_temp_data(temp_data):
    print('------------------------\ntemp data is')
    # for debugging
    # print('dot_data', [hex(x) for x in dot_data])
    # print('dot_data', [bin(x) for x in dot_data])
    for k, i in enumerate(temp_data):
        for j in range(7,-1,-1):
            print(' ', end=' ') if (j+1) % 2 == 0 else 0
            print('●' if i & (1 << j) else '○',end=' ')
        print() if (k+1) % step == 0 else 0


def debug_hex_data(hex_data):
    print('------------------------\nhex data is')
    for line in hex_data:
        for dot in line:
            for i in range(7,-1,-1):
                print('  ', end='') if (i+1) % 2 == 0 else 0
                print('●' if (dot & 1<<i)>>i else '○', end=' ')
        print('')


def debug_Row_Data(Row_Data):
    print('------------------------\nRow Data is')
    for line in Row_Data:
        for i, dot in enumerate(line): # 조심
            print('  ', end='') if (i+2) % 2 == 0 else 0
            print('●' if dot else '○',end=' ')
        print('')
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Deubg Function


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
    if not mbed.isOpen() and not FOR_DEBUGGING:
       autoSerial()
       print(mbed)
       if not mbed.isOpen():
           ctypes.windll.user32.MessageBoxW(None, '프린터가 연결되지 않았습니다.', '오류', 0)
           return 0
    # mbed = serial.Serial(port='COM6', baudrate=115200, timeout=30)
    doubles = [spread(x) for x in kor_to_braille.translate(string)]
    Send_list = [x for double in doubles for x in double]
    Row_Data = [Send_list[i::3] for i in range(3)]  # 1,2,3열의 데이터 생성
    hex_data = [bit2byte(Row_Data[i]) for i in range(3)]
    send_data = [0]

    #debug_Row_Data(Row_Data)
    #debug_hex_data(hex_data)
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
        debug_temp_data(temp_data)
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
                print('print failed, reply:', reply)
        elif reply == LINE_COMPLETE:
            print('complete a line')
            line += 1
        else: print('irregular occured, reply:', reply)
        print(f'line is {line}, page_line is {page_line}, send_data is {len(send_data)}')
        if line % page_line == 0 and line < len(send_data):
            print('reload paper to print next page')
            mbed.write(bytes([]))
            ctypes.windll.user32.MessageBoxW(None, '종이를 교체해주세요', '대기중', 0)
            print('paper loaded')
    mbed.close()
    print('complete print')
    
Data_Send('asdfasdf')