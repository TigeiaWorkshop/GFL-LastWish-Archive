# cython: language_level=3
from Source.init import *

def dialogCreator(chapter_name,screen,setting,part):
    #卸载音乐
    Zero.unloadBackgroundMusic()
    #加载对话
    DIALOG = Zero.DialogSystemDev("main_chapter",chapter_name,setting['Language'])
    #主循环
    while True:
        if not DIALOG.display(screen):
            Zero.display.flip()
        else:
            break
