# cython: language_level=3
import Zero3 as Zero
import pygame

def dialog(chapter_name,screen,setting,part):
    window_x,window_y = screen.get_size()
    #帧率控制器
    Display = Zero.DisplayController(setting['FPS'])
    #加载动画
    LoadingImgAbove = Zero.loadImg("Assets/image/UI/LoadingImgAbove.png",window_x+8,window_y/1.7)
    LoadingImgBelow = Zero.loadImg("Assets/image/UI/LoadingImgBelow.png",window_x+8,window_y/2.05)

    #开始加载-渐入效果
    for i in range(101):
        Zero.drawImg(LoadingImgAbove,(-4,LoadingImgAbove.get_height()/100*i-LoadingImgAbove.get_height()),screen)
        Zero.drawImg(LoadingImgBelow,(-4,window_y-LoadingImgBelow.get_height()/100*i),screen)
        Zero.inputHolder()
        Display.flip()
    
    #卸载音乐
    pygame.mixer.music.unload()
    DIALOG = Zero.DialogSystem("Data/main_chapter/{0}_dialogs_{1}.yaml".format(chapter_name,setting['Language']),part)

    #加载完成-淡出效果
    for i in range(100,-1,-1):
        DIALOG.backgroundContent.display(screen)
        Zero.drawImg(LoadingImgAbove,(-4,LoadingImgAbove.get_height()/100*i-LoadingImgAbove.get_height()),screen)
        Zero.drawImg(LoadingImgBelow,(-4,window_y-LoadingImgBelow.get_height()/100*i),screen)
        Zero.inputHolder()
        Display.flip()
    
    #背景音乐可以开始播放了
    DIALOG.ready()

    #主循环
    while True:
        if not DIALOG.display(screen):
            #按键判定
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        exit()
            Display.flip()
        else:
            break

    #返回玩家做出的选项
    return DIALOG.dialog_options
