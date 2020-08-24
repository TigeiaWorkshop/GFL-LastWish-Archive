# cython: language_level=3
import Zero3 as Zero

def dialogCreator(chapter_name,screen,setting,part):
    #卸载音乐
    Zero.unloadBackgroundMusic()
    #加载对话
    DIALOG = Zero.DialogSystemDev("Data/main_chapter/{0}_dialogs_{1}.yaml".format(chapter_name,setting['Language']))
    #主循环
    while True:
        if not DIALOG.display(screen):
            Zero.display.flip()
        else:
            break
