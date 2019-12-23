from Zero2_tool.mainMenu import *

#加载设置
with open("Data/setting.yaml", "r", encoding='utf-8') as f:
        setting = yaml.load(f.read(),Loader=yaml.FullLoader)
        window_x = setting['Screen_size_x']
        window_y =  setting['Screen_size_y']
        lang = setting['Language']

#mainMenu(window_x,window_y,lang)


# 创建窗口
import pygame
pygame.init()
text_title ="test"
screen = pygame.display.set_mode([window_x, window_y])
pygame.display.set_caption(text_title) #窗口标题
dialog_display_function("chapter1",window_x,window_y,screen,lang,id="")
