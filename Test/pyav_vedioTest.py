import av
import pygame
import threading, queue
import math
import os
pygame.init()

def getAudioFromVideo(moviePath,audioType="mp3"):
    #获取路径
    filePath = os.path.split(moviePath)[0]
    outPutPath = filePath+"Tmp."+audioType
    if os.path.exists(outPutPath):
        return outPutPath

    #把视频载入到流中
    input_container = av.open(moviePath)
    input_container.streams.video[0].thread_type = 'AUTO'
    input_stream = input_container.streams.get(audio=0)[0]
    
    output_container = av.open(outPutPath, 'w')
    output_stream = output_container.add_stream(audioType)

    for frame in input_container.decode(input_stream):
        frame.pts = None
        for packet in output_stream.encode(frame):
            output_container.mux(packet)

    input_container.close()

    for packet in output_stream.encode(None):
        output_container.mux(packet)

    output_container.close()

    return outPutPath

def loadAudioAsMusic(moviePath):
    pygame.mixer.music.unload()
    path = getAudioFromVideo(moviePath)
    pygame.mixer.music.load(path)

def loadAudioAsSound(moviePath):
    path = getAudioFromVideo(moviePath)
    PygameAudio = pygame.mixer.Sound(path)
    os.remove(path)
    return PygameAudio

class VedioFrame(threading.Thread):
    def __init__(self,path,loop=0,with_music=False):
        threading.Thread.__init__(self)
        self._video_container = av.open(path,mode='r')
        self._video_stream = self._video_container.streams.video[0]
        self._video_stream.thread_type = 'AUTO'
        self.frameNum = self._video_container.streams.video[0].frames
        self.frameRate = math.ceil(self._video_container.streams.video[0].average_rate)
        self.frameIndex = 0
        self.frameQueue = queue.Queue()
        self.__stopped = False
        self.__clock = pygame.time.Clock()
        self.__allowFrameDelay = 10
        self.loop = loop
        self.looped = -1
        self.bgm = loadAudioAsSound() if with_music else None
        self.bgm_channel = pygame.mixer.find_channel()
    def getFrameNum(self):
        return self.frameNum
    def getFrameRate(self):
        return self.frameRate
    def run(self):
        for frame in self._video_container.decode(self._video_stream):
            if self.__stopped:
                break
            while self.frameQueue.qsize() > self.frameRate*3:
                pass
            array = frame.to_ndarray(width=1920,height=1080,format='rgb24')
            array = array.swapaxes(0,1)
            self.frameQueue.put(array)
            self.frameIndex += 1
            if not int(pygame.mixer.music.get_pos()/1000*self.frameRate)-self.frameIndex >= self.__allowFrameDelay:
                self.__clock.tick(self.frameRate)
    def display(self,screen):
        pygame.surfarray.blit_array(screen, self.frameQueue.get())
        if self.bgm != None and not self.bgm_channel.get_busy() and self.looped < self.loop:
            self.bgm_channel.play(self.bgm)
    def stop(self):
        self.__stopped = True

#视频捕捉系统
class VedioPlayer(threading.Thread):
    def __init__(self,path):
        threading.Thread.__init__(self)
        self._video_container = av.open(path,mode='r')
        self._video_stream = self._video_container.streams.video[0]
        self._video_stream.thread_type = 'AUTO'
        self.frameNum = self._video_container.streams.video[0].frames
        self.frameRate = math.ceil(self._video_container.streams.video[0].average_rate)
        self.frameIndex = 0
        self.frameQueue = queue.Queue()
        self.__stopped = False
        self.__clock = pygame.time.Clock()
        self.__allowFrameDelay = 10
        loadAudioAsMusic(path)
    def getFrameNum(self):
        return self.frameNum
    def getFrameRate(self):
        return self.frameRate
    def run(self):
        pygame.mixer.music.play()
        for frame in self._video_container.decode(self._video_stream):
            if self.__stopped:
                break
            while self.frameQueue.qsize() > self.frameRate*3:
                pass
            array = frame.to_ndarray(width=1920,height=1080,format='rgb24')
            array = array.swapaxes(0,1)
            self.frameQueue.put(array)
            self.frameIndex += 1
            if not int(pygame.mixer.music.get_pos()/1000*self.frameRate)-self.frameIndex >= self.__allowFrameDelay:
                self.__clock.tick(self.frameRate)
    def display(self,screen):
        pygame.surfarray.blit_array(screen, self.frameQueue.get())
    def stop(self):
        self.__stopped = True


mediaTmp = VedioPlayer('..\Assets\movie\WhatAmIFightingFor.mp4')



width = 1920
height = 1080

screen = pygame.display.set_mode((width, height),pygame.DOUBLEBUF | pygame.SCALED | pygame.FULLSCREEN)
playMovie = True

white_bar = (255,255,255)
white_bar_height = 10
mediaTmp.start()

while True:

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            playMovie = False

    if not playMovie:
        mediaTmp.stop()
        break
    
    mediaTmp.display(screen)
    pygame.draw.rect(screen,white_bar,(10,height-white_bar_height*2,(width-10*2)*mediaTmp.frameIndex/mediaTmp.frameNum,white_bar_height))


    pygame.display.flip()

