#!/usr/bin/env python3

'''
Author: Jose Eduardo Soto

Description: Creates a video stream that turns the video into grayscale
video. It uses a chain of producer/consumer functions. It pulls the frames
from the mp4 file, converts them to grayscale, and displays them. Its also known
as a 'Rendering Pipeline'. There is supposed to be only 24 frames. Use semaphores
and mutexes

Logs:
    10/20/2020 01:06AM - Initiated the file. Tested the ExtractFrames.py file.
Deleted the frames files. Rewatching stuff about the semaphores. My thoughts are
that we can seperate each function by threads. Their runs work 1 way but they
are going to share I think 2 queue's. But there needs to be some blocking and etc.
in order to have a good 'flow'. Guess I can start with the thread classes. DONE
        - Make appropriate classes for the three functions. DONE
        - Setup args for this program. DONE
        - Setup help dialog. DONE
        - Add debug switch DONE
        - Read more on semaphores from book
        - Try to implement with Queue w/ threadsafe for now
        - Ask David Pruitt about queueing jpg data vs jpg files.
'''
import argparse, base64, cv2, os, queue, sys, threading

arg_parse = argparse.ArgumentParser(prog='gray-player',
                                    description='Renders grayscale video and plays it.',
                                    epilog='Email jesoto4@miners.utep.edu',
                                    add_help=True)
arg_parse.add_argument('-i', '--input', help='Takes the video filename as input',
                       metavar='filename', dest='filename')
arg_parse.add_argument('-d', '--debug', help='Enables debugging output.',
                       dest='debug', action='store_true')
args = arg_parse.parse_args() # This will get the arguments from the command line.
d = args.debug # Easier namespace. Used for debugging.

q = queue.Queue(24) # Easy queue for testing. Capacity @ 24.

def main():
    zone = 'GP>main>'
    if d: print('%s started...' % zone)
    # Create all the threads
    if d: print('%s initiating Frame Extractor, Gray Scaler, & VideoDisplayer...' % zone)
    frame_extractor = FrameExtractor()
    gray_scaler = GrayScaler()
    video_displayer = VideoDisplayer()
    if d: print('%s finished initializing.' % zone)
    if d: print('%s starting threads...' % zone)
    frame_extractor.start()
    gray_scaler.start()
    video_displayer.start()
    if d: print('%s threads are running.' % zone)
    if d: print('%s done.' % zone)


class FrameExtractor (threading.Thread):

    def __init__(self):
        zone = '\tFM>init>'
        threading.Thread.__init__(self, name='FrameExtractor')
        if d: print('%s initiated.' % zone)
        pass

    def run(self):
        zone = 'FM>run>'
        if d: 
        video_cap = cv2.VideoCapture(args.filename) #Open file
        success,image = video_cap.read() #Take one image from file.
        while success:
            success, jpg = cv2.imencode('.jpg', image) #Encode to a jpeg format
            jpg_text = base64.b64encode(jpg) #Turn jpg data to encoded text
            #TODO What do we put into the queue. How can Grayscaler convert data
            success, image = video_cap.read()
    
class GrayScaler (threading.Thread):

    def __init__(self):
        zone = '\tGS>init>'
        threading.Thread.__init__(self, name='Grayscaler')
        if d: print('%s initiated.' % zone)
        pass
    
    def run(self):
        zone = '\t\tGS>run>'
        pass
    
class VideoDisplayer (threading.Thread):

    def __init__(self):
        zone = '\tVD>init>'
        threading.Thread.__init__(self, name='VideoDisplayer')
        if d: print('%s initiated.' % zone)
        pass
    
    def run(self):
        zone = '\t\tVD>run>'
        pass

main()
