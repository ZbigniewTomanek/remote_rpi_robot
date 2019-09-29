from robot_hardware import drive_control
import time

ride_time = 1


def ride_forward_test():
    print('forward')
    drive_control.forward()
    time.sleep(ride_time)
    drive_control.stop()


def ride_backward_test():
    print('backward')
    drive_control.backward()
    time.sleep(ride_time)
    drive_control.stop()


def ride_left_test():
    print('left')
    drive_control.left()
    time.sleep(ride_time)
    drive_control.stop()


def ride_right_test():
    print('right')
    drive_control.right()
    time.sleep(ride_time)
    drive_control.stop()


def set_speed_test():
    drive_control.set_speed(150)


if __name__ == '__main__':
    drive_control.write(102)

    ride_forward_test()
    ride_backward_test()
    ride_left_test()
    ride_right_test()
