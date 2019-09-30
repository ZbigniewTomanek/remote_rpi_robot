from threading import Thread
import json
import socket
from constants import SERVER, PORT, BUFF_SIZE
import logging
import sys

from typing import List


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
        self.sock = socket.socket()
        self.receiver_thread = None
        self.is_disposed = False

    def connect(self):
        utils_logger.info('Trying connect to server')
        self.sock.connect((SERVER, PORT))

        self.receiver_thread = Thread(target=self.receive)
        self.receiver_thread.start()

    def dispose(self):
        self.is_disposed = True
        self.receiver_thread.join()
        self.sock.close()

    def receive(self):
        while not self.is_disposed:
            try:
                bits = self.sock.recv(BUFF_SIZE)
                message = bits.decode('ascii')

                if message:
                    utils_logger.info('Received message: {}'.format(message))

                    try:
                        message = json.loads(message)
                        self.notify_observers(message)
                    except ValueError:
                        utils_logger.error('Broken message')

            except socket.error:
                utils_logger.info('Connection was remotely closed, shutting down')
                self.dispose()

    def send(self, message):
        message = json.dumps(message)
        utils_logger.info('Sending message: {}'.format(message))
        self.sock.send(bytearray(message, 'ascii'))


file_handler = logging.FileHandler('robot.log')
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

std_handler = logging.StreamHandler(sys.stdout)
std_handler.setLevel(logging.DEBUG)
std_handler.setFormatter(formatter)

utils_logger = logging.getLogger(__name__)
utils_logger.setLevel(logging.INFO)
utils_logger.addHandler(file_handler)
utils_logger.addHandler(std_handler)

steering_logger = logging.getLogger('Steering')
steering_logger.setLevel(logging.INFO)
steering_logger.addHandler(std_handler)

soft_logger = logging.getLogger('Control')
soft_logger.setLevel(logging.INFO)
soft_logger.addHandler(file_handler)
soft_logger.addHandler(std_handler)
