import glob
import os
import time
from sys import exit

import numpy as np
import cv2
import pygame
import yaml
from pygame.locals import *

from Zero2.basic import *
from Zero2.dialog import *

pygame.init()

def mainMenu(window_x,window_y,lang,mode=""):
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
        c1 = fontRenderPro(lang_cn['chapter']['c1'],"enable")
        c2 = fontRenderPro(lang_cn['chapter']['c2'],"disable")
        c3 = fontRenderPro(lang_cn['chapter']['c3'],"disable")
        c4 = fontRenderPro(lang_cn['chapter']['c4'],"disable")
        c5 = fontRenderPro(lang_cn['chapter']['c5'],"disable")
        c6 = fontRenderPro(lang_cn['chapter']['c6'],"disable")
        c7 = fontRenderPro(lang_cn['chapter']['c7'],"disable")
        c8 = fontRenderPro(lang_cn['chapter']['c8'],"disable")
        back_button = fontRenderPro(lang_cn['chapter']['back'],"enable")

    # 创建窗口
    screen = pygame.display.set_mode((window_x, window_y))
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
    
    # 游戏主循环
    while True:
        for event in pygame.event.get():
            if event.type == KEYDOWN and event.key == K_s:
                pygame.display.toggle_fullscreen()
            elif event.type == MOUSEBUTTONDOWN:
                #退出
                if isGetClick(text_exit.b, (txt_location,750)):
                    if menu_type == 0:
                        exit()
                #选择章节
                elif isGetClick(text_chooseChapter.b, (txt_location,350)):
                    if menu_type == 0:
                        menu_type = 1
                #返回
                elif isGetClick(back_button.b, (txt_location,window_y-150)):
                    if menu_type == 1:
                        menu_type = 0
                #章节选择
                elif isGetClick(c1.b, (txt_location,(window_y-200)/9*1)):
                    if menu_type == 1:
                        dialog_display_function("chapter1",window_x,window_y,screen,lang)
                        
        #背景图片
        if videoCapture.isOpened():
            ret, frame = videoCapture.read()
            try:
                frame = np.rot90(frame,k=-1)
            except:
                continue
            if videoCapture.get(1) >= 3105:
                videoCapture.set(1, 935)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = pygame.surfarray.make_surface(frame)
            frame = pygame.transform.flip(frame,False,True)
            frame = pygame.transform.scale(frame, (1920,1080))
            printf(frame, (0,0),screen)
        
        if isGetClick(c1.b, (txt_location,(window_y-200)/9*1)):
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
            if isGetClick(c1.n, (txt_location,(window_y-200)/9*1)):
                printf(c1.b, (txt_location,(window_y-200)/9*1),screen)
            else:
                printf(c1.n, (txt_location,(window_y-200)/9*1),screen)
            if isGetClick (c2.n, (txt_location,(window_y-200)/9*2)):
                printf(c2.b, (txt_location,(window_y-200)/9*2),screen)
            else:
                printf(c2.n, (txt_location,(window_y-200)/9*2),screen)
            printf(c3.n, (txt_location,(window_y-200)/9*3),screen)
            printf(c4.n, (txt_location,(window_y-200)/9*4),screen)
            printf(c5.n, (txt_location,(window_y-200)/9*5),screen)
            printf(c6.n, (txt_location,(window_y-200)/9*6),screen)
            printf(c7.n, (txt_location,(window_y-200)/9*7),screen)
            printf(c8.n, (txt_location,(window_y-200)/9*8),screen)
            if isGetClick(back_button.n, (txt_location,window_y-150)):
                printf(back_button.b, (txt_location,window_y-150),screen)
            else:
                printf(back_button.n, (txt_location,window_y-150),screen)

        while pygame.mixer.music.get_busy() != 1:
            pygame.mixer.music.load('Assets/music/LoadOut.mp3')
            pygame.mixer.music.play(loops=9999, start=0.0)
        pygame.display.update()
