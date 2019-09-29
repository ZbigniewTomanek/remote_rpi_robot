from smbus2 import SMBus
import board
import busio
import adafruit_vl53l0x

import time
import logging
from constants import *

log = logging.getLogger('Hardware')


class I2cDevice:
    address = None
    error_count = 0

    def write(self, value):
        try:
            with SMBus(1) as b:
                b.write_byte_data(self.address, 0, value)
                self.error_count = 0

        except OSError:
            self.error_count += 1

            if self.error_count > 4:
                log.error('Byte "{}" cannot be written to device on address {}'.format(value, self.address))

            time.sleep(0.05)
            self.write(value)

    def read_number(self):
        try:
            with SMBus(1) as b:
                number = b.read_byte(self.address)

            return number
        except OSError:
            return -1


class Drive(I2cDevice):
    speed = 255
    state = STOP_ROBOT_CMD

    def __init__(self, address):
        self.address = address

    def set_speed(self, speed):
        if speed < 0 or speed > 255:
            log.error('Wrong speed value')
            return

        try:
            self.write(SETTING_SPEED_FLAG)
            self.write(speed)
            self.speed = speed

            log.info('Speed of robot set to {}'.format(speed))
        except ValueError:
            log.error('Value of robot speed was not set')

    def forward(self):
        self.write(FORWARD)
        self.state = RUN_FORWARD_CMD

    def backward(self):
        self.write(BACKWARD)
        self.state = RUN_BACKWARD_CMD

    def left(self):
        self.write(LEFT)
        self.state = RUN_LEFT_CMD

    def right(self):
        self.write(RIGHT)
        self.state = RUN_RIGHT_CMD

    def stop(self):
        self.write(STOP)
        self.state = STOP_ROBOT_CMD

    def turn_camera_right(self):
        self.write(TURN_CAMERA_RIGHT)

    def turn_camera_left(self):
        self.write(TURN_CAMERA_LEFT)

    def turn_camera_up(self):
        self.write(TURN_CAMERA_UP)

    def turn_camera_down(self):
        self.write(TURN_CAMERA_DOWN)

    def set_camera_position_x(self, pos):
        if abs(pos) > 90:
            log.error('Rotating camera in x for {} degrees is not possible'.format(pos))

        if pos < 0:
            self.write(SET_POSITION_SERVO_X_FLAG)
            self.write(SET_SIGN_NEGATIVE_FLAG)
            self.write(-pos)
        else:
            self.write(SET_POSITION_SERVO_X_FLAG)
            self.write(SET_SIGN_POSITIVE_FLAG)
            self.write(pos)

    def set_camera_position_y(self, pos):
        if abs(pos) > 90:
            log.error('Rotating camera in y for {} degrees is not possible'.format(pos))

        if pos < 0:
            self.write(SET_POSITION_SERVO_Y_FLAG)
            self.write(SET_SIGN_NEGATIVE_FLAG)
            self.write(-pos)
        else:
            self.write(SET_POSITION_SERVO_Y_FLAG)
            self.write(SET_SIGN_POSITIVE_FLAG)
            self.write(pos)


class Encoder(I2cDevice):
    def __init__(self, address):
        self.address = address

    def reset(self):
        self.write(0)

    def stop(self):
        self.write(1)

    def start(self):
        self.write(2)

    def get_steps(self):
        steps = 0
        self.write(3)
        steps += self.read_number() * 255
        self.write(4)
        steps += self.read_number()
        return steps


class Encoders(I2cDevice):
    # tick_length = 0.2042035
    tick_length = 1

    def __init__(self, l_encoder_addr, r_encoder_addr):
        self.l_encoder = Encoder(l_encoder_addr)
        self.r_encoder = Encoder(r_encoder_addr)

    def get_distances(self):
        left_ticks = self.l_encoder.get_steps()  # * self.tick_length
        right_ticks = self.r_encoder.get_steps()  # * self.tick_length
        print('left:', left_ticks, 'cm', 'right:', right_ticks, 'cm')

        return left_ticks, right_ticks

    def reset(self):
        self.l_encoder.reset()
        self.r_encoder.reset()


class Sensor(I2cDevice):
    servo_pos = 90
    servo_delta = 5

    i2c = busio.I2C(board.SCL, board.SDA)
    vl53 = adafruit_vl53l0x.VL53L0X(i2c)

    def __init__(self, address):
        self.address = address

    def set_delta(self, delta):
        self.servo_delta = delta
        self.write(0)
        self.write(delta)

    def range(self):
        return self.servo_pos, self.vl53.range

    def turn_right(self):
        if self.servo_pos + self.servo_delta <= 180:
            self.servo_pos += self.servo_delta
            self.write(5)

    def turn_left(self):
        if self.servo_pos - self.servo_delta >= 0:
            self.servo_pos -= self.servo_delta
            self.write(6)

    def scan(self, delta=2):
        if 180 % delta != 0:
            delta = 2

        distances = []

        self.set_delta(90)
        self.turn_left()

        self.set_delta(delta)

        for i in range(int(180 / delta)):
            distances.append(self.range())
            self.turn_right()

        self.set_delta(90)
        self.turn_left()
        self.set_delta(self.servo_delta)

        return distances


encoders = Encoders(LEFT_ENCODER_ADDR, RIGHT_ENCODER_ADDR)
distance_sensor = Sensor(SERVO_W_DISTANCE_SENSOR_ADDR)
drive_control = Drive(WHEELS_CAMERA_ADDR)

if __name__ == '__main__':
    # e = Encoder(0x06)

    e = Encoders()
    while 1:
        temp = input('podaj komende: ')
        if temp == '0':
            e.reset()
        elif temp == '1':
            # print(e.get_steps())
            e.get_distances()

    s = Sensor(SERVO_W_DISTANCE_SENSOR_ADDR)

    while 1:
        temp = input('podaj komende: ')
        if temp == '0':
            s.set_delta(1)
        elif temp == '1':
            print(s.scan())
        elif temp == '2':
            print('odleglosc od czujnika: ' + str(s.range()) + 'mm')
        elif temp == '3':
            s.set_delta(20)
        elif temp == '4':
            s.turn_left()
        elif temp == '6':
            s.turn_right()
