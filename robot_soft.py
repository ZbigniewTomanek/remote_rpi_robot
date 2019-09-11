import socket
import logging
import subprocess
import sys
import shlex
from utils import *
from robot_hardware import encoders, drive_control, distance_sensor


class CommunicationService:
    log = logging.getLogger('Communication Service')
    client = None

    def __init__(self, executor):
        self.cmd_executor = executor
        executor.attach_communicator(self)

        self.server_thread = StoppableThread(target=self.server_listener)
        self.server_thread.start()

        self.receiver_thread = StoppableThread(target=self.receive)
        self.receiver_thread.start()

    def server_listener(self):
        """
        Keeps on listening for incoming connection request and connects a client when there is no current session
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()

            while True:
                if not self.client:
                    conn, addr = s.accept()
                    self.log.info('Client connected from', addr)
                    self.client = conn

    def receive(self):
        while True:
            if self.client:
                try:
                    bits = self.client.recv(BUFF_SIZE)
                    message = bits.decode('ascii')

                    self.log.info('Received message:', message)

                    if message == 'exit': # TODO
                        self.log.info('Shutting down')
                    else:
                        self.cmd_executor.execute(message)

                except ConnectionResetError:
                    self.log.info('Connection with client was closed')
                    self.cmd_executor.execute(CLIENT_LOST)
                    self.client = None

    def send(self, message):
        if self.client:
            self.log.info('Sending message:', message)
            self.client.send(bytearray(message, 'ascii'))
        else:
            self.log.error('There is no client to send message:', message)

    def dispose(self):
        if self.client:
            self.client.close()

        self.server_thread.stop()
        self.receiver_thread.stop()


class CommandExecutor:
    """Executes given command on robot"""

    log = logging.getLogger('Command Executor')

    communicator = None
    streaming_thread = None

    def attach_communicator(self, communicator):
        self.communicator = communicator

    def execute(self, message):
        data = message.split(' ')

        command = data[0]
        arguments = data[1:]

        if command == START_STREAM_CMD:
            self.start_streaming()
        elif command == STOP_STREAM_CMD:
            self.stop_streaming()
        elif command == SHUTDOWN_CMD:
            self.dispose()

    def dispose(self):
        self.log.info('Shutting down whole system')

        drive_control.stop()

        self.stop_streaming()
        self.communicator.dispose()

        subprocess.call([SHUTDOWN])

    def start_streaming(self):
        self.streaming_thread = StoppableThread(target=self.stream_worker)
        self.streaming_thread.start()

    def stop_streaming(self):
        self.log.info('Streaming service closed')
        self.streaming_thread.stop()

    def stream_worker(self):
        self.log.info('Starting streaming service')

        process = subprocess.Popen(
            shlex.split(START_STREAM),
            stdout=subprocess.PIPE)

        self.communicator.send(STREAM_ENABLED)

        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                self.communicator.send(CANT_OPEN_STREAM)
                self.log.error(output.strip())

        rc = process.poll()
        return rc


def configure_logger():
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    logging.basicConfig(filename=LOGNAME,
                        filemode='a',
                        format=formatter,
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)

    logging.getLogger().addHandler(handler)


def init():
    configure_logger()
    logging.info('Script was launched')


if __name__ == '__main__':
    init()
