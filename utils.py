import threading
import json
import socket
import logging

# values used for video streaming
from typing import List

START_STREAM = './scripts/netcatStream.sh'
START_NETWORK_STREAM = './scripts/networkStream.sh'
READ_STREAM = './scripts/readStream.sh'
FIFO_FILE = 'fifo264'

# values used for socket communication
HOST = '0.0.0.0'
SERVER = '192.168.100.18'
PORT = 6760
BUFF_SIZE = 1024

LOGNAME = 'robot_log.txt'

# messages passed from server to client
STREAM_ENABLED = 'stream_enabled'
CANT_OPEN_STREAM = 'unable_to_open_stream'
CLIENT_LOST = 'client_lost'

# commands used in communication
SHUTDOWN = './scripts/shutdown.sh'
START_STREAM_CMD = 'start_stream'
STOP_STREAM_CMD = 'stop_stream'
START_NETWORK_STREAM_CMD = 'start_network_stream'
STOP_NETWORK_STREAM_CMD = 'stop_network_stream'
SHUTDOWN_CMD = 'shutdown'
RUN_FORWARD_CMD = 'forward'
RUN_BACKWARD_CMD = 'backward'
RUN_RIGHT_CMD = 'right'
RUN_LEFT_CMD = 'left'
STOP_ROBOT_CMD = 'stop'
SET_SPEED_CMD = 'speed'
CAMERA_RIGHT_CMD = 'camera_right'
CAMERA_LEFT_CMD = 'camera_left'
CAMERA_UP_CMD = 'camera_up'
CAMERA_DOWN_CMD = 'camera_down'
MEASURE_DISTANCE_CMD = 'measure'
SENSOR_RIGHT_CMD = 'sensor_right'
SENSOR_LEFT_CMD = 'sensor_left'
SET_SENSOR_DELTA_CMD = 'set_sensor_delta'
TO_CLOSE_TO_OBSTACLE_MSG = 'obstacle'

# hardware constants
WHEELS_CAMERA_ADDR = 0X04
RIGHT_ENCODER_ADDR = 0x06
LEFT_ENCODER_ADDR = 0x07
SERVO_W_DISTANCE_SENSOR_ADDR = 0x08
OBSTACLE_CHECK_TIME = 0.2
MIN_DISTANCE = 100

# one byte commands passed to arduino
SETTING_SPEED_FLAG = ord('q')
FORWARD = ord('f')
BACKWARD = ord('b')
LEFT = ord('l')
RIGHT = ord('r')
STOP = ord('h')
TURN_CAMERA_DOWN = ord('w')
TURN_CAMERA_UP = ord('s')
TURN_CAMERA_RIGHT = ord('d')
TURN_CAMERA_LEFT = ord('a')
SET_POSITION_SERVO_X_FLAG = ord('z')
SET_POSITION_SERVO_Y_FLAG = ord('y')
SET_SIGN_POSITIVE_FLAG = 0
SET_SIGN_NEGATIVE_FLAG = 1


class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, target, args=()):
        super(StoppableThread, self).__init__(target=target, args=args)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


class Observer:
    def notify(self, value):
        pass


class Observable:
    observers = []  # type: List[Observer]

    def attach_observer(self, observer):
        self.observers.append(observer)

    def detach_observer(self, observer):
        self.observers.remove(observer)

    def notify_observers(self, value: object) -> None:
        for obs in self.observers:
            obs.notify(value)


class CommunicationClient(Observable):
    """Uses a socket in order to connect to robot server"""

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.receiver_thread = None

    def connect(self):
        logging.info('Trying connect to server')
        self.sock.connect((SERVER, PORT))

        self.receiver_thread = StoppableThread(target=self.receive())
        self.receiver_thread.start()

    def dispose(self):
        self.receiver_thread.stop()
        self.sock.close()

    def receive(self):
        while True:
            try:
                bits = self.sock.recv(BUFF_SIZE)
                message = bits.decode('ascii')

                message = json.loads(message)
                logging.info('Received message:', message)

            except ConnectionResetError:
                logging.info('Connection was remotely closed, shutting down')
                self.dispose()

    def send(self, message):
        message = json.dumps(message)
        logging.info('Sending message:', message)
        self.sock.send(bytearray(message, 'ascii'))
