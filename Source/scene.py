# cython: language_level=3
import Zero3 as Zero

def scene(chapterType,chapterName,screen,startPoint="dialog_before_battle",dialogId="head",dialog_options={}):
    if startPoint == "dialog_before_battle":
        dialog(chapterType,chapterName,screen,"dialog_before_battle",dialogId,dialog_options)
        if Zero.pause_menu.checkIfBackToMainMenu() == False:
            battle(chapterType,chapterName,screen)
        else:
            return
        if Zero.pause_menu.checkIfBackToMainMenu() == False:
            dialog(chapterType,chapterName,screen,"dialog_after_battle")
    elif startPoint == "battle":
        battle(chapterType,None,screen)
        if Zero.pause_menu.checkIfBackToMainMenu() == False:
            dialog(chapterType,chapterName,screen,"dialog_after_battle")
    elif startPoint == "dialog_after_battle":
        dialog(chapterType,chapterName,screen,"dialog_after_battle",dialogId,dialog_options)

def dialog(chapterType,chapterName,screen,part,dialogId="head",dialog_options={}):
    #加载闸门动画的图片素材
    LoadingImgAbove = Zero.loadImg("Assets/image/UI/LoadingImgAbove.png",screen.get_width()+8,screen.get_height()/1.7)
    LoadingImgBelow = Zero.loadImg("Assets/image/UI/LoadingImgBelow.png",screen.get_width()+8,screen.get_height()/2.05)
    #开始加载-闸门关闭的效果
    for i in range(101):
        Zero.drawImg(LoadingImgAbove,(-4,LoadingImgAbove.get_height()/100*i-LoadingImgAbove.get_height()),screen)
        Zero.drawImg(LoadingImgBelow,(-4,screen.get_height()-LoadingImgBelow.get_height()/100*i),screen)
        Zero.display.flip(True)
    #卸载音乐
    Zero.unloadBackgroundMusic()
    #初始化对话系统模块
    DIALOG = Zero.DialogSystem(chapterType,chapterName,part,dialogId,dialog_options)
    #加载完成-闸门开启的效果
    for i in range(100,-1,-1):
        DIALOG.backgroundContent.display(screen)
        Zero.drawImg(LoadingImgAbove,(-4,LoadingImgAbove.get_height()/100*i-LoadingImgAbove.get_height()),screen)
        Zero.drawImg(LoadingImgBelow,(-4,screen.get_height()-LoadingImgBelow.get_height()/100*i),screen)
        Zero.display.flip(True)
    #背景音乐可以开始播放了
    DIALOG.ready()
    #DIALOG.auto_save = True
    #主循环
    while True:
        if not DIALOG.display(screen):
            Zero.display.flip()
        else:
            break
    #返回玩家做出的选项
    return DIALOG.dialog_options

def dialogCreator(chapterType,chapterName,screen,part):
    #卸载音乐
    Zero.unloadBackgroundMusic()
    #加载对话
    DIALOG = Zero.DialogSystemDev(chapterType,chapterName,part)
    #主循环
    while True:
        if not DIALOG.display(screen):
            Zero.display.flip()
        else:
            break

def battle(chapterType,chapter_name,screen):
    #卸载音乐
    Zero.unloadBackgroundMusic()
    BATTLE = Zero.BattleSystem(chapterType,chapter_name)
    if chapter_name != None:
        BATTLE.initialize(screen)
    else:
        BATTLE.load(screen)
    #战斗系统主要loop
    while BATTLE.isPlaying == True:
        BATTLE.display(screen)
    #暂停声效 - 尤其是环境声
    Zero.unloadBackgroundMusic()
    return BATTLE.resultInfo

def mapCreator(chapterType,chapter_name,screen):
    #卸载音乐
    Zero.unloadBackgroundMusic()
    MAPCREATOR = Zero.mapCreator(chapterType,chapter_name)
    MAPCREATOR.initialize(screen)
    #战斗系统主要loop
    while MAPCREATOR.isPlaying == True:
        MAPCREATOR.display(screen)
    #暂停声效 - 尤其是环境声
    Zero.unloadBackgroundMusic()