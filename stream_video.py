import subprocess
import shlex
import cv2
import threading
import time
import numpy as np


def open_pipe():
    process = subprocess.Popen(
        shlex.split(' /bin/bash  /home/zbigniew/PycharmProjects/opencv/readStream.sh'),
        stdout=subprocess.PIPE)

    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())
    rc = process.poll()
    return rc


def init():
    t = threading.Thread(target=open_pipe)
    t.start()

    time.sleep(1)
    print('ready')
    cap = cv2.VideoCapture('fifo264')

    while cap.isOpened():
        ret, frame = cap.read()

        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    t.join()


if __name__ == '__main__':
    init()
