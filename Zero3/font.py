# cython: language_level=3
import pygame
from pygame.locals import *
import pygame.freetype
from pygame.colordict import THECOLORS
from Zero3.config import *
pygame.init()

#初始化字体的配置文件
ZERO_FONT = ZERO_DATA["Font"]
ZERO_FONTTYPE = ZERO_DATA["FontType"]
ZERO_MODE = ZERO_DATA["Antialias"]
ZERO_STANDARD_FONTSIZE = None

#获取文字信息
def get_font():
    return ZERO_FONT
def get_fontType():
    return ZERO_FONTTYPE
def get_fontMode():
    return ZERO_MODE
def get_fontDetails():
    return ZERO_FONT,ZERO_FONTTYPE,ZERO_MODE
#设置和获取标准文字大小
def set_standard_font_size(size):
    if isinstance (size,int) and size > 0:
        global ZERO_STANDARD_FONTSIZE
        ZERO_STANDARD_FONTSIZE = size
    else:
        raise Exception('ZeroEngine-Error: Standard font size must be positive interger!')
def get_standard_font_size(size):
    return ZERO_STANDARD_FONTSIZE

#重新获取设置信息
def reload_setting():
    global ZERO_DATA
    global ZERO_FONT
    global ZERO_FONTTYPE
    global ZERO_MODE
    with open("Save/setting.yaml", "r", encoding='utf-8') as f:
        ZERO_DATA = yaml.load(f.read(),Loader=yaml.FullLoader)
        ZERO_FONT = ZERO_DATA["Font"]
        ZERO_FONTTYPE = ZERO_DATA["FontType"]
        ZERO_MODE = ZERO_DATA["Antialias"]

#创建字体
def createFont(size,ifBold=False,ifItalic=False):
    if ZERO_FONTTYPE == "default":
        try:
            return pygame.font.SysFont(ZERO_FONT,int(size),ifBold,ifItalic)
        except BaseException:
            pygame.font.init()
            normal_font = pygame.font.Font("Assets/font/{}.ttf".format(ZERO_FONT),int(size))
    elif ZERO_FONTTYPE == "custom":
        try:
            normal_font = pygame.font.Font("Assets/font/{}.ttf".format(ZERO_FONT),int(size))
        #如果文字没有初始化
        except BaseException:
            pygame.ZERO_FONT.init()
            normal_font = pygame.font.Font("Assets/font/{}.ttf".format(ZERO_FONT),int(size))
        if ifBold:
            normal_font.set_bold(ifBold)
        if ifItalic:
            normal_font.set_italic(ifItalic)
        return normal_font
    else:
        raise Exception('ZeroEngine-Error: FontType option in setting file is incorrect!')

#创建FreeType字体
def createFreeTypeFont(size,ifBold=False,ifItalic=False):
    if ZERO_FONTTYPE == "default":
        try:
            return pygame.freetype.SysFont(ZERO_FONT,int(size),ifBold,ifItalic)
        except BaseException:
            pygame.freetype.init()
            return pygame.freetype.SysFont(ZERO_FONT,int(size),ifBold,ifItalic)
    elif ZERO_FONTTYPE == "custom":
        try:
            normal_font = pygame.freetype.Font("Assets/font/{}.ttf".format(ZERO_FONT),int(size))
        #如果文字没有初始化
        except BaseException:
            pygame.freetype.init()
            normal_font = pygame.freetype.Font("Assets/font/{}.ttf".format(ZERO_FONT),int(size))
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
        text_out = normal_font.render(txt, ZERO_MODE, findColorRGBA(color))
    else:
        text_out = normal_font.render(txt, ZERO_MODE, color)
    return text_out

#文字制作模块：接受文字，颜色，文字大小，文字样式，模式，返回制作完的文字
def freeTypeRender(txt,color,size,ifBold=False,ifItalic=False):
    normal_font = createFreeTypeFont(size,ifBold,ifItalic)
    if isinstance(color,str):
        text_out = normal_font.render(txt, ZERO_MODE, findColorRGBA(color))
    else:
        text_out = normal_font.render(txt, ZERO_MODE, color)
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
    def draw(self,screen):
        self.display(screen)
    def ifHover(self):
        return self.__ifHover
    def get_pos(self):
        return self.n_x,self.n_y

#高级文字制作模块：接受文字，颜色，位置，文字大小，文字样式，模式，返回制作完的文字Class，该Class具有一大一普通的字号
def fontRenderPro(txt,color,pos,size=50,ifBold=False,ifItalic=False):
    return TextSurface(fontRender(txt,color,size,ifBold,ifItalic),fontRender(txt,color,size*1.5,ifBold,ifItalic),pos[0],pos[1])

#给定一个颜色的名字，返回对应的RGB列表
def findColorRGBA(color):
    if isinstance(color,(tuple,list)):
        return color
    elif isinstance(color,(str)):
        if color == "gray" or color == "grey" or color == "disable":
            return (105, 105, 105, 255)
        elif color == "white" or color == "enable":
            return (255, 255, 255, 255)
        else:
            try:
                return THECOLORS[color]
            except BaseException:
                raise Exception('ZeroEngine-Error: This color is currently not available!')
    else:
        raise Exception('ZeroEngine-Error: The color has to be a string, tuple or list!')