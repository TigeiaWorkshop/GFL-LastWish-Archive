# cython: language_level=3
import cv2
import pygame

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
    def __init__(self,moviePath,musicPath,ifLoop=False,endPoint=None,loopStartPoint=None):
        VideoObject.__init__(self,moviePath,ifLoop,endPoint,loopStartPoint)
        self._video.set(cv2.CAP_PROP_BUFFERSIZE,3)
        self.musicPath = musicPath
        self.musicPlayed = False
        self.__clock = pygame.time.Clock()
        pygame.mixer.music.unload()
    def display(self,screen):
        super().display(screen)
        if self.musicPlayed == False:
            pygame.mixer.music.load(self.musicPath)
            pygame.mixer.music.play()
            self.musicPlayed = True
        elif pygame.mixer.music.get_busy() == False and self.ifLoop == True:
            pygame.mixer.music.load(self.musicPath)
            pygame.mixer.music.play()
        self.__clock.tick(self._fps)
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