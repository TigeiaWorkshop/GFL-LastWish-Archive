# cython: language_level=3
import cv2
import pygame
import av
import os

def getAudioFromVideo(moviePath):
    #把视频载入到流中
    input_container = av.open(moviePath)
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

    for packet in output_stream.encode(None):
        output_container.mux(packet)

    output_container.close()

    return outPutPath

def loadAudioAsSound(moviePath):
    path = getAudioFromVideo(moviePath)
    PygameAudio = pygame.mixer.Sound(path)
    os.remove(path)
    return PygameAudio

def loadAudioAsMusic(moviePath):
    pygame.mixer.music.unload()
    path = getAudioFromVideo(moviePath)
    pygame.mixer.music.load(path)
    

#视频捕捉系统
class VideoObject:
    def __init__(self,path,ifLoop=False,endPoint=None,loopStartPoint=None):
        self._video = cv2.VideoCapture(path)
        self.ifLoop = ifLoop
        self.endPoint = endPoint if endPoint != None and endPoint > 1 else self.getFrameNum()
        self.loopStartPoint = loopStartPoint if loopStartPoint != None and loopStartPoint > 1 else 1
        self._fps = self._video.get(cv2.CAP_PROP_FPS)
    def getFPS(self):
        return self._fps
    def getFrameNum(self):
        return self._video.get(7)
    def getFrame(self):
        return self._video.get(1)
    def setFrame(self,num):
        self._video.set(1,num)
    def display(self,screen):
        if self.getFrame() >= self.endPoint:
            if self.ifLoop == True:
                self.setFrame(self.loopStartPoint)
            else:
                return True
        #获取帧
        ret,frame = self._video.read()
        if frame.shape[0] != screen.get_width() or frame.shape[1] != screen.get_height():
            frame = cv2.resize(frame,(screen.get_width(),screen.get_height()))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = frame.swapaxes(0,1)
        pygame.surfarray.blit_array(screen, frame)

#视频捕捉系统
class VideoObjectWithMusic(VideoObject):
    def __init__(self,moviePath,ifLoop=False,endPoint=None,loopStartPoint=None):
        VideoObject.__init__(self,moviePath,ifLoop,endPoint,loopStartPoint)
        loadAudioAsMusic(moviePath)
        self.musicPlayed = False
        self.__clock = pygame.time.Clock()
        self.calibrationNum = 0
    def display(self,screen):
        if not self.musicPlayed:
            pygame.mixer.stop()
            pygame.mixer.music.play()
            self.musicPlayed = True
        elif pygame.mixer.music.get_busy() == False and self.ifLoop == True:
            pygame.mixer.music.play()
        self.__clock.tick(self._fps)
        CurrentFrame = int(pygame.mixer.music.get_pos()/1000*self._fps)
        if CurrentFrame - self.getFrame() > 10:
            self.setFrame(CurrentFrame)
            self.calibrationNum +=1
        return super().display(screen)
        #framePlayed = self.getFrameNum()
        #print(int(pygame.mixer.music.get_pos()/1000))
        #if framePlayed %5 == 0 and framePlayed :

#过场动画
def cutscene(screen,videoPath,bgmPath=None):
    thevideo = VideoObjectWithMusic(videoPath,bgmPath)
    width,height = screen.get_size()
    black_bg = pygame.Surface((width,height),flags=pygame.SRCALPHA).convert_alpha()
    pygame.draw.rect(black_bg,(0,0,0),(0,0,width,height))
    black_bg.set_alpha(0)
    skip_button_x = int(screen.get_width()*0.92)
    skip_button_y = int(screen.get_height()*0.05)
    skip_button_width = int(screen.get_width()*0.055)
    skip_button_height = int(screen.get_height()*0.06)
    skip_button_x_end = skip_button_x+skip_button_width
    skip_button_y_end = skip_button_y+skip_button_height
    skip_button = pygame.transform.scale(pygame.image.load("Assets/image/UI/dialog_skip.png").convert_alpha(), (skip_button_width,skip_button_height))
    ifSkip = False
    while True:
        if thevideo.display(screen) == True:
            break
        screen.blit(skip_button,(skip_button_x,skip_button_y))
        events_of_mouse_click = pygame.event.get(pygame.MOUSEBUTTONDOWN)
        if len(events_of_mouse_click) > 0:
            for event in events_of_mouse_click:
                if event.button == 1:
                    mouse_x,mouse_y = pygame.mouse.get_pos()
                    if skip_button_x<mouse_x<skip_button_x_end and skip_button_y<mouse_y<skip_button_y_end and ifSkip == False:
                        ifSkip = True
                        pygame.mixer.music.fadeout(5000)
                    break
        if ifSkip == True:
            temp_alpha = black_bg.get_alpha()
            if temp_alpha < 255:
                black_bg.set_alpha(temp_alpha+5)
            else:
                break
            screen.blit(black_bg,(0,0))
        pygame.display.flip()
    pygame.mixer.music.stop()