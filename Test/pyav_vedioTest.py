import av
import pygame

#视频捕捉系统
class VideoObjectPyAv:
    def __init__(self,path,ifLoop=False,endPoint=None,loopStartPoint=None):
        self._video = av.open(path)
        self.ifLoop = ifLoop
        self.endPoint = endPoint if endPoint != None and endPoint > 1 else self.getFrameNum()
        self.loopStartPoint = loopStartPoint if loopStartPoint != None and loopStartPoint > 1 else 1
        self._fps = self._video.streams.video[0].framerate
    def getFrameNum(self):
        return self._video.streams.video[0].frames
    def getFrameRate(self):
        return self._video.streams.video[0].framerate

container = av.open('..\Assets\movie\WhatAmIFightingFor.mp4',mode='r') # libx264 en-/decoded, pixel format yuv420p
container.streams.video[0].thread_type = 'AUTO'

pygame.init()

width = 1920
height = 1080

screen = pygame.display.set_mode((width, height),pygame.DOUBLEBUF | pygame.SCALED | pygame.FULLSCREEN)


for frame in container.decode(video=0):
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            playMovie = False

    
    #frame.reformat(width,height)
    array = frame.to_ndarray(format='rgb24')

    
    array = array.swapaxes(0,1)


    pygame.surfarray.blit_array(screen, array)
    pygame.display.flip()
