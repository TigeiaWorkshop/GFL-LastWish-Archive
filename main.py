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

def character_creater(character_name,action,range_len):
    character_gif=[]
    for i in range(range_len):
        path = "img/character/"+character_name+"/"+action+"/"+character_name+"_"+action+"_"+str(i)+".png"
        character_gif.append(pygame.image.load(path))
    return character_gif

# 加载并转换主菜单背景图
#background_main = pygame.image.load('img/main_1600X900.png')

#加载背景
forestPineSnowCovered = pygame.image.load('img/environment/forestPineSnowCovered02.png')

#加载角色
wait_gif_id=0
wait_gif_total = 54
gsh18_gif_wait_list = character_creater("gsh-18","wait",wait_gif_total)

move_gif_id=0
move_gif_total = 24
gsh18_gif_move_list = character_creater("gsh-18","move",move_gif_total)



# 游戏主循环
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            # 接收到退出时间后退出程序
            exit()

    #角色动作
    screen.blit(gsh18_gif_wait_list[wait_gif_id], (40,40))
    screen.blit(forestPineSnowCovered, (400,30))
    screen.blit(gsh18_gif_move_list[move_gif_id], (380,60))

    wait_gif_id += 1
    if wait_gif_id == wait_gif_total:
        wait_gif_id = 0

    move_gif_id += 1
    if move_gif_id == move_gif_total:
        move_gif_id = 0
    time.sleep(0.025)
    pygame.display.flip()
