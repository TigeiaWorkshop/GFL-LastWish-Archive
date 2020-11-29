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

class VedioInterface(threading.Thread):
    def __init__(self,path):
        threading.Thread.__init__(self)
        self._video_container = av.open(path,mode='r')
        self._video_stream = self._video_container.streams.video[0]
        self._video_stream.thread_type = 'AUTO'
        self._frameNum = self._video_stream.frames
        self._frameRate = math.ceil(self._video_stream.average_rate)
        self.__frameIndex = 0
        self._frameQueue = queue.Queue()
        self._stopped = False
        self._clock = pygame.time.Clock()
    def get_frameNum(self):
        return self._frameNum
    def get_frameRate(self):
        return self._frameRate
    def get_frameIndex(self):
        return self.__frameIndex
    def set_frameIndex(self,index):
        self.__frameIndex = index
        timeOffset = int(self.__frameIndex/self._frameRate/self._video_stream.time_base)
        self._video_container.seek(timeOffset,stream=self._video_stream)
    def get_percentagePlayed(self):
        return self.__frameIndex/self._frameNum
    def stop(self):
        self._stopped = True
    def _processFrame(self,frame):
        while self._frameQueue.qsize() > self._frameRate*3:
            pass
        array = frame.to_ndarray(width=1920,height=1080,format='rgb24')
        array = array.swapaxes(0,1)
        self._frameQueue.put(array)
        self.__frameIndex += 1
    def display(self,screen):
        pygame.surfarray.blit_array(screen, self._frameQueue.get())

class VedioFrame(VedioInterface):
    def __init__(self,path,loop=0,with_music=False):
        VedioInterface.__init__(self,path)
        self.loop = loop
        self.looped = -1
        self.bgm = loadAudioAsSound() if with_music else None
        self.bgm_channel = pygame.mixer.find_channel()
    def run(self):
        for frame in self._video_container.decode(self._video_stream):
            if self._stopped:
                break
            self._processFrame(frame)
            self._clock.tick(self._frameRate)
    def display(self,screen):
        super().display(screen)
        if self.bgm != None and not self.bgm_channel.get_busy() and self.looped < self.loop:
            self.bgm_channel.play(self.bgm)

#视频捕捉系统
class VedioPlayer(VedioInterface):
    def __init__(self,path):
        VedioInterface.__init__(self,path)
        self.__allowFrameDelay = 10
        loadAudioAsMusic(path)
    def run(self):
        pygame.mixer.music.play()
        for frame in self._video_container.decode(self._video_stream):
            if self._stopped:
                break
            self._processFrame(frame)
            if not int(pygame.mixer.music.get_pos()/1000*self._frameRate)-self.get_frameIndex() >= self.__allowFrameDelay:
                self._clock.tick(self._frameRate)

mediaTmp = VedioFrame('..\Assets\movie\WhatAmIFightingFor.mp4')

width = 1920
height = 1080

screen = pygame.display.set_mode((width, height),pygame.DOUBLEBUF | pygame.SCALED | pygame.FULLSCREEN)
playMovie = True

white_bar = (255,255,255)
white_bar_height = 10
mediaTmp.set_frameIndex(1000)
mediaTmp.start()

while True:

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            playMovie = False

    if not playMovie:
        mediaTmp.stop()
        break
    
    mediaTmp.display(screen)
    pygame.draw.rect(screen,white_bar,(10,height-white_bar_height*2,(width-10*2)*mediaTmp.get_percentagePlayed(),white_bar_height))


    pygame.display.flip()

