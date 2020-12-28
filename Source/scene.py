# cython: language_level=3
import Zero3 as Zero

def scene(chapterType,chapterId,screen,startPoint,dialogId,dialog_options,collectionName=None):
    if startPoint == "dialog_before_battle":
        dialog(chapterType,chapterId,screen,"dialog_before_battle",dialogId,dialog_options)
        if Zero.pause_menu.checkIfBackToMainMenu() == False:
            battle(chapterType,chapterId,screen)
        else:
            return
        if Zero.pause_menu.checkIfBackToMainMenu() == False:
            dialog(chapterType,chapterId,screen,"dialog_after_battle")
    elif startPoint == "battle":
        battle(chapterType,None,screen)
        if Zero.pause_menu.checkIfBackToMainMenu() == False:
            dialog(chapterType,chapterId,screen,"dialog_after_battle")
    elif startPoint == "dialog_after_battle":
        dialog(chapterType,chapterId,screen,"dialog_after_battle",dialogId,dialog_options)

#对话系统
def dialog(chapterType,chapterId,screen,part,dialogId="head",dialog_options={}):
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
    DIALOG = Zero.DialogSystem(chapterType,chapterId,part,dialogId,dialog_options)
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

#战斗系统
def battle(chapterType,chapterId,screen):
    #卸载音乐
    Zero.unloadBackgroundMusic()
    BATTLE = Zero.BattleSystem(chapterType,chapterId)
    if chapterId != None:
        BATTLE.initialize(screen)
    else:
        BATTLE.load(screen)
    #战斗系统主要loop
    while BATTLE.isPlaying == True:
        BATTLE.display(screen)
    #暂停声效 - 尤其是环境声
    Zero.unloadBackgroundMusic()
    return BATTLE.resultInfo

#对话编辑器
def dialogCreator(chapterType,chapterId,screen,part,collectionName=None):
    #卸载音乐
    Zero.unloadBackgroundMusic()
    #加载对话
    DIALOG = Zero.DialogSystemDev(chapterType,chapterId,part,collectionName)
    #主循环
    while True:
        if not DIALOG.display(screen):
            Zero.display.flip()
        else:
            break

#地图编辑器
def mapCreator(chapterType,chapterId,screen,collectionName=None):
    #卸载音乐
    Zero.unloadBackgroundMusic()
    MAPCREATOR = Zero.mapCreator(chapterType,chapterId,collectionName)
    MAPCREATOR.initialize(screen)
    #战斗系统主要loop
    while MAPCREATOR.isPlaying == True:
        MAPCREATOR.display(screen)
    #暂停声效 - 尤其是环境声
    Zero.unloadBackgroundMusic()

#blit载入页面
def dispaly_loading_screen(screen,start,end,value):
    window_x,window_y = screen.get_size()
    #获取健康游戏忠告
    HealthyGamingAdvice = Zero.get_lang("HealthyGamingAdvice")
    if HealthyGamingAdvice == None:
        HealthyGamingAdvice = []
    else:
        for i in range(len(HealthyGamingAdvice)):
            HealthyGamingAdvice[i] = Zero.fontRender(HealthyGamingAdvice[i],"white",window_x/64)
    #其他载入页面需要的数据
    text1 = Zero.fontRender(Zero.get_lang("title1"),"white",window_x/64)
    text2 = Zero.fontRender(Zero.get_lang("title2"),"white",window_x/64)
    #主循环
    for i in range(start,end,value):
        screen.fill(Zero.findColorRGBA("black"))
        text1.set_alpha(i)
        Zero.drawImg(text1,(window_x/64,window_y*0.9),screen)
        text2.set_alpha(i)
        Zero.drawImg(text2,(window_x/64,window_y*0.9-window_x/32),screen)
        for a in range(len(HealthyGamingAdvice)):
            HealthyGamingAdvice[a].set_alpha(i)
            Zero.drawImg(HealthyGamingAdvice[a],(window_x-window_x/32-HealthyGamingAdvice[a].get_width(),window_y*0.9-window_x/64*a*1.5),screen)
        Zero.display.flip(True)