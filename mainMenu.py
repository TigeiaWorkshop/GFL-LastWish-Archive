#image purchased from unity store and internet
import pygame
from pygame.locals import *
from sys import exit
import time
import os
import yaml
pygame.init()

#加载主菜单文字
my_font = pygame.font.SysFont("font/font.ttf", 200)
lang_yaml = open("lang/zh_cn.yaml", "r", encoding='utf-8')
lang_yaml = lang_yaml.read()

text_title = my_font.render("少女前线", True, (255, 255, 255))
text_continue = my_font.render("继续游戏", True, (0,0,0))
text_chooseChapter = my_font.render("选择章节", True, (0,0,0))
text_setting = my_font.render("设置", True, (0,0,0))
text_dlc = my_font.render("可下载内容", True, (0,0,0))
text_wrokshop = my_font.render("创意工坊", True, (0,0,0))
text_exit = my_font.render("退出", True, (0,0,0))

# 创建窗口
window_x = 1920
window_y = 1080
screen = pygame.display.set_mode((1920, 1080), 0, 32)
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
    background_img_list.append(pygame.image.load(os.path.join(path)))
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
    screen.blit(text_title, (100,100))
    background_img_id += 1
    if background_img_id == 374:
        background_img_id = 0
    while pygame.mixer.music.get_busy() != 1:
        pygame.mixer.music.load('music/White_Front.mp3')
        pygame.mixer.music.play(loops=9999, start=0.0)
    pygame.display.update()
    time.sleep(1/20)
