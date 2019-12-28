import glob
import os
import time
from sys import exit

import pygame
import yaml
from pygame.locals import *

from Zero2_tool.dialog import *
from Zero2_tool.IsGetClick import *

pygame.init()

def mainMenu(window_x,window_y,lang,mode=""):
    #加载主菜单文字
    with open("Lang/"+lang+".yaml", "r", encoding='utf-8') as f:
        lang_cn = yaml.load(f.read(),Loader=yaml.FullLoader)
        my_font =pygame.font.SysFont('simsunnsimsun',50)
        now_loading = lang_cn['main_menu']['now_loading']
        text_title =  lang_cn['main_menu']['text_title']
        text_continue = my_font.render(lang_cn['main_menu']['text_continue'], True, (105,105,105))
        text_chooseChapter = my_font.render(lang_cn['main_menu']['text_chooseChapter'], True, (255, 255, 255))
        text_setting = my_font.render(lang_cn['main_menu']['text_setting'], True, (105,105,105))
        text_dlc = my_font.render(lang_cn['main_menu']['text_dlc'], True, (105,105,105))
        text_workshop = my_font.render(lang_cn['main_menu']['text_workshop'], True, (105,105,105))
        text_exit = my_font.render(lang_cn['main_menu']['text_exit'], True, (255, 255, 255))
        c1 = my_font.render(lang_cn['chapter']['c1'], True, (255, 255, 255))
        c2 = my_font.render(lang_cn['chapter']['c2'], True, (105,105,105))
        c3 = my_font.render(lang_cn['chapter']['c3'], True, (105,105,105))
        c4 = my_font.render(lang_cn['chapter']['c4'], True, (105,105,105))
        c5 = my_font.render(lang_cn['chapter']['c5'], True, (105,105,105))
        c6 = my_font.render(lang_cn['chapter']['c6'], True, (105,105,105))
        c7 = my_font.render(lang_cn['chapter']['c7'], True, (105,105,105))
        c8 = my_font.render(lang_cn['chapter']['c8'], True, (105,105,105))
        back_button = my_font.render(lang_cn['chapter']['back'], True, (255, 255, 255))

    # 创建窗口
    screen = pygame.display.set_mode([window_x, window_y])
    pygame.display.set_caption(text_title) #窗口标题

    #加载主菜单背景
    background_img_id = 0
    background_img_list=[]
    loading_img =  pygame.transform.scale(pygame.image.load(os.path.join("Assets/img/loading_img/img1.png")),(window_x,window_y))
    cover_img = pygame.transform.scale(pygame.image.load(os.path.join("Assets/img/covers/chapter1.png")),(window_x,window_y))
    while True:
        for event in pygame.event.get():
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                exit()
            if event.type == KEYDOWN and event.key == K_s:
                pygame.display.toggle_fullscreen()
        path = "Assets/img/main_menu/background_img"+str(background_img_id)+".jpg"
        background_img_list.append(pygame.transform.scale(pygame.image.load(os.path.join(path)).convert_alpha(),(window_x,window_y)))
        percent_of_img_loaded = '{:.0f}%'.format(background_img_id/374*100)
        background_img_id+=1
        if mode == "test":
            if background_img_id == 1:
                break
        else:
            if background_img_id == 375:
                break
        screen.blit(loading_img, (0,0))
        the_str = my_font.render(now_loading+": "+str(percent_of_img_loaded), True, (255, 255, 255))
        screen.blit(the_str, ((window_x-the_str.get_width())/2,window_y-100))
        pygame.display.update()
    #数值初始化
    cover_alpha = 0
    background_img_id = 0
    menu_type = 0
    txt_location = int(window_x*2/3)

    
    # 游戏主循环
    while True:
        for event in pygame.event.get():
            if event.type == KEYDOWN and event.key == K_s:
                pygame.display.toggle_fullscreen()
            elif event.type == MOUSEBUTTONDOWN:
                #退出
                if IsGetClick(text_exit, (txt_location,750)):
                    if menu_type == 0:
                        exit()
                #选择章节
                elif IsGetClick(text_chooseChapter, (txt_location,350)):
                    if menu_type == 0:
                        menu_type = 1
                #返回
                elif IsGetClick(back_button, (txt_location,window_y-150)):
                    if menu_type == 1:
                        menu_type = 0
                #章节选择
                elif IsGetClick(c1, (txt_location,(window_y-200)/9*1)):
                    if menu_type == 1:
                        dialog_display_function("chapter1",window_x,window_y,screen,lang)

        screen.blit(background_img_list[background_img_id], (0,0))
        
        if IsGetClick(c1, (txt_location,(window_y-200)/9*1)):
            if cover_alpha < 250:
                cover_alpha+=10
        else:
            if cover_alpha >= 0:
                cover_alpha -=10

        if menu_type == 1:
            cover_img.set_alpha(cover_alpha)
            screen.blit(cover_img, (0,0))

        #菜单选项
        if menu_type == 0:
            screen.blit(text_continue, (txt_location,250))
            screen.blit(text_chooseChapter, (txt_location,350))
            screen.blit(text_setting, (txt_location,450))
            screen.blit(text_dlc, (txt_location,550))
            screen.blit(text_workshop, (txt_location,650))
            screen.blit(text_exit, (txt_location,750))
        elif menu_type == 1:
            screen.blit(c1, (txt_location,(window_y-200)/9*1))
            screen.blit(c2, (txt_location,(window_y-200)/9*2))
            screen.blit(c3, (txt_location,(window_y-200)/9*3))
            screen.blit(c4, (txt_location,(window_y-200)/9*4))
            screen.blit(c5, (txt_location,(window_y-200)/9*5))
            screen.blit(c6, (txt_location,(window_y-200)/9*6))
            screen.blit(c7, (txt_location,(window_y-200)/9*7))
            screen.blit(c8, (txt_location,(window_y-200)/9*8))
            screen.blit(back_button, (txt_location,window_y-150))
        
        #背景图片动画
        if background_img_id == 374:
            background_img_id = 0
        else:
            if mode != "test":
                background_img_id += 1
        
        time.sleep(0.04)
        while pygame.mixer.music.get_busy() != 1:
            pygame.mixer.music.load('Assets/music/White_Front.mp3')
            pygame.mixer.music.play(loops=9999, start=0.0)
        pygame.display.update()
