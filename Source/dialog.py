# cython: language_level=3
import Zero3 as Zero

def dialog(chapter_name,screen,setting,part):
    #加载闸门动画的图片素材
    LoadingImgAbove = Zero.loadImg("Assets/image/UI/LoadingImgAbove.png",screen.get_width()+8,screen.get_height()/1.7)
    LoadingImgBelow = Zero.loadImg("Assets/image/UI/LoadingImgBelow.png",screen.get_width()+8,screen.get_height()/2.05)
    #开始加载-闸门关闭的效果
    for i in range(101):
        Zero.drawImg(LoadingImgAbove,(-4,LoadingImgAbove.get_height()/100*i-LoadingImgAbove.get_height()),screen)
        Zero.drawImg(LoadingImgBelow,(-4,screen.get_height()-LoadingImgBelow.get_height()/100*i),screen)
        Zero.inputHolder()
        Zero.display.flip()
    #卸载音乐
    Zero.unloadBackgroundMusic()
    #初始化对话系统模块
    DIALOG = Zero.DialogSystem("Data/main_chapter/{0}_dialogs_{1}.yaml".format(chapter_name,setting['Language']),part)
    #加载完成-闸门开启的效果
    for i in range(100,-1,-1):
        DIALOG.backgroundContent.display(screen)
        Zero.drawImg(LoadingImgAbove,(-4,LoadingImgAbove.get_height()/100*i-LoadingImgAbove.get_height()),screen)
        Zero.drawImg(LoadingImgBelow,(-4,screen.get_height()-LoadingImgBelow.get_height()/100*i),screen)
        Zero.inputHolder()
        Zero.display.flip()
    #背景音乐可以开始播放了
    DIALOG.ready()
    #主循环
    while True:
        if not DIALOG.display(screen):
            Zero.display.flip()
        else:
            break
    #返回玩家做出的选项
    return DIALOG.dialog_options
