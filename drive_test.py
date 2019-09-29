from robot_hardware import drive_control
import time


def ride_forward_test():
    drive_control.forward()
    time.sleep(1)
    drive_control.stop()


if __name__ == '__main__':
    ride_forward_test()
