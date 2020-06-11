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

#调整图片亮度
def changeDarkness(surface,value):
    dark = pygame.Surface((surface.get_width(), surface.get_height()), flags=pygame.SRCALPHA)
    dark.fill((abs(int(value)),abs(int(value)),abs(int(value)),0))
    if value > 0:
        surface.blit(dark, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    elif value < 0:
        surface.blit(dark, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    return surface

#重新编辑尺寸
def resizeImg(img,imgSize=(None,None)):
    if imgSize[1]!= None and imgSize[1] >= 0 and imgSize[0] == None:
        img = pygame.transform.scale(img,(round(imgSize[1]/img.get_height()*img.get_width()), round(imgSize[1])))
    elif imgSize[1] == None and imgSize[0]!= None and imgSize[0] >= 0:
        img = pygame.transform.scale(img,(round(imgSize[0]), round(imgSize[0]/img.get_width()*img.get_height())))
    elif imgSize[0] >= 0 and imgSize[1] >= 0:
        img = pygame.transform.scale(img, (round(imgSize[0]), round(imgSize[1])))
    elif imgSize[0] < 0 or imgSize[1] < 0:
        raise Exception('Both width and height must be positive interger!')
    return img

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
        if self.width != None and self.height != None:
            screen.blit(pygame.transform.scale(self.img, (int(self.width),int(self.height))),(self.x+local_x,self.y+local_y))
        elif self.width != None:
            image = resizeImg(self.img, (self.width,None))
            screen.blit(image,(self.x+local_x,self.y+local_y))
            self.height = image.get_height()
        elif self.height != None:
            image = resizeImg(self.img, (None,self.height))
            screen.blit(image,(self.x+local_x,self.y+local_y))
            self.width = image.get_width()
        else:
            screen.blit(self.img,(self.x+local_x,self.y+local_y))
    def set_alpha(self,value):
        self.img.set_alpha(value)
    def get_alpha(self):
        return self.img.get_alpha()

#高级图片加载模块：接收图片路径（或者已经载入的图片）,位置:[x,y],长,高,返回对应的图片class
def loadImage(path,the_object_position,width=None,height=None,description="Default",ifConvertAlpha=True):
    if isinstance(path,str):
        if ifConvertAlpha == False:
            return ImageSurface(pygame.image.load(os.path.join(path)),the_object_position[0],the_object_position[1],width,height,description)
        else:
            return ImageSurface(pygame.image.load(os.path.join(path)).convert_alpha(),the_object_position[0],the_object_position[1],width,height,description)
    else:
        return ImageSurface(path,the_object_position[0],the_object_position[1],width,height,description)

#文字制作模块：接受文字，颜色，文字大小，文字样式，模式，返回制作完的文字
def fontRender(txt,color,size=50,ifBold=False,ifItalic=False,font="simhei",mode=True):
    normal_font = pygame.font.SysFont(font,int(size),ifBold,ifItalic)
    if color == "gray" or color == "grey" or color == "disable":
        text_out = normal_font.render(txt, mode, (105,105,105))
    elif color == "white" or color == "enable":
        text_out = normal_font.render(txt, mode, (255, 255, 255))
    elif color == "black":
        text_out = normal_font.render(txt, mode, (0, 0, 0))
    elif color == "green":
        text_out = normal_font.render(txt, mode, (0,255,0))
    elif color == "red":
        text_out = normal_font.render(txt, mode, (255, 0, 0))
    else:
        text_out = normal_font.render(txt, mode, color)
    return text_out

#高级文字制作模块：接受文字，颜色，文字大小，文字样式，模式，返回制作完的文字Class，该Class具有一大一普通的字号
def fontRenderPro(txt,color,size=50,ifBold=False,ifItalic=False,font="simhei",mode=True):
    class TextSurface:
        def __init__(self, n, b):
            self.n = n
            self.b = b
    #文字设定
    normal_font = pygame.font.SysFont(font,int(size),ifBold,ifItalic)
    big_font = pygame.font.SysFont(font,int(size*1.5),ifBold,ifItalic)
    if color == "gray" or color == "grey" or color == "disable":
        text_out = TextSurface(normal_font.render(txt, mode, (105,105,105)),big_font.render(txt, mode, (105,105,105)))
    elif color == "white" or color == "enable":
        text_out = TextSurface(normal_font.render(txt, mode, (255, 255, 255)),big_font.render(txt, mode, (255, 255, 255)))
    else:
        text_out = TextSurface(normal_font.render(txt, mode, color),big_font.render(txt, mode, color))
    return text_out

#检测是否被点击
def isHoverOn(the_object,the_object_position,local_x=0,local_y=0):
    mouse_x,mouse_y=pygame.mouse.get_pos()
    if the_object_position[0]<mouse_x-local_x<the_object_position[0]+the_object.get_width() and the_object_position[1]<mouse_y-local_y<the_object_position[1]+the_object.get_height():
        return True
    else:
        return False

#检测是否鼠标在物体上
def isHover(theImgClass,local_x=0,local_y=0):
    mouse_x,mouse_y=pygame.mouse.get_pos()
    if theImgClass.x<mouse_x-local_x<theImgClass.x+theImgClass.width and theImgClass.y<mouse_y-local_y<theImgClass.y+theImgClass.height:
        return True
    else:
        return False

#中心展示模块1：接受两个item和item2的x和y，将item1展示在item2的中心位置,但不展示item2：
def displayInCenter(item1,item2,x,y,screen,local_x=0,local_y=0):
    added_x = (item2.get_width()-item1.get_width())/2
    added_y = (item2.get_height()-item1.get_height())/2
    screen.blit(item1,(x+added_x+local_x,y+added_y+local_y))

#中心展示模块2：接受两个item和item2的x和y，展示item2后，将item1展示在item2的中心位置：
def displayWithInCenter(item1,item2,x,y,screen,local_x=0,local_y=0):
    added_x = (item2.get_width()-item1.get_width())/2
    added_y = (item2.get_height()-item1.get_height())/2
    screen.blit(item2,(x+local_x,y+local_y))
    screen.blit(item1,(x+added_x+local_x,y+added_y+local_y))

#字典合并
def dicMerge(dict1, dict2): 
    res = {**dict1, **dict2} 
    return res

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

#加载路径下的所有图片，储存到一个list当中，然后返回
def loadAllImgInFile(pathRule,width=None,height=None):
    allImg = glob.glob(pathRule)
    for i in range(len(allImg)):
        allImg[i] = loadImg(allImg[i],width,height)
    return allImg

#增加图片暗度
def addDarkness(img,value):
    newImg = pygame.transform.scale(img,(img.get_width(), img.get_height()))
    dark = pygame.Surface((img.get_width(), img.get_height()), flags=pygame.SRCALPHA)
    dark.fill((value,value,value))
    newImg.blit(dark, (0, 0), special_flags=pygame.BLEND_RGB_SUB)
    return newImg

#减少图片暗度
def removeDarkness(img,value):
    newImg = pygame.transform.scale(img,(img.get_width(), img.get_height()))
    dark = pygame.Surface((img.get_width(), img.get_height()), flags=pygame.SRCALPHA)
    dark.fill((value,value,value))
    newImg.blit(dark, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
    return newImg

#画面更新控制器
class DisplayController:
    def __init__(self,fps):
        self.fps = fps
        self.clock = pygame.time.Clock()
    def flip(self):
        self.clock.tick(self.fps)
        pygame.display.flip()

#npc立绘系统
class NpcImage:
    def __init__(self):
        self.imgDic = {}
    def display(self,name,x,y,screen):
        if name not in self.imgDic:
            if "&dark" in name:
                nameTemp = name.replace("&dark","")
                if nameTemp not in self.imgDic:
                    self.imgDic[nameTemp] = {"img":loadImg("Assets/image/npc/"+nameTemp+".png"),"alpha":250}
                    self.imgDic[nameTemp]["img"].set_alpha(0)
                self.imgDic[name] = {"img":addDarkness(self.imgDic[nameTemp]["img"],50),"alpha":250}
                self.imgDic[name]["img"].set_alpha(0)
            else:
                self.imgDic[name] = {"img":loadImg("Assets/image/npc/"+name+".png"),"alpha":250}
                self.imgDic[name]["img"].set_alpha(0)
        tempAlpha = self.imgDic[name]["img"].get_alpha()
        if tempAlpha != self.imgDic[name]["alpha"]:
            if tempAlpha > self.imgDic[name]["alpha"]:
                tempAlpha -= 25
            else:
                tempAlpha += 25
            self.imgDic[name]["img"].set_alpha(tempAlpha)
        screen.blit(pygame.transform.scale(self.imgDic[name]["img"], (int(screen.get_width()/2),int(screen.get_width()/2))),(x,y))

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

#退出游戏
def quitGame():
    exit()

#设置UI
class settingContoller:
    def __init__(self,window_x,window_y,settingdata,langTxt):
        self.ifDisplay = False
        self.baseImgWidth = window_x/3
        self.baseImgHeight = window_x/3
        self.baseImg = loadImg("Assets/image/UI/setting_baseImg.png",self.baseImgWidth,self.baseImgHeight)
        self.baseImg.set_alpha(200)
        self.baseImgX = int((window_x-self.baseImgWidth)/2)
        self.baseImgY = int((window_y-self.baseImgHeight)/2)
        self.bar_height = round(window_x/60)
        self.bar_width = round(window_x/5)
        self.button = loadImg("Assets/image/UI/setting_bar_circle.png",self.bar_height,self.bar_height*2)
        self.bar_empty = loadImg("Assets/image/UI/setting_bar_empty.png",self.bar_width,self.bar_height)
        self.bar_full = loadImg("Assets/image/UI/setting_bar_full.png",self.bar_width,self.bar_height)
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
        self.fontSize = window_x/50
        self.settingTitleTxt = fontRender(langTxt["setting"],"white",self.fontSize*1.5)
        self.settingTitleTxt_x = int(self.baseImgX+(self.baseImgWidth-self.settingTitleTxt.get_width())/2)
        self.settingTitleTxt_y = self.baseImgY+self.baseImgHeight*0.05
        #语言
        self.languageTxt = fontRender(langTxt["language"]+": "+langTxt["currentLang"],"white",self.fontSize)
        #背景音乐
        self.backgroundMusicTxt = langTxt["background_music"]
        #音效
        self.soundEffectsTxt = langTxt["sound_effects"]
        #环境声效
        self.soundEnvironmentTxt = langTxt["sound_environment"]
        #确认
        self.confirmTxt = fontRenderPro(langTxt["confirm"],"white",self.fontSize)
        #取消
        self.cancelTxt = fontRenderPro(langTxt["cancel"],"white",self.fontSize)
        #确认和取消按钮的位置
        self.buttons_y = self.baseImgY + self.baseImgHeight*0.88
        self.buttons_x1 = self.baseImgX + self.confirmTxt.b.get_width()*2.5
        self.buttons_x2 = self.buttons_x1 + self.confirmTxt.b.get_width()
    def display(self,screen):
        if self.ifDisplay == True:
            #底部图
            screen.blit(self.baseImg,(self.baseImgX,self.baseImgY))
            screen.blit(self.settingTitleTxt,(self.settingTitleTxt_x,self.settingTitleTxt_y))
            #语言
            screen.blit(self.languageTxt,(self.bar_x,self.bar_y0))
            #背景音乐
            screen.blit(fontRender(self.backgroundMusicTxt+": "+str(self.soundVolume_background_music),"white",self.fontSize),(self.bar_x,self.bar_y1-self.fontSize*1.4))
            screen.blit(self.bar_empty,(self.bar_x,self.bar_y1))
            barImgWidth = round(self.bar_full.get_width()*self.soundVolume_background_music/100)
            screen.blit(pygame.transform.scale(self.bar_full,(barImgWidth,self.bar_height)),(self.bar_x,self.bar_y1))
            screen.blit(self.button,(self.bar_x+barImgWidth-self.button.get_width()/2,self.bar_y1-self.bar_height/2))
            #音效
            screen.blit(fontRender(self.soundEffectsTxt+": "+str(self.soundVolume_sound_effects),"white",self.fontSize),(self.bar_x,self.bar_y2-self.fontSize*1.4))
            screen.blit(self.bar_empty,(self.bar_x,self.bar_y2))
            barImgWidth = round(self.bar_full.get_width()*self.soundVolume_sound_effects/100)
            screen.blit(pygame.transform.scale(self.bar_full,(barImgWidth,self.bar_height)),(self.bar_x,self.bar_y2))
            screen.blit(self.button,(self.bar_x+barImgWidth-self.button.get_width()/2,self.bar_y2-self.bar_height/2))
            #环境声
            screen.blit(fontRender(self.soundEnvironmentTxt+": "+str(self.soundVolume_sound_environment),"white",self.fontSize),(self.bar_x,self.bar_y3-self.fontSize*1.4))
            screen.blit(self.bar_empty,(self.bar_x,self.bar_y3))
            barImgWidth = round(self.bar_full.get_width()*self.soundVolume_sound_environment/100)
            screen.blit(pygame.transform.scale(self.bar_full,(barImgWidth,self.bar_height)),(self.bar_x,self.bar_y3))
            screen.blit(self.button,(self.bar_x+barImgWidth-self.button.get_width()/2,self.bar_y3-self.bar_height/2))
            #显示确认和取消按钮
            if isHoverOn(self.cancelTxt.n,(self.buttons_x1,self.buttons_y)):
                screen.blit(self.cancelTxt.b,(self.buttons_x1,self.buttons_y))
            else:
                screen.blit(self.cancelTxt.n,(self.buttons_x1,self.buttons_y))
            if isHoverOn(self.confirmTxt.n,(self.buttons_x2,self.buttons_y)):
                screen.blit(self.confirmTxt.b,(self.buttons_x2,self.buttons_y))
            else:
                screen.blit(self.confirmTxt.n,(self.buttons_x2,self.buttons_y))
            #判定按钮
            if pygame.mouse.get_pressed()[0]:
                mouse_x,mouse_y=pygame.mouse.get_pos()
                if self.bar_x<=mouse_x<=self.bar_x+self.bar_width:
                    #如果碰到背景音乐的音量条
                    if self.bar_y1-self.bar_height/2<mouse_y<self.bar_y1+self.bar_height*1.5:
                        self.soundVolume_background_music = int(100*(mouse_x-self.bar_x)/self.bar_width)
                    #如果碰到音效的音量条
                    elif self.bar_y2-self.bar_height/2<mouse_y<self.bar_y2+self.bar_height*1.5:
                        self.soundVolume_sound_effects = int(100*(mouse_x-self.bar_x)/self.bar_width)
                    #如果碰到环境声的音量条
                    elif self.bar_y3-self.bar_height/2<mouse_y<self.bar_y3+self.bar_height*1.5:
                        self.soundVolume_sound_environment = int(100*(mouse_x-self.bar_x)/self.bar_width)
                #取消
                if isHoverOn(self.cancelTxt.n,(self.buttons_x1,self.buttons_y)):
                    with open("Save/setting.yaml", "r", encoding='utf-8') as f:
                        settingData = yaml.load(f.read(),Loader=yaml.FullLoader)
                        self.soundVolume_background_music = settingData["Sound"]["background_music"]
                        self.soundVolume_sound_effects = settingData["Sound"]["sound_effects"]
                        self.soundVolume_background_music = settingData["Sound"]["background_music"]
                    self.ifDisplay = False
                #确认
                elif isHoverOn(self.confirmTxt.n,(self.buttons_x2,self.buttons_y)):
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
        return False
