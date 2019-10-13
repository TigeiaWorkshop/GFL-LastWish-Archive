#image purchased from unity store and internet
import pygame
import time
from pygame.locals import *
from sys import exit
import os
pygame.init()

# 创建窗口
screen = pygame.display.set_mode((1600, 900), 0, 32)
pygame.display.set_caption("Girls frontline-Last Wish") #窗口标题

#加载背景
background_img_id = 0
background_img_list=[]
for i in range(130):
    path = "img/main_menu/background_img"+str(i)+".png"
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
    time.sleep(1)
    pygame.display.update()
