
///////////설정값//////////////////////
#define Pulley_radius 7 //풀리의 반지름
#define MOTOR_STEP_ANGLE 1.8 //스텝각
#define MICRO_STEP_DIV 2 // 마이크로스텝 분할수
#define STEP_CYCLE 1.25//스텝주기, 단위 : ms (스텝모터의 속도 설정)
///////////설정값//////////////////////

#define DESIRED_STEPS_PER_SEC (1000/STEP_CYCLE*0.8) //1000ms / 20ms(1step주기)  ,50, 초당 스텝수
#define MOTOR_STEPS_PER_REV 360/MOTOR_STEP_ANGLE // 모터 1회전 스텝수
#define MICRO_STEP_PER_REV (MOTOR_STEPS_PER_REV*MICRO_STEP_DIV)//1회전당 총 마이크로 스텝수
#define DESIRED_MICRO_STEPS_PER_SEC (MICRO_STEP_DIV*DESIRED_STEPS_PER_SEC) // 1600 , 초당 마이크로 스텝수
#define SAMPLE_TIME (1000000L/DESIRED_MICRO_STEPS_PER_SEC) //625 , 샘플타임

class DRV8825
{

    BusOut _bus;
    Timer tmr;

private:
    void step();
 //   int Calculation(double distance);

    int32_t _steps;
    enum {CW=1,CCW=0} _dir;
    int InputStep;
    bool start;
//    double radian, degree;
    int micro_step;


public:
    DRV8825(PinName pin1, PinName pin2);
    void Move(double distance);
    void Sleep();
    void Enable();
};

////////////////////////////////////Private////////////////////////////////////
DRV8825::DRV8825(PinName pin1, PinName pin2): _bus(pin1,pin2)  // 생성자
{
    _dir =CW;
    _steps=0;
}
void DRV8825::step()
{
    _bus= _dir ? 0b11:0b01; //_dir이 1면 11반환 , _dir이 거짓이면 01반환
    wait_us(1); //minimum pulse width
    _bus= _dir ? 0b10:0b00;
    _steps+= _dir? -1: 1; // updating current steps
}

////////////////////////////////////Public////////////////////////////////////

void DRV8825::Move(double distance)
{
    InputStep = distance*10; //(0.1mm가 1step)
    start = true; //회전 시작 flag

    if(InputStep>0) _dir = CW;
    else if(InputStep<0) _dir = CCW;
    tmr.start();
    while(start) {
        if(tmr.read_us()>SAMPLE_TIME) {
            tmr.reset();
            step(); //1step 이동


            if(_steps*_steps >= InputStep*InputStep) {  //특정 스텝수만큼 이동하면 stop
                start = false;
                _steps = 0;
            }
        }
    }
}
void DRV8825::Sleep(){
    _bus = 0b11;
}
void DRV8825::Enable(){
    _bus = 0b01;
}
    
