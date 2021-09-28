# MIT License
# Copyright (c) 2019 JetsonHacks
# See LICENSE for OpenCV license and additional information

# https://docs.opencv.org/3.3.1/d7/d8b/tutorial_py_face_detection.html
# On the Jetson Nano, OpenCV comes preinstalled
# Data files are in /usr/sharc/OpenCV
import numpy as np
import cv2
import signal
import os
from cysystemd import journal


run = True
def handler_stop_signals(signum, frame):
    global run
    run = False
    journal.send(message="[INFO] SIGTERM signal received. Script PID: {}".format(str(os.getpid())),priority=journal.Priority.INFO, PID=str(os.getpid()), PTYPE='SUB')

signal.signal(signal.SIGTERM, handler_stop_signals)

# gstreamer_pipeline returns a GStreamer pipeline for capturing from the CSI camera
# Defaults to 1280x720 @ 30fps
# Flip the image by setting the flip_method (most common values: 0 and 2)
# display_width and display_height determine the size of the window on the screen


def gstreamer_pipeline(
    capture_width=1920,
    capture_height=1080,
    display_width=1920,
    display_height=1080,
    framerate=29,
    flip_method=2,
):
    return (
        "nvarguscamerasrc ! "
        "video/x-raw(memory:NVMM), "
        "width=(int)%d, height=(int)%d, "
        "format=(string)NV12, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )


def cameracap():
    journal.send(message="[INFO] OpenCV Script started. Script PID: {}".format(str(os.getpid())),priority=journal.Priority.INFO, PID=str(os.getpid()), PTYPE='SUB')
    cap = cv2.VideoCapture(gstreamer_pipeline(), cv2.CAP_GSTREAMER)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('/home/dogukan/output.mp4',fourcc, 20, (1920,1080))
    # [TODO] Add gstreamer writing pipeline instead of opencv videowriter
    if cap.isOpened():
        while run:
            ret, img = cap.read()
            out.write(img)

        cap.release()
        out.release()
        cv2.destroyAllWindows()
        journal.send(message="[INFO] OpenCV VideoCapture ended. Script PID: {}".format(str(os.getpid())),priority=journal.Priority.INFO, PID=str(os.getpid()), PTYPE='SUB')
    else:
        journal.send(message="[INFO] Unable to open camera. Script PID: {}".format(str(os.getpid())),priority=journal.Priority.INFO, PID=str(os.getpid()), PTYPE='SUB')
        print("Unable to open camera")


if __name__ == "__main__":
    cameracap()
