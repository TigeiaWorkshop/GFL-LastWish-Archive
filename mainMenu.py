#image purchased from unity store and internet
import pygame
import time
from pygame.locals import *
from sys import exit
import os
pygame.init()

# 创建窗口
screen = pygame.display.set_mode((1920, 1080), 0, 32)
pygame.display.set_caption("Girls frontline-Last Wish") #窗口标题

#加载主菜单文字
my_font = pygame.font.SysFont("other/font.ttf", 42)
text_title = my_font.render("少女前线-遗愿", True, (0,0,0))
text_continue = my_font.render("继续游戏", True, (0,0,0))
text_chooseChapter = my_font.render("选择章节", True, (0,0,0))
text_setting = my_font.render("设置", True, (0,0,0))
text_dlc = my_font.render("可下载内容", True, (0,0,0))
text_wrokshop = my_font.render("创意工坊", True, (0,0,0))
text_exit = my_font.render("退出", True, (0,0,0))

#加载背景
background_img_id = 0
background_img_list=[]
for i in range(374):
    path = "img/main_menu/background_img"+str(i)+".jpg"
    background_img_list.append(pygame.image.load(path))
background_img_list = tuple(background_img_list)


# 游戏主循环
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            # 接收到退出时间后退出程序
            exit()

    #角色动作
    screen.blit(background_img_list[background_img_id], (0,0))

    background_img_id += 1
    if background_img_id == 130:
        background_img_id = 0
    while pygame.mixer.music.get_busy() != 1:
        pygame.mixer.music.load('music/White_Front.mp3')
        pygame.mixer.music.play(loops=9999, start=0.0)
    pygame.display.update()
