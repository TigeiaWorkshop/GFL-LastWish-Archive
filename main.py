#image purchased from unity store and internet
import pygame
import time
from pygame.locals import *
from sys import exit
import os
import glob
import yaml
import random
from hpManager import *
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

#读取并初始化章节信息
with open("data/main_chapter/chapter1.yaml", "r", encoding='utf-8') as f:
    chapter_info = yaml.load(f.read(),Loader=yaml.FullLoader)
    block_x = chapter_info["map"]["size"][0]
    block_y =  chapter_info["map"]["size"][1]
    characters = chapter_info["character"]
    sangvisFerris = chapter_info["sangvisFerri"]
block_x_length = window_x/block_x
block_y_length = window_y/block_y

#动图制作模块：接受一个友方角色名和动作，返回对应角色动作list和
def character_creater(character_name,action,kind="character"):
    global block_x_length
    global block_y_length
    character_gif=[]
    files_amount = 0
    for file in os.listdir("img/"+kind+"/"+character_name+"/"+action):
        files_amount+=1
    for i in range(files_amount):
        path = "img/"+kind+"/"+character_name+"/"+action+"/"+character_name+"_"+action+"_"+str(i)+".png"
        character_gif.append(pygame.transform.scale(pygame.image.load(os.path.join(path)), (int(block_x_length*2), int(block_y_length*2))))
    return [character_gif,files_amount]

#动图字典制作模块：接受一个友方角色名，返回对应的动图字典：
def character_gif_dic(character_name,kind="character"):
    if kind == "character":
        gif_dic = {
            "attack":[character_creater(character_name,"attack"),0],
            "die":[character_creater(character_name,"die"),0],
            "move":[character_creater(character_name,"move"),0],
            "victory":[character_creater(character_name,"victory"),0],
            "victoryloop":[character_creater(character_name,"victoryloop"),0],
            "wait":[character_creater(character_name,"wait"),0],
        }
    else:
        gif_dic = {
        "attack":[character_creater(character_name,"attack",kind),0],
        "die":[character_creater(character_name,"die",kind),0],
        "move":[character_creater(character_name,"move",kind),0],
        "wait":[character_creater(character_name,"wait",kind),0],
        }
    return gif_dic

#加载友方角色
characters_dic={}
for character in characters:
    characters_dic[character] = character_gif_dic(character)
#加载敌方角色
sangvisFerris_dic={}
for sangvisFerri in sangvisFerris:
    sangvisFerris_dic[sangvisFerri] = character_gif_dic(sangvisFerri,"sangvisFerri")

#加载动作：接受一个带有[动作]的gif字典，完成对应的指令
def action_displayer(gif_dic,action,x,y,isContinue=True):
    img_of_char = gif_dic[action][0][0][gif_dic[action][1]]
    screen.blit(img_of_char,(x,y))
    gif_dic[action][1]+=1
    if gif_dic[action][1] == 5 and action == "attack":
        bullets_list.append(Bullet(characters_data.x+img_of_char.get_width()-20,characters_data.y+img_of_char.get_height()/2-5,300))
    if gif_dic[action][1] == gif_dic[action][0][1]:
        gif_dic[action][1] = 0

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

#初始化角色信息
#hpManager(self, 最小攻击力, 最大攻击力, 血量上限 , 当前血量, x轴位置，y轴位置，移动速度)
characters_data = characterDataManager("sv-98",50,100,500,500,10,40,5)
sangvisFerris_data = {}
for enemy in sangvisFerris:
    sangvisFerris_data[enemy] = characterDataManager(enemy,50,100,500,500,10,40,10)

#加载子弹图片
bullet_img = pygame.transform.scale(pygame.image.load(os.path.join("img/others/bullet.png")), (int(block_x_length/6), int(block_y_length/12)))
bullets_list = []

# 游戏主循环
while True:
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
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


    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        if keys[pygame.K_a]:
            characters_data.x -= characters_data.speed
        if keys[pygame.K_d]:
            characters_data.x += characters_data.speed
        characters_data.y -= characters_data.speed
        action_displayer(characters_dic[characters_data.name],"move",characters_data.x,characters_data.y)
    elif keys[pygame.K_s]:
        if keys[pygame.K_a]:
            characters_data.x -= characters_data.speed
        if keys[pygame.K_d]:
            characters_data.x += characters_data.speed
        characters_data.y += characters_data.speed
        action_displayer(characters_dic[characters_data.name],"move",characters_data.x,characters_data.y)
    elif keys[pygame.K_a]:
        characters_data.x -= characters_data.speed
        action_displayer(characters_dic[characters_data.name],"move",characters_data.x,characters_data.y)
    elif keys[pygame.K_d]:
        characters_data.x += characters_data.speed
        action_displayer(characters_dic[characters_data.name],"move",characters_data.x,characters_data.y)
    elif keys[pygame.K_f]:
        action_displayer(characters_dic[characters_data.name],"attack",characters_data.x,characters_data.y)
    else:
        action_displayer(characters_dic[characters_data.name],"wait",characters_data.x,characters_data.y)

    for per_bullet in bullets_list:
        screen.blit(bullet_img, (per_bullet.x,per_bullet.y))
        per_bullet.x += 100
        if per_bullet.x > window_x:
            bullets_list.remove(per_bullet)

    while pygame.mixer.music.get_busy() != 1:
        pygame.mixer.music.load('music/Snowflake.mp3')
        pygame.mixer.music.play(loops=9999, start=0.0)

    time.sleep(0.025)
    pygame.display.update()
