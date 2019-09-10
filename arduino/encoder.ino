#include <Wire.h>
#define SLAVE_ADDRESS 0x06

unsigned int number = 0;

volatile word steps;


void setup() {
  Serial.begin(9600);
  pinMode(2, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(2), onStep, FALLING);

  Wire.begin(SLAVE_ADDRESS);
  Wire.onRequest(sendData);
  Wire.onReceive(receiveData);
}


void onStep() {
  //Serial.println(steps);
  steps++;
}


void getDiv() {
  noInterrupts();
  number = steps/255;
  Serial.println(number);
  interrupts();
}

void getMod() {
  noInterrupts();
  Serial.println(number);
  number = steps%255;
  interrupts();
}

void reset() {
  noInterrupts();
  steps = 0;
  interrupts();
}

void executeCommand(int n) {
  switch(n) {
    case 0: reset();
      break;
    case 3: getDiv();
      break;
    case 4: getMod();
      break;
  }
}


void receiveData(int byteCount){
  while(Wire.available()) {
    number = Wire.read();
    executeCommand(number);
  }
}


void sendData(){
  Wire.write(number);
}


void loop() {
//  if(Serial.available()) {
//    int n = Serial.read() - '0';
//    executeCommand(n);
//  }
}

