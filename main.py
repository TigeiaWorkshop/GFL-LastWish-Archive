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

#动图制作模块：接受一个角色名和动作，返回对应角色动作list和
def character_creater(character_name,action):
    character_gif=[]
    files_amount = 0
    for file in os.listdir("img/character/"+character_name+"/"+action):
        files_amount+=1
    for i in range(files_amount):
        path = "img/character/"+character_name+"/"+action+"/"+character_name+"_"+action+"_"+str(i)+".png"
        character_gif.append(pygame.image.load(os.path.join(path)))
    return [character_gif,files_amount]
#动图字典制作模块：接受一个角色名，返回对应的动图字典：
def character_gif_dic(character_name):
    gif_dic = {
        "attack":[character_creater(character_name,"attack"),0],
        "die":[character_creater(character_name,"die"),0],
        "move":[character_creater(character_name,"move"),0],
        "victory":[character_creater(character_name,"victory"),0],
        "victoryloop":[character_creater(character_name,"victoryloop"),0],
        "wait":[character_creater(character_name,"victoryloop"),0],
    }
    return gif_dic

#加载背景
forestPineSnowCovered = pygame.image.load('img/environment/forestPineSnowCovered02.png').convert_alpha()

#加载角色
gsh18_gif_dic = character_gif_dic("gsh-18")
asval_gif_dic = character_gif_dic("asval")
pp1901_gif_dic = character_gif_dic("pp1901")
sv98_gif_dic = character_gif_dic("sv-98")

#加载动作：接受一个带有[动作]的gif字典，完成对应的指令
def action_displayer(gif_dic,x,y,Iscontinue=True):
    if gif_dic[1] < gif_dic[0][1]:
        screen.blit(gif_dic[0][0][gif_dic[1]], (x,y))
        gif_dic[1]+=1
        if Iscontinue==True:
            if gif_dic[1] == gif_dic[0][1]:
                gif_dic[1] = 0

# 游戏主循环
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            # 接收到退出时间后退出程序
            exit()

    #角色动作
    screen.blit(forestPineSnowCovered, (400,30))
    action_displayer(gsh18_gif_dic["move"],40,40,True)
    action_displayer(sv98_gif_dic["attack"],340,40,False)



    time.sleep(0.025)
    pygame.display.update()
