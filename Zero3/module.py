# cython: language_level=3
import glob
import math
import os
import random
from sys import exit
import threading
import platform
from Zero3.font import *
import time

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
    def get_width(self):
        return self.width
    def get_height(self):
        return self.height
    def rotate(self,angle):
        self.img = pygame.transform.rotate(self.img,angle)
    def flip(self,vertical=False,horizontal=False):
        self.img = pygame.transform.flip(self.img,vertical,horizontal)

#需要移动的动态图片
class DynamicImageSurface(ImageSurface):
    def __init__(self,img,x,y,target_x,target_y,moveSpeed_x,moveSpeed_y,width=None,height=None,description="Default"):
        ImageSurface.__init__(self,img,x,y,width,height,description)
        self.default_x = x
        self.default_y = y
        self.target_x = target_x
        self.target_y = target_y
        self.moveSpeed_x = moveSpeed_x
        self.moveSpeed_y = moveSpeed_y
        self.__towardTargetPos = False
    def draw(self,screen,local_x=0,local_y=0):
        super().draw(screen,local_x,local_y)
        if self.__towardTargetPos == True:
            if self.default_x < self.target_x and self.x < self.target_x:
                self.x += self.moveSpeed_x
            elif self.default_x > self.target_x and self.x > self.target_x:
                self.x -= self.moveSpeed_x
            if self.default_y < self.target_y and self.y < self.target_y:
                self.y += self.moveSpeed_y
            elif self.default_y > self.target_y and self.y > self.target_y:
                self.y -= self.moveSpeed_y
        else:
            if self.default_x < self.target_x and self.x > self.default_x:
                self.x -= self.moveSpeed_x
            elif self.default_x > self.target_x and self.x < self.default_x:
                self.x += self.moveSpeed_x
            if self.default_y < self.target_y and self.y > self.default_y:
                self.y -= self.moveSpeed_y
            elif self.default_y > self.target_y and self.y < self.default_y:
                self.y += self.moveSpeed_y
    def switch(self):
        self.__towardTargetPos = not self.__towardTargetPos
    def ifToward(self):
        return self.__towardTargetPos

#画面更新控制器
class DisplayController:
    def __init__(self,fps):
        self.fps = fps
        self.__clock = pygame.time.Clock()
    def flip(self,pump=False):
        self.__clock.tick(self.fps)
        controller.display()
        if pump == True:
            pygame.event.pump()
        pygame.display.flip()
    def update(self,rectangle=None,pump=False):
        self.__clock.tick(self.fps)
        controller.display()
        if pump == True:
            pygame.event.pump()
        if rectangle == None:
            pygame.display.flip()
        else:
            pygame.display.update(rectangle)
    def set_caption(self,title):
        pygame.display.set_caption(title)
    def get_size(self):
        return get_setting("Screen_size_x"),get_setting("Screen_size_y")
    def quit(self):
        #退出游戏
        exit()

#帧率控制器
display = DisplayController(get_setting("FPS"))

#射击音效 -- 频道2
class AttackingSoundManager:
    def __init__(self,channel,volume):
        self.__soundsData = {
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
        self.__channel = channel
        self.volume = volume
        for key in self.__soundsData:
            for i in range(len(self.__soundsData[key])):
                self.__soundsData[key][i] = pygame.mixer.Sound(self.__soundsData[key][i])
                self.__soundsData[key][i].set_volume(volume/100.0)
    def play(self,kind):
        if kind in self.__soundsData:
            pygame.mixer.Channel(self.__channel).play(self.__soundsData[kind][random.randint(0,len(self.__soundsData[kind])-1)])

#环境系统
class WeatherSystem:
    def  __init__(self,weather,window_x,window_y):
        self.name = 0
        self.img_list = []
        for imgPath in glob.glob("Assets/image/environment/"+weather+"/*.png"):
            self.img_list.append(pygame.image.load(os.path.join(imgPath)).convert_alpha())
        self.ImgObject = []
        for i in range(50):
            imgId = random.randint(0,len(self.img_list)-1)
            img_size = random.randint(5,10)
            img_speed = random.randint(1,3)
            img_x = random.randint(1,window_x*1.5)
            img_y = random.randint(1,window_y)
            self.ImgObject.append(Snow(imgId,img_size,img_speed,img_x,img_y))
    def display(self,screen,perBlockWidth,perBlockHeight,local_x=0,local_y=0):
        speed_unit = perBlockWidth/5
        for i in range(len(self.ImgObject)):
            if 0<=self.ImgObject[i].x<=screen.get_width() and 0<=self.ImgObject[i].y+local_y<=screen.get_height():
                imgTemp = pygame.transform.scale(self.img_list[self.ImgObject[i].imgId], (round(perBlockWidth/self.ImgObject[i].size), round(perBlockWidth/self.ImgObject[i].size)))
                screen.blit(imgTemp,(self.ImgObject[i].x,self.ImgObject[i].y+local_y))
            self.ImgObject[i].x -= self.ImgObject[i].speed*speed_unit
            self.ImgObject[i].y += self.ImgObject[i].speed*speed_unit
            if self.ImgObject[i].x <= 0 or self.ImgObject[i].y+local_y >= screen.get_height():
                self.ImgObject[i].y = random.randint(-50,0)
                self.ImgObject[i].x = random.randint(0,screen.get_width()*2)

#雪花片
class Snow:
    def  __init__(self,imgId,size,speed,x,y):
        self.imgId = imgId
        self.size = size
        self.speed = speed
        self.x = x
        self.y = y

#设置UI
class SettingContoller:
    def __init__(self,window_x,window_y,settingData,langTxt):
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
        self.soundVolume_background_music = settingData["Sound"]["background_music"]
        self.soundVolume_sound_effects = settingData["Sound"]["sound_effects"]
        self.soundVolume_sound_environment = settingData["Sound"]["sound_environment"]
        #设置UI中的文字
        self.FONTSIZE = round(window_x/50)
        self.fontSizeBig = round(window_x/50*1.5)
        self.normalFont = createFont(self.FONTSIZE)
        self.bigFont = createFont(self.fontSizeBig)
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
        self.buttons_x1 = self.baseImgX + self.baseImgWidth*0.2
        self.buttons_x2 = self.buttons_x1 + self.cancelTxt_n.get_width()*1.7
    def display(self,screen):
        if self.ifDisplay == True:
            #底部图
            screen.blit(self.baseImg,(self.baseImgX,self.baseImgY))
            screen.blit(self.settingTitleTxt,(self.settingTitleTxt_x,self.settingTitleTxt_y))
            #语言
            screen.blit(self.languageTxt,(self.bar_x,self.bar_y0))
            #背景音乐
            screen.blit(self.normalFont.render(self.backgroundMusicTxt+": "+str(self.soundVolume_background_music),True,(255, 255, 255)),(self.bar_x,self.bar_y1-self.FONTSIZE*1.4))
            screen.blit(self.bar_empty,(self.bar_x,self.bar_y1))
            barImgWidth = round(self.bar_full.get_width()*self.soundVolume_background_music/100)
            screen.blit(pygame.transform.scale(self.bar_full,(barImgWidth,self.bar_height)),(self.bar_x,self.bar_y1))
            screen.blit(self.button,(self.bar_x+barImgWidth-self.button.get_width()/2,self.bar_y1-self.bar_height/2))
            #音效
            screen.blit(self.normalFont.render(self.soundEffectsTxt+": "+str(self.soundVolume_sound_effects),True,(255, 255, 255)),(self.bar_x,self.bar_y2-self.FONTSIZE*1.4))
            screen.blit(self.bar_empty,(self.bar_x,self.bar_y2))
            barImgWidth = round(self.bar_full.get_width()*self.soundVolume_sound_effects/100)
            screen.blit(pygame.transform.scale(self.bar_full,(barImgWidth,self.bar_height)),(self.bar_x,self.bar_y2))
            screen.blit(self.button,(self.bar_x+barImgWidth-self.button.get_width()/2,self.bar_y2-self.bar_height/2))
            #环境声
            screen.blit(self.normalFont.render(self.soundEnvironmentTxt+": "+str(self.soundVolume_sound_environment),True,(255, 255, 255)),(self.bar_x,self.bar_y3-self.FONTSIZE*1.4))
            screen.blit(self.bar_empty,(self.bar_x,self.bar_y3))
            barImgWidth = round(self.bar_full.get_width()*self.soundVolume_sound_environment/100)
            screen.blit(pygame.transform.scale(self.bar_full,(barImgWidth,self.bar_height)),(self.bar_x,self.bar_y3))
            screen.blit(self.button,(self.bar_x+barImgWidth-self.button.get_width()/2,self.bar_y3-self.bar_height/2))
            #获取鼠标坐标
            mouse_x,mouse_y=pygame.mouse.get_pos()
            #取消按钮
            if self.buttons_x1<mouse_x<self.buttons_x1+self.cancelTxt_n.get_width() and self.buttons_y<mouse_y<self.buttons_y+self.cancelTxt_n.get_height():
                screen.blit(self.cancelTxt_b,(self.buttons_x1,self.buttons_y))
                if controller.get_event() == "comfirm":
                    with open("Save/setting.yaml", "r", encoding='utf-8') as f:
                        settingData = yaml.load(f.read(),Loader=yaml.FullLoader)
                        self.soundVolume_background_music = settingData["Sound"]["background_music"]
                        self.soundVolume_sound_effects = settingData["Sound"]["sound_effects"]
                        self.soundVolume_sound_environment = settingData["Sound"]["sound_environment"]
                    self.ifDisplay = False
            else:
                screen.blit(self.cancelTxt_n,(self.buttons_x1,self.buttons_y))
            #确认按钮
            if self.buttons_x2<mouse_x<self.buttons_x2+self.confirmTxt_n.get_width() and self.buttons_y<mouse_y<self.buttons_y+self.confirmTxt_n.get_height():
                screen.blit(self.confirmTxt_b,(self.buttons_x2,self.buttons_y))
                if controller.get_event() == "comfirm":
                    with open("Save/setting.yaml", "r", encoding='utf-8') as f:
                        settingData = yaml.load(f.read(),Loader=yaml.FullLoader)
                        settingData["Sound"]["background_music"] = self.soundVolume_background_music
                        settingData["Sound"]["sound_effects"] = self.soundVolume_sound_effects
                        settingData["Sound"]["sound_environment"] = self.soundVolume_sound_environment
                    with open("Save/setting.yaml", "w", encoding='utf-8') as f:
                        yaml.dump(settingData, f)
                    pygame.mixer.music.set_volume(settingData["Sound"]["background_music"]/100.0)
                    self.ifDisplay = False
                    return True
            else:
                screen.blit(self.confirmTxt_n,(self.buttons_x2,self.buttons_y))
            #其他按键的判定按钮
            if controller.get_event() == "comfirm":
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
        self.FONT = createFont(fontSize)
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

class ButtonWithDes(Button):
    def __init__(self,path,x,y,width,height,des):
        Button.__init__(self,path,x,y)
        self.img2 = self.img.copy()
        self.img.set_alpha(150)
        self.width = width
        self.height = height
        self.des = des
        self.des_font_surface = fontRender(des,"black",self.height*0.8)
        self.des_surface = pygame.Surface((self.des_font_surface.get_width()*1.2,self.height),flags=pygame.SRCALPHA).convert_alpha()
        pygame.draw.rect(self.des_surface,(255,255,255),(0,0, self.des_surface.get_width(),self.des_surface.get_height()))
        self.des_surface.blit(self.des_font_surface,(self.des_font_surface.get_width()*0.1,0))
    def displayDes(self,screen):
        if self.hoverEventTriggered == True:
            screen.blit(self.des_surface,pygame.mouse.get_pos())

#输入管理组件
class GameController:
    def __init__(self,mouse_icon_width,speed,custom=False):
        self.joystick = Joystick()
        if custom == True:
            pygame.mouse.set_visible(False)
            self.iconImg = pygame.transform.scale(pygame.image.load(os.path.join("Assets/image/UI/","mouse_icon.png")).convert_alpha(),(int(mouse_icon_width),int(mouse_icon_width*1.3)))
        else:
            self.iconImg = None
        self.mouse_x,self.mouse_y = pygame.mouse.get_pos()
        self.movingSpeed = speed
    def display(self,screen=None):
        self.mouse_x,self.mouse_y = pygame.mouse.get_pos()
        if self.joystick.inputController != None:
            if self.joystick.get_axis(0)>0.1 or self.joystick.get_axis(0)<-0.1:
                self.mouse_x += int(self.movingSpeed*round(self.joystick.get_axis(0),1))
            if self.joystick.get_axis(1)>0.1 or self.joystick.get_axis(1)<-0.1:
                self.mouse_y += int(self.movingSpeed*round(self.joystick.get_axis(1),1))
            pygame.mouse.set_pos((self.mouse_x,self.mouse_y))
        if self.iconImg != None and screen != None:
            screen.blit(self.iconImg,(self.mouse_x,self.mouse_y))
    def get_event(self,pygame_events=None):
        if pygame_events == None:
            pygame_events = pygame.event.get()
        for event in pygame_events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 or event.type == pygame.JOYBUTTONDOWN and self.joystick.get_button(0) == 1:
                return "comfirm"
        return None
    def get_pos(self):
        return self.mouse_x,self.mouse_y

#手柄控制组件
class Joystick:
    def __init__(self):
        if pygame.joystick.get_init() == False:
            pygame.joystick.init()
        if pygame.joystick.get_count()>0:
            self.inputController = pygame.joystick.Joystick(0)
            self.inputController.init()
        else:
            self.inputController = None
            pygame.joystick.quit()
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

#控制器输入组件初始化
controller = GameController(get_setting("MouseIconWidth"),get_setting("MouseMoveSpeed"))

#对话框基础模块
class DialogInterface:
    def __init__(self,img,fontSize):
        self.dialoguebox = img
        self.FONTSIZE = int(fontSize)
        self.FONT = createFont(self.FONTSIZE)
        self.content = []
        self.narrator = None
        self.textIndex = None
        self.displayedLine = None
    def update(self,txt,narrator):
        self.textIndex = 0
        self.displayedLine = 0
        self.content = txt
        self.narrator = narrator

#对话框和对话框内容
class DialogBox(DialogInterface):
    def __init__(self,imgPath,width,height,x,y,fontSize):
        DialogInterface.__init__(self,pygame.transform.scale(pygame.image.load(os.path.join(imgPath)).convert_alpha(),(int(width),int(height))),fontSize)
        self.__surface = None
        self.x = x
        self.y = y
        self.deafult_x = x
        self.deafult_y = y
        self.txt_x = fontSize
        self.txt_y = fontSize*2
        self.narrator_icon = None
        self.narrator_x = fontSize*3
        self.narrator_y = fontSize/2
        self.updated = False
        self.drew = False
        self.__flipped = False
    def get_width(self):
        return self.dialoguebox.get_width()
    def get_height(self):
        return self.dialoguebox.get_height()
    def set_size(self,width,height):
        self.dialoguebox = pygame.transform.scale(self.dialoguebox,(int(width),int(height)))
    def display(self,screen,characterInfoBoardUI=None):
        if self.drew == False:
            self.__surface = self.dialoguebox.copy()
            if self.__flipped == True:
                #讲述人名称
                if self.narrator != None:
                    self.__surface.blit(self.FONT.render(self.narrator,get_fontMode(),(255,255,255)),(self.get_width()*0.6+self.narrator_x,self.narrator_y))
                #角色图标
                if self.narrator_icon != None and characterInfoBoardUI != None:
                    img = characterInfoBoardUI.characterIconImages[self.narrator_icon]
                    self.__surface.blit(img,(self.get_width()-self.txt_x,self.txt_y))
                x = self.txt_x
            else:
                #讲述人名称
                if self.narrator != None:
                    self.__surface.blit(self.FONT.render(self.narrator,get_fontMode(),(255,255,255)),(self.narrator_x,self.narrator_y))
                #角色图标
                if self.narrator_icon != None and characterInfoBoardUI != None:
                    img = characterInfoBoardUI.characterIconImages[self.narrator_icon]
                    self.__surface.blit(img,(self.txt_x,self.txt_y))
                    x = self.txt_x+img.get_width() + self.FONTSIZE
                else:
                    x = self.txt_x
            y = self.txt_y
            #已经播放的行
            for i in range(self.displayedLine):
                self.__surface.blit(self.FONT.render(self.content[i],get_fontMode(),(255,255,255)),(x,y))
                y += self.FONTSIZE*1.2
            #正在播放的行
            content = self.FONT.render(self.content[self.displayedLine][:self.textIndex],get_fontMode(),(255,255,255))
            self.__surface.blit(content,(x,y))
            if self.textIndex < len(self.content[self.displayedLine]):
                self.textIndex += 1
            elif self.displayedLine < len(self.content)-1:
                self.displayedLine += 1
                self.textIndex = 0
            elif self.textIndex >= len(self.content[self.displayedLine]):
                self.drew = True
        screen.blit(self.__surface,(self.x,self.y))
    def update(self,txt,narrator,narrator_icon=None):
        super().update(txt,narrator)
        self.updated = True
        self.drew = False
        self.narrator_icon = narrator_icon
    def reset_pos(self):
        self.x = self.deafult_x
        self.y = self.deafult_y
    def flip(self):
        self.dialoguebox = pygame.transform.flip(self.dialoguebox,True,False)
        self.__flipped = not self.__flipped

#文字输入框
class InputBox:
    def __init__(self,x,y,default_width=150):
        self.FONTSIZE = 32
        self.FONT = createFont(self.FONTSIZE)
        self.default_width = default_width
        self.input_box = pygame.Rect(x, y, default_width, self.FONTSIZE*1.5)
        self.color_inactive = pygame.Color('lightskyblue3')
        self.color_active = pygame.Color('dodgerblue2')
        self.color = self.color_inactive
        self.active = False
        self.hidden = True
        self.text = ""
        self.__holder = self.FONT.render("|",get_fontMode(),self.color_active)
        self.x = x
        self.y = y
        self.removingTxt = False
    def get_width(self):
        return self.input_box.w
    def get_height(self):
        return self.input_box.h
    def set_width(self,width):
        self.default_width = width
        self.input_box.w = width
    def set_height(self,height):
        self.input_box.h = height
    def set_pos(self,x,y):
        self.x = x
        self.y = y
        self.input_box = pygame.Rect(x, y, self.default_width, self.FONTSIZE*1.5)
    def display(self,screen,pygame_events=None):
        if pygame_events == None:
            pygame_events = pygame.event.get()
        anyKeyDown = False
        for event in pygame_events:
            if event.type == pygame.KEYDOWN:
                anyKeyDown = True
                if event.key == pygame.K_BACKSPACE:
                    self.removingTxt = True
            if event.type == pygame.KEYUP and event.key == pygame.K_BACKSPACE:
                self.removingTxt = False
        #是否删除最后一个字符（按了BACKSPACE）
        if self.removingTxt == True:
            self.text = self.text[:-1]
        txt_surface = self.FONT.render(self.text,get_fontMode(),self.color)
        # Resize the box if the text is too long.
        width = max(self.default_width, txt_surface.get_width()+self.FONTSIZE/2)
        self.input_box.w = width
        # 画出文字
        screen.blit(txt_surface, (self.x+5, self.y))
        # 画出输入框
        pygame.draw.rect(screen, self.color, self.input_box, 2)
        if int(time.time()%2)==0 or anyKeyDown == True:
            screen.blit(self.__holder, (self.x+5+txt_surface.get_width(), self.y))

#控制台
class Console(InputBox):
    def __init__(self,x,y,default_width=150):
        InputBox.__init__(self,x,y,default_width)
        self.events = {}
        self.txtOutput = []
        self.textHistory = []
        self.backwordID = 1
    def get_events(self,key=None):
        if key==None:
            return self.events
        elif key!=None and key in self.events:
            return self.events[key]
        else:
            return None
    def display(self,screen,pygame_events=None):
        if pygame_events == None:
            pygame_events = pygame.event.get()
        if self.hidden == True:
            for event in pygame_events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_BACKQUOTE:
                    self.hidden = False
                    break
        elif self.hidden == False:
            for event in pygame_events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x,mouse_y = pygame.mouse.get_pos()
                    if self.x <= mouse_x <= self.x+self.input_box.w and self.y <= mouse_y <= self.y+self.input_box.h:
                        self.active = not self.active
                        # Change the current color of the input box.
                        self.color = self.color_active if self.active else self.color_inactive
                    else:
                        self.active = False
                        self.color = self.color_inactive
                elif event.type == pygame.KEYDOWN:
                    if self.active:
                        if event.key == pygame.K_RETURN:
                            if self.text[0]=="/":
                                if self.text == "/cheat on":
                                    self.events["cheat"] = True
                                    self.txtOutput.append("Cheat mode activated")
                                elif self.text == "/cheat off":
                                    self.events["cheat"] = False
                                    self.txtOutput.append("Cheat mode deactivated")
                                elif self.text[:5] == "/say ":
                                    self.txtOutput.append(self.text[5:])
                                elif self.text == "/dev on":
                                    self.txtOutput.append("Development mode activated")
                                    self.events["dev"] = True
                                elif self.text == "/dev off":
                                    self.txtOutput.append("Development mode deactivated")
                                    self.events["dev"] = False
                                else:
                                    self.txtOutput.append("Unknown command")
                            else:
                                self.txtOutput.append(self.text)
                            self.textHistory.append(self.text)
                            self.text = ""
                            self.backwordID = 1
                        elif event.key == pygame.K_UP and self.backwordID<len(self.textHistory):
                            self.backwordID += 1
                            self.text = self.textHistory[len(self.textHistory)-self.backwordID]
                        elif event.key == pygame.K_DOWN and self.backwordID>1:
                            self.backwordID -= 1
                            self.text = self.textHistory[len(self.textHistory)-self.backwordID]
                        elif event.key == pygame.K_ESCAPE:
                            self.active = not self.active
                            # Change the current color of the input box.
                            self.color = self.color_active if self.active else self.color_inactive
                        else:
                            self.text += event.unicode
                    else:
                        if event.key == pygame.K_BACKQUOTE or event.key == pygame.K_ESCAPE:
                            self.hidden = True
                            self.text = ""
            #画出输出信息
            for i in range(len(self.txtOutput)):
                screen.blit(self.FONT.render(self.txtOutput[i],get_fontMode(),self.color),(self.x+5, self.y-(len(self.txtOutput)-i)*self.FONTSIZE*1.5))
            super().display(screen,pygame_events)
