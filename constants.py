START_STREAM = './scripts/netcatStream.sh'
START_NETWORK_STREAM = './scripts/networkStream.sh'
READ_STREAM = './scripts/readStream.sh'
FIFO_FILE = 'fifo264'

# values used for socket communication
HOST = '0.0.0.0'
#SERVER = '192.168.100.18'
SERVER = '127.0.0.1'
PORT = 45060
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
