import subprocess
from tkinter import *
import shlex
import cv2
import time
import threading
from utils import Observer, CommunicationClient
from utils import steering_logger as logger
from constants import *
import os


communicator: CommunicationClient = None
root = Tk()


def open_pipe():
    process = subprocess.Popen(
        shlex.split(READ_STREAM),
        stdout=subprocess.PIPE)

    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())
    rc = process.poll()
    return rc


def start_stream():
    class StreamObserver(Observer):
        def notify(self, value):
            if value == STREAM_ENABLED:
                logger.info('Started streaming to opencv')
                cap = cv2.VideoCapture(FIFO_FILE)

                while cap.isOpened():
                    ret, frame = cap.read()

                    cv2.imshow('frame', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

                cap.release()
                cv2.destroyAllWindows()
            elif value == CANT_OPEN_STREAM:
                logger.error('Cant stream video to opencv')
                communicator.detach_observer(self)

    t = threading.Thread(target=open_pipe)
    t.start()

    time.sleep(1)
    logger.info('Opened streaming pipe')

    communicator.attach_observer(StreamObserver())
    communicator.send(START_STREAM_CMD)


def dispose():
    os.system('xset r on')
    root.destroy()
    exit(0)


def key_pressed(event):
    value = repr(event.char)
    c = value[1]

    key_pressed.key_pressed = c
    if key_pressed.old_value != c:
        if c == 'w':
            communicator.send(RUN_FORWARD_CMD)
        elif c == 's':
            communicator.send(RUN_BACKWARD_CMD)
        elif c == 'a':
            communicator.send(RUN_LEFT_CMD)
        elif c == 'd':
            communicator.send(RUN_RIGHT_CMD)
        key_pressed.old_value = c

    if c == 'i':
        communicator.send(CAMERA_UP_CMD)
    elif c == 'k':
        communicator.send(CAMERA_DOWN_CMD)
    elif c == 'j':
        communicator.send(CAMERA_LEFT_CMD)
    elif c == 'l':
        communicator.send(CAMERA_RIGHT_CMD)
    elif c == ',':
        communicator.send(MEASURE_DISTANCE_CMD)
    elif c == 'r':
        communicator.send(SHUTDOWN_CMD)
        dispose()
    elif c == 'q':
        communicator.send(TURN_SENSOR_LEFT_CMD)
    elif c == 'e':
        communicator.send(TURN_SENSOR_RIGHT_CMD)
    elif c == 'x':
        communicator.send(START_NETWORK_STREAM_CMD)
    elif c == 'z':
        start_stream()
    elif c == '+':
        if key_pressed.speed + 10 <= 255:
            key_pressed.speed += 10

            msg = SET_SPEED_CMD + " " + str(key_pressed.speed)
            communicator.send(msg)

    elif c == '-':
        if key_pressed.speed - 10 >= 0:
            key_pressed.speed -= 10
            msg = SET_SPEED_CMD + " " + str(key_pressed.speed)
            communicator.send(msg)


key_pressed.old_value = 'h'
key_pressed.speed = 180
key_pressed.key_pressed = 'h'


def key_released(event):
    if key_pressed.key_pressed in 'wsad':
        communicator.send(STOP_ROBOT_CMD)
        key_pressed.old_value = 'h'


class DistanceObserver(Observer):
    def notify(self, value: dict):
        if type(value) == dict and value:
            try:
                angle = value['angle']
                distance = value['distance']
            except TypeError and KeyError:
                pass


def init():

    global communicator
    communicator = CommunicationClient()

    try:
        communicator.connect()
    except ConnectionError as e:
        print(e)
        logger.error('Cant connect to server')
        return

    logger.info('Connection established')

    os.system('xset r off')

    communicator.attach_observer(DistanceObserver())

    frame = Frame(root, width=100, height=100)
    frame.bind("<KeyPress>", key_pressed)
    frame.bind("<KeyRelease>", key_released)
    frame.focus_set()
    frame.pack()

    root.mainloop()


if __name__ == '__main__':
    init()
