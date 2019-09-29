from robot_hardware import drive_control
import time

if __name__ == '__main__':
    drive_control.forward()
    time.sleep(1)
    drive_control.stop()
