import smbus2
import board
import busio

import adafruit_vl53l0x
import time
import sys


class Encoder(object):
    count = 0

    def __init__(self, address):
        self.bus = smbus2.SMBus(1)
        self.address = address

    def write(self, value):
        try:
            self.bus.write_byte(self.address, value)
            self.count = 0
            time.sleep(0.01)
        except OSError:
            self.count += 1
            if self.count > 4:
                print('fatal bus error')
                sys.exit()

            time.sleep(0.05)
            self.write(value)

    def read_number(self):
        try:
            time.sleep(0.1)
            number = self.bus.read_byte(self.address)
            return number
        except OSError:
            time.sleep(0.5)
            return -1

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


class Encoders(object):
    l_encoder = None
    r_encoder = None
    # tick_length = 0.2042035
    tick_length = 1

    def __init__(self):
        self.l_encoder = Encoder(0x07)
        self.r_encoder = Encoder(0x06)

    def get_distances(self):
        left_ticks = self.l_encoder.get_steps()  # * self.tick_length
        right_ticks = self.r_encoder.get_steps()  # * self.tick_length
        print('left:', left_ticks, 'cm', 'right:', right_ticks, 'cm')

        return left_ticks, right_ticks

    def reset(self):
        self.l_encoder.reset()
        self.r_encoder.reset()


class Sensor(object):
    servo_pos = 90
    servo_delta = 5

    address = None
    bus = None

    count = 0
    i2c = busio.I2C(board.SCL, board.SDA)
    vl53 = adafruit_vl53l0x.VL53L0X(i2c)

    def __init__(self, address):
        self.bus = smbus2.SMBus(1)
        self.address = address

    def write(self, value):
        try:
            self.bus.write_byte(self.address, value)
            self.count = 0
            time.sleep(0.01)
        except OSError:
            self.count += 1
            if self.count > 4:
                print('fatal bus error')
                sys.exit()

            time.sleep(0.1)
            self.write(value)

    def read_number(self):
        try:
            time.sleep(0.1)
            number = self.bus.read_byte(self.address)
            return number
        except OSError:
            time.sleep(0.5)
            return -1

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

    s = Sensor(0x08)

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
