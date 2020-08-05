# cython: language_level=3
import cv2
import pygame

#视频捕捉系统
class VideoObject:
    def __init__(self,path,ifLoop=False,endPoint=None,loopStartPoint=None):
        self.video = cv2.VideoCapture(path)
        self.ifLoop = ifLoop
        if endPoint != None:
            self.endPoint = endPoint
        else:
            self.endPoint = self.getFrameNum()
        if loopStartPoint != None:
            self.loopStartPoint = loopStartPoint
        else:
            self.loopStartPoint = 1
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

#过场动画
def cutscene(screen,videoPath,bgmPath=None):
    try:
        from moviepy.editor import VideoFileClip
        clip = VideoFileClip(videoPath)
        clip.preview()
    except BaseException:
        thevideo = VideoObject(videoPath)
        fpsClock = pygame.time.Clock()
        video_fps = int(thevideo.getFPS()+2)
        black_bg = loadImage("Assets/image/UI/black.png",(0,0),surface.get_width(),surface.get_height())
        black_bg.set_alpha(0)
        skip_button = loadImage("Assets/image/UI/skip.png",(surface.get_width()*0.92,surface.get_height()*0.05),surface.get_width()*0.055,surface.get_height()*0.03)
        ifSkip = False
        if bgmPath != None and os.path.exists(bgmPath):
            pygame.mixer.music.load(bgmPath)
            pygame.mixer.music.play()
        while True:
            ifEnd = thevideo.display(surface,screen)
            if ifEnd == True:
                break
            skip_button.draw(screen)
            for event in pygame.event.get():
                if event.type == MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0] and isHover(skip_button) and ifSkip == False:
                    ifSkip = True
                    pygame.mixer.music.fadeout(5000)
                    break
            if ifSkip == True:
                temp_alpha = black_bg.get_alpha()
                if temp_alpha < 255:
                    black_bg.set_alpha(temp_alpha+5)
                else:
                    break
            black_bg.draw(screen)
            fpsClock.tick(video_fps)
            pygame.display.update()
        pygame.mixer.music.stop()