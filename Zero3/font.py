# cython: language_level=3
import pygame
from pygame.locals import *
import pygame.freetype
from Zero3.config import *
pygame.init()

#初始化字体的配置文件
FONT = DATA["Font"]
FONTTYPE = DATA["FontType"]
MODE = DATA["Antialias"]

#获取文字信息
def get_font():
    return FONT
def get_fontType():
    return FONTTYPE
def get_fontMode():
    return MODE
def get_fontDetails():
    return FONT,FONTTYPE,MODE

#重新获取设置信息
def reload_setting():
    global DATA
    global FONT
    global FONTTYPE
    global MODE
    with open("Save/setting.yaml", "r", encoding='utf-8') as f:
        DATA = yaml.load(f.read(),Loader=yaml.FullLoader)
        FONT = DATA["Font"]
        FONTTYPE = DATA["FontType"]
        MODE = DATA["Antialias"]

#创建字体
def createFont(size,ifBold=False,ifItalic=False):
    if FONTTYPE == "default":
        try:
            return pygame.font.SysFont(FONT,int(size),ifBold,ifItalic)
        except BaseException:
            pygame.font.init()
            normal_font = pygame.font.Font("Assets/font/{}.ttf".format(FONT),int(size))
    elif FONTTYPE == "custom":
        try:
            normal_font = pygame.font.Font("Assets/font/{}.ttf".format(FONT),int(size))
        #如果文字没有初始化
        except BaseException:
            pygame.font.init()
            normal_font = pygame.font.Font("Assets/font/{}.ttf".format(FONT),int(size))
        if ifBold:
            normal_font.set_bold(ifBold)
        if ifItalic:
            normal_font.set_italic(ifItalic)
        return normal_font
    else:
        raise Exception('ZeroEngine-Error: FontType option in setting file is incorrect!')

#创建FreeType字体
def createFreeTypeFont(size,ifBold=False,ifItalic=False):
    if FONTTYPE == "default":
        try:
            return pygame.freetype.SysFont(FONT,int(size),ifBold,ifItalic)
        except BaseException:
            pygame.freetype.init()
            return pygame.freetype.SysFont(FONT,int(size),ifBold,ifItalic)
    elif FONTTYPE == "custom":
        try:
            normal_font = pygame.freetype.Font("Assets/font/{}.ttf".format(FONT),int(size))
        #如果文字没有初始化
        except BaseException:
            pygame.freetype.init()
            normal_font = pygame.freetype.Font("Assets/font/{}.ttf".format(FONT),int(size))
        if ifBold:
            normal_font.set_bold(ifBold)
        if ifItalic:
            normal_font.set_italic(ifItalic)
        return normal_font
    else:
        raise Exception('ZeroEngine-Error: FontType option in setting file is incorrect!')

#文字制作模块：接受文字，颜色，文字大小，文字样式，模式，返回制作完的文字
def fontRender(txt,color,size,ifBold=False,ifItalic=False):
    normal_font = createFont(size,ifBold,ifItalic)
    if isinstance(color,str):
        text_out = normal_font.render(txt, MODE, findColorRGB(color))
    else:
        text_out = normal_font.render(txt, MODE, color)
    return text_out

#文字制作模块：接受文字，颜色，文字大小，文字样式，模式，返回制作完的文字
def freeTypeRender(txt,color,size,ifBold=False,ifItalic=False):
    normal_font = createFreeTypeFont(size,ifBold,ifItalic)
    if isinstance(color,str):
        text_out = normal_font.render(txt, MODE, findColorRGB(color))
    else:
        text_out = normal_font.render(txt, MODE, color)
    return text_out

#文字画面类
class TextSurface:
    def __init__(self,n,b,x,y):
        self.n = n
        self.b = b
        self.n_x = x
        self.n_y = y
        self.b_x = x - (self.b.get_width()-self.n.get_width())/2
        self.b_y = y - (self.b.get_height()-self.n.get_height())/2
        self.__ifHover = False
    def display(self,screen):
        mouse_x,mouse_y = pygame.mouse.get_pos()
        if self.n_x<=mouse_x<=self.n_x+self.n.get_width() and self.n_y<=mouse_y<=self.n_y+self.n.get_height():
            screen.blit(self.b,(self.b_x,self.b_y))
            self.__ifHover = True
        else:
            screen.blit(self.n,(self.n_x,self.n_y))
            self.__ifHover = False
        return self.__ifHover
    def ifHover(self):
        return self.__ifHover

#高级文字制作模块：接受文字，颜色，位置，文字大小，文字样式，模式，返回制作完的文字Class，该Class具有一大一普通的字号
def fontRenderPro(txt,color,pos,size=50,ifBold=False,ifItalic=False):
    return TextSurface(fontRender(txt,color,size,ifBold,ifItalic),fontRender(txt,color,size*1.5,ifBold,ifItalic),pos[0],pos[1])

#给定一个颜色的名字，返回对应的RGB列表
def findColorRGB(colorName):
    color_rgb = None
    if colorName == "gray" or colorName == "grey" or colorName == "disable":
        color_rgb = (105, 105, 105)
    elif colorName == "white" or colorName == "enable":
        color_rgb = (255, 255, 255)
    elif colorName == "black":
        color_rgb = (0, 0, 0)
    elif colorName == "green":
        color_rgb = (0, 255, 0)
    elif colorName == "red":
        color_rgb = (255, 0, 0)
    return color_rgb