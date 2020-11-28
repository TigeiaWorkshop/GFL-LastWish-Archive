import av
import pygame
import threading, queue
import math
import os
pygame.init()

def getAudioFromVideo(moviePath):
    #把视频载入到流中
    input_container = av.open(moviePath)
    input_container.streams.video[0].thread_type = 'AUTO'
    input_stream = input_container.streams.get(audio=0)[0]
    #获取路径
    filePath = os.path.split(moviePath)[0]

    i = 0
    while os.path.exists(filePath+"Tmp"+str(i)):
        i+=1
    outPutPath = filePath+"Tmp"+str(i)+".mp3"
    output_container = av.open(outPutPath, 'w')
    output_stream = output_container.add_stream('mp3')

    for frame in input_container.decode(input_stream):
        frame.pts = None
        for packet in output_stream.encode(frame):
            output_container.mux(packet)

    input_container.close()

    for packet in output_stream.encode(None):
        output_container.mux(packet)

    output_container.close()

    return outPutPath

def loadAudioAsSound(moviePath):
    path = getAudioFromVideo(moviePath)
    PygameAudio = pygame.mixer.Sound(path)
    os.remove(path)
    return PygameAudio

#视频捕捉系统
class VideoObjectPyAv(threading.Thread):
    def __init__(self,path,ifLoop=False,endPoint=None,loopStartPoint=None):
        threading.Thread.__init__(self)
        self._video_container = av.open(path,mode='r')
        self._video_container.streams.video[0].thread_type = 'AUTO'
        self.frameNum = self._video_container.streams.video[0].frames
        self.frameRate = math.ceil(self._video_container.streams.video[0].average_rate)
        self.frameIndex = 0
        self.frameQueue = queue.Queue()
        self.__stopped = False
        self.__clock = pygame.time.Clock()
        #self.sound = pygame.mixer.Sound(loadAudioAsSound(path))
    def getFrameNum(self):
        return self.frameNum
    def getFrameRate(self):
        return self.frameRate
    def getFrame(self):
        return self.frameQueue.get()
    def run(self):
        for frame in self._video_container.decode(video=0):
            while self.frameQueue.qsize() > self.frameRate:
                pass
            array = frame.to_ndarray(width=1920,height=1080,format='rgb24')
            array = array.swapaxes(0,1)
            self.frameQueue.put(array)
            self.frameIndex += 1
            if self.__stopped:
                break
            self.__clock.tick(self.frameRate)
    def stop(self):
        self.__stopped = True




mediaTmp = VideoObjectPyAv('..\Assets\movie\WhatAmIFightingFor.mp4')



width = 1920
height = 1080

screen = pygame.display.set_mode((width, height),pygame.DOUBLEBUF | pygame.SCALED | pygame.FULLSCREEN)
playMovie = True


mediaTmp.start()
print(mediaTmp.frameRate)
#mediaTmp.sound.play()

while True:

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            playMovie = False

    if not playMovie:
        mediaTmp.stop()
        break
    

    pygame.surfarray.blit_array(screen, mediaTmp.getFrame())

    pygame.display.flip()

