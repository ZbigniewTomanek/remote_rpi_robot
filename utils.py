import threading

# values used for video streaming
START_STREAM = './netcatStream.sh'
READ_STREAM = './readStream.sh'
FIFO_FILE = 'fifo264'

# values used for socket communication
HOST = '127.0.0.1'
SERVER = '192.168.100.13'
PORT = 69420
BUFF_SIZE = 1024

LOGNAME = 'robot_log.txt'

# messages passed from server to client
STREAM_ENABLED = 'stream_enabled'
CANT_OPEN_STREAM = 'unable_to_open_stream'
CLIENT_LOST = 'client_lost'

# commands used in communication
SHUTDOWN = './shutdown.sh'
START_STREAM_CMD = 'start_stream'
STOP_STREAM_CMD = 'stop_stream'
SHUTDOWN_CMD = 'shutdown'

# hardware constants
WHEELS_CAMERA_ADDR = 0X04
RIGHT_ENCODER_ADDR = 0x06
LEFT_ENCODER_ADDR = 0x07
SERVO_W_DISTANCE_SENSOR_ADDR = 0x08

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

    def __init__(self, target):
        super(StoppableThread, self).__init__(target=target)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()
