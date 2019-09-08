import subprocess
import socket
import shlex
import cv2
import time
from utils import *
import numpy as np


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

def receive(self):
    while True:
        try:
            bits = sock.recv(BUFF_SIZE)
            message = bits.decode('ascii')

            log.info('Received message:', message)

            if message == 'exit': # TODO
                log.info('Shutting down')
            else:
                cmd_executor.execute(message)

        except ConnectionResetError:
            log.info('Connection was remotely closed, shutting down')
            dispose()

def send(self, message):
    log.info('Sending message:', message)
    sock.send(bytearray(message, 'ascii'))


def server_worker():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()

        with conn:
            print('Client connected by', addr)

            while True:
                data = conn.recv(1024)


def init():
    t = threading.Thread(target=open_pipe)
    t.start()

    time.sleep(1)
    print('ready')
    cap = cv2.VideoCapture(FIFO_FILE)

    while cap.isOpened():
        ret, frame = cap.read()

        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    init()
