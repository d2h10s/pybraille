import serial
from serial.tools import list_ports
import translator.kor_to_braille as kor_to_braille
## communication ascii code
STX = 0x02
ETX = 0x03
COMMA = 0x2C
ACK = b'\x06'
NAK = b'\x15'
CMD_PRINT = 0x01
COMPLETE = b'\x19'
### Flag
COM_COMPLETE = True

step = 7

mbed = serial.Serial()

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


def bit2byte(bit_data): # [1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0]
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
    k =1
    for i in dot_data:
        for j in range(7,-1,-1):
            if (j+1) % 2 == 0:
                print(' ', end=' ')
            if i & (1 << j):
                print('●',end=' ')
            else:
                print('○', end=' ')
        if k % step == 0:
            print()
        k += 1
    # for debugging
    
def spread(dot):
    bit = []
    if dot == ' ':
        return [0,0,0,0,0,0]
    s = bin(ord(dot) - 10240)[2:]
    while len(s) < 6:
        s = '0' + s
    for i in range(6):
        bit.append(int(s[i]))
    bit.reverse()
    return bit

def Data_Send(string):
    if not mbed.isOpen():
       autoSerial()
       if not mbed.isOpen():
           return 0
    #mbed = serial.Serial(port='COM11', baudrate=115200, timeout=30)
    mbed.flush()
    braille = kor_to_braille.translate(string)
    doubles = [spread(x) for x in braille]
    Send_list = [x for double in doubles for x in double]
    Row_Data = [0, 0, 0]
    hex_data = []

    for i in range(3):
        Row_Data[i] = Send_list[i::3]  # 1,2,3열의 데이터 생성
    for i in range(3):
        hex_data.append(bit2byte(Row_Data[i])) # [[227, 132, 244, 99, 250, 228, 55, 198, 163, 91, 174, 24], [236, 124, 112, 223, 54, 27, 8, 65, 147, 167, 97, 11], [16, 113, 140, 16, 136, 33, 8, 134, 48, 136, 130, 69]]
    for line in Row_Data:
        i = 1
        for dot in line:
            if (i+1) % 2 == 0:
                print('  ', end='')
            if dot:
                print('●',end=' ')
            else:
                print('○', end=' ')
            i += 1
        print('')
    print(hex_data)
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
        send_data = [STX, CMD_PRINT, len(temp_data)] + temp_data + [CS(temp_data), ETX] #보낼 데이터
        mbed.write(bytes(send_data))   #---송신
        print('송신 완료')

        print('에코 기다리기')
        mbed.flush()
        a = mbed.read()    #--- 답장 ACK or NAK 받기
        print("보드의 답장 : ",a)

        if a == NAK:        # 만약 보드가 못받았으면
            mbed.write(bytes(send_data))       # 다시 보내기
            print("재전송")
        elif a == ACK:             #잘 받았으면
            print("프린트 완료까지 대기")
            a = mbed.read()        # 1줄 프린트 완료까지 대기
            if a == COMPLETE:
                print("한 줄 끝")
                start += step
                end = min(end + step, len(hex_data[0]))
            else:
                print('failed', a)
        else:
            print(a)
    print('프린트 완료')

#Data_Send('서울과학기술대학교')