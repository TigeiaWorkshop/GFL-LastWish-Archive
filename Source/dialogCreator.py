# cython: language_level=3
import Zero3 as Zero
import pygame

def dialogCreator(chapter_name,screen,setting,part):
    window_x,window_y = screen.get_size()
    #帧率控制器
    Display = Zero.DisplayController(setting['FPS'])
    
    #卸载音乐
    pygame.mixer.music.unload()

    DIALOG = Zero.DialogSystem("Data/main_chapter/{0}_dialogs_{1}.yaml".format(chapter_name,setting['Language']),part)
    
    #背景音乐可以开始播放了
    DIALOG.ready()

    #主循环
    while True:
        if not DIALOG.display(screen):
            #按键判定
            for event in Zero.get_events():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        exit()
            Display.flip()
        else:
            break
