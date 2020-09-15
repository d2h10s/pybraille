import serial
from . import kor_to_braille

ser = serial.Serial(port='COM4', baudrate=115200)

def Bit_shift(Row_Data1, Row_Data2, Row_Data3):
    str_list = [0, 0, 0]

    if len(Row_Data1) < 32:
        for i in range(len(Row_Data1)):
            if Row_Data1[i] == 1:
                str_list[0] = str_list[0] << 1
                str_list[0] += 1
            else:
                str_list[0] = str_list[0] << 1

            if Row_Data2[i] == 1:
                str_list[1] = str_list[1] << 1
                str_list[1] += 1
            else:
                str_list[1] = str_list[1] << 1

            if Row_Data3[i] == 1:
                str_list[2] = str_list[2] << 1
                str_list[2] += 1
            else:
                str_list[2] = str_list[2] << 1
    else:
        for i in range(0, 32):
            if Row_Data1[i] == 1:
                str_list[0] = str_list[0] << 1
                str_list[0] += 1
            else:
                str_list[0] = str_list[0] << 1

            if Row_Data2[i] == 1:
                str_list[1] = str_list[1] << 1
                str_list[1] += 1
            else:
                str_list[1] = str_list[1] << 1

            if Row_Data3[i] == 1:
                str_list[2] = str_list[2] << 1
                str_list[2] += 1
            else:
                str_list[2] = str_list[2] << 1

    return str_list

def Bit_cleanup():
    Send_list = kor_to_braille.Dot_bit
    Row_Data = [0,0,0]
    for i in range(3):
        Row_Data[i] = Send_list[i:len(Send_list):3]

    for i in range(0,len(Row_Data[0]),32):
        str1 = Bit_shift(Row_Data[0], Row_Data[1], Row_Data[2])
        str_data = str(str1[0]) + ',' + str(str1[1]) + ',' + str(str1[2]) + '\n'
        #print(str_data)
        ser.write(str_data.encode('utf-8'))
        #print(str_data.encode('utf-8'))
        #print(len(Row_Data[0]))
        #print(Row_Data[0])
        if len(Row_Data[0])>=33:
            del Row_Data[0][0:32]
            del Row_Data[1][0:32]
            del Row_Data[2][0:32]
