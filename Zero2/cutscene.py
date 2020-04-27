# cython: language_level=3
from Zero2.basic import *
import pygame
from pygame.locals import *
from moviepy.editor import *

def cutscene(screen,surface,videoPath,bgmPath):
    """
    thevideo = VideoObject(videoPath)
    fpsClock = pygame.time.Clock()
    video_fps = int(thevideo.getFPS()+2)
    black_bg = loadImage("Assets/image/UI/black.png",(0,0),surface.get_width(),surface.get_height())
    black_bg.set_alpha(0)
    skip_button = loadImage("Assets/image/UI/skip.png",(surface.get_width()*0.92,surface.get_height()*0.05),surface.get_width()*0.055,surface.get_height()*0.03)
    ifSkip = False
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
    """
    clip = VideoFileClip(videoPath)
    clip.preview()
    