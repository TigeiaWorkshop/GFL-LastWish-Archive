# cython: language_level=3
from Zero3.basic import *
from Zero3.characterDataManager import *
from Zero3.map import *

def towerDefense(chapter_name,screen,setting):
    #创建手柄组件
    joystick = Joystick()
    #获取屏幕的尺寸
    window_x,window_y = screen.get_size()
    #卸载音乐
    pygame.mixer.music.unload()
    #帧率控制器
    Display = DisplayController(setting['FPS'])
    #从设置中获取语言文件
    lang = setting['Language']