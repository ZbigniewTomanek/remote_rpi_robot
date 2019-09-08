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
