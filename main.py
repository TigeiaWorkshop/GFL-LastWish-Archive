#image purchased from unity store and internet
import pygame
import time
from pygame.locals import *
from sys import exit
import os
import glob
import yaml
import random
pygame.init()

#加载设置
with open("setting.yaml", "r", encoding='utf-8') as f:
    setting = yaml.load(f.read(),Loader=yaml.FullLoader)
    window_x = setting['Screen_size_x']
    window_y =  setting['Screen_size_y']
    lang_file = setting['Language']

# 创建窗口
screen = pygame.display.set_mode([window_x, window_y])
pygame.display.set_caption("Girls frontline-Last Wish") #窗口标题

#加载背景图片
all_env_file_list = glob.glob(r'img\environment\*.png')
env_img_list={}
for i in range(len(all_env_file_list)):
    img_name = all_env_file_list[i].replace("img","").replace("environment","").replace(".png","").replace("\\","").replace("/","")
    env_img_list[img_name] = pygame.image.load(os.path.join(all_env_file_list[i])).convert_alpha()

#背景初始化
with open("data/main_chapter/chapter1.yaml", "r", encoding='utf-8') as f:
    chapter_info = yaml.load(f.read(),Loader=yaml.FullLoader)
    block_x = chapter_info["$map"]["size"][0]
    block_y =  chapter_info["$map"]["size"][1]
block_x_length = window_x/block_x
block_y_length = window_y/block_y

#动图制作模块：接受一个友方角色名和动作，返回对应角色动作list和
def character_creater(character_name,action):
    global block_x_length
    global block_y_length
    character_gif=[]
    files_amount = 0
    for file in os.listdir("img/character/"+character_name+"/"+action):
        files_amount+=1
    for i in range(files_amount):
        path = "img/character/"+character_name+"/"+action+"/"+character_name+"_"+action+"_"+str(i)+".png"
        character_gif.append(pygame.transform.scale(pygame.image.load(os.path.join(path)), (int(block_x_length*2), int(block_y_length*2))))
    return [character_gif,files_amount]

#动图字典制作模块：接受一个友方角色名，返回对应的动图字典：
def character_gif_dic(character_name):
    gif_dic = {
        "attack":[character_creater(character_name,"attack"),0],
        "die":[character_creater(character_name,"die"),0],
        "move":[character_creater(character_name,"move"),0],
        "victory":[character_creater(character_name,"victory"),0],
        "victoryloop":[character_creater(character_name,"victoryloop"),0],
        "wait":[character_creater(character_name,"wait"),0],
    }
    return gif_dic

#动图制作模块：接受一个友方角色名和动作，返回对应角色动作list和
def enemies_creater(character_name,action):
    global block_x_length
    global block_y_length
    character_gif=[]
    files_amount = 0
    for file in os.listdir("img/enemies/"+character_name+"/"+action):
        files_amount+=1
    for i in range(files_amount):
        path = "img/enemies/"+character_name+"/"+action+"/"+character_name+"_"+action+"_"+str(i)+".png"
        character_gif.append(pygame.transform.scale(pygame.image.load(os.path.join(path)), (int(block_x_length*2), int(block_y_length*2))))
    return [character_gif,files_amount]

#动图字典制作模块：接受一个友方角色名，返回对应的动图字典：
def enemies_gif_dic(character_name):
    gif_dic = {
        "attack":[enemies_creater(character_name,"attack"),0],
        "die":[enemies_creater(character_name,"die"),0],
        "move":[enemies_creater(character_name,"move"),0],
        "wait":[enemies_creater(character_name,"wait"),0],
    }
    return gif_dic

#加载友方角色
gsh18_gif_dic = character_gif_dic("gsh-18")
pp1901_gif_dic = character_gif_dic("pp1901")
asval_gif_dic = character_gif_dic("asval")
sv98_gif_dic = character_gif_dic("sv-98")
#加载敌方角色
guard_gif_dic = enemies_gif_dic("guard")
jaeger_gif_dic = enemies_gif_dic("jaeger")
prowler_gif_dic = enemies_gif_dic("prowler")
ripper_gif_dic = enemies_gif_dic("ripper")
vespid_gif_dic = enemies_gif_dic("vespid")

#加载动作：接受一个带有[动作]的gif字典，完成对应的指令
def action_displayer(gif_dic,x,y,Iscontinue=True):
    if gif_dic[1] < gif_dic[0][1]:
        screen.blit(gif_dic[0][0][gif_dic[1]],((x*2-1)*gsh18_gif_dic["wait"][0][0][0].get_width()/4,(y*2-1)*gsh18_gif_dic["wait"][0][0][0].get_width()/4-20))
        gif_dic[1]+=1
        if Iscontinue==True:
            if gif_dic[1] == gif_dic[0][1]:
                gif_dic[1] = 0
            return False
    else:
        return True
#随机化山的结构
randMountainNumLists = []
for i in range(block_y):
    randMountainNumList = []
    for a in range(block_x):
        if i==0 or i==block_y-1 or a==0 or a==block_x-1:
            randMountainNumList.append(str(random.randint(0,7)))
        else:
            randMountainNumList.append(str(random.randint(0,3)))
    randMountainNumLists.append(randMountainNumList)

# 游戏主循环
while True:
    for event in pygame.event.get():
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            exit()
    #场景加载
    for i in range(block_y):
        for a in range(block_x):
            if i == 0:
                img = pygame.transform.scale(env_img_list["mountainSnow"+randMountainNumLists[i][a]], (int(block_x_length), int(block_y_length*1.5)))
            elif i == block_y-1:
                    img = pygame.transform.scale(env_img_list["mountainSnow"+randMountainNumLists[i][a]], (int(block_x_length), int(block_y_length*1.5)))
            else:
                if a == 0:
                    img = pygame.transform.scale(env_img_list["mountainSnow"+randMountainNumLists[i][a]], (int(block_x_length), int(block_y_length*1.5)))
                elif a == block_x-1:
                    img = pygame.transform.scale(env_img_list["mountainSnow"+randMountainNumLists[i][a]], (int(block_x_length), int(block_y_length*1.5)))
                else:
                    img = pygame.transform.scale(env_img_list["plainsColdSnowCovered"+randMountainNumLists[i][a]], (int(block_x_length), int(block_y_length*1.5)))
            screen.blit(img,(a*block_x_length,i*block_y_length-block_x_length/2))

    #角色动作
    action_displayer(gsh18_gif_dic["wait"],5,5)
    action_displayer(sv98_gif_dic["wait"],2,1)
    action_displayer(asval_gif_dic["wait"],2,5)
    action_displayer(pp1901_gif_dic["wait"],4,4)
    action_displayer(guard_gif_dic["wait"],7,4)
    while pygame.mixer.music.get_busy() != 1:
        pygame.mixer.music.load('music/Snowflake.mp3')
        pygame.mixer.music.play(loops=9999, start=0.0)
    time.sleep(0.025)
    pygame.display.update()
