# remote_rpi_robot
This repository contains code that runs robot that i built myself from scratch with use of raspberry pi 3, arduinos, camera, sensors and# 

## What's inside?

I'm sharing this project hoping that it can help somebody that is looking for example code or solutions :)

![alt text](https://raw.githubusercontent.com/ZbigniewTomanek/remote_rpi_robot/master/images/front.png)

This is a robot I made completly from scratch using cheap parts from aliexpress.

It's heart is raspebrry pi 3 which passes all commands that comes on certain port to arduinos by i2c interface.

For this moment robot has 640x480 camera on two servos, two laser encoders and adafruit vl53l0x laser distance sensor on servo.
For wheels and camera servos handling i used arduino uno with motor shield. Sensor servo and encoders are controlled by three arudinos nano

I used so many controllers because I wanted accuretly know encoders ticks and they are counted by interruption.

![alt text](https://raw.githubusercontent.com/ZbigniewTomanek/remote_rpi_robot/master/images/up.png)

All of this stuff is run by 4x18650 li-ion batteries whose output voltage is reduced from 13 to 5V.
On the bottom it also has a led stripes for cool effect.

![alt text](https://raw.githubusercontent.com/ZbigniewTomanek/remote_rpi_robot/master/images/bottom.png)

Behaviour is controlled from python and bash scripts levels. Code for arduinos of course was made in arduino IDE.

## How does it work

For now i'm able to manually controll the machine using keyboard. 
Commands from my local machine are passed by tcp port to robot_soft.py script which executes them on hardware.
This interface is made with intention to be easy to zip with tools like unity or tensorflow.

That's how effect look like:

![alt text](https://raw.githubusercontent.com/ZbigniewTomanek/remote_rpi_robot/master/images/vid1.gif)


![alt text](https://raw.githubusercontent.com/ZbigniewTomanek/remote_rpi_robot/master/images/vid2.gif)


![alt text](https://raw.githubusercontent.com/ZbigniewTomanek/remote_rpi_robot/master/images/vid3.gif)

## Further development
I want to use this platform to learn how to programm autonomus vehicle using opencv imaage processing and neural nets on remote device.
For this moment video is streamed via local network by internet socket of linux fifo queue.
