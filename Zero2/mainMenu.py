import time
from sys import exit

import cv2
import pygame
import yaml
from pygame.locals import *

from Zero2.basic import *
from Zero2.dialog import *

pygame.init()

def mainMenu(window_x,window_y,lang,fps,mode=""):
    #加载主菜单文字
    with open("Lang/"+lang+".yaml", "r", encoding='utf-8') as f:
        lang_cn = yaml.load(f.read(),Loader=yaml.FullLoader)
        now_loading = lang_cn['main_menu']['now_loading']
        text_title =  lang_cn['main_menu']['text_title']
        text_continue = fontRenderPro(lang_cn['main_menu']['text_continue'],"disable")
        text_chooseChapter = fontRenderPro(lang_cn['main_menu']['text_chooseChapter'],"enable")
        text_setting = fontRenderPro(lang_cn['main_menu']['text_setting'],"disable")
        text_dlc = fontRenderPro(lang_cn['main_menu']['text_dlc'],"disable")
        text_workshop = fontRenderPro(lang_cn['main_menu']['text_workshop'],"disable")
        text_exit = fontRenderPro(lang_cn['main_menu']['text_exit'],"enable")
        chapter_select = lang_cn['chapter']
    
    #加载菜单选择页面的文字
    for i in range(len(chapter_select)):
        chapter_select[i] = fontRenderPro(chapter_select[i],"disable")

    # 创建窗口
    screen = pygame.display.set_mode((window_x, window_y),pygame.SCALED)
    pygame.display.set_caption(text_title) #窗口标题

    #加载主菜单背景
    videoCapture = cv2.VideoCapture("Assets/movie/SquadAR.mp4")
    #数值初始化
    cover_alpha = 0
    background_img_id = 0
    menu_type = 0
    txt_location = int(window_x*2/3)
    #关卡选择的封面
    cover_img = loadImg("Assets/img/covers/chapter1.png",window_x,window_y)
    #帧数控制器
    surface = pygame.surface.Surface((window_x, window_y))
    fpsClock = pygame.time.Clock()
    
    # 游戏主循环
    while True:
        for event in pygame.event.get():
            if event.type == KEYDOWN and event.key == K_s:
                pygame.display.toggle_fullscreen()
            elif event.type == MOUSEBUTTONDOWN:
                if menu_type == 0:
                    #退出
                    if isGetClick(text_exit.b, (txt_location,750)):
                        exit()
                    #选择章节
                    elif isGetClick(text_chooseChapter.b, (txt_location,350)):
                        menu_type = 1
                elif menu_type == 1:
                    #返回
                    if isGetClick(chapter_select[0-1].b, (txt_location,(window_y-200)/9*(len(chapter_select)))):
                        menu_type = 0
                    #章节选择
                    else:
                        for i in range(len(chapter_select)-1):
                            if isGetClick(chapter_select[i].b, (txt_location,(window_y-200)/9*(i+1))) and i != len(chapter_select)-1:
                                dialog("chapter"+str(i+1),window_x,window_y,screen,lang,fps,"dialog_before_battle")
                                battle("chapter"+str(i+1),window_x,window_y,screen,lang,fps)
                                dialog("chapter"+str(i+1),window_x,window_y,screen,lang,fps,"dialog_after_battle")
                                break
        #背景图片
        if videoCapture.get(1) >= 3105:
            videoCapture.set(1, 935)
        ret, frame = videoCapture.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.transpose(frame)
        pygame.surfarray.blit_array(surface, frame)
        screen.blit(surface, (0,0))

        if isGetClick(chapter_select[1].b, (txt_location,(window_y-200)/9*1)):
            if cover_alpha < 250:
                cover_alpha+=10
        else:
            if cover_alpha >= 0:
                cover_alpha -=10

        if menu_type == 1:
            cover_img.set_alpha(cover_alpha)
            printf(cover_img, (0,0),screen)

        #菜单选项
        if menu_type == 0:
            printf(text_continue.n, (txt_location,250),screen)
            if isGetClick(text_chooseChapter.n, (txt_location,350)):
                printf(text_chooseChapter.b, (txt_location,350),screen)
            else:
                printf(text_chooseChapter.n, (txt_location,350),screen)
            printf(text_setting.n, (txt_location,450),screen)
            printf(text_dlc.n, (txt_location,550),screen)
            printf(text_workshop.n, (txt_location,650),screen)
            if isGetClick(text_exit.n, (txt_location,750)):
                printf(text_exit.b, (txt_location,750),screen)
            else:
                printf(text_exit.n, (txt_location,750),screen)
        elif menu_type == 1:
            for i in range(len(chapter_select)):
                if isGetClick(chapter_select[i].n, (txt_location,(window_y-200)/9*(i+1))):
                    printf(chapter_select[i].b, (txt_location,(window_y-200)/9*(i+1)),screen)
                else:
                    printf(chapter_select[i].n, (txt_location,(window_y-200)/9*(i+1)),screen)

        while pygame.mixer.music.get_busy() != 1:
            pygame.mixer.music.load('Assets/music/LoadOut.mp3')
            pygame.mixer.music.play(loops=9999, start=0.0)

        fpsClock.tick(fps)
        pygame.display.update()
