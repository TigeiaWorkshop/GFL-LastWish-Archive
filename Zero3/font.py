# cython: language_level=3
import pygame
import yaml
from pygame.locals import *

#字体
with open("Save/setting.yaml", "r", encoding='utf-8') as f:
    DATA = yaml.load(f.read(),Loader=yaml.FullLoader)
    FONT = DATA["Font"]
    FONTTYPE = DATA["FontType"]
    MODE = DATA["Antialias"]

def get_mode():
    return MODE

#创建字体
def createFont(size,ifBold=False,ifItalic=False):
    if FONTTYPE == "default":
        return pygame.font.SysFont(FONT,int(size),ifBold,ifItalic)
    elif FONTTYPE == "custom":
        normal_font = pygame.font.Font("Assets/font/{}.ttf".format(FONT),int(size))
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


#高级文字制作模块：接受文字，颜色，文字大小，文字样式，模式，返回制作完的文字Class，该Class具有一大一普通的字号
def fontRenderPro(txt,color,size=50,ifBold=False,ifItalic=False):
    class TextSurface:
        def __init__(self, n, b):
            self.n = n
            self.b = b
    #文字设定
    normal_font = createFont(size,ifBold,ifItalic)
    big_font = createFont(int(size*1.5),ifBold,ifItalic)
    if isinstance(color,str):
        color = findColorRGB(color)
        text_out = TextSurface(normal_font.render(txt, MODE, color),big_font.render(txt, MODE, color))
    else:
        text_out = TextSurface(normal_font.render(txt, MODE, color),big_font.render(txt, MODE, color))
    return text_out

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