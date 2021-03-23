#include "mbed.h"
#define SIZE 30
Serial pc(USBTX,USBRX);

volatile int BIndex = 0;
volatile uint8_t buffer[SIZE] ="0,";
volatile uint8_t Data[SIZE]="0,";
volatile uint8_t CMD=0;
volatile uint8_t LEN = 0;
volatile uint8_t ReceivedCS =0;

volatile bool CheckFlag = false;
volatile bool bufferFlag =false;
volatile bool SaveFlag =false;
volatile bool PrintFlag = false;
volatile bool EchoFlag = false;
volatile bool AbortFlag = false;

enum {STX=0x02, ETX=0x03, ACK=0x06, NAK=0x15, EM =0x19} PROTOCOL;
void RX_ISR();
void CheckSum();
void Flush_array(volatile uint8_t *array);
void save_data();
void Echo();

void RX_ISR()
{
    buffer[BIndex] = pc.getc();
    if(!bufferFlag) {
        if(buffer[0]==STX) {
            bufferFlag=true;
            BIndex++;
        }
    } else {
        if(BIndex==1) {
            CMD = buffer[BIndex++];
        } else if (BIndex == 2) {
            LEN = buffer[BIndex++];
        } else if(BIndex<(LEN+3))BIndex++;
        else if(BIndex== 3+LEN) {
            ReceivedCS = buffer[BIndex++];
        } else if(BIndex>3+LEN) {
            if(buffer[BIndex]==ETX) CheckFlag = true;
            else CheckFlag = false;
            BIndex = 0;
            bufferFlag = false;
            SaveFlag=(LEN>0);
            EchoFlag = true;
            AbortFlag = (CMD==2);
        }
    }
}
void save_data()
{
    for(int i =0 ; i<LEN; i++) {
        *(Data+i)=*(buffer+3+i);
        SaveFlag = false;

    }
}
void Echo()
{
    CheckSum();
    if(CheckFlag) {
        pc.putc(ACK);
        if(CMD==3){}
        else{
        PrintFlag = true;}
    } else {pc.putc(NAK); PrintFlag=false;}
    Flush_array(buffer);
    EchoFlag = false;

}
void Flush_array(volatile uint8_t *array)
{
    for(int i=0; i<SIZE; i++) {
        *(array+i) = 0;
    }
}
void CheckSum()
{
    uint16_t temp = 0;
    for(int i=0; i<LEN; i++) {
        temp += *(Data+i);
    }
    temp = (~temp)&0xff;
    CheckFlag = (temp==ReceivedCS);
}
