import serial
import translator.kor_to_braille as kor_to_braille
import time
mbed = serial.Serial(port='COM11', baudrate=115200)

STX = 0x02
ETX = 0x03
COMMA = 0x2C
ACK = b'\x06'
NAK = b'\x15'
CMD_PRINT = 0x01
COMPLETE = b'\x19'

def CS(data):
    return (~sum(data)) & 0xFF


def Bit_shift(bit_data): # [1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0]
    hex_list = []
    size = len(bit_data)
    i = 0
    temp = 0
    for j in range(size):
        temp |= bit_data[j]
        if j == size - 1:
            break
        if (j+1) % 8 == 0:
            hex_list.append(temp)
            temp = 0
        else:
            temp <<= 1
    return hex_list # [0x21 0x3F 0xFA 0x27]



def Data_Send(string):
    kor_to_braille.translate(string)
    Send_list = kor_to_braille.Dot_bit
    Row_Data = [0, 0, 0]
    hex_data = []

    for i in range(3):
        Row_Data[i] = Send_list[i:len(Send_list):3]  # 1,2,3열의 데이터 생성
    print(" ")
    print(Send_list)
    print(Row_Data)
    for i in range(3):
        hex_data.append(Bit_shift(Row_Data[i])) # [[227, 132, 244, 99, 250, 228, 55, 198, 163, 91, 174, 24], [236, 124, 112, 223, 54, 27, 8, 65, 147, 167, 97, 11], [16, 113, 140, 16, 136, 33, 8, 134, 48, 136, 130, 69]]

    start = 0
    end = min(4, len(hex_data[0]))
    while start < len(hex_data[0]):     #4b,4b,4b 로 끊어서 데이터 만들기
        temp_data = []
        for i in range(3):
            for j in range(start, end):
                temp_data.append(hex_data[i][j])
            if i < 2:
                temp_data.append(COMMA)

        send_data = [STX, CMD_PRINT, len(temp_data)] + temp_data + [CS(temp_data), ETX] #보낼 데이터
        #print([hex(x) for x in send_data])
        mbed.write(bytes(send_data))   #---송신
        print('송신 완료')

        a = mbed.read()    #--- 답장 ACK or NAK 받기
        print("보드의 답장 : ",a)

        if a == NAK:        # 만약 보드가 못받았으면
            mbed.write(bytes(send_data))       # 다시 보내기
            print("재전송")
        elif a == ACK:             #잘 받았으면
            print("프린트 완료까지 대기")
            a = mbed.read()        # 1줄 프린트 완료까지 대기
            if a == COMPLETE:
                print("프린트끝")
                start += 4
                end = min(end + 4, len(hex_data[0]))
            else:
                print(a)
        else:
            print(a)


Data_Send("임베디드 소프트웨어 경진대회에 오신 것을 환영합니다.")