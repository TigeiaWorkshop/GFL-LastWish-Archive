# cython: language_level=3
import cv2
import pygame
import os
try:
    from moviepy.editor import VideoFileClip
except BaseException:
    print('ZeroEngine-Warning: Cannot load moviepy module!')

#视频捕捉系统
class VideoObject:
    def __init__(self,path,ifLoop=False,endPoint=None,loopStartPoint=None):
        self.video = cv2.VideoCapture(path)
        self.ifLoop = ifLoop
        self.endPoint = endPoint if endPoint != None and endPoint > 1 else self.getFrameNum()
        self.loopStartPoint = loopStartPoint if loopStartPoint != None and loopStartPoint > 1 else 1
    def getFPS(self):
        return self.video.get(cv2.CAP_PROP_FPS)
    def getFrameNum(self):
        return self.video.get(7)
    def getFrame(self):
        return self.video.get(1)
    def setFrame(self,num):
        self.video.set(1,num)
    def display(self,screen):
        if self.getFrame() >= self.endPoint:
            if self.ifLoop == True:
                self.setFrame(self.loopStartPoint)
            else:
                return True
        ret, frame = self.video.read()
        if frame.shape[0] != screen.get_width() or frame.shape[1] != screen.get_height():
            frame = cv2.resize(frame,(screen.get_width(),screen.get_height()))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.transpose(frame)
        pygame.surfarray.blit_array(screen, frame)

#视频捕捉系统
class VideoObjectWithMusic(VideoObject):
    def __init__(self,movie_path,music_path,ifLoop=False,endPoint=None,loopStartPoint=None):
        VideoObject.__init__(self,movie_path,ifLoop,endPoint,loopStartPoint)
        self.fps = self.video.get(cv2.CAP_PROP_FPS)
        self.musicPlayed = False
        pygame.mixer.music.unload()
        pygame.mixer.music.load(music_path)
    def getFPS(self):
        return self.fps
    def display(self,screen):
        if self.musicPlayed == False:
            pygame.mixer.music.play()
            self.musicPlayed = True
        super().display(screen)
        #framePlayed = self.getFrameNum()
        #print(int(pygame.mixer.music.get_pos()/1000))
        #if framePlayed %5 == 0 and framePlayed :

#过场动画
def cutscene(screen,videoPath,bgmPath=None):
    try:
        clip = VideoFileClip(videoPath)
        clip.preview()
    except BaseException:
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
        skip_button = pygame.transform.scale(pygame.image.load(os.path.join("Assets/image/UI/dialog_skip.png")).convert_alpha(), (skip_button_width,skip_button_height))
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