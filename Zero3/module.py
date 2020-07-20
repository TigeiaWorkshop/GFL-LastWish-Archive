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
from moviepy.editor import *

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

#npc立绘系统
class NpcImageSystem:
    def __init__(self):
        self.imgDic = {}
        self.npcLastRound = []
        self.npcLastRoundImgAlpha = 255
        self.npcThisRound = []
        self.npcThisRoundImgAlpha = 0
        self.npcBothRound = []
        self.communication = pygame.image.load(os.path.join("Assets/image/UI/communication.png")).convert_alpha()
    def displayTheNpc(self,name,x,y,alpha,screen):
        if alpha <= 0:
            return False
        nameTemp = name.replace("&communication","").replace("&dark","")
        img_width = int(screen.get_width()/2)
        #加载npc的基础立绘
        if nameTemp not in self.imgDic:
            self.imgDic[nameTemp] = {"normal":pygame.transform.scale(pygame.image.load(os.path.join("Assets/image/npc/"+nameTemp+".png")).convert_alpha(),(img_width,img_width))}
            #生成深色图片
            self.imgDic[nameTemp]["dark"] = self.imgDic[nameTemp]["normal"].copy()
            self.imgDic[nameTemp]["dark"].fill((50, 50, 50), special_flags=pygame.BLEND_RGB_SUB) 
        if "&communication" in name:
            if "communication" not in self.imgDic[nameTemp]:
                #生成通讯图片
                self.imgDic[nameTemp]["communication"] = pygame.Surface((int(img_width/1.9), int(img_width/1.8)), flags=pygame.SRCALPHA)
                self.imgDic[nameTemp]["communication"].blit(self.imgDic[nameTemp]["normal"],(-int(img_width/4),0))
                self.imgDic[nameTemp]["communication"].blit(pygame.transform.scale(self.communication,(int(img_width/1.9), int(img_width/1.7))),(0,0))
                #生成深色的通讯图片
                self.imgDic[nameTemp]["communication_dark"] = self.imgDic[nameTemp]["communication"].copy()
                dark = pygame.Surface((int(img_width/1.9), int(img_width/1.8)), flags=pygame.SRCALPHA).convert_alpha()
                dark.fill((50,50,50))
                self.imgDic[nameTemp]["communication_dark"].blit(dark, (0, 0), special_flags=pygame.BLEND_RGB_SUB)
            x+=int(img_width/4)
            if "&dark" in name:
                img = self.imgDic[nameTemp]["communication_dark"]
            else:
                img = self.imgDic[nameTemp]["communication"]
        elif "&dark" in name:
            img = self.imgDic[nameTemp]["dark"]
        else:
            img = self.imgDic[nameTemp]["normal"]
        if img.get_alpha() != alpha:
            img.set_alpha(alpha)
        screen.blit(img,(x,y))
    def display(self,screen):
        window_x = screen.get_width()
        window_y = screen.get_height()
        if self.npcLastRoundImgAlpha != 0 and len(self.npcLastRound)>0:
            #调整alpha值
            self.npcLastRoundImgAlpha -= 15
            #画上上一幕的立绘
            if len(self.npcLastRound)==2:
                if self.npcLastRound[0] not in self.npcBothRound:
                    self.displayTheNpc(self.npcLastRound[0],0,window_y-window_x/2,self.npcLastRoundImgAlpha,screen)
                if self.npcLastRound[1] not in self.npcBothRound:
                    self.displayTheNpc(self.npcLastRound[1],window_x/2,window_y-window_x/2,self.npcLastRoundImgAlpha,screen)
            elif len(self.npcLastRound)==1 and self.npcLastRound[0] not in self.npcBothRound:
                self.displayTheNpc(self.npcLastRound[0],window_x/4,window_y-window_x/2,self.npcLastRoundImgAlpha,screen)
        #加载对话人物立绘
        if len(self.npcThisRound)>0:
            #调整alpha值
            if self.npcThisRoundImgAlpha < 255:
                self.npcThisRoundImgAlpha += 25
            #画上当前幕的立绘
            if len(self.npcThisRound)==2:
                if self.npcThisRound[0] not in self.npcBothRound:
                    self.displayTheNpc(self.npcThisRound[0],0,window_y-window_x/2,self.npcThisRoundImgAlpha,screen)
                else:
                    self.displayTheNpc(self.npcThisRound[0],0,window_y-window_x/2,255,screen)
                if self.npcThisRound[1] not in self.npcBothRound:
                    self.displayTheNpc(self.npcThisRound[1],window_x/2,window_y-window_x/2,self.npcThisRoundImgAlpha,screen)
                else:
                    self.displayTheNpc(self.npcThisRound[1],window_x/2,window_y-window_x/2,255,screen)
            elif len(self.npcThisRound)==1:
                if self.npcThisRound[0] not in self.npcBothRound:
                    self.displayTheNpc(self.npcThisRound[0],window_x/4,window_y-window_x/2,self.npcThisRoundImgAlpha,screen)
                else:
                    self.displayTheNpc(self.npcThisRound[0],window_x/4,window_y-window_x/2,255,screen)
    def process(self,lastRoundCharacterNameList,thisRoundCharacterNameList):
        if lastRoundCharacterNameList == None:
            self.npcLastRound = []
        else:
            self.npcLastRound = lastRoundCharacterNameList
        if thisRoundCharacterNameList == None:
            self.npcThisRound = []
        else:
            self.npcThisRound = thisRoundCharacterNameList
        self.npcLastRoundImgAlpha = 255
        self.npcThisRoundImgAlpha = 5
        self.npcBothRound = []
        for name in self.npcThisRound:
            if name in self.npcLastRound:
                self.npcBothRound.append(name)

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

#对话框和对话框内容
class DialogContent:
    def __init__(self,fontSize):
        self.content = ""
        self.textIndex = None
        self.displayedLine = None
        self.textPlayingSound = pygame.mixer.Sound("Assets/sound/ui/dialog_words_playing.ogg")
        with open("Save/setting.yaml", "r", encoding='utf-8') as f:
            DATA = yaml.load(f.read(),Loader=yaml.FullLoader)
            self.FONT = DATA["Font"]
            self.MODE = DATA["Antialias"]
            self.READINGSPEED = DATA["ReadingSpeed"]
        self.FONTSIZE = int(fontSize)
        self.FONT = pygame.font.SysFont(self.FONT,self.FONTSIZE)
        self.dialoguebox = pygame.image.load(os.path.join("Assets/image/UI/dialoguebox.png")).convert_alpha()
        self.dialoguebox_y = None
        self.dialoguebox_height = 0
        self.dialoguebox_max_height = None
        self.narrator = None
        #鼠标图标
        self.mouseImg_none = pygame.image.load(os.path.join("Assets/image/UI/mouse_none.png")).convert_alpha()
        self.mouseImg_click = pygame.image.load(os.path.join("Assets/image/UI/mouse.png")).convert_alpha()
        self.mouse_gif_id = 0
        self.ifHide = False
        self.readTime = 0
        self.totalLetters = 0
        self.autoMode = False
    def hideSwitch(self):
        if self.ifHide == False:
            self.ifHide = True
        else:
            self.ifHide = False
    def updateContent(self,txt,narrator,forceNotResizeDialoguebox=False):
        self.content = txt
        self.totalLetters = 0
        self.readTime = 0
        for i in range(len(self.content)):
            self.totalLetters += len(self.content[i])
        if self.narrator != narrator:
            if forceNotResizeDialoguebox == False:
                self.resetDialogueboxData()
            else:
                pass
            self.narrator = narrator
        self.textIndex = 0
        self.displayedLine = 0
        if pygame.mixer.get_busy() == True:
            self.textPlayingSound.stop()
    def resetDialogueboxData(self):
        self.dialoguebox_height = 0
        self.dialoguebox_y = None
    def setSoundVolume(self,num):
        self.textPlayingSound.set_volume(num/100.0)
    def playAll(self):
        self.displayedLine = len(self.content)-1
        self.textIndex = len(self.content[self.displayedLine])-1
    def display(self,screen):
        if self.ifHide == False:
            #如果对话框图片的最高高度没有被设置，则根据屏幕大小设置一个
            if self.dialoguebox_max_height == None:
                self.dialoguebox_max_height = screen.get_height()/4
            #如果当前对话框图片的y坐标不存在（一般出现在对话系统例行初始化后），则根据屏幕大小设置一个
            if self.dialoguebox_y == None:
                self.dialoguebox_y = screen.get_height()*0.65+self.dialoguebox_max_height/2
            #画出对话框图片
            screen.blit(pygame.transform.scale(self.dialoguebox,(int(screen.get_width()*0.74),int(self.dialoguebox_height))),(screen.get_width()*0.13,self.dialoguebox_y))
            #如果对话框图片还在放大阶段
            if self.dialoguebox_height < self.dialoguebox_max_height:
                self.dialoguebox_height += self.dialoguebox_max_height/12
                self.dialoguebox_y -= self.dialoguebox_max_height/24
            #如果已经放大好了
            else:
                x = int(screen.get_width()*0.2)
                y = int(screen.get_height()*0.74)
                #写上当前讲话人的名字
                if self.narrator != None:
                    screen.blit(self.FONT.render(self.narrator,self.MODE,(255, 255, 255)),(x,self.dialoguebox_y+self.FONTSIZE))
                #鼠标gif的ID
                if self.mouse_gif_id<100:
                    self.mouse_gif_id += 0.25
                else:
                    self.mouse_gif_id = 0
                #根据ID画出鼠标gif
                if int(self.mouse_gif_id/10)%2==0:
                    screen.blit(pygame.transform.scale(self.mouseImg_none,(self.FONTSIZE,self.FONTSIZE)),(screen.get_width()*0.82,screen.get_height()*0.83))
                else:
                    screen.blit(pygame.transform.scale(self.mouseImg_click,(self.FONTSIZE,self.FONTSIZE)),(screen.get_width()*0.82,screen.get_height()*0.83))
                #对话框已播放的内容
                for i in range(self.displayedLine):
                    screen.blit(self.FONT.render(self.content[i],self.MODE,(255, 255, 255)),(x,y+self.FONTSIZE*1.5*i))
                #对话框正在播放的内容
                screen.blit(self.FONT.render(self.content[self.displayedLine][:self.textIndex],self.MODE,(255, 255, 255)),(x,y+self.FONTSIZE*1.5*self.displayedLine))
                #如果当前行的字符还没有完全播出
                if self.textIndex < len(self.content[self.displayedLine]):
                    if pygame.mixer.get_busy() == False:
                        self.textPlayingSound.play()
                    self.textIndex +=1
                #当前行的所有字都播出后，播出下一行
                elif self.displayedLine < len(self.content)-1:
                    if pygame.mixer.get_busy() == False:
                        self.textPlayingSound.play()
                    self.textIndex = 1
                    self.displayedLine += 1
                #当所有行都播出后
                else:
                    if pygame.mixer.get_busy() == True:
                        self.textPlayingSound.stop()
                    if self.autoMode == True and self.readTime < self.totalLetters:
                        self.readTime += self.READINGSPEED
                    return True
        return False
    def forceUpdate(self):
        if self.autoMode == True and self.readTime > self.totalLetters:
            return True
        else:
            return False

#背景音乐和图片管理
class DialogBackground:
    def __init__(self,backgroundMusicVolume):
        self.backgroundImgName = None
        self.backgroundImgSurface = None
        self.nullSurface = pygame.image.load(os.path.join("Assets/image/UI/black.png")).convert_alpha()
        self.backgroundMusicName = None
        self.setBgmVolume(backgroundMusicVolume)
    def setBgmVolume(self,backgroundMusicVolume):
        self.backgroundMusicVolume = backgroundMusicVolume/100.0
        pygame.mixer.music.set_volume(self.backgroundMusicVolume)
    def update(self,backgroundImgName,backgroundMusicName):
        #如果需要更新背景图片
        if self.backgroundImgName != backgroundImgName:
            self.backgroundImgName = backgroundImgName
            if self.backgroundImgName != None:
                if os.path.exists("Assets/image/dialog_background/{}.png".format(self.backgroundImgName)):
                    self.backgroundImgSurface = pygame.image.load(os.path.join("Assets/image/dialog_background/{}.png".format(self.backgroundImgName))).convert_alpha()
                elif os.path.exists("Assets/image/dialog_background/{}.jpg".format(self.backgroundImgName)):
                    self.backgroundImgSurface = pygame.image.load(os.path.join("Assets/image/dialog_background/{}.jpg".format(self.backgroundImgName))).convert_alpha()
                elif os.path.exists("Assets/movie/"+self.backgroundImgName):
                    self.backgroundImgSurface = VideoObject("Assets/movie/"+self.backgroundImgName,True)
                else:
                    raise Exception('Warning: Cannot find background image or video file.')
            else:
                self.backgroundImgSurface = None
        #如果需要更新背景音乐
        if self.backgroundMusicName != backgroundMusicName:
            self.backgroundMusicName = backgroundMusicName
            if self.backgroundMusicName != None:
                if os.path.exists("Assets/music/{}.mp3".format(self.backgroundMusicName)):
                    pygame.mixer.music.load("Assets/music/{}.mp3".format(self.backgroundMusicName))
                elif os.path.exists("Assets/music/{}.ogg".format(self.backgroundMusicName)):
                    pygame.mixer.music.load("Assets/music/{}.ogg".format(self.backgroundMusicName))
                else:
                    raise Exception('Warning: Cannot find background music file.')
                pygame.mixer.music.play(loops=9999, start=0.0)
            else:
                pygame.mixer.music.unload()
    def display(self,screen):
        if self.backgroundImgName != None:
            if isinstance(self.backgroundImgSurface,VideoObject):
                self.backgroundImgSurface.display(screen)
            else:
                screen.blit(pygame.transform.scale(self.backgroundImgSurface,screen.get_size()),(0,0))
        else:
            screen.blit(pygame.transform.scale(self.nullSurface,screen.get_size()),(0,0))

#对话系统按钮UI模块
class DialogButtons:
    def __init__(self):
        with open("Save/setting.yaml", "r", encoding='utf-8') as f:
            setting = yaml.load(f.read(),Loader=yaml.FullLoader)
            window_x = int(setting['Screen_size_x'])
            window_y = int(setting['Screen_size_y'])
            self.FONTSIZE = int(window_x*0.0175)
            self.FONT = pygame.font.SysFont(setting["Font"],self.FONTSIZE)
            self.FONTMODE = setting["Antialias"]
        with open("Lang/"+setting['Language']+".yaml", "r", encoding='utf-8') as f:
            dialog_txt = yaml.load(f.read(),Loader=yaml.FullLoader)["Dialog"]
            #生成跳过按钮
            tempButtonIcon = pygame.transform.scale(pygame.image.load(os.path.join("Assets/image/UI/dialog_skip.png")).convert_alpha(),(self.FONTSIZE,self.FONTSIZE))
            tempButtonTxt = self.FONT.render(dialog_txt["skip"],self.FONTMODE,(255, 255, 255))
            temp_w = tempButtonTxt.get_width()+self.FONTSIZE*1.5
            self.skipButton = pygame.Surface((temp_w, self.FONTSIZE),flags=pygame.SRCALPHA).convert_alpha()
            self.skipButtonHovered = pygame.Surface((temp_w, self.FONTSIZE),flags=pygame.SRCALPHA).convert_alpha()
            self.skipButtonHovered.blit(tempButtonIcon,(tempButtonTxt.get_width()+self.FONTSIZE*0.5,0))
            self.skipButtonHovered.blit(tempButtonTxt,(0,0))
            tempButtonTxt = self.FONT.render(dialog_txt["skip"],self.FONTMODE,(105, 105, 105))
            tempButtonIcon.fill((100,100,100), special_flags=pygame.BLEND_RGB_SUB)
            self.skipButton.blit(tempButtonIcon,(tempButtonTxt.get_width()+self.FONTSIZE*0.5,0))
            self.skipButton.blit(tempButtonTxt,(0,0))
            self.skipButton = ImageSurface(self.skipButton,window_x*0.9,window_y*0.05)
            self.skipButtonHovered = ImageSurface(self.skipButtonHovered,window_x*0.9,window_y*0.05)
            #生成自动播放按钮
            self.autoIconHovered = pygame.transform.scale(pygame.image.load(os.path.join("Assets/image/UI/dialog_auto.png")).convert_alpha(),(self.FONTSIZE,self.FONTSIZE))
            self.autoIcon = self.autoIconHovered.copy()
            self.autoIcon.fill((100,100,100), special_flags=pygame.BLEND_RGB_SUB)
            self.autoIconDegree = 0
            self.autoIconDegreeChange = (2**0.5-1)*self.FONTSIZE/45
            self.autoMode = False
            tempButtonTxt = self.FONT.render(dialog_txt["auto"],self.FONTMODE,(105, 105, 105))
            temp_w = tempButtonTxt.get_width()+self.FONTSIZE*1.5
            self.autoButton = pygame.Surface((temp_w, self.FONTSIZE),flags=pygame.SRCALPHA).convert_alpha()
            self.autoButtonHovered = pygame.Surface((temp_w, self.FONTSIZE),flags=pygame.SRCALPHA).convert_alpha()
            self.autoButton.blit(tempButtonTxt,(0,0))
            self.autoButtonHovered.blit(self.FONT.render(dialog_txt["auto"],self.FONTMODE,(255, 255, 255)),(0,0))
            self.autoButton = ImageSurface(self.autoButton,window_x*0.8,window_y*0.05)
            self.autoButton.description = int(self.autoButton.x+self.autoButton.img.get_width()-self.FONTSIZE)
            self.autoButtonHovered = ImageSurface(self.autoButtonHovered,window_x*0.8,window_y*0.05)
            self.autoButtonHovered.description = int(self.autoButtonHovered.x+self.autoButtonHovered.img.get_width()-self.FONTSIZE)
            #隐藏按钮
            hideUI_img = pygame.transform.scale(pygame.image.load(os.path.join("Assets/image/UI/dialog_hide.png")).convert_alpha(),(self.FONTSIZE,self.FONTSIZE))
            hideUI_imgTemp = hideUI_img.copy()
            hideUI_imgTemp.fill((100,100,100), special_flags=pygame.BLEND_RGB_SUB)
            self.hideButton = Button(hideUI_imgTemp,window_x*0.05,window_y*0.05)
            self.hideButton.setHoverImg(hideUI_img)
            #历史回溯按钮
            history_img = pygame.transform.scale(pygame.image.load(os.path.join("Assets/image/UI/dialog_history.png")).convert_alpha(),(self.FONTSIZE,self.FONTSIZE))
            history_imgTemp = history_img.copy()
            history_imgTemp.fill((100,100,100), special_flags=pygame.BLEND_RGB_SUB)
            self.historyButton = Button(history_imgTemp,window_x*0.1,window_y*0.05)
            self.historyButton.setHoverImg(history_img)
    def display(self,screen,theGameController):
        self.hideButton.display(screen)
        self.historyButton.display(screen)
        action = ""
        if theGameController.ifHover(self.skipButton):
            self.skipButtonHovered.draw(screen)
            action = "skip"
        else:
            self.skipButton.draw(screen)
        if theGameController.ifHover(self.autoButton):
            self.autoButtonHovered.draw(screen)
            if self.autoMode == True:
                rotatedIcon = pygame.transform.rotate(self.autoIconHovered,self.autoIconDegree)
                screen.blit(rotatedIcon,(self.autoButtonHovered.description+self.autoIconHovered.get_width()/2-rotatedIcon.get_width()/2,self.autoButtonHovered.y+self.autoIconHovered.get_height()/2-rotatedIcon.get_height()/2))
                if self.autoIconDegree < 180:
                    self.autoIconDegree+=1
                else:
                    self.autoIconDegree=0
            else:
                screen.blit(self.autoIconHovered,(self.autoButtonHovered.description,self.autoButtonHovered.y))
            action = "auto"
        else:
            if self.autoMode == True:
                self.autoButtonHovered.draw(screen)
                rotatedIcon = pygame.transform.rotate(self.autoIconHovered,self.autoIconDegree)
                screen.blit(rotatedIcon,(self.autoButtonHovered.description+self.autoIconHovered.get_width()/2-rotatedIcon.get_width()/2,self.autoButtonHovered.y+self.autoIconHovered.get_height()/2-rotatedIcon.get_height()/2))
                if self.autoIconDegree < 180:
                    self.autoIconDegree+=1
                else:
                    self.autoIconDegree=0
            else:
                self.autoButton.draw(screen)
                screen.blit(self.autoIcon,(self.autoButton.description,self.autoButton.y))
        if theGameController.ifHover(self.hideButton):
            action = "hide"
        elif theGameController.ifHover(self.historyButton):
            action = "history"
        return action
    def autoModeSwitch(self):
        if self.autoMode == False:
            self.autoMode = True
        else:
            self.autoMode = False
            self.autoIconDegree = 0

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
        self.iconImg = pygame.transform.scale(pygame.image.load(os.path.join("Assets/image/UI/","mouse_icon.png")).convert_alpha(),(int(screen.get_width()*0.013),int(screen.get_width()*0.015)))
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

class DialogSystem:
    def __init__(self,chapter_name,screen,setting,part):
        #控制器输入组件
        self.InputController = GameController(screen)
        #获取屏幕的尺寸
        self.window_x,self.window_y = screen.get_size()
        #读取章节信息
        with open("Data/main_chapter/{0}_dialogs_{1}.yaml".format(chapter_name,setting['Language']), "r", encoding='utf-8') as f:
            self.dialog_content = yaml.load(f.read(),Loader=yaml.FullLoader)[part]
            if len(self.dialog_content)==0:
                raise Exception('Warning: The dialog has no content!')
        #选项栏
        self.optionBox = pygame.image.load(os.path.join("Assets/image/UI/option.png")).convert_alpha()
        #UI按钮
        self.ButtonsMananger = DialogButtons()
        #黑色帘幕
        self.black_bg = ImageSurface(pygame.image.load(os.path.join("Assets/image/UI/black.png")).convert_alpha(),0,0,self.window_x,self.window_y)
        #加载对话框系统
        self.dialogTxtSystem = DialogContent(self.window_x*0.015)
        #设定初始化
        self.dialogId = "head"
        #如果dialog_content没有头
        if self.dialogId not in self.dialog_content:
            raise Exception('Warning: The dialog must have a head!')
        else:
            self.dialogTxtSystem.updateContent(self.dialog_content[self.dialogId]["content"],self.dialog_content[self.dialogId]["narrator"])
        #玩家在对话时做出的选择
        self.dialog_options = {}
        #加载npc立绘系统并初始化
        self.npc_img_dic = NpcImageSystem()
        self.npc_img_dic.process(None,self.dialog_content[self.dialogId]["characters_img"])
        #加载对话的背景图片
        self.backgroundContent = DialogBackground(setting["Sound"]["background_music"])
        self.backgroundContent.update(self.dialog_content[self.dialogId]["background_img"],None)
    def ready(self):
        self.backgroundContent.update(self.dialog_content[self.dialogId]["background_img"],self.dialog_content[self.dialogId]["background_music"])
    def display(self,screen,Display):
        if_skip = False
        #背景
        self.backgroundContent.display(screen)
        self.npc_img_dic.display(screen)
        #按钮
        buttonEvent = self.ButtonsMananger.display(screen,self.InputController)
        #显示对话框和对应文字
        dialogPlayResult = self.dialogTxtSystem.display(screen)
        if dialogPlayResult == True:
            if self.dialog_content[self.dialogId]["next_dialog_id"] != None and self.dialog_content[self.dialogId]["next_dialog_id"][0] == "option":
                #显示选项
                optionBox_y_base = (self.window_y*3/4-(len(self.dialog_content[self.dialogId]["next_dialog_id"])-1)*2*self.window_x*0.03)/4
                for i in range(1,len(self.dialog_content[self.dialogId]["next_dialog_id"])):
                    option_txt = self.dialogTxtSystem.FONT.render(self.dialog_content[self.dialogId]["next_dialog_id"][i][0],self.dialogTxtSystem.MODE,(255, 255, 255))
                    optionBox_scaled = pygame.transform.scale(self.optionBox,(int(option_txt.get_width()+self.window_x*0.05),int(self.window_x*0.05)))
                    optionBox_x = (self.window_x-optionBox_scaled.get_width())/2
                    optionBox_y = i*2*self.window_x*0.03+optionBox_y_base
                    displayWithInCenter(option_txt,optionBox_scaled,optionBox_x,optionBox_y,screen)
                    if pygame.mouse.get_pressed()[0] and self.InputController.ifHover(optionBox_scaled,(optionBox_x,optionBox_y)):
                        #下一个dialog的Id
                        theNextDialogId = self.dialog_content[self.dialogId]["next_dialog_id"][i][1]
                        #更新背景
                        self.backgroundContent.update(self.dialog_content[theNextDialogId]["background_img"],self.dialog_content[theNextDialogId]["background_music"])
                        #保存选取的选项
                        self.dialog_options[len(self.dialog_options)] = i
                        #重设立绘系统
                        self.npc_img_dic.process(self.dialog_content[self.dialogId]["characters_img"],self.dialog_content[theNextDialogId]["characters_img"])
                        #切换dialogId
                        self.dialogId = theNextDialogId
                        self.dialogTxtSystem.updateContent(self.dialog_content[self.dialogId]["content"],self.dialog_content[self.dialogId]["narrator"])
                        break
        #按键判定
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    Display.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.JOYBUTTONDOWN:
                if pygame.mouse.get_pressed()[0] or self.InputController.joystick.get_button(0) == 1:
                    if buttonEvent == "hide":
                        self.dialogTxtSystem.hideSwitch()
                    #如果接来下没有文档了或者玩家按到了跳过按钮
                    elif buttonEvent == "skip" or self.dialog_content[self.dialogId]["next_dialog_id"] == None:
                        #淡出
                        pygame.mixer.music.fadeout(1000)
                        for i in range(0,255,5):
                            self.black_bg.set_alpha(i)
                            self.black_bg.draw(screen)
                            Display.flip()
                        if_skip = True
                    elif buttonEvent == "auto":
                        self.ButtonsMananger.autoModeSwitch()
                    #如果所有行都没有播出，则播出所有行
                    elif dialogPlayResult == False:
                        self.dialogTxtSystem.playAll()
                    elif self.dialog_content[self.dialogId]["next_dialog_id"][0] == "default":
                        theNextDialogId = self.dialog_content[self.dialogId]["next_dialog_id"][1]
                        #更新背景
                        self.backgroundContent.update(self.dialog_content[theNextDialogId]["background_img"],self.dialog_content[theNextDialogId]["background_music"])
                        #重设立绘系统
                        self.npc_img_dic.process(self.dialog_content[self.dialogId]["characters_img"],self.dialog_content[theNextDialogId]["characters_img"])
                        #切换dialogId
                        self.dialogId = theNextDialogId
                        self.dialogTxtSystem.updateContent(self.dialog_content[self.dialogId]["content"],self.dialog_content[self.dialogId]["narrator"])
                    #如果是切换场景
                    elif self.dialog_content[self.dialogId]["next_dialog_id"][0] == "changeScene":
                        #淡出
                        pygame.mixer.music.fadeout(1000)
                        for i in range(0,255,5):
                            self.black_bg.set_alpha(i)
                            self.black_bg.draw(screen)
                            Display.flip()
                        time.sleep(2)
                        self.dialogId = self.dialog_content[self.dialogId]["next_dialog_id"][1]
                        self.dialogTxtSystem.resetDialogueboxData()
                        self.dialogTxtSystem.updateContent(self.dialog_content[self.dialogId]["content"],self.dialog_content[self.dialogId]["narrator"])
                        self.backgroundContent.update(self.dialog_content[self.dialogId]["background_img"],None)
                        for i in range(255,0,-5):
                            self.backgroundContent.display(screen)
                            self.black_bg.set_alpha(i)
                            self.black_bg.draw(screen)
                            Display.flip()
                        #重设black_bg的alpha值以便下一次使用
                        self.black_bg.set_alpha(255)
                        #更新背景（音乐）
                        self.backgroundContent.update(self.dialog_content[self.dialogId]["background_img"],self.dialog_content[self.dialogId]["background_music"])
                #返回上一个对话场景（在被允许的情况下）
                elif pygame.mouse.get_pressed()[2] or self.InputController.joystick.get_button(1) == 1:
                    theNextDialogId = self.dialog_content[self.dialogId]["last_dialog_id"]
                    if theNextDialogId != None:
                        #更新背景
                        self.backgroundContent.update(self.dialog_content[theNextDialogId]["background_img"],self.dialog_content[theNextDialogId]["background_music"])
                        #重设立绘系统
                        self.npc_img_dic.process(self.dialog_content[self.dialogId]["characters_img"],self.dialog_content[theNextDialogId]["characters_img"])
                        #切换dialogId
                        self.dialogId = theNextDialogId
                        self.dialogTxtSystem.updateContent(self.dialog_content[self.dialogId]["content"],self.dialog_content[self.dialogId]["narrator"],True)
        self.InputController.display(screen)
        return if_skip

#中心展示模块2：接受两个item和item2的x和y，展示item2后，将item1展示在item2的中心位置：
def displayWithInCenter(item1,item2,x,y,screen,local_x=0,local_y=0):
    added_x = (item2.get_width()-item1.get_width())/2
    added_y = (item2.get_height()-item1.get_height())/2
    screen.blit(item2,(x+local_x,y+local_y))
    screen.blit(item1,(x+added_x+local_x,y+added_y+local_y))