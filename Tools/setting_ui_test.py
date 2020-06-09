import pygame
import os
from pygame.locals import *
pygame.init()

screen = pygame.display.set_mode((1920, 1080))

#图片加载模块：接收图片路径,长,高,返回对应图片
def loadImg(path,width=None,height=None,setAlpha=None,ifConvertAlpha=True):
    img = None
    if isinstance(path,str):
        if ifConvertAlpha == False:
            img = pygame.image.load(os.path.join(path))
        else:
            img = pygame.image.load(os.path.join(path)).convert_alpha()
    else:
        img = path
    if setAlpha != None:
        img.set_alpha(setAlpha)
    if width == None and height == None:
        pass
    elif height!= None and height >= 0 and width == None:
        img = pygame.transform.scale(img,(round(height/img.get_height()*img.get_width()), round(height)))
    elif height == None and width!= None and width >= 0:
        img = pygame.transform.scale(img,(round(width), round(width/img.get_width()*img.get_height())))
    elif width >= 0 and height >= 0:
        img = pygame.transform.scale(img, (int(width), int(height)))
    elif width < 0 or height < 0:
        raise Exception('Both width and height must be positive interger!')
    return img
        
#图片blit模块：接受图片，位置（列表格式），屏幕，如果不是UI层需要local_x和local_y
def drawImg(img,position,screen,local_x=0,local_y=0):
    screen.blit(img,(position[0]+local_x,position[1]+local_y))

window_x = screen.get_width()
window_y = screen.get_height()

class settingUI:
    def __init__(self,window_x,window_y):
        self.baseImg = loadImg("../Assets/image/UI/setting_baseImg.png",window_x/3.5,window_x/3.5)
        self.baseImg.set_alpha(50)
        self.circle = loadImg("../Assets/image/UI/setting_bar_circle.png",window_x/35,window_x/35)
        self.bar_empty = loadImg("../Assets/image/UI/setting_bar_empty.png",window_x/5,window_x/70)
        self.bar_full = loadImg("../Assets/image/UI/setting_bar_full.png",window_x/5,window_x/70)
    def display(self,screen):
        posTemp_x = int((screen.get_width()-self.baseImg.get_width())/2)
        posTemp_y = int((screen.get_height()-self.baseImg.get_height())/2)
        screen.blit(self.baseImg,(posTemp_x,posTemp_y))
        posTemp_x1 = posTemp_x+int((self.baseImg.get_width()-self.bar_empty.get_width())/2)
        posTemp_y+=300
        screen.blit(self.bar_empty,(posTemp_x1,posTemp_y))
        screen.blit(self.bar_full,(posTemp_x1,posTemp_y))
        screen.blit(self.circle,(posTemp_x1+self.bar_full.get_width()-self.circle.get_width()/2,posTemp_y-self.circle.get_height()/4))


settingUI_test = settingUI(window_x,window_y)

running = True
while running:
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
        elif event.type == MOUSEBUTTONDOWN:
            pass
    settingUI_test.display(screen)
    pygame.display.flip()

pygame.quit()