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

#         cap = cv2.VideoCapture(sys.argv[1])

#         # Check if camera opened successfully
#         if (cap.isOpened() == False):
#             print("Unable to read video file:")

#         # Default resolutions of the frame are obtained.The default resolutions are system dependent.
#         # We convert the resolutions from float to integer.
#         frame_width = int(cap.get(3))
#         frame_height = int(cap.get(4))

#         time = 0
#         millis_per_frame = 40   # Millis per frame in a 25 fps video
#         ret, frame = None, None
#         prev_timestamp = 0

#         persons = []
#         while finished == False:
#             response = self.rek.get_person_tracking(JobId=jobId,
#                                                     MaxResults=maxResults,
#                                                     NextToken=paginationToken,
#                                                     SortBy='TIMESTAMP')

#             if first_page:
#                 out = cv2.VideoWriter(sys.argv[1][:sys.argv[1].index('.')] + '_processed.mp4', cv2.VideoWriter_fourcc(
#                     *'mp4v'), int(response['VideoMetadata']['FrameRate']), (frame_width, frame_height))
#                 millis_per_frame = int(
#                     1000 / int(response['VideoMetadata']['FrameRate']))
#                 first_page = False

#             persons.extend(response['Persons'])
#             if 'NextToken' in response:
#                 paginationToken = response['NextToken']
#             else:
#                 finished = True

#         num_persons = len(persons)
#         i = 0
#         print('Writing new processed video.')
#         while i < num_persons:
#             personDetection = persons[i]
#             # print(personDetection)
#             # In millis from beginning of video
#             timestamp = personDetection['Timestamp']

#             while(time < timestamp):
#                 ret, frame = cap.read()
#                 if ret == False:
#                     break

#                 time += millis_per_frame
#                 out.write(frame)

#             ret, frame = cap.read()
#             if ret == True:
#                 while True:
#                     personDetection = persons[i]
#                     box = personDetection['Person']['BoundingBox']
#                     x1 = int(box['Left'] * frame_width)
#                     y1 = int(box['Top'] * frame_height)
#                     x2 = int(x1 + (box['Width'] * frame_width))
#                     y2 = int(y1 + (box['Height'] * frame_height))
#                     # In millis from beginning of video
#                     timestamp = personDetection['Timestamp']
#                     random.seed(personDetection['Person']['Index'])
#                     cv2.rectangle(frame, (x1, y1), (x2, y2), (random.randint(
#                         0, 255), random.randint(0, 255), random.randint(0, 255)), 3)

#                     if i + 1 >= num_persons or persons[i + 1]['Timestamp'] != timestamp:
#                         break
#                     i += 1

#                 time += millis_per_frame
#                 out.write(frame)
#             else:
#                 break

#             i += 1

#         # When everything done, release the video capture and video write objects
#         cap.release()
#         out.release()

#         # Closes all the frames
#         cv2.destroyAllWindows()


# if __name__ == "__main__":
#     analyzer = VideoDetect()
#     analyzer.main()
