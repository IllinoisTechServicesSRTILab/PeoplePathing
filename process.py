# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# PDX-License-Identifier: MIT-0 (For details, see https://github.com/awsdocs/amazon-rekognition-developer-guide/blob/master/LICENSE-SAMPLECODE.)

import boto3
import json
import sys
import json
import cv2
import time


class VideoDetect:
    jobId = ''
    rek = boto3.client('rekognition')
    queueUrl = ''
    roleArn = ''
    topicArn = ''
    bucket = ''
    video = ''

    with open('configuration.json') as json_file:
        data = json.load(json_file)
        jobId = data['jobId']
        rek = boto3.client(data['rek'])
        queueUrl = data['queueUrl']
        roleArn = data['roleArn']
        topicArn = data['topicArn']
        bucket = data['bucket']
        video = data['video']

    def main(self):

        jobFound = False
        sqs = boto3.client('sqs')
        # self.GetResultsPersons(self.jobId)
        # return

        # =====================================
        response = self.rek.start_person_tracking(Video={'S3Object': {'Bucket': self.bucket, 'Name': self.video}},
                                                  NotificationChannel={'RoleArn': self.roleArn, 'SNSTopicArn': self.topicArn})
        # =====================================
        print('Start Job Id: ' + response['JobId'])
        dotLine = 0
        print('Waiting for AWS Rekognition to process video', end='')
        while jobFound == False:
            sqsResponse = sqs.receive_message(QueueUrl=self.queueUrl, MessageAttributeNames=['ALL'],
                                              MaxNumberOfMessages=10)

            if sqsResponse:
                if 'Messages' not in sqsResponse:
                    if dotLine < 5:
                        print('.', end='')
                        dotLine = dotLine+1
                    else:
                        print('\rWaiting for AWS Rekognition to process video', end='')
                        dotLine = 0
                    
                    time.sleep(1)
                    sys.stdout.flush()
                    continue
                
                print()
                for message in sqsResponse['Messages']:
                    notification = json.loads(message['Body'])
                    rekMessage = json.loads(notification['Message'])
                    print(rekMessage['JobId'])
                    print(rekMessage['Status'])
                    if str(rekMessage['JobId']) == response['JobId']:
                        print('Matching Job Found:' + rekMessage['JobId'])
                        jobFound = True
                        # =============================================
                        self.GetResultsPersons(rekMessage['JobId'])
                        # =============================================

                        sqs.delete_message(QueueUrl=self.queueUrl,
                                           ReceiptHandle=message['ReceiptHandle'])
                    else:
                        print("Job didn't match:" +
                              str(rekMessage['JobId']) + ' : ' + str(response['JobId']))
                    # Delete the unknown message. Consider sending to dead letter queue
                    sqs.delete_message(QueueUrl=self.queueUrl,
                                       ReceiptHandle=message['ReceiptHandle'])

        print('done')

    def GetResultsLabels(self, jobId):
        maxResults = 10
        paginationToken = ''
        finished = False

        while finished == False:
            response = self.rek.get_label_detection(JobId=jobId,
                                                    MaxResults=maxResults,
                                                    NextToken=paginationToken,
                                                    SortBy='TIMESTAMP')

            print(response['VideoMetadata']['Codec'])
            print(str(response['VideoMetadata']['DurationMillis']))
            print(response['VideoMetadata']['Format'])
            print(response['VideoMetadata']['FrameRate'])

            for labelDetection in response['Labels']:
                label = labelDetection['Label']

                print("Timestamp: " + str(labelDetection['Timestamp']))
                print("   Label: " + label['Name'])
                print("   Confidence: " + str(label['Confidence']))
                print("   Instances:")
                for instance in label['Instances']:
                    print("      Confidence: " + str(instance['Confidence']))
                    print("      Bounding box")
                    print("        Top: " +
                          str(instance['BoundingBox']['Top']))
                    print("        Left: " +
                          str(instance['BoundingBox']['Left']))
                    print("        Width: " +
                          str(instance['BoundingBox']['Width']))
                    print("        Height: " +
                          str(instance['BoundingBox']['Height']))
                    print()
                print()
                print("   Parents:")
                for parent in label['Parents']:
                    print("      " + parent['Name'])
                print()

                if 'NextToken' in response:
                    paginationToken = response['NextToken']
                else:
                    finished = True

    def GetResultsPersons(self, jobId):
        print('Getting rekognition results')
        maxResults = 10
        paginationToken = ''
        finished = False
        first_page = True
        cap = cv2.VideoCapture(self.video)
 
        # Check if camera opened successfully
        if (cap.isOpened() == False): 
            print("Unable to read video file:")
        
        # Default resolutions of the frame are obtained.The default resolutions are system dependent.
        # We convert the resolutions from float to integer.
        frame_width = int(cap.get(3))
        frame_height = int(cap.get(4))

        time = 0
        millis_per_frame = 40   # Millis per frame in a 25 fps video
        ret, frame = None, None
        prev_timestamp = 0

        persons = []
        while finished == False:
            response = self.rek.get_person_tracking(JobId=jobId,
                                                    MaxResults=maxResults,
                                                    NextToken=paginationToken,
                                                    SortBy='TIMESTAMP')

            if first_page:
                out = cv2.VideoWriter(self.video[:self.video.index('.')] + '_processed.mp4', cv2.VideoWriter_fourcc(*'mp4v'), int(response['VideoMetadata']['FrameRate']), (frame_width,frame_height))
                millis_per_frame = int(1000 / int(response['VideoMetadata']['FrameRate']))
                first_page = False

            persons.extend(response['Persons'])
            if 'NextToken' in response:
                paginationToken = response['NextToken']
            else:
                finished = True


        num_persons = len(persons)
        i = 0
        print('Writing new processed video.')
        while i < num_persons:
            personDetection = persons[i]
            # print(personDetection)
            timestamp = personDetection['Timestamp'] # In millis from beginning of video

            while(time < timestamp):
                ret, frame = cap.read()
                if ret == False:
                    break

                time += millis_per_frame
                out.write(frame)
            

            ret, frame = cap.read()
            if ret == True:
                while True: 
                    personDetection = persons[i]
                    box = personDetection['Person']['BoundingBox']
                    x1 = int(box['Left'] * frame_width)
                    y1 = int(box['Top'] * frame_height)
                    x2 = int(x1 + (box['Width'] * frame_width))
                    y2 = int(y1 + (box['Height'] * frame_height))
                    timestamp = personDetection['Timestamp'] # In millis from beginning of video
                    cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),3)

                    if i + 1 >= num_persons or persons[i + 1]['Timestamp'] != timestamp:
                        break
                    i += 1
                    

                time += millis_per_frame
                out.write(frame)
            else:
                break

            i += 1
        
        # When everything done, release the video capture and video write objects
        cap.release()
        out.release()
        
        # Closes all the frames
        cv2.destroyAllWindows()


if __name__ == "__main__":
    analyzer = VideoDetect()
    analyzer.main()
