import time
from sys import exit

import cv2
import pygame
import yaml
from pygame.locals import *

from Zero2.basic import *
from Zero2.dialog import *

def mainMenu(screen,window_x,window_y,lang,fps,mode=""):
    #加载主菜单文字
    with open("Lang/"+lang+".yaml", "r", encoding='utf-8') as f:
        loadData = yaml.load(f.read(),Loader=yaml.FullLoader)
        game_title = loadData['game_title']
        main_menu_txt = loadData['main_menu']
        chapter_select = loadData['chapter']
    
    #加载主菜单选择页面的文字
    for txt in main_menu_txt:
        if txt == "text_exit" or txt == "text_chooseChapter":
            main_menu_txt[txt] = fontRenderPro(main_menu_txt[txt],"enable",window_x/38)
        else:
            main_menu_txt[txt] = fontRenderPro(main_menu_txt[txt],"disable",window_x/38)
    
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
    videoCapture = cv2.VideoCapture("Assets/movie/SquadAR.mp4")
    #数值初始化
    cover_alpha = 0
    background_img_id = 0
    menu_type = 0
    txt_location = int(window_x*2/3)
    main_menu_txt_start_height = (window_y-len(main_menu_txt)*window_x/38*2)/2
    chapter_select_txt_start_height = (window_y-len(chapter_select)*window_x/38*2)/2
    #关卡选择的封面
    cover_img = loadImg("Assets/image/covers/chapter1.png",window_x,window_y)
    #帧数控制器
    fpsClock = pygame.time.Clock()
    video_fps = videoCapture.get(cv2.CAP_PROP_FPS)
    #视频面
    surface = pygame.surface.Surface((window_x, window_y))
    #音效
    click_button_sound = pygame.mixer.Sound("Assets/sound/ui/main_menu_click_button.ogg")
    hover_on_button_sound = pygame.mixer.Sound("Assets/sound/ui/main_menu_hover_on_button.ogg")
    hover_sound_play_on = None
    last_hover_sound_play_on = None

    the_black = loadImage("Assets/image/UI/black.png",(0,0),window_x,window_y)
    t1 = fontRender("缇吉娅工坊 呈现","white",30)
    t2 = fontRender("警告：所有内容仍处于研发阶段，不代表最终效果","white",30)

    for i in range(0,250,2):
        the_black.draw(screen)
        t1.set_alpha(i)
        drawImg(t1,(30,window_y-130),screen)
        t2.set_alpha(i)
        drawImg(t2,(30,window_y-80),screen)
        time.sleep(0.01)
        pygame.display.flip()
    
    for i in range(250,0,-2):
        the_black.draw(screen)
        t1.set_alpha(i)
        drawImg(t1,(30,window_y-130),screen)
        t2.set_alpha(i)
        drawImg(t2,(30,window_y-80),screen)
        time.sleep(0.01)
        pygame.display.flip()

    # 游戏主循环
    while True:
        #背景图片
        if videoCapture.get(1) >= 3105:
            videoCapture.set(1, 935)
        ret, frame = videoCapture.read()
        if frame.shape[0] != window_x or frame.shape[1] != window_y:
            frame = cv2.resize(frame,(window_x,window_y))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.transpose(frame)
        pygame.surfarray.blit_array(surface, frame)
        screen.blit(surface, (0,0))

        if isHoverOn(chapter_select[1].b, (txt_location,(window_y-200)/9*1)):
            if cover_alpha < 250:
                cover_alpha+=10
        else:
            if cover_alpha >= 0:
                cover_alpha -=10

        if menu_type == 1:
            cover_img.set_alpha(cover_alpha)
            drawImg(cover_img, (0,0),screen)
        
        #菜单选项
        if menu_type == 0:
            i=0
            for txt in main_menu_txt:
                if isHoverOn(main_menu_txt[txt].n, (txt_location,main_menu_txt_start_height+window_x/38*2*i)):
                    hover_sound_play_on = "0_"+str(i)
                    drawImg(main_menu_txt[txt].b, (txt_location,main_menu_txt_start_height+window_x/38*2*i),screen)
                else:
                    drawImg(main_menu_txt[txt].n, (txt_location,main_menu_txt_start_height+window_x/38*2*i),screen)
                i+=1
        elif menu_type == 1:
            for i in range(len(chapter_select)):
                if isHoverOn(chapter_select[i].n, (txt_location,chapter_select_txt_start_height+window_x/38*2*i)):
                    hover_sound_play_on = "1_"+str(i)
                    drawImg(chapter_select[i].b, (txt_location,chapter_select_txt_start_height+window_x/38*2*i),screen)
                else:
                    drawImg(chapter_select[i].n, (txt_location,chapter_select_txt_start_height+window_x/38*2*i),screen)

        if last_hover_sound_play_on != hover_sound_play_on:
            hover_on_button_sound.play()
            last_hover_sound_play_on = hover_sound_play_on

        for event in pygame.event.get():
            if event.type == MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]:
                click_button_sound.play()
                click_button_sound
                if menu_type == 0:
                    i=0
                    for txt in main_menu_txt:
                        if txt == "text_exit" and isHoverOn(main_menu_txt["text_exit"].b,(txt_location,main_menu_txt_start_height+window_x/38*2*i)):
                            exit()
                        #选择章节
                        elif txt == "text_chooseChapter" and isHoverOn(main_menu_txt["text_chooseChapter"].b,(txt_location,main_menu_txt_start_height+window_x/38*2*i)):
                            menu_type = 1
                        i+=1
                elif menu_type == 1:
                    for i in range(len(chapter_select)):
                        if i == len(chapter_select)-1 and isHoverOn(chapter_select[-1].b,(txt_location,chapter_select_txt_start_height+window_x/38*2*i)):
                            menu_type = 0
                        #章节选择
                        elif isHoverOn(chapter_select[i].b,(txt_location,chapter_select_txt_start_height+window_x/38*2*i)):
                            dialog("chapter"+str(i+1),window_x,window_y,screen,lang,fps,"dialog_before_battle")
                            battle("chapter"+str(i+1),window_x,window_y,screen,lang,fps)
                            dialog("chapter"+str(i+1),window_x,window_y,screen,lang,fps,"dialog_after_battle")
                            videoCapture.set(1,1)
                            break
            
        while pygame.mixer.music.get_busy() != 1:
            pygame.mixer.music.load('Assets/music/LoadOut.mp3')
            pygame.mixer.music.play(loops=9999, start=0.0)

        fpsClock.tick(video_fps)
        pygame.display.update()
