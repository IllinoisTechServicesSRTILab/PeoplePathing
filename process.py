import cv2
import time
import sys

if len(sys.argv) < 2:
    print('Usage: python3 process.py <filename-of-video>')

person_cascade = cv2.CascadeClassifier('haarcascade_fullbody.xml')
cap = cv2.VideoCapture(sys.argv[1])
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))
fps = cap.get(cv2.CAP_PROP_FPS)
out = cv2.VideoWriter(sys.argv[1][:sys.argv[1].index('.')] + '_processed.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))

while True:
    r, frame = cap.read()
    if r:
        start_time = time.time()
        # Downscale to improve frame rate
        # frame = cv2.resize(frame, (640, 360))
        # Haar-cascade classifier needs a grayscale image
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        rects = person_cascade.detectMultiScale(gray_frame)

        end_time = time.time()
        # print("Elapsed Time:", end_time-start_time)

        for (x, y, w, h) in rects:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        out.write(frame)
    else:
        break

cap.release()
out.release()

# Closes all the frames
cv2.destroyAllWindows()