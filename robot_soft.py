import subprocess
import sys
import shlex
from utils import *
import json
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

                    message = json.loads(message)

                    if type(message) == str:
                        self.cmd_executor.execute(message)

                except ConnectionResetError:
                    self.log.info('Connection with client was closed')
                    self.cmd_executor.execute(CLIENT_LOST)
                    self.client = None

    def send(self, message):
        if self.client:
            self.log.info('Sending message:', message)
            message = json.dumps(message)
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
        self.log.info('Received command:', message)

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

    def start_network_streaming(self):
        self.streaming_thread = StoppableThread(target=self.network_stream_worker)
        self.streaming_thread.start()

    def stop_network_streaming(self):
        self.log.info('Streaming service closed')
        self.streaming_thread.stop()

    def network_stream_worker(self):
        self.log.info('Starting streaming service')

        process = subprocess.Popen(
            shlex.split(START_NETWORK_STREAM),
            stdout=subprocess.PIPE)

        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                self.communicator.send(CANT_OPEN_STREAM)
                self.log.error(output.strip())

        rc = process.poll()
        return rc

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


def dont_crash(communicator):
    while True:
        angle, distance = distance_sensor.range()

        if distance < MIN_DISTANCE and drive_control.state != STOP_ROBOT_CMD:
            drive_control.stop()
            logging.error('Stopping robot to avoid crash!')
            communicator.send(TO_CLOSE_TO_OBSTACLE_MSG)


def init():
    configure_logger()
    logging.info('Script was launched')

    executor = CommandExecutor()
    communicator = CommunicationService(executor)

    t = StoppableThread(target=dont_crash, args=(communicator,))
    t.start()


init()

if __name__ == '__main__':
    init()
