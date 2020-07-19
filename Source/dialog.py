# cython: language_level=3
from Zero3.basic import *

def dialog(chapter_name,screen,setting,part):
    #控制器输入组件
    InputController = GameController(screen)
    #获取屏幕的尺寸
    window_x,window_y = screen.get_size()
    #加载动画
    LoadingImgAbove = loadImg("Assets/image/UI/LoadingImgAbove.png",window_x+8,window_y/1.7)
    LoadingImgBelow = loadImg("Assets/image/UI/LoadingImgBelow.png",window_x+8,window_y/2.05)
    #帧率控制器
    Display = DisplayController(setting['FPS'])

    #开始加载-渐入效果
    for i in range(101):
        drawImg(LoadingImgAbove,(-4,LoadingImgAbove.get_height()/100*i-LoadingImgAbove.get_height()),screen)
        drawImg(LoadingImgBelow,(-4,window_y-LoadingImgBelow.get_height()/100*i),screen)
        Display.flip()
    
    #卸载音乐
    pygame.mixer.music.unload()

    #读取章节信息
    with open("Data/main_chapter/{0}_dialogs_{1}.yaml".format(chapter_name,setting['Language']), "r", encoding='utf-8') as f:
        dialog_content = yaml.load(f.read(),Loader=yaml.FullLoader)[part]
        if len(dialog_content)==0:
            raise Exception('Warning: The dialog has no content!')


    #选项栏
    optionBox = loadImg("Assets/image/UI/option.png")
    #UI按钮
    ButtonsMananger = DialogButtons()
    if_skip = False
    #黑色帘幕
    black_bg = loadImage("Assets/image/UI/black.png",(0,0),window_x,window_y)
    #加载对话框系统
    dialogTxtSystem = DialogContent(window_x*0.015)
    #设定初始化
    dialogId = "head"
    #如果dialog_content没有头
    if dialogId not in dialog_content:
        raise Exception('Warning: The dialog must have a head!')
    else:
        dialogTxtSystem.updateContent(dialog_content[dialogId]["content"],dialog_content[dialogId]["narrator"])
    #玩家在对话时做出的选择
    dialog_options = {}

    #加载npc立绘系统并初始化
    npc_img_dic = NpcImageSystem()
    npc_img_dic.process(None,dialog_content[dialogId]["characters_img"])

    #加载对话的背景图片
    backgroundContent = DialogBackground(setting["Sound"]["background_music"])
    backgroundContent.update(dialog_content[dialogId]["background_img"],None)

    #加载完成-淡出效果
    for i in range(100,-1,-1):
        backgroundContent.display(screen)
        drawImg(LoadingImgAbove,(-4,LoadingImgAbove.get_height()/100*i-LoadingImgAbove.get_height()),screen)
        drawImg(LoadingImgBelow,(-4,window_y-LoadingImgBelow.get_height()/100*i),screen)
        Display.flip()
    
    #音效
    backgroundContent.update(dialog_content[dialogId]["background_img"],dialog_content[dialogId]["background_music"])

    #主循环
    while if_skip == False:
        #背景
        backgroundContent.display(screen)
        npc_img_dic.display(screen)
        #按钮
        buttonEvent = ButtonsMananger.display(screen,InputController)
        
        #显示对话框和对应文字
        dialogPlayResult = dialogTxtSystem.display(screen)
        if dialogPlayResult == True:
            if dialog_content[dialogId]["next_dialog_id"] != None and dialog_content[dialogId]["next_dialog_id"][0] == "option":
                #显示选项
                optionBox_y_base = (window_y*3/4-(len(dialog_content[dialogId]["next_dialog_id"])-1)*2*window_x*0.03)/4
                for i in range(1,len(dialog_content[dialogId]["next_dialog_id"])):
                    option_txt = fontRender(dialog_content[dialogId]["next_dialog_id"][i][0],"white",window_x*0.025)
                    optionBox_scaled = pygame.transform.scale(optionBox,(int(option_txt.get_width()+window_x*0.05),int(window_x*0.05)))
                    optionBox_x = (window_x-optionBox_scaled.get_width())/2
                    optionBox_y = i*2*window_x*0.03+optionBox_y_base
                    displayWithInCenter(option_txt,optionBox_scaled,optionBox_x,optionBox_y,screen)
                    if pygame.mouse.get_pressed()[0] and InputController.ifHover(optionBox_scaled,(optionBox_x,optionBox_y)):
                        #下一个dialog的Id
                        theNextDialogId = dialog_content[dialogId]["next_dialog_id"][i][1]
                        #更新背景
                        backgroundContent.update(dialog_content[theNextDialogId]["background_img"],dialog_content[theNextDialogId]["background_music"])
                        #保存选取的选项
                        dialog_options[len(dialog_options)] = i
                        #重设立绘系统
                        npc_img_dic.process(dialog_content[dialogId]["characters_img"],dialog_content[theNextDialogId]["characters_img"])
                        #切换dialogId
                        dialogId = theNextDialogId
                        dialogTxtSystem.updateContent(dialog_content[dialogId]["content"],dialog_content[dialogId]["narrator"])
                        break
        

        #按键判定
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    Display.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.JOYBUTTONDOWN:
                if pygame.mouse.get_pressed()[0] or InputController.joystick.get_button(0) == 1:
                    if buttonEvent == "hide":
                        dialogTxtSystem.hideSwitch()
                    #如果接来下没有文档了或者玩家按到了跳过按钮
                    elif buttonEvent == "skip" or dialog_content[dialogId]["next_dialog_id"] == None:
                        #淡出
                        pygame.mixer.music.fadeout(1000)
                        for i in range(0,255,5):
                            black_bg.set_alpha(i)
                            black_bg.draw(screen)
                            Display.flip()
                        if_skip = True
                    elif buttonEvent == "auto":
                        ButtonsMananger.autoModeSwitch()
                    #如果所有行都没有播出，则播出所有行
                    elif dialogPlayResult == False:
                        dialogTxtSystem.playAll()
                    elif dialog_content[dialogId]["next_dialog_id"][0] == "default":
                        theNextDialogId = dialog_content[dialogId]["next_dialog_id"][1]
                        #更新背景
                        backgroundContent.update(dialog_content[theNextDialogId]["background_img"],dialog_content[theNextDialogId]["background_music"])
                        #重设立绘系统
                        npc_img_dic.process(dialog_content[dialogId]["characters_img"],dialog_content[theNextDialogId]["characters_img"])
                        #切换dialogId
                        dialogId = theNextDialogId
                        dialogTxtSystem.updateContent(dialog_content[dialogId]["content"],dialog_content[dialogId]["narrator"])
                    #如果是切换场景
                    elif dialog_content[dialogId]["next_dialog_id"][0] == "changeScene":
                        #淡出
                        pygame.mixer.music.fadeout(1000)
                        for i in range(0,255,5):
                            black_bg.set_alpha(i)
                            black_bg.draw(screen)
                            Display.flip()
                        time.sleep(2)
                        dialogId = dialog_content[dialogId]["next_dialog_id"][1]
                        dialogTxtSystem.resetDialogueboxData()
                        dialogTxtSystem.updateContent(dialog_content[dialogId]["content"],dialog_content[dialogId]["narrator"])
                        backgroundContent.update(dialog_content[dialogId]["background_img"],None)
                        for i in range(255,0,-5):
                            backgroundContent.display(screen)
                            black_bg.set_alpha(i)
                            black_bg.draw(screen)
                            Display.flip()
                        #重设black_bg的alpha值以便下一次使用
                        black_bg.set_alpha(255)
                        #更新背景（音乐）
                        backgroundContent.update(dialog_content[dialogId]["background_img"],dialog_content[dialogId]["background_music"])
                #返回上一个对话场景（在被允许的情况下）
                elif pygame.mouse.get_pressed()[2] or InputController.joystick.get_button(1) == 1:
                    theNextDialogId = dialog_content[dialogId]["last_dialog_id"]
                    if theNextDialogId != None:
                        #更新背景
                        backgroundContent.update(dialog_content[theNextDialogId]["background_img"],dialog_content[theNextDialogId]["background_music"])
                        #重设立绘系统
                        npc_img_dic.process(dialog_content[dialogId]["characters_img"],dialog_content[theNextDialogId]["characters_img"])
                        #切换dialogId
                        dialogId = theNextDialogId
                        dialogTxtSystem.updateContent(dialog_content[dialogId]["content"],dialog_content[dialogId]["narrator"],True)
        InputController.display(screen)
        Display.flip()

    #返回玩家做出的选项
    return dialog_options
