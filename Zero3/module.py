# cython: language_level=3
import glob
import math
import os
import random
import time
from sys import exit

import cv2
import pygame
import yaml
from pygame.locals import *

#高级图形类
class ImageSurface:
    def __init__(self,img,x,y,width=None,height=None,description="Default"):
        self.img = img
        self.x = x
        self.y = y
        self.xTogo = x
        self.yTogo = y
        self.items = []
        self.width = width
        self.height = height
        self.description = description
        if self.width == None and self.height == None:
            self.width,self.height = self.img.get_size()
        elif self.width == None and self.height != None:
            self.width = self.height/self.img.get_height()*self.img.get_width()
        elif self.width != None and self.height == None:
            self.height = self.width/self.img.get_width()*self.img.get_height()
    def draw(self,screen,local_x=0,local_y=0):
        screen.blit(pygame.transform.scale(self.img, (round(self.width),round(self.height))),(self.x+local_x,self.y+local_y))
    def set_alpha(self,value):
        self.img.set_alpha(value)
    def get_alpha(self):
        return self.img.get_alpha()

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

#画面更新控制器
class DisplayController:
    def __init__(self,fps):
        self.fps = fps
        self.clock = pygame.time.Clock()
    def flip(self):
        self.clock.tick(self.fps)
        pygame.display.flip()
    def quit(self):
        #退出游戏
        exit()

#射击音效 -- 频道2
class attackingSoundManager:
    def __init__(self,volume):
        self.soundsData = {
            #突击步枪
            "AR": glob.glob(r'Assets/sound/attack/ar_*.ogg'),
            #手枪
            "HG": glob.glob(r'Assets/sound/attack/hg_*.ogg'),
            #机枪
            "MG": glob.glob(r'Assets/sound/attack/mg_*.ogg'),
            #步枪
            "RF": glob.glob(r'Assets/sound/attack/rf_*.ogg'),
            #冲锋枪
            "SMG": glob.glob(r'Assets/sound/attack/smg_*.ogg'),
        }
        self.volume = volume
        for key in self.soundsData:
            for i in range(len(self.soundsData[key])):
                self.soundsData[key][i] = pygame.mixer.Sound(self.soundsData[key][i])
                self.soundsData[key][i].set_volume(volume/100.0)
    def play(self,kind):
        if kind in self.soundsData:
            pygame.mixer.Channel(2).play(self.soundsData[kind][random.randint(0,len(self.soundsData[kind])-1)])

#设置UI
class settingContoller:
    def __init__(self,window_x,window_y,settingdata,langTxt):
        self.ifDisplay = False
        self.baseImgWidth = round(window_x/3)
        self.baseImgHeight = round(window_x/3)
        self.baseImg = pygame.transform.scale(pygame.image.load(os.path.join("Assets/image/UI/setting_baseImg.png")).convert_alpha(),(self.baseImgWidth,self.baseImgHeight))
        self.baseImg.set_alpha(200)
        self.baseImgX = int((window_x-self.baseImgWidth)/2)
        self.baseImgY = int((window_y-self.baseImgHeight)/2)
        self.bar_height = round(window_x/60)
        self.bar_width = round(window_x/5)
        self.button = pygame.transform.scale(pygame.image.load(os.path.join("Assets/image/UI/setting_bar_circle.png")).convert_alpha(),(self.bar_height,self.bar_height*2))
        self.bar_empty = pygame.transform.scale(pygame.image.load(os.path.join("Assets/image/UI/setting_bar_empty.png")).convert_alpha(),(self.bar_width,self.bar_height))
        self.bar_full = pygame.transform.scale(pygame.image.load(os.path.join("Assets/image/UI/setting_bar_full.png")).convert_alpha(),(self.bar_width,self.bar_height))
        self.bar_x = int(self.baseImgX+(self.baseImgWidth-self.bar_empty.get_width())/2)
        self.bar_y0 = self.baseImgY + self.baseImgHeight*0.2
        self.bar_y1 = self.baseImgY + self.baseImgHeight*0.4
        self.bar_y2 = self.baseImgY + self.baseImgHeight*0.6
        self.bar_y3 = self.baseImgY + self.baseImgHeight*0.8
        #音量数值
        self.soundVolume_background_music = settingdata["Sound"]["background_music"]
        self.soundVolume_sound_effects = settingdata["Sound"]["sound_effects"]
        self.soundVolume_sound_environment = settingdata["Sound"]["sound_environment"]
        #设置UI中的文字
        self.fontSize = round(window_x/50)
        self.fontSizeBig = round(window_x/50*1.5)
        self.normalFont = pygame.font.SysFont("simhei",int(self.fontSize))
        self.bigFont = pygame.font.SysFont("simhei",int(self.fontSizeBig))
        self.settingTitleTxt = self.bigFont.render(langTxt["setting"],True,(255, 255, 255))
        self.settingTitleTxt_x = int(self.baseImgX+(self.baseImgWidth-self.settingTitleTxt.get_width())/2)
        self.settingTitleTxt_y = self.baseImgY+self.baseImgHeight*0.05
        #语言
        self.languageTxt = self.normalFont.render(langTxt["language"]+": "+langTxt["currentLang"],True,(255, 255, 255))
        #背景音乐
        self.backgroundMusicTxt = langTxt["background_music"]
        #音效
        self.soundEffectsTxt = langTxt["sound_effects"]
        #环境声效
        self.soundEnvironmentTxt = langTxt["sound_environment"]
        #确认
        self.confirmTxt_n = self.normalFont.render(langTxt["confirm"],True,(255, 255, 255))
        self.confirmTxt_b = self.bigFont.render(langTxt["confirm"],True,(255, 255, 255))
        #取消
        self.cancelTxt_n = self.normalFont.render(langTxt["cancel"],True,(255, 255, 255))
        self.cancelTxt_b = self.bigFont.render(langTxt["cancel"],True,(255, 255, 255))
        #确认和取消按钮的位置
        self.buttons_y = self.baseImgY + self.baseImgHeight*0.88
        self.buttons_x1 = self.baseImgX + self.confirmTxt_b.get_width()*2.5
        self.buttons_x2 = self.buttons_x1 + self.confirmTxt_b.get_width()
    def display(self,screen):
        if self.ifDisplay == True:
            #底部图
            screen.blit(self.baseImg,(self.baseImgX,self.baseImgY))
            screen.blit(self.settingTitleTxt,(self.settingTitleTxt_x,self.settingTitleTxt_y))
            #语言
            screen.blit(self.languageTxt,(self.bar_x,self.bar_y0))
            #背景音乐
            screen.blit(self.normalFont.render(self.backgroundMusicTxt+": "+str(self.soundVolume_background_music),True,(255, 255, 255)),(self.bar_x,self.bar_y1-self.fontSize*1.4))
            screen.blit(self.bar_empty,(self.bar_x,self.bar_y1))
            barImgWidth = round(self.bar_full.get_width()*self.soundVolume_background_music/100)
            screen.blit(pygame.transform.scale(self.bar_full,(barImgWidth,self.bar_height)),(self.bar_x,self.bar_y1))
            screen.blit(self.button,(self.bar_x+barImgWidth-self.button.get_width()/2,self.bar_y1-self.bar_height/2))
            #音效
            screen.blit(self.normalFont.render(self.soundEffectsTxt+": "+str(self.soundVolume_sound_effects),True,(255, 255, 255)),(self.bar_x,self.bar_y2-self.fontSize*1.4))
            screen.blit(self.bar_empty,(self.bar_x,self.bar_y2))
            barImgWidth = round(self.bar_full.get_width()*self.soundVolume_sound_effects/100)
            screen.blit(pygame.transform.scale(self.bar_full,(barImgWidth,self.bar_height)),(self.bar_x,self.bar_y2))
            screen.blit(self.button,(self.bar_x+barImgWidth-self.button.get_width()/2,self.bar_y2-self.bar_height/2))
            #环境声
            screen.blit(self.normalFont.render(self.soundEnvironmentTxt+": "+str(self.soundVolume_sound_environment),True,(255, 255, 255)),(self.bar_x,self.bar_y3-self.fontSize*1.4))
            screen.blit(self.bar_empty,(self.bar_x,self.bar_y3))
            barImgWidth = round(self.bar_full.get_width()*self.soundVolume_sound_environment/100)
            screen.blit(pygame.transform.scale(self.bar_full,(barImgWidth,self.bar_height)),(self.bar_x,self.bar_y3))
            screen.blit(self.button,(self.bar_x+barImgWidth-self.button.get_width()/2,self.bar_y3-self.bar_height/2))
            #获取鼠标坐标
            mouse_x,mouse_y=pygame.mouse.get_pos()
            #取消按钮
            if self.buttons_x1<mouse_x<self.buttons_x1+self.cancelTxt_n.get_width() and self.buttons_y<mouse_y<self.buttons_y+self.cancelTxt_n.get_height():
                screen.blit(self.cancelTxt_b,(self.buttons_x1,self.buttons_y))
                if pygame.mouse.get_pressed()[0]:
                    with open("Save/setting.yaml", "r", encoding='utf-8') as f:
                        settingData = yaml.load(f.read(),Loader=yaml.FullLoader)
                        self.soundVolume_background_music = settingData["Sound"]["background_music"]
                        self.soundVolume_sound_effects = settingData["Sound"]["sound_effects"]
                        self.soundVolume_background_music = settingData["Sound"]["background_music"]
                    self.ifDisplay = False
            else:
                screen.blit(self.cancelTxt_n,(self.buttons_x1,self.buttons_y))
            #确认按钮
            if self.buttons_x2<mouse_x<self.buttons_x2+self.confirmTxt_n.get_width() and self.buttons_y<mouse_y<self.buttons_y+self.confirmTxt_n.get_height():
                screen.blit(self.confirmTxt_b,(self.buttons_x2,self.buttons_y))
                if pygame.mouse.get_pressed()[0]:
                    with open("Save/setting.yaml", "r", encoding='utf-8') as f:
                        settingData = yaml.load(f.read(),Loader=yaml.FullLoader)
                        settingData["Sound"]["background_music"] = self.soundVolume_background_music
                        settingData["Sound"]["sound_effects"] = self.soundVolume_sound_effects
                        settingData["Sound"]["background_music"] = self.soundVolume_background_music
                    with open("Save/setting.yaml", "w", encoding='utf-8') as f:
                        yaml.dump(settingData, f)
                    pygame.mixer.music.set_volume(settingData["Sound"]["background_music"]/100.0)
                    self.ifDisplay = False
                    return True
            else:
                screen.blit(self.confirmTxt_n,(self.buttons_x2,self.buttons_y))
            #其他按键的判定按钮
            if pygame.mouse.get_pressed()[0]:
                if self.bar_x<=mouse_x<=self.bar_x+self.bar_width:
                    #如果碰到背景音乐的音量条
                    if self.bar_y1-self.bar_height/2<mouse_y<self.bar_y1+self.bar_height*1.5:
                        self.soundVolume_background_music = round(100*(mouse_x-self.bar_x)/self.bar_width)
                    #如果碰到音效的音量条
                    elif self.bar_y2-self.bar_height/2<mouse_y<self.bar_y2+self.bar_height*1.5:
                        self.soundVolume_sound_effects = round(100*(mouse_x-self.bar_x)/self.bar_width)
                    #如果碰到环境声的音量条
                    elif self.bar_y3-self.bar_height/2<mouse_y<self.bar_y3+self.bar_height*1.5:
                        self.soundVolume_sound_environment = round(100*(mouse_x-self.bar_x)/self.bar_width)
        return False

#行动点数管理器（塔防模式）
class ApSystem:
    def __init__(self,fontSize):
        self.point = 0
        self.coolDown = 0
        with open("Save/setting.yaml", "r", encoding='utf-8') as f:
            DATA = yaml.load(f.read(),Loader=yaml.FullLoader)
            self.FONT = DATA["Font"]
            self.MODE = DATA["Antialias"]
        self.FONT = pygame.font.SysFont(self.FONT,int(fontSize))
    def display(self,screen,x,y):
        screen.blit(self.FONT.render(self.point,self.MODE,(255, 255, 255)),(x,y))
        if self.coolDown == 100:
            self.point += 1
            self.coolDown = 0
        else:
            self.coolDown += 1

#按钮
class Button:
    def __init__(self,path,x,y):
        self.img = pygame.image.load(os.path.join(path)) if isinstance(path,str) else path
        self.img2 = None
        self.hoverEventTriggered = False
        self.x = x
        self.y = y
        if isinstance(path,str):
            pass
    def setHoverImg(self,img):
        self.img2 = img
    def display(self,screen):
        screen.blit(self.img,(self.x,self.y))
    def hoverEventOn(self):
        if self.img2 != None and self.hoverEventTriggered == False:
            tempSurface = self.img
            self.img = self.img2
            self.img2 = tempSurface
            self.hoverEventTriggered = True
    def hoverEventOff(self):
        if self.img2 != None and self.hoverEventTriggered == True:
            tempSurface = self.img
            self.img = self.img2
            self.img2 = tempSurface
            self.hoverEventTriggered = False

#输入管理组件
class GameController:
    def __init__(self,screen):
        self.joystick = Joystick()
        self.mouse = MouseInput(screen)
        self.mouse_x,self.mouse_y = pygame.mouse.get_pos()
    def display(self,screen):
        self.mouse_x,self.mouse_y = pygame.mouse.get_pos()
        self.mouse.display(screen,(self.mouse_x,self.mouse_y))
    def get_pos(self):
        return self.mouse_x,self.mouse_y
    #检测是否被点击
    def ifHover(self,imgObject,objectPos=(0,0),local_x=0,local_y=0):
        #如果是pygame的面
        if isinstance(imgObject,pygame.Surface):
            if objectPos[0]<self.mouse_x-local_x<objectPos[0]+imgObject.get_width() and objectPos[1]<self.mouse_y-local_y<objectPos[1]+imgObject.get_height():
                return True
            else:
                return False
        #如果是zero引擎的Image类
        elif isinstance(imgObject,ImageSurface):
            if imgObject.x<self.mouse_x-local_x<imgObject.x+imgObject.width and imgObject.y<self.mouse_y-local_y<imgObject.y+imgObject.height:
                return True
            else:
                return False
        #如果是zero引擎的Button类
        elif isinstance(imgObject,Button):
            if imgObject.x<=self.mouse_x-local_x<=imgObject.x+imgObject.img.get_width() and imgObject.y<=self.mouse_y-local_y<=imgObject.y+imgObject.img.get_height():
                imgObject.hoverEventOn()
                return True
            else:
                imgObject.hoverEventOff()
                return False
        else:
            raise Exception('Error: Unable to check current object.')

#鼠标管理系统
class MouseInput:
    def __init__(self,screen):
        pygame.mouse.set_visible(False)
        self.iconImg = pygame.transform.scale(pygame.image.load(os.path.join("Assets/image/UI/","mouse_icon.png")).convert_alpha(),(int(screen.get_width()*0.01),int(screen.get_width()*0.013)))
    def display(self,screen,pos):
        screen.blit(self.iconImg,pos)

#手柄控制组件
class Joystick:
    def __init__(self):
        if pygame.joystick.get_count()>0:
            self.inputController = pygame.joystick.Joystick(0)
            self.inputController.init()
        else:
            self.inputController = None
    def get_init(self):
        if self.inputController != None:
            return self.inputController.get_init()
        else:
            return False
    def get_button(self,buttonId):
        if self.inputController != None and self.inputController.get_init() == True:
            return self.inputController.get_button(buttonId)
        else:
            return None
    def get_axis(self,buttonId):
        if self.inputController != None and self.inputController.get_init() == True:
            return self.inputController.get_axis(buttonId)
        else:
            return 0