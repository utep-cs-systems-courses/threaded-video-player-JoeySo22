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
        - Read more on semaphores from book DONE
        - Try to implement with Queue w/ threadsafe for now TBC
        - Ask David Pruitt about queueing jpg data vs jpg files. DONE

    10/27/2020 11:56PM - After talking with David about the question on the jpeg 
objects and files, I've learned what the code is doing in the examples. ExtractFrames.py
basically just gets some image data when reading. Although it was named jpeg, its just 
data.
        - Check on frame extractor and implement its job. DONE
        - Implement for GrayScaler & VideoDisplayer
    I just realized that the cv2.read() method returns a boolean value to signify the
end of the reading. I need a way for the threads to flag globally that their job is done
and should stop waiting for the pipe to feed more to the queue. So two things should be
asserted before a thread is done. The previous thread is done and the queue is empty.
        - Implement the above. DONE
    10/28/2020 3:03AM - I have a bug where the Frame Extractor is filling up the q1 but the Gray Scaler is
already done. Need to fix that.

    11/1/2020 8:22PM - Working on debugging the queue's. Something appears to be off. Can't tell what it
is yet.
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

global q1, q2
#Removed video_displayer_complete because it isn't used.
global frame_extractor_complete, gray_scaler_complete
frame_extractor_complete = False
gray_scaler_complete = False

def main():
    global q1, q2, frame_extracter_complete, gray_scaler_complete
    zone = 'GP>main>'
    if d: print('%s started...' % zone)
    # Create all the threads
    if d: print('%s initiating Frame Extractor, Gray Scaler, & Video Displayer...' % zone)
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
        zone = '\tFE>init>'
        threading.Thread.__init__(self, name='FrameExtractor')
        self.counter = 0
        if d: print('%s initiated.' % zone)

    def run(self):
        global q1, frame_extractor_complete
        zone = '\t\tFE>run>'
        if d: print('%s running' % zone)
        video_cap = cv2.VideoCapture(args.filename) #Open file
        success,image = video_cap.read() #Take one image from file.
        while success:
            self.counter += 1
            q1.put(image) # Just stuff it into the queue
            if d: print('%s frame: %d' % (zone, self.counter))
            success, image = video_cap.read() # Redo it again.
        frame_extractor_complete = True # Flag that this thread is finished.
        if d: print('%s done.' % zone)

        
class GrayScaler (threading.Thread):

    def __init__(self):
        zone = '\tGS>init>'
        threading.Thread.__init__(self, name='Grayscaler')
        self.counter = 0
        if d: print('%s initiated.' % zone)
    
    def run(self):
        global q1, q2, frame_extractor_complete, gray_scaler_complete
        zone = '\t\tGS>run>'
        if d: print('%s running' % zone)
        while not frame_extractor_complete:
            '''
            I'm afraid that this process will take up a lot of memory. So I will shorten
            the expression by stuffing the function calls inside of each other rather
            than being explicit.
        
            frame = q1.get()
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            q2.put(gray_frame)
            '''
            if not q1.empty():
                q2.put(cv2.cvtColor(q1.get(), cv2.COLOR_BGR2GRAY))
                self.counter += 1
                if d: print('%s frame: %d' % (zone, self.counter))
        while not q1.empty():
            q2.put(cv2.cvtColor(q1.get(), cv2.COLOR_BGR2GRAY))
            self.counter += 1
            if d: print('%s frame: %d' % (zone, self.counter))
        gray_scaler_complete = True # Flag that this thread is finished.
        if d: print('%s done.' % zone)

        
class VideoDisplayer (threading.Thread):

    def __init__(self):
        zone = '\tVD>init>'
        threading.Thread.__init__(self, name='VideoDisplayer')
        self.counter = 0
        if d: print('%s initiated.' % zone)
    
    def run(self):
        global q2, gray_scaler_complete
        zone = '\t\tVD>run>'
        if d: print('%s running' % zone)
        while not gray_scaler_complete:
            if not q2.empty():
                cv2.imshow('Video', q2.get())
                self.counter += 1
                if d: print('%sMAIN frame: %d' % (zone, self.counter))
                cv2.waitKey(42)
        while not q2.empty():
            cv2.imshow('Video', q2.get())
            self.counter += 1
            if d: print('%s frame: %d' % (zone, self.counter))
            cv2.waitKey(42)
        cv2.destroyAllWindows()
        if d: print('%s done.' % zone)


class TSQueue:

    def __init__(self, size):
        self.size = size
        self.list = []
        self.full = threading.Semaphore(0)
        self.empty = threading.Semaphore(size)
        self.lock = threading.Lock()

    def get(self):
        self.full.acquire()
        element = list.pop()
        self.empty.release()
        return element
        
    def put(self, element):
        self.empty.acquire()
        self.list.append(element)
        self.full.release()

q1 = TSQueue(24)
q2 = TSQueue(24)
main()
