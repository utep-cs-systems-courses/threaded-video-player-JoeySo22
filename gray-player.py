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
        - Rewatch the semaphore material. DONE
        - Try to implement with Queue w/ threadsafe for now
        - Add debug switch DONE
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
    if d: print(zone)
    pass


class FrameExtractor (threading.Thread):

    def __init__(self):
        zone = 'FM>init>'
        threading.Thread.__init__(self, name='FrameExtractor')
        pass

    def run(self):
        zone = 'FM>run>'
        video_cap = cv2.VideoCapture(args.filename) #Open file
        success,image = video_cap.read() #Take one image from file.
        while success:
            success, jpg = cv2.imencode('.jpg', image) #Encode to a jpeg format
            jpg_text = base64.b64encode(jpg) #Turn jpg data to encoded text
            #TODO What do we put into the queue. How can Grayscaler convert data
            success, image = video_cap.read()
    
class Grayscaler (threading.Thread):

    def __init__(self):
        zone = 'GS>init>'
        threading.Thread.__init__(self, name='Grayscaler')
        pass
    
    def run(self):
        zone = 'GS>run>'
        pass
    
class VideoDisplayer (threading.Thread):

    def __init__(self):
        zone = 'VD>init>'
        threading.Thread.__init__(self, name='VideoDisplayer')
        pass
    
    def run(self):
        zone = 'VD>run>'
        pass

main()
