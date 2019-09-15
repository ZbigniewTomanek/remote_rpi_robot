#include <Servo.h>
#include <Wire.h>
#define SLAVE_ADDRESS 0x08

Servo myservo;

int servoPosition = 90;
const int servo_min = 0;
const int servo_max = 180;
int servo_delay = 20;
int servoDelta = 5;

bool ifSetDelta = false;
int number = 0;

void setup() {
  Serial.begin(9600);
  myservo.attach(9);
  myservo.write(servoPosition);
  
  
  Wire.begin(SLAVE_ADDRESS);
  Wire.onRequest(sendData);
  Wire.onReceive(receiveData);
}

void executeCommand(int n) {
  switch(n) {
    case 0: ifSetDelta = true;
      break;
    case 5: turnServo(servoDelta);
      break;
    case 6: turnServo(-servoDelta);
      break;
  }
}

void setDelta(int delta) {
  servoDelta = delta;
}

void receiveData(int byteCount){
  while(Wire.available()) {
    number = Wire.read();
    Serial.println(number);
    
    if (ifSetDelta) {
      setDelta(number);
      ifSetDelta = false;
    } else
      executeCommand(number);
  }
}

void sendData(){
  Wire.write(number);
}

void turnServo(int n) {
  if(n > 0) {
    if(servoPosition + n <= servo_max) {
      for(int i = 0; i < n; i++) {
        servoPosition++;
        myservo.write(servoPosition);
        delay(servo_delay);
      }
    }
  } else {
    n *= -1;
    if(servoPosition - n >= servo_min) {
      for(int i = 0; i < n; i++) {
        servoPosition--;
        myservo.write(servoPosition);
        delay(servo_delay);
        }
      }
    }
  }

void test() {
 for (servoPosition = 0; servoPosition <= 180; servoPosition += 1) {

   myservo.write(servoPosition);
   delay(15);
 }

 for (servoPosition = 180; servoPosition >= 0; servoPosition -= 1) {
   myservo.write(servoPosition);
   delay(15);
 }
}
void loop() {
  test();
}
