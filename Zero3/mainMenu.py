# cython: language_level=3
from Zero3.basic import *
from Zero3.dialog import *
from Zero3.mapCreator import *

def mainMenu(screen,setting):
    #获取屏幕的尺寸
    window_x,window_y = screen.get_size()
    #帧率控制器
    Display = DisplayController(setting['FPS'])
    HealthyGamingAdvice = []
    #从设置中获取语言文件
    lang = setting['Language']

    #加载主菜单文字
    try:
        with open("Lang/"+lang+".yaml", "r", encoding='utf-8') as f:
            loadData = yaml.load(f.read(),Loader=yaml.FullLoader)
    except BaseException:
        raise Exception('Error: Current language is not supported, please check the "setting.yaml" file in Save folder!')
    game_title = loadData['GameTitle']
    main_menu_txt = loadData['MainMenu']
    chapter_select = loadData['Chapter']
    settingUI = settingContoller(window_x,window_y,setting,loadData["SettingUI"])
    if "HealthyGamingAdvice" in loadData:
        HealthyGamingAdvice = loadData["HealthyGamingAdvice"]

    #当前可用的菜单选项
    enabled_option = ["text0_start","text1_setting","text3_exit","text1_chooseChapter","text4_mapCreator","text6_back"]
    #加载主菜单选择页面的文字
    for text in main_menu_txt:
        for key,txt in main_menu_txt[text].items():
            if key in enabled_option:
                main_menu_txt[text][key] = fontRenderPro(txt,"enable",window_x/38)
            else:
                main_menu_txt[text][key] = fontRenderPro(txt,"disable",window_x/38)
    
    #加载菜单章节选择页面的文字
    for i in range(len(chapter_select)):
        if i == 0 or i == len(chapter_select)-1:
            chapter_select[i] = fontRenderPro(chapter_select[i],"enable",window_x/38)
        else:
            chapter_select[i] = fontRenderPro(chapter_select[i],"disable",window_x/38)

    # 创建窗口
    icon_img = loadImg("Assets/image/UI/icon.png")
    pygame.display.set_icon(icon_img)
    pygame.display.set_caption(game_title) #窗口标题
    
    #加载主菜单背景
    videoCapture = VideoObject("Assets/movie/SquadAR.mp4",True,3105,935)
    #数值初始化
    cover_alpha = 0
    menu_type = 0
    txt_location = int(window_x*2/3)
    main_menu_txt_start_height0 = (window_y-len(main_menu_txt["menu_0"])*window_x/38*2)/2
    main_menu_txt_start_height1 = (window_y-len(main_menu_txt["menu_1"])*window_x/38*2)/2
    chapter_select_txt_start_height = (window_y-len(chapter_select)*window_x/38*2)/2
    #关卡选择的封面
    cover_img = loadImg("Assets/image/covers/chapter1.png",window_x,window_y)
    #音效
    click_button_sound = pygame.mixer.Sound("Assets/sound/ui/main_menu_click_button.ogg")
    click_button_sound.set_volume(setting["Sound"]["sound_effects"]/100.0)
    hover_on_button_sound = pygame.mixer.Sound("Assets/sound/ui/main_menu_hover_on_button.ogg")
    hover_on_button_sound.set_volume(setting["Sound"]["sound_effects"]/100.0)
    hover_sound_play_on = None
    last_hover_sound_play_on = None

    the_black = loadImage("Assets/image/UI/black.png",(0,0),window_x,window_y)
    t1 = fontRender("缇吉娅工坊 呈现","white",window_x/64)
    t2 = fontRender("警告：所有内容仍处于研发阶段，不代表最终效果","white",window_x/64)
    for i in range(len(HealthyGamingAdvice)):
        HealthyGamingAdvice[i] = fontRender(HealthyGamingAdvice[i],"white",window_x/64)

    #载入页面 - 渐入渐出
    for i in range(0,250,2):
        the_black.draw(screen)
        t1.set_alpha(i)
        drawImg(t1,(window_x/64,window_y*0.9),screen)
        t2.set_alpha(i)
        drawImg(t2,(window_x/64,window_y*0.9-window_x/32),screen)
        for a in range(len(HealthyGamingAdvice)):
            HealthyGamingAdvice[a].set_alpha(i)
            drawImg(HealthyGamingAdvice[a],(window_x-window_x/32-HealthyGamingAdvice[a].get_width(),window_y*0.9-window_x/64*a*1.5),screen)
        Display.flip()
    
    for i in range(250,0,-2):
        the_black.draw(screen)
        t1.set_alpha(i)
        drawImg(t1,(window_x/64,window_y*0.9),screen)
        t2.set_alpha(i)
        drawImg(t2,(window_x/64,window_y*0.9-window_x/32),screen)
        for a in range(len(HealthyGamingAdvice)):
            HealthyGamingAdvice[a].set_alpha(i)
            drawImg(HealthyGamingAdvice[a],(window_x-window_x/32-HealthyGamingAdvice[a].get_width(),window_y*0.9-window_x/64*a*1.5),screen)
        Display.flip()

    # 游戏主循环
    while True:
        #背景图片
        videoCapture.display(screen)

        if isHoverOn(chapter_select[1].b, (txt_location,(window_y-200)/9*1)):
            if cover_alpha < 250:
                cover_alpha+=10
        else:
            if cover_alpha >= 0:
                cover_alpha -=10

        if cover_alpha > 10:
            cover_img.set_alpha(cover_alpha)
            drawImg(cover_img, (0,0),screen)
        
        #菜单选项
        if menu_type == 0:
            i=0
            for key,text in main_menu_txt["menu_0"].items():
                if isHoverOn(text.n, (txt_location,main_menu_txt_start_height0+window_x/38*2*i)):
                    hover_sound_play_on = "0_"+str(i)
                    drawImg(text.b, (txt_location,main_menu_txt_start_height0+window_x/38*(2*i-0.25)),screen)
                else:
                    drawImg(text.n, (txt_location,main_menu_txt_start_height0+window_x/38*2*i),screen)
                i+=1
        elif menu_type == 1:
            i=0
            for key,text in main_menu_txt["menu_1"].items():
                if isHoverOn(text.n, (txt_location,main_menu_txt_start_height1+window_x/38*2*i)):
                    hover_sound_play_on = "0_"+str(i)
                    drawImg(text.b, (txt_location,main_menu_txt_start_height1+window_x/38*(2*i-0.25)),screen)
                else:
                    drawImg(text.n, (txt_location,main_menu_txt_start_height1+window_x/38*2*i),screen)
                i+=1
        elif menu_type == 2:
            for i in range(len(chapter_select)):
                if isHoverOn(chapter_select[i].n, (txt_location,chapter_select_txt_start_height+window_x/38*2*i)):
                    hover_sound_play_on = "2_"+str(i)
                    drawImg(chapter_select[i].b, (txt_location,chapter_select_txt_start_height+window_x/38*(2*i-0.25)),screen)
                else:
                    drawImg(chapter_select[i].n, (txt_location,chapter_select_txt_start_height+window_x/38*2*i),screen)

        if last_hover_sound_play_on != hover_sound_play_on:
            hover_on_button_sound.play()
            last_hover_sound_play_on = hover_sound_play_on

        #展示设置UI
        if settingUI.display(screen) == True:
            click_button_sound.set_volume(settingUI.soundVolume_sound_effects/100.0)
            hover_on_button_sound.set_volume(settingUI.soundVolume_sound_effects/100.0)

        #判断按键
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0] and settingUI.ifDisplay != True:
                click_button_sound.play()
                if menu_type == 0:
                    if isHoverOn(main_menu_txt["menu_0"]["text0_start"].n,(txt_location,main_menu_txt_start_height0)):
                        menu_type = 1
                    elif isHoverOn(main_menu_txt["menu_0"]["text1_setting"].n,(txt_location,main_menu_txt_start_height0+window_x/38*2*1)):
                        settingUI.ifDisplay = True
                    elif isHoverOn(main_menu_txt["menu_0"]["text2_developer_team"].n,(txt_location,main_menu_txt_start_height0+window_x/38*2*2)):
                        pass
                    elif isHoverOn(main_menu_txt["menu_0"]["text3_exit"].n,(txt_location,main_menu_txt_start_height0+window_x/38*2*3)):
                        Display.quit()
                elif menu_type == 1:
                    if isHoverOn(main_menu_txt["menu_1"]["text1_chooseChapter"].n,(txt_location,main_menu_txt_start_height1+window_x/38*2*1)):
                        menu_type = 2
                    elif isHoverOn(main_menu_txt["menu_1"]["text4_mapCreator"].n,(txt_location,main_menu_txt_start_height1+window_x/38*2*4)):
                        mapCreator("chapter1",screen,setting)
                    elif isHoverOn(main_menu_txt["menu_1"]["text6_back"].n,(txt_location,main_menu_txt_start_height1+window_x/38*2*6)):
                        menu_type = 0
                elif menu_type == 2:
                    for i in range(len(chapter_select)):
                        if i == len(chapter_select)-1 and isHoverOn(chapter_select[-1].n,(txt_location,chapter_select_txt_start_height+window_x/38*2*i)):
                            menu_type = 1
                        #章节选择
                        elif isHoverOn(chapter_select[i].n,(txt_location,chapter_select_txt_start_height+window_x/38*2*i)) and i==0:
                            dialog("chapter"+str(i+1),screen,setting,"dialog_before_battle")
                            battle("chapter"+str(i+1),screen,setting)
                            dialog("chapter"+str(i+1),screen,setting,"dialog_after_battle")
                            cutscene(screen,"Assets\movie\WhatAmIFightingFor.mp4","Assets/music/WhatAmIFightingFor.ogg")
                            videoCapture.setFrame(1)
                            break
            
        while pygame.mixer.music.get_busy() != 1:
            pygame.mixer.music.load('Assets/music/LoadOut.mp3')
            pygame.mixer.music.play(loops=9999, start=0.0)
            pygame.mixer.music.set_volume(setting["Sound"]["background_music"]/100.0)

        Display.flip()
