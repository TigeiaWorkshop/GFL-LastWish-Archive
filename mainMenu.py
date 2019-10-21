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
    text_title = my_font.render(lang_cn['main_menu']['text_title'], True, (255, 255, 255))
    text_continue = my_font.render(lang_cn['main_menu']['text_continue'], True, (255, 255, 255))
    text_chooseChapter = my_font.render(lang_cn['main_menu']['text_chooseChapter'], True, (255, 255, 255))
    text_setting = my_font.render(lang_cn['main_menu']['text_setting'], True, (255, 255, 255))
    text_dlc = my_font.render(lang_cn['main_menu']['text_dlc'], True, (255, 255, 255))
    text_wrokshop = my_font.render(lang_cn['main_menu']['text_wrokshop'], True, (255, 255, 255))
    text_exit = my_font.render(lang_cn['main_menu']['text_exit'], True, (255, 255, 255))

# 创建窗口
screen = pygame.display.set_mode((window_x, window_y), 0, 32)
pygame.display.set_caption("Girls frontline-Last Wish") #窗口标题

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

# 游戏主循环
while True:
    for event in pygame.event.get():
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            exit()
        if event.type == KEYDOWN and event.key == K_s:
            pygame.display.toggle_fullscreen()

    #角色动作
    screen.blit(background_img_list[background_img_id], (0,0))
    screen.blit(text_title, (1300,100))
    screen.blit(text_continue, (1500,250))
    screen.blit(text_chooseChapter, (1500,350))
    screen.blit(text_setting, (1500,450))
    screen.blit(text_dlc, (1500,550))
    screen.blit(text_wrokshop, (1500,650))
    screen.blit(text_exit, (1500,750))
    background_img_id += 1
    if background_img_id == 374:
        background_img_id = 0
    while pygame.mixer.music.get_busy() != 1:
        pygame.mixer.music.load('music/White_Front.mp3')
        pygame.mixer.music.play(loops=9999, start=0.0)
    pygame.display.update()
    time.sleep(1/25)
