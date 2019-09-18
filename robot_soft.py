import subprocess
import shlex
from constants import *
import socket
from utils import StoppableThread
from utils import soft_logger as logger
import json
from robot_hardware import encoders, drive_control, distance_sensor


class CommunicationService:
    client = None
    receiver_thread = None

    def __init__(self, executor):
        self.cmd_executor = executor
        executor.attach_communicator(self)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.get_connection()

    def get_connection(self):
        """
        Keeps on listening for incoming connection request and connects a client when there is no current session
        """

        self.sock.bind((HOST, PORT))
        self.sock.listen()

        conn, addr = self.sock.accept()
        logger.info('Client connected from {}'.format(addr))
        self.client = conn

        self.receiver_thread = StoppableThread(target=self.receive)
        self.receiver_thread.start()

    def receive(self):
        while True:

            if self.client:
                try:
                    bits = self.client.recv(BUFF_SIZE)
                    message = bits.decode('ascii')

                    if message:
                        logger.info('Received message: {}'.format(message))

                        message = json.loads(message)

                        if type(message) == str:
                            self.cmd_executor.execute(message)

                except socket.error as e:
                    logger.error(str(e))
                    logger.info('Connection with client was closed')
                    self.cmd_executor.execute(CLIENT_LOST)
                    self.dispose()

    def send(self, message):
        if self.client:
            logger.info('Sending message: {}'.format(message))
            message = json.dumps(message)
            self.client.send(bytearray(message, 'ascii'))
        else:
            logger.error('There is no client to send message: {}'.format(message))

    def dispose(self):
        if self.client:
            self.client.close()

        self.sock.close()

        self.receiver_thread.stop()
        self.client = None

        self.get_connection()


class CommandExecutor:
    """Executes given command on robot"""

    communicator = None
    streaming_thread = None

    def attach_communicator(self, communicator):
        self.communicator = communicator

    def execute(self, message):
        logger.info('Received command: {}'.format(message))

        data = message.split(' ')

        command = data[0]
        arguments = data[1:]

        if command == START_STREAM_CMD:
            self.start_streaming()

        elif command == STOP_STREAM_CMD:
            self.stop_streaming()

        elif command == START_NETWORK_STREAM_CMD:
            self.start_network_streaming()

        elif command == STOP_NETWORK_STREAM_CMD:
            self.stop_network_streaming()

        elif command == SHUTDOWN_CMD:
            self.dispose()

        elif command == RUN_FORWARD_CMD:
            drive_control.forward()

        elif command == RUN_BACKWARD_CMD:
            drive_control.backward()

        elif command == RUN_LEFT_CMD:
            drive_control.left()

        elif command == RUN_RIGHT_CMD:
            drive_control.right()

        elif command == STOP_ROBOT_CMD:
            drive_control.stop()

        elif command == SET_SPEED_CMD:
            speed = int(arguments[0])
            drive_control.set_speed(speed)

        elif command == CAMERA_DOWN_CMD:
            drive_control.turn_camera_down()

        elif command == CAMERA_UP_CMD:
            drive_control.turn_camera_up()

        elif command == CAMERA_RIGHT_CMD:
            drive_control.turn_camera_right()

        elif command == CAMERA_LEFT_CMD:
            drive_control.turn_camera_left()

        elif command == MEASURE_DISTANCE_CMD:
            angle, distance = distance_sensor.range()
            data = {'angle': angle, 'distance': distance}
            self.communicator.send(data)

        elif command == SENSOR_LEFT_CMD:
            distance_sensor.turn_left()

        elif command == SENSOR_RIGHT_CMD:
            distance_sensor.turn_right()

        elif command == SET_SENSOR_DELTA_CMD:
            delta = int(arguments[0])
            distance_sensor.set_delta(delta)

    def dispose(self):
        logger.info('Shutting down whole system')

        drive_control.stop()

        self.stop_streaming()
        self.communicator.dispose()

        subprocess.call([SHUTDOWN])

    def start_streaming(self):
        self.streaming_thread = StoppableThread(target=self.stream_worker)
        self.streaming_thread.start()

    def stop_streaming(self):
        logger.info('Streaming service closed')
        self.streaming_thread.stop()

    def start_network_streaming(self):
        self.streaming_thread = StoppableThread(target=self.network_stream_worker)
        self.streaming_thread.start()

    def stop_network_streaming(self):
        logger.info('Streaming service closed')
        self.streaming_thread.stop()

    def network_stream_worker(self):
        logger.info('Starting streaming service')

        process = subprocess.Popen(
            shlex.split(START_NETWORK_STREAM),
            stdout=subprocess.PIPE)

        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                self.communicator.send(CANT_OPEN_STREAM)
                logger.error(output.strip())

        rc = process.poll()
        return rc

    def stream_worker(self):
        logger.info('Starting streaming service')

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
                logger.error(output.strip())

        rc = process.poll()
        return rc


def dont_crash(communicator):
    while True:
        angle, distance = distance_sensor.range()

        if distance < MIN_DISTANCE and drive_control.state != STOP_ROBOT_CMD:
            drive_control.stop()
            logger.error('Stopping robot to avoid crash!')
            communicator.send(TO_CLOSE_TO_OBSTACLE_MSG)


def init():
    logger.info('Script was launched')

    executor = CommandExecutor()
    communicator = CommunicationService(executor)

    t = StoppableThread(target=dont_crash, args=(communicator,))
    t.start()


init()

if __name__ == '__main__':
    init()
