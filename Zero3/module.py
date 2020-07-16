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
    def draw(self,screen,local_x=0,local_y=0):
        if self.width == None and self.height == None:
            screen.blit(self.img,(self.x+local_x,self.y+local_y))
        else:
            if self.width == None:
                self.width = self.height/self.img.get_height()*self.img.get_width()
            elif self.height == None:
                self.height = self.width/self.img.get_width()*self.img.get_height()
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
            dark = pygame.Surface((img_width,img_width), flags=pygame.SRCALPHA).convert_alpha()
            dark.fill((50,50,50))
            self.imgDic[nameTemp]["dark"].blit(dark, (0, 0), special_flags=pygame.BLEND_RGB_SUB)
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
    def updateContent(self,txt,narrator,forceNotResizeDialoguebox=False):
        self.content = txt
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
                return True
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

#过场动画
def cutscene(screen,videoPath,bgmPath):
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

class Button:
    def __init__(self,path,x,y):
        self.img = pygame.image.load(os.path.join(path)) if isinstance(path,str) else path
        self.img2 = None
        self.hoverEventTriggered = False
        self.x = x
        self.y = y
        if isinstance(path,str):
            pass
    def display(self,screen):
        screen.blit(self.img,(self.x,self.y))
    def hoverEvent(self):
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
    def isHoverOn(self,mouse_pos=None):
        if mouse_pos == None:
            mouse_pos=pygame.mouse.get_pos()
        if self.x<=mouse_pos[0]<=self.x+self.img.get_width() and self.y<=mouse_pos[1]<=self.y+self.img.get_height():
            self.hoverEvent()
            return True
        else:
            self.hoverEventOff()
            return False

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
        if isinstance(imgObject,pygame.Surface):
            if objectPos[0]<self.mouse_x-local_x<objectPos[0]+imgObject.get_width() and objectPos[1]<self.mouse_y-local_y<objectPos[1]+imgObject.get_height():
                return True
            else:
                return False
        elif isinstance(imgObject,ImageSurface):
            if imgObject.x<self.mouse_x-local_x<imgObject.x+imgObject.width and imgObject.y<self.mouse_y-local_y<imgObject.y+imgObject.height:
                return True
            else:
                return False

#鼠标管理系统
class MouseInput:
    def __init__(self,screen):
        pygame.mouse.set_visible(False)
        self.iconImg = pygame.transform.scale(pygame.image.load(os.path.join("Assets/image/UI/","mouse_icon.png")).convert_alpha(),(int(screen.get_width()*0.04),int(screen.get_width()*0.04)))
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