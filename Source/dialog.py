# cython: language_level=3
from Zero3.basic import *

def dialog(chapter_name,screen,setting,part):
    #创建手柄组件
    joystick = Joystick()
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

    #从设置中获取语言文件
    lang = setting['Language']
    #读取章节信息
    with open("Data/main_chapter/"+chapter_name+"_dialogs_"+lang+".yaml", "r", encoding='utf-8') as f:
        dialog_content = yaml.load(f.read(),Loader=yaml.FullLoader)[part]
    
    #加载对话的背景图片（注意是jpg）
    all_dialog_bg_file_list = glob.glob(r'Assets/image/dialog_background/*.jpg')
    dialog_bg_img_dic={}
    for i in range(len(all_dialog_bg_file_list)):
        img_name = all_dialog_bg_file_list[i].replace("Assets","").replace("image","").replace("dialog_background","").replace(".jpg","").replace("\\","").replace("/","")
        dialog_bg_img_dic[img_name] = loadImage(all_dialog_bg_file_list[i],(0,0),window_x,window_y)

    #选项栏
    optionBox = loadImg("Assets/image/UI/option.png")
    #跳过按钮
    skip_button = loadImage("Assets/image/UI/skip.png",(window_x*0.92,window_y*0.05),window_x*0.055,window_x*0.025)
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

    videoCapture = None

    #加载npc立绘系统并初始化
    npc_img_dic = NpcImageSystem()
    npc_img_dic.process(None,dialog_content[dialogId]["characters_img"])

    #加载完成-淡出效果
    for i in range(100,-1,-1):
        if dialog_content[dialogId]["background_img"] == None:
            black_bg.draw(screen)
        elif dialog_content[dialogId]["background_img"] in dialog_bg_img_dic:
            dialog_bg_img_dic[dialog_content[dialogId]["background_img"]].draw(screen)
        else:
            if videoCapture == None:
                if os.path.exists("Assets/movie/"+dialog_content[dialogId]["background_img"]) == False:
                    raise Exception('The video file is not exist')
                videoCapture = VideoObject("Assets/movie/"+dialog_content[dialogId]["background_img"],True)
                frames_num = videoCapture.getFrameNum()
            else:
                videoCapture.display(screen)
        drawImg(LoadingImgAbove,(-4,LoadingImgAbove.get_height()/100*i-LoadingImgAbove.get_height()),screen)
        drawImg(LoadingImgBelow,(-4,window_y-LoadingImgBelow.get_height()/100*i),screen)
        Display.flip()
    
    while if_skip == False:
        #音效
        if dialog_content[dialogId]["background_music"] != None:
            try:
                pygame.mixer.music.load("Assets/music/"+dialog_content[dialogId]["background_music"]+".mp3")
            except BaseException:
                pygame.mixer.music.load("Assets/music/"+dialog_content[dialogId]["background_music"]+".ogg")
            pygame.mixer.music.play(loops=9999, start=0.0)
            pygame.mixer.music.set_volume(setting["Sound"]["background_music"]/100.0)
        dialog_is_playing_sound = pygame.mixer.Sound("Assets/sound/ui/dialog_words_playing.ogg")
        dialog_is_playing_sound.set_volume(setting["Sound"]["sound_effects"]/100.0)

        #主循环
        while len(dialog_content)!=0 and if_skip == False:
            #背景
            if dialog_content[dialogId]["background_img"] == None:
                black_bg.draw(screen)
            elif dialog_content[dialogId]["background_img"] in dialog_bg_img_dic:
                dialog_bg_img_dic[dialog_content[dialogId]["background_img"]].draw(screen)
            else:
                if videoCapture == None:
                    if os.path.exists("Assets/movie/"+dialog_content[dialogId]["background_img"]) == False:
                        raise Exception('The video file is not exist')
                    videoCapture = VideoObject("Assets/movie/"+dialog_content[dialogId]["background_img"],True)
                    frames_num = videoCapture.getFrameNum()
                else:
                    videoCapture.display(screen)
            #加载对话人物立绘
            npc_img_dic.display(screen)
            #跳过按钮
            skip_button.draw(screen)
            #显示对话框和对应文字
            dialogPlayResult = dialogTxtSystem.display(screen)
            if dialogPlayResult == True:
                if dialog_content[dialogId]["next_dialog_id"] != None and dialog_content[dialogId]["next_dialog_id"][0] == "option":
                    optionBox_y_base = (window_y*3/4-(len(dialog_content[dialogId]["next_dialog_id"])-1)*2*window_x*0.03)/4
                    for i in range(1,len(dialog_content[dialogId]["next_dialog_id"])):
                        option_txt = fontRender(dialog_content[dialogId]["next_dialog_id"][i][0],"white",window_x*0.025)
                        optionBox_scaled = pygame.transform.scale(optionBox,(int(option_txt.get_width()+window_x*0.05),int(window_x*0.05)))
                        optionBox_x = (window_x-optionBox_scaled.get_width())/2
                        optionBox_y = i*2*window_x*0.03+optionBox_y_base
                        displayWithInCenter(option_txt,optionBox_scaled,optionBox_x,optionBox_y,screen)
                        if pygame.mouse.get_pressed()[0] and isHoverOn(optionBox_scaled,(optionBox_x,optionBox_y)):
                            #下一个dialog的Id
                            theNextDialogId = dialog_content[dialogId]["next_dialog_id"][i][1]
                            if dialog_content[theNextDialogId]["background_img"] != dialog_content[dialogId]["background_img"]:
                                videoCapture = None
                            if dialog_content[theNextDialogId]["background_music"] != None and dialog_content[theNextDialogId]["background_music"] != dialog_content[dialogId]["background_music"]:
                                try:
                                    pygame.mixer.music.load("Assets/music/"+dialog_content[theNextDialogId]["background_music"]+".mp3")
                                except BaseException:
                                    pygame.mixer.music.load("Assets/music/"+dialog_content[theNextDialogId]["background_music"]+".ogg")
                                pygame.mixer.music.play(loops=9999, start=0.0)
                                pygame.mixer.music.set_volume(setting["Sound"]["background_music"]/100.0)
                            elif dialog_content[theNextDialogId]["background_music"] == None:
                                pygame.mixer.music.unload()
                            dialog_options[len(dialog_options)] = i
                            #重设立绘系统
                            npc_img_dic.process(dialog_content[dialogId]["characters_img"],dialog_content[theNextDialogId]["characters_img"])
                            #切换dialogId
                            dialogId = theNextDialogId
                            dialogTxtSystem.updateContent(dialog_content[dialogId]["content"],dialog_content[dialogId]["narrator"])
                            break


            #按键判定
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        Display.quit()
                elif event.type == MOUSEBUTTONDOWN or event.type == pygame.JOYBUTTONDOWN:
                    if pygame.mouse.get_pressed()[0] or joystick.get_button(0) == 1:
                        #如果接来下没有文档了或者玩家按到了跳过按钮
                        if isHover(skip_button) or dialog_content[dialogId]["next_dialog_id"] == None:
                            if_skip = True
                        #如果所有行都没有播出，则播出所有行
                        elif dialogPlayResult == False:
                            dialogTxtSystem.playAll()
                        elif dialog_content[dialogId]["next_dialog_id"][0] == "default":
                            theNextDialogId = dialog_content[dialogId]["next_dialog_id"][1]
                            #如果当前正播放视频但下一幕不是当前视频，则取消视频
                            if dialog_content[theNextDialogId]["background_img"] != dialog_content[dialogId]["background_img"]:
                                videoCapture = None
                            if dialog_content[theNextDialogId]["background_music"] != None and dialog_content[theNextDialogId]["background_music"] != dialog_content[dialogId]["background_music"]:
                                try:
                                    pygame.mixer.music.load("Assets/music/"+dialog_content[theNextDialogId]["background_music"]+".mp3")
                                except BaseException:
                                    pygame.mixer.music.load("Assets/music/"+dialog_content[theNextDialogId]["background_music"]+".ogg")
                                pygame.mixer.music.play(loops=9999, start=0.0)
                                pygame.mixer.music.set_volume(setting["Sound"]["background_music"]/100.0)
                            elif dialog_content[theNextDialogId]["background_music"] == None:
                                pygame.mixer.music.unload()
                            #重设立绘系统
                            npc_img_dic.process(dialog_content[dialogId]["characters_img"],dialog_content[theNextDialogId]["characters_img"])
                            #切换dialogId
                            dialogId = theNextDialogId
                            dialogTxtSystem.updateContent(dialog_content[dialogId]["content"],dialog_content[dialogId]["narrator"])
                        #如果是切换场景
                        elif dialog_content[dialogId]["next_dialog_id"][0] == "changeScene":
                            if_skip = True
                    #返回上一个对话场景（在被允许的情况下）
                    elif pygame.mouse.get_pressed()[2] or joystick.get_button(1) == 1:
                        theNextDialogId = dialog_content[dialogId]["last_dialog_id"]
                        if theNextDialogId != None:
                            if dialog_content[theNextDialogId]["background_img"] != dialog_content[dialogId]["background_img"]:
                                videoCapture = None
                            if dialog_content[theNextDialogId]["background_music"] != None and dialog_content[theNextDialogId]["background_music"] != dialog_content[dialogId]["background_music"]:
                                try:
                                    pygame.mixer.music.load("Assets/music/"+dialog_content[theNextDialogId]["background_music"]+".mp3")
                                except BaseException:
                                    pygame.mixer.music.load("Assets/music/"+dialog_content[theNextDialogId]["background_music"]+".ogg")
                                pygame.mixer.music.play(loops=9999, start=0.0)
                                pygame.mixer.music.set_volume(setting["Sound"]["background_music"]/100.0)
                            elif dialog_content[theNextDialogId]["background_music"] == None:
                                pygame.mixer.music.unload()
                            #重设立绘系统
                            npc_img_dic.process(dialog_content[dialogId]["characters_img"],dialog_content[theNextDialogId]["characters_img"])
                            #切换dialogId
                            dialogId = theNextDialogId
                            dialogTxtSystem.updateContent(dialog_content[dialogId]["content"],dialog_content[dialogId]["narrator"],True)
            Display.flip()
        
        #淡出
        pygame.mixer.music.fadeout(1000)
        for i in range(0,255,5):
            black_bg.set_alpha(i)
            black_bg.draw(screen)
            Display.flip()
        
        #如果是因changeScene跳出
        if dialog_content[dialogId]["next_dialog_id"] != None and dialog_content[dialogId]["next_dialog_id"][0] == "changeScene":
            if_skip = False
            videoCapture = None
            time.sleep(2)
            dialogId = dialog_content[dialogId]["next_dialog_id"][1]
            dialogTxtSystem.resetDialogueboxData()
            dialogTxtSystem.updateContent(dialog_content[dialogId]["content"],dialog_content[dialogId]["narrator"])
            for i in range(255,0,-5):
                if dialog_content[dialogId]["background_img"] == None:
                    black_bg.draw(screen)
                else:
                    if dialog_content[dialogId]["background_img"] in dialog_bg_img_dic:
                        dialog_bg_img_dic[dialog_content[dialogId]["background_img"]].draw(screen)
                    else:
                        if videoCapture == None:
                            if os.path.exists("Assets/movie/"+dialog_content[dialogId]["background_img"]) == False:
                                raise Exception('The video file is not exist')
                            videoCapture = VideoObject("Assets/movie/"+dialog_content[dialogId]["background_img"],True)
                            frames_num = videoCapture.getFrameNum()
                        else:
                            videoCapture.display(screen)
                    black_bg.set_alpha(i)
                    black_bg.draw(screen)
                Display.flip()
            #重设black_bg的alpha值以便下一次使用
            black_bg.set_alpha(255)

    if len(dialog_options) == 0:
        return True
    else:
        return dialog_options
