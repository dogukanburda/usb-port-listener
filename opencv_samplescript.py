import cv2
import numpy as np


cap = cv2.VideoCapture('vid.mp4')
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output.mp4',fourcc, 5, (640,480))


while True:
    ret, frame = cap.read()
    if ret == True:
        resized = cv2.resize(frame,(640,480), interpolation = cv2.INTER_CUBIC)
        out.write(resized)
    else:
        break
    
cap.release()
out.release()
cv2.destroyAllWindows()