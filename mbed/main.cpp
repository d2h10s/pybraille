#include "mbed.h"
#define SIZE 30
extern class Serial pc;
extern class InterruptIn YLimit;
extern volatile uint8_t buffer[SIZE];
extern volatile uint8_t Data[SIZE];
extern volatile uint8_t CMD;
extern volatile uint8_t LEN ;
extern volatile uint8_t ReceivedCS;
extern volatile int BIndex;
extern volatile bool CheckFlag;
extern volatile bool SaveFlag;
extern volatile bool EchoFlag;
extern volatile bool PrintFlag;
extern volatile bool ResetFlag;
extern void Echo(); // do echo after serial
extern void Print(); // 1Line Letters (3 lines of braille)
extern void XReset(); // move to X axis' origin
extern void YReset(); // move to Y axis' origin
extern void save_data();
extern void RX_ISR();

uint32_t ResetCount = 0;
int main()
{
    pc.baud(115200);
    pc.attach(&RX_ISR);
    DigitalOut VCC(A0);

    VCC= 1;
    XReset();

    while(true) {
        if(SaveFlag) save_data();
        if(EchoFlag) Echo();
        wait_us(100);
        if(PrintFlag) Print();
        ResetCount++;
        if(ResetFlag) {
            if((ResetCount%100000)==0){ResetCount=0;
            ResetFlag=false;
            XReset();
            YReset();}
        }
    }
}
