#include <Wire.h>
#include <AFMotor.h>
#include <Servo.h> 

#define SLAVE_ADDRESS 0x04
int number = 0;

AF_DCMotor motorRF(1);
AF_DCMotor motorRB(4);
AF_DCMotor motorLF(3);
AF_DCMotor motorLB(2);

bool Forward = false;
bool Backward = false;
bool Left = false;
bool Right = false;

Servo servoH, servoV;
const int servo_start = 85;
int servoVPosition = 90;
int servoHPosition = 90;
const int servo_min = 0;
const int servo_max = 180;
int servo_delay = 20;

const int MAX_SPEED = 255;
int speed = MAX_SPEED;
int rideDelay = 50;

//motor FL(RF) forward 
//Motor BR(LF) backward 3
//motor FR(RB) backward 4
//motor BL(LB) backrward 1

void setup() {
  Serial.begin(9600); // start serial for output
  Wire.begin(SLAVE_ADDRESS);
  Wire.onReceive(receiveData);
  Wire.onRequest(sendData);

  halt();
  applySpeed();
  applySpeed();

  servoH.attach(9);
  servoV.attach(10);

  servoH.write(servo_start);
  servoV.write(servo_start);
  
  Serial.println("Ready");
}

void sendData(){
  Wire.write(number);
}

void turnServoH(int n) {
  if(n > 0) {
    if(servoHPosition + n <= servo_max) {
      for(int i = 0; i < n; i++) {
        servoHPosition++;
        servoH.write(servoHPosition);
        delay(servo_delay);
      }
    }
  } else {
    n *= -1;
    if(servoHPosition - n >= servo_min) {
      for(int i = 0; i < n; i++) {
        servoHPosition--;
        servoH.write(servoHPosition);
        delay(servo_delay);
        }
      }
    }
  }


void turnServoV(int n) {
  if(n > 0) {
    if(servoVPosition + n <= servo_max) {
      for(int i = 0; i < n; i++) {
        servoVPosition++;
        servoV.write(servoVPosition);
        delay(servo_delay);
      }
    }
  } else {
    n *= -1;
    if(servoVPosition - n >= servo_min) {
      for(int i = 0; i < n; i++) {
        servoVPosition--;
        servoV.write(servoVPosition);
        delay(servo_delay);
        }
      }
    }
  }


bool increaseSpeed(int n) {
  if(speed + n <= MAX_SPEED) {
    speed += n; 
    applySpeed();
    return true;
  } else {
    return false;
  }
}

bool decreaseSpeed(int n) {
  if(speed - n >= 0) {
    speed -= n;
    applySpeed();
    return true;
  } else {
    return false;
  }
}

void applySpeed() {
 motorRF.setSpeed(speed);
 motorRB.setSpeed(speed);
 motorLF.setSpeed(speed);
 motorLB.setSpeed(speed);
}

void halt() {
  Left = false;
  Right = false;
  Forward = false;
  Backward = false;

  motorLF.run(RELEASE);
  motorLB.run(RELEASE);
  motorRF.run(RELEASE);
  motorRB.run(RELEASE);
  delay(rideDelay);
}


void right(){
  if(Right == false)
   halt();

  Right = true;
  motorRF.run(FORWARD);
  motorLB.run(BACKWARD);
  motorRB.run(FORWARD);
  motorLF.run(BACKWARD);
}


void left() {
  if(Left == false)
   halt();

  Left = true;
  motorRF.run(BACKWARD);
  motorLB.run(FORWARD);
  motorRB.run(BACKWARD);
  motorLF.run(FORWARD);
}

void forward(){
  if(Forward == false)
   halt();
   
  Forward = true;
  motorLF.run(FORWARD);
  motorLB.run(BACKWARD);
  motorRF.run(FORWARD);
  motorRB.run(BACKWARD);
}


void backward(){
  if(Backward == false)
   halt();
   
  Backward = true;
  motorLF.run(BACKWARD);
  motorLB.run(FORWARD);
  motorRF.run(BACKWARD);
  motorRB.run(FORWARD);
 
}

boolean set_speed = false;
boolean move_in_x_axis = false;
boolean move_in_y_axis = false;
boolean got_sign_of_value = false;
int minus = 1;

void executeCommand(int message) {
 Serial.println(message);
 
 if(move_in_x_axis == true && got_sign_of_value == true) {
  turnServoH(minus * message);
  move_in_x_axis = false;
  got_sign_of_value = false;
 }

 if(move_in_y_axis == true && got_sign_of_value == true) {
  turnServoV(minus * message);
  move_in_y_axis = false;
  got_sign_of_value = false;
 }

 if((move_in_x_axis == true && got_sign_of_value == false) || (move_in_y_axis == true && got_sign_of_value == false)) {
  
  if(message == 0)
    minus = -1;
  else
    minus = 1;

  got_sign_of_value = true;
 }

  if(set_speed == true) {
    speed = message;
    applySpeed();
    set_speed = false;
 }
  
 if(set_speed == false && move_in_x_axis == false && move_in_y_axis == false) {
  char msg = message;
  
  switch(msg) {
     case 'f': forward();
        break;
     case 'b': backward();
      break;
      case 'r': right();
      break;
     case 'l': left();
      break;
     case 'h': halt();
      break;
     case 'w': turnServoV(-10);
      break;
     case 's': turnServoV(10);
      break;
     case 'a': turnServoH(10);
      break;
     case 'd': turnServoH(-10);
      break;
     case 'q': set_speed = true;
      break;
     case 'z': move_in_x_axis = true;
      break;
     case 'y': move_in_y_axis = true;
      break;
    }
 }


}

void receiveData(int byteCount){
  while(Wire.available()) {
    number = Wire.read();
    executeCommand(number);
  }
}


void loop() {
 
}
