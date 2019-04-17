import cv2
import time
import sys

if len(sys.argv) < 2:
    print('Usage: python3 process.py <filename-of-video>')

hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
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
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        rects, weights = hog.detectMultiScale(gray_frame)
        
        # Measure elapsed time for detections
        end_time = time.time()
        # print("Elapsed time:", end_time-start_time)
        
        for i, (x, y, w, h) in enumerate(rects):
            if weights[i] < 0.7:
                continue
            cv2.rectangle(frame, (x,y), (x+w,y+h),(0,255,0),2)
        out.write(frame)
    else:
        break

cap.release()
out.release()

# Closes all the frames
cv2.destroyAllWindows()