#image purchased from unity store and internet
import pygame
from pygame.locals import *
from sys import exit
import time
import os
import yaml
pygame.init()

#加载设置
with open("setting.yaml", "r", encoding='utf-8') as f:
    setting = yaml.load(f.read(),Loader=yaml.FullLoader)
    window_x = setting['Screen_size_x']
    window_y =  setting['Screen_size_y']
    lang_file = setting['Language']

#加载主菜单文字
with open("lang/"+lang_file+".yaml", "r", encoding='utf-8') as f:
    lang_cn = yaml.load(f.read(),Loader=yaml.FullLoader)
    my_font =pygame.font.SysFont('simsunnsimsun',60)
    text_title =  lang_cn['main_menu']['text_title']
    text_continue = my_font.render(lang_cn['main_menu']['text_continue'], True, (105,105,105))
    text_chooseChapter = my_font.render(lang_cn['main_menu']['text_chooseChapter'], True, (255, 255, 255))
    text_setting = my_font.render(lang_cn['main_menu']['text_setting'], True, (105,105,105))
    text_dlc = my_font.render(lang_cn['main_menu']['text_dlc'], True, (105,105,105))
    text_wrokshop = my_font.render(lang_cn['main_menu']['text_wrokshop'], True, (105,105,105))
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

#加载背景
background_img_id = 0
background_img_list=[]
loading_img = pygame.image.load(os.path.join("img/loading_img/img1.png"))
while True:
    for event in pygame.event.get():
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            exit()
        if event.type == KEYDOWN and event.key == K_s:
            pygame.display.toggle_fullscreen()

    path = "img/main_menu/background_img"+str(background_img_id)+".jpg"
    background_img_list.append(pygame.image.load(os.path.join(path)).convert_alpha())
    percent_of_img_loaded = '{:.0f}%'.format(background_img_id/374*100)
    background_img_id+=1
    if background_img_id == 375:
        break
    screen.blit(loading_img, (0,0))
    screen.blit(my_font.render(str(percent_of_img_loaded), True, (255, 255, 255)), (10,10))
    pygame.display.update()
background_img_id = 0
menu_type = 0
txt_location = int(window_x*2/3)

# 游戏主循环
while True:
    for event in pygame.event.get():
        if event.type == KEYDOWN and event.key == K_s:
            pygame.display.toggle_fullscreen()
        elif event.type == MOUSEBUTTONDOWN:
            mouse_x,mouse_y=pygame.mouse.get_pos()
            if txt_location<mouse_x<txt_location+text_exit.get_width() and 750<mouse_y<750+text_exit.get_height():
                exit()
            elif txt_location<mouse_x<txt_location+text_chooseChapter.get_width() and 350<mouse_y<350+text_chooseChapter.get_height():
                if menu_type == 0:
                    menu_type = 1
            elif txt_location<mouse_x<txt_location+back_button.get_width() and window_y-150<mouse_y<window_y-150+back_button.get_height():
                if menu_type == 1:
                    menu_type = 0

    screen.blit(background_img_list[background_img_id], (0,0))
    #角色动作
    if menu_type == 0:
        screen.blit(text_continue, (txt_location,250))
        screen.blit(text_chooseChapter, (txt_location,350))
        screen.blit(text_setting, (txt_location,450))
        screen.blit(text_dlc, (txt_location,550))
        screen.blit(text_wrokshop, (txt_location,650))
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

    background_img_id += 1
    if background_img_id == 374:
        background_img_id = 0
    while pygame.mixer.music.get_busy() != 1:
        pygame.mixer.music.load('music/White_Front.mp3')
        pygame.mixer.music.play(loops=9999, start=0.0)
    time.sleep(0.04)
    pygame.display.update()
