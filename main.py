#image purchased from unity store and internet
import pygame
import time
from pygame.locals import *
from sys import exit
import os
import os.path
pygame.init()

# 创建窗口
pygame.init()
screen = pygame.display.set_mode((1600, 900), 0, 32)
pygame.display.set_caption("Girls frontline-Last Wish") #窗口标题

# 加载图片并转换
background_main = pygame.image.load('img/main_1600X900.png')


# 游戏主循环
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            # 接收到退出时间后退出程序
            exit()

    # 将背景图画上去
    screen.blit(background_main, (0, 0))
    pygame.display.update()
