# cython: language_level=3
from Zero3.basic import *

def dialog(chapter_name,screen,setting,part):
    window_x,window_y = screen.get_size()
    #帧率控制器
    Display = DisplayController(setting['FPS'])
    #加载动画
    LoadingImgAbove = loadImg("Assets/image/UI/LoadingImgAbove.png",window_x+8,window_y/1.7)
    LoadingImgBelow = loadImg("Assets/image/UI/LoadingImgBelow.png",window_x+8,window_y/2.05)

    #开始加载-渐入效果
    for i in range(101):
        drawImg(LoadingImgAbove,(-4,LoadingImgAbove.get_height()/100*i-LoadingImgAbove.get_height()),screen)
        drawImg(LoadingImgBelow,(-4,window_y-LoadingImgBelow.get_height()/100*i),screen)
        Display.flip()
    
    #卸载音乐
    pygame.mixer.music.unload()

    DIALOG = DialogSystem(chapter_name,screen,setting,part)

    #加载完成-淡出效果
    for i in range(100,-1,-1):
        DIALOG.backgroundContent.display(screen)
        drawImg(LoadingImgAbove,(-4,LoadingImgAbove.get_height()/100*i-LoadingImgAbove.get_height()),screen)
        drawImg(LoadingImgBelow,(-4,window_y-LoadingImgBelow.get_height()/100*i),screen)
        Display.flip()
    #音效
    DIALOG.ready()
    if_skip = False
    #主循环
    while if_skip == False:
        if_skip = DIALOG.display(screen,Display)
        Display.flip()

    #返回玩家做出的选项
    return DIALOG.dialog_options
