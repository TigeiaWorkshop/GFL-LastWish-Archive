# cython: language_level=3
from Source.scene import *

def mainMenu(screen):
    #获取屏幕的尺寸
    window_x,window_y = screen.get_size()
    #设置引擎的标准文字大小
    Zero.set_standard_font_size(int(window_x/38),"medium")
    #修改控制台的位置
    Zero.console.set_pos(window_x*0.1,window_y*0.8)
    game_title = Zero.get_lang('GameTitle')
    main_menu_txt = Zero.get_lang('MainMenu')
    chapter_select = Zero.get_lang('Chapter')
    #选项模块
    settingUI = Zero.SettingContoller(window_x,window_y,Zero.get_lang("SettingUI"))
    #健康游戏忠告
    HealthyGamingAdvice = Zero.get_lang("HealthyGamingAdvice")
    if HealthyGamingAdvice == None:
        HealthyGamingAdvice = []
    #当前可用的菜单选项
    enabled_option = ["text0_start","text1_setting","text3_exit","text1_chooseChapter","text4_mapCreator","text5_dialogCreator","text7_back"]
    if os.path.exists("Save/save.yaml"):
        enabled_option.append("text0_continue")
        continueButtonIsOn = True
    else:
        continueButtonIsOn = False
    #加载主菜单页面的文字设置
    txt_location = int(window_x*2/3)
    font_size2 = Zero.get_standard_font_size("medium")*2
    main_menu_txt_start_height0 = (window_y-len(main_menu_txt["menu_0"])*font_size2)/2
    main_menu_txt_start_height1 = (window_y-len(main_menu_txt["menu_1"])*font_size2)/2
    chapter_select_txt_start_height = (window_y-len(chapter_select)*font_size2)/2
    #加载主菜单选择页面的文字
    for text in main_menu_txt:
        for key,txt in main_menu_txt[text].items():
            if key in enabled_option:
                mode = "enable"
            else:
                mode = "disable"
            yTmp = 0
            if text == "menu_0":
                yTmp = main_menu_txt_start_height0
                main_menu_txt_start_height0 += font_size2
            elif text == "menu_1":
                yTmp = main_menu_txt_start_height1
                main_menu_txt_start_height1 += font_size2
            main_menu_txt[text][key] = Zero.fontRenderPro(txt,mode,(txt_location,yTmp),Zero.get_standard_font_size("medium"))
    #加载菜单章节选择页面的文字
    for i in range(len(chapter_select)):
        if i == 0 or i == len(chapter_select)-1:
            mode = "enable"
        else:
            mode = "disable"
        chapter_select[i] = Zero.fontRenderPro(chapter_select[i],mode,(txt_location,chapter_select_txt_start_height),Zero.get_standard_font_size("medium"))
        chapter_select_txt_start_height += font_size2
    #加载完成，删除不需要的数据
    del txt_location,font_size2,main_menu_txt_start_height0,main_menu_txt_start_height1,chapter_select_txt_start_height,enabled_option

    # 创建窗口
    icon_img = Zero.loadImg("Assets/image/UI/icon.png")
    pygame.display.set_icon(icon_img)
    pygame.display.set_caption(game_title) #窗口标题
    
    #加载主菜单背景
    videoCapture = Zero.VedioFrame("Assets/movie/SquadAR.mp4",window_x,window_y,True,True,(3105,935))
    pygame.mixer.music.set_volume(Zero.get_setting("Sound","background_music")/100.0)
    #数值初始化
    cover_alpha = 0
    menu_type = 0
    #关卡选择的封面
    cover_img = Zero.loadImg("Assets/image/covers/chapter1.png",window_x,window_y)
    #音效
    click_button_sound = pygame.mixer.Sound("Assets/sound/ui/main_menu_click_button.ogg")
    click_button_sound.set_volume(Zero.get_setting("Sound","sound_effects")/100.0)
    hover_on_button_sound = pygame.mixer.Sound("Assets/sound/ui/main_menu_hover_on_button.ogg")
    hover_on_button_sound.set_volume(Zero.get_setting("Sound","sound_effects")/100.0)
    hover_sound_play_on = None
    last_hover_sound_play_on = None

    the_black = Zero.get_SingleColorSurface("black")
    t1 = Zero.fontRender(Zero.get_lang("title1"),"white",window_x/64)
    t2 = Zero.fontRender(Zero.get_lang("title2"),"white",window_x/64)
    for i in range(len(HealthyGamingAdvice)):
        HealthyGamingAdvice[i] = Zero.fontRender(HealthyGamingAdvice[i],"white",window_x/64)

    #载入页面 - 渐入渐出
    for i in range(0,250,2):
        the_black.draw(screen)
        t1.set_alpha(i)
        Zero.drawImg(t1,(window_x/64,window_y*0.9),screen)
        t2.set_alpha(i)
        Zero.drawImg(t2,(window_x/64,window_y*0.9-window_x/32),screen)
        for a in range(len(HealthyGamingAdvice)):
            HealthyGamingAdvice[a].set_alpha(i)
            Zero.drawImg(HealthyGamingAdvice[a],(window_x-window_x/32-HealthyGamingAdvice[a].get_width(),window_y*0.9-window_x/64*a*1.5),screen)
        Zero.display.flip(True)
    
    for i in range(250,0,-2):
        the_black.draw(screen)
        t1.set_alpha(i)
        Zero.drawImg(t1,(window_x/64,window_y*0.9),screen)
        t2.set_alpha(i)
        Zero.drawImg(t2,(window_x/64,window_y*0.9-window_x/32),screen)
        for a in range(len(HealthyGamingAdvice)):
            HealthyGamingAdvice[a].set_alpha(i)
            Zero.drawImg(HealthyGamingAdvice[a],(window_x-window_x/32-HealthyGamingAdvice[a].get_width(),window_y*0.9-window_x/64*a*1.5),screen)
        Zero.display.flip(True)

    videoCapture.start()

    # 游戏主循环
    while True:
        #背景图片
        videoCapture.display(screen)
        if menu_type == 2 and Zero.ifHover(chapter_select[0]):
            if cover_alpha < 255:
                cover_alpha+=15
        elif cover_alpha >= 0:
            cover_alpha-=15

        if cover_alpha > 10:
            cover_img.set_alpha(cover_alpha)
            Zero.drawImg(cover_img, (0,0),screen)
        
        #菜单选项
        i=0
        if menu_type == 0:
            for key,text in main_menu_txt["menu_0"].items():
                if text.display(screen):
                    hover_sound_play_on = "0_"+str(i)
                i+=1
        elif menu_type == 1:
            for key,text in main_menu_txt["menu_1"].items():
                if text.display(screen):
                    hover_sound_play_on = "1_"+str(i)
                i+=1
        elif menu_type == 2:
            for text in chapter_select:
                if text.display(screen):
                    hover_sound_play_on = "2_"+str(i)
                i+=1

        if last_hover_sound_play_on != hover_sound_play_on:
            hover_on_button_sound.play()
            last_hover_sound_play_on = hover_sound_play_on

        #展示设置UI
        if settingUI.display(screen) == True:
            click_button_sound.set_volume(settingUI.soundVolume_sound_effects/100.0)
            hover_on_button_sound.set_volume(settingUI.soundVolume_sound_effects/100.0)
        
        events = pygame.event.get()
        #展示控制台
        Zero.console.display(screen,events)

        #判断按键
        if Zero.controller.get_event(events) == "comfirm" and settingUI.ifDisplay != True:
            click_button_sound.play()
            if menu_type == 0:
                if Zero.ifHover(main_menu_txt["menu_0"]["text0_start"]):
                    menu_type = 1
                elif Zero.ifHover(main_menu_txt["menu_0"]["text1_setting"]):
                    settingUI.ifDisplay = True
                elif Zero.ifHover(main_menu_txt["menu_0"]["text2_developer_team"]):
                    pass
                elif Zero.ifHover(main_menu_txt["menu_0"]["text3_exit"]):
                    videoCapture.stop()
                    Zero.display.quit()
            elif menu_type == 1:
                if Zero.ifHover(main_menu_txt["menu_1"]["text0_continue"]):
                    if os.path.exists("Save/save.yaml"):
                        with open("Save/save.yaml", "r", encoding='utf-8') as f:
                            SAVE = yaml.load(f.read(),Loader=yaml.FullLoader)
                        if SAVE["type"] == "battle":
                            SAVE["id"] = "head"
                            SAVE["dialog_options"] = {}
                        videoCapture.stop()
                        scene(SAVE["chapterType"],SAVE["chapterName"],screen,SAVE["type"],SAVE["id"],SAVE["dialog_options"])
                        videoCapture.start()
                        #是否可以继续游戏了（save文件是否被创建）
                        if os.path.exists("Save/save.yaml") and continueButtonIsOn == False:
                            main_menu_txt["menu_1"]["text0_continue"] = Zero.fontRenderPro(Zero.get_lang("MainMenu")["menu_1"]["text0_continue"],"enable",main_menu_txt["menu_1"]["text0_continue"].get_pos(),Zero.get_standard_font_size("medium"))
                            continueButtonIsOn = True
                        elif not os.path.exists("Save/save.yaml") and continueButtonIsOn == True:
                            main_menu_txt["menu_1"]["text0_continue"] = Zero.fontRenderPro(Zero.get_lang("MainMenu")["menu_1"]["text0_continue"],"disable",main_menu_txt["menu_1"]["text0_continue"].get_pos(),Zero.get_standard_font_size("medium"))
                            continueButtonIsOn = False
                    else:
                        #raise Exception('ZeroEngine-Error: The save.yaml is not exist')
                        pass
                if Zero.ifHover(main_menu_txt["menu_1"]["text1_chooseChapter"]):
                    menu_type = 2
                elif Zero.ifHover(main_menu_txt["menu_1"]["text4_mapCreator"]):
                    mapCreator("main_chapter","chapter1",screen)
                elif Zero.ifHover(main_menu_txt["menu_1"]["text5_dialogCreator"]):
                    dialogCreator("main_chapter","chapter1",screen,"dialog_before_battle")
                elif Zero.ifHover(main_menu_txt["menu_1"]["text7_back"]):
                    menu_type = 0
            elif menu_type == 2:
                for i in range(len(chapter_select)):
                    if i == len(chapter_select)-1 and Zero.ifHover(chapter_select[-1]):
                        menu_type = 1
                    #章节选择
                    elif Zero.ifHover(chapter_select[i]) and i==0:
                        videoCapture.stop()
                        scene("main_chapter","chapter"+str(i+1),screen)
                        videoCapture.start()
                        #是否可以继续游戏了（save文件是否被创建）
                        if os.path.exists("Save/save.yaml") and continueButtonIsOn == False:
                            main_menu_txt["menu_1"]["text0_continue"] = Zero.fontRenderPro(Zero.get_lang("MainMenu")["menu_1"]["text0_continue"],"enable",main_menu_txt["menu_1"]["text0_continue"].get_pos(),Zero.get_standard_font_size("medium"))
                            continueButtonIsOn = True
                        elif not os.path.exists("Save/save.yaml") and continueButtonIsOn == True:
                            main_menu_txt["menu_1"]["text0_continue"] = Zero.fontRenderPro(Zero.get_lang("MainMenu")["menu_1"]["text0_continue"],"disable",main_menu_txt["menu_1"]["text0_continue"].get_pos(),Zero.get_standard_font_size("medium"))
                            continueButtonIsOn = False
                        break
        Zero.display.flip()
