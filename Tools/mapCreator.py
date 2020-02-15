#image purchased from unity store and internet
import glob
import os
import time
from sys import exit

import pygame
import yaml
from pygame.locals import *

from Zero2.basic import *
from Zero2.characterAnimation import *
from Zero2.characterDataManager import *
from Zero2.map import *

pygame.init()

#加载动作：接受角色名，动作，方位，完成对应的指令
def action_displayer(chara_name,action,x,y,isContinue=True,ifFlip=False):
    hidden = False
    if chara_name in sangvisFerris_data:
        gif_dic = sangvisFerris_data[chara_name].gif
    elif chara_name in characters_data:
        gif_dic = characters_data[chara_name].gif
    img_of_char = pygame.transform.scale(gif_dic[action][0][0][gif_dic[action][1]], (int(perBlockWidth*2), int(perBlockHeight*2)))
    if ifFlip == True:
        drawImg(pygame.transform.flip(img_of_char,True,False),(x*perBlockWidth-perBlockWidth/2,y*perBlockHeight-perBlockHeight/2),screen)
    else:
        drawImg(img_of_char,(x*perBlockWidth-perBlockWidth/2,y*perBlockHeight-perBlockHeight/2),screen)
    gif_dic[action][1]+=1
    if isContinue==True:
        if gif_dic[action][1] == gif_dic[action][0][1]:
            gif_dic[action][1] = 0
    elif isContinue==False:
        if gif_dic[action][1] == gif_dic[action][0][1]:
            gif_dic[action][1]-=1

#加载设置
with open("../Data/setting.yaml", "r", encoding='utf-8') as f:
    setting = yaml.load(f.read(),Loader=yaml.FullLoader)
    window_x = setting['Screen_size_x']
    window_y =  setting['Screen_size_y']
    lang_file = setting['Language']

# 创建窗口
screen = pygame.display.set_mode([window_x, window_y])
pygame.display.set_caption("Girls frontline-Last Wish") #窗口标题

#加载背景图片
all_env_file_list = glob.glob(r'../Assets/img/environment/*.png')
env_img_list={}
for i in range(len(all_env_file_list)):
    img_name = all_env_file_list[i].replace(".","").replace("Assets","").replace("img","").replace("environment","").replace("png","").replace("\\","").replace("/","")
    env_img_list[img_name] = pygame.image.load(os.path.join(all_env_file_list[i]))

#读取地图
with open("../Data/main_chapter/chapter1_map.yaml", "r", encoding='utf-8') as f:
    loadData = yaml.load(f.read(),Loader=yaml.FullLoader)
    map = loadData["map"]
    characters = loadData["character"]
    sangvisFerris = loadData["sangvisFerri"]

block_x = 48
block_y = 24
block_x_length = int(window_x/block_x*0.9)
block_y_length = int(window_y/block_y*0.9)

perBlockWidth = block_x_length
perBlockHeight = block_y_length
#初始化角色信息
#hpManager(名字, 最小攻击力, 最大攻击力, 血量上限 , 当前血量, x轴位置，y轴位置，攻击范围，移动范围,gif字典)
characters_data = {}
for jiaose in characters:
    characters_data[jiaose] = characterDataManager(characters[jiaose]["min_damage"],characters[jiaose]["max_damage"],characters[jiaose]["max_hp"],characters[jiaose]["current_hp"],characters[jiaose]["start_position"],characters[jiaose]["x"],characters[jiaose]["y"],characters[jiaose]["attack_range"],characters[jiaose]["action_point"],characters[jiaose]["undetected"],character_gif_dic(jiaose,perBlockWidth,perBlockHeight),characters[jiaose]["current_bullets"],characters[jiaose]["maximum_bullets"])

sangvisFerris_data = {}
for enemy in sangvisFerris:
    sangvisFerris_data[enemy] = sangvisFerriDataManager(sangvisFerris[enemy]["min_damage"],sangvisFerris[enemy]["max_damage"],sangvisFerris[enemy]["max_hp"],sangvisFerris[enemy]["current_hp"],sangvisFerris[enemy]["x"],sangvisFerris[enemy]["y"],sangvisFerris[enemy]["attack_range"],sangvisFerris[enemy]["move_range"],character_gif_dic(sangvisFerris[enemy]["type"],perBlockWidth,perBlockHeight,"sangvisFerri"),sangvisFerris[enemy]["current_bullets"],sangvisFerris[enemy]["maximum_bullets"],sangvisFerris[enemy]["patrol_path"])

#所有的角色文件
all_characters_list  = glob.glob(r'../Assets/img/character/*')
all_characters_img_list={}
for i in range(len(all_characters_list)):
    img_name = all_characters_list[i].replace(".","").replace("Assets","").replace("img","").replace("character","").replace("\\","").replace("/","")
    all_characters_img_list[img_name] = loadImg(all_characters_list[i]+"/wait/"+img_name+"_wait_0.png",perBlockWidth*2.5,perBlockHeight*2.5)

all_sangvisFerris_list  = glob.glob(r'../Assets/img/sangvisFerri/*')
all_sangvisFerris_img_list={}
for i in range(len(all_sangvisFerris_list)):
    img_name = all_sangvisFerris_list[i].replace(".","").replace("Assets","").replace("img","").replace("sangvisFerri","").replace("\\","").replace("/","")
    all_sangvisFerris_img_list[img_name] = loadImg(all_sangvisFerris_list[i]+"/wait/"+img_name+"_wait_0.png",perBlockWidth*2.5,perBlockHeight*2.5)

#初始化地图
if len(map) == 0:
    default_map = []
    for i in range(block_y):
        map_per_line = []
        for a in range(block_x):
            if i == 0 or i == block_y-1:
                map_per_line.append(0)
            else:
                if a == 0 or a ==block_x-1:
                    map_per_line.append(0)
                else:
                    map_per_line.append(1)
        default_map.append(map_per_line)

    with open("../Data/main_chapter/chapter1_map.yaml", "w", encoding='utf-8') as f:
        loadData["map"] = default_map
        yaml.dump(chapter_info, f)

    with open("../Data/main_chapter/chapter1_map.yaml", "r", encoding='utf-8') as f:
        map = loadData["map"]

#生存随机方块名
with open("../Data/blocks.yaml", "r", encoding='utf-8') as f:
    reader = yaml.load(f.read(),Loader=yaml.FullLoader)
    blocks_setting = reader["blocks"]
map_img_list = randomBlock(map,blocks_setting)

#绿色方块/方块标准
green = pygame.transform.scale(pygame.image.load(os.path.join("../Assets/img/UI/green.png")), (block_x_length, int(block_y_length)))
green.set_alpha(100)
new_block_type = 0
img_name_list = ["mountainSnow0","plainsColdSnowCovered0","forestPineSnowCovered0","ocean0"]
object_to_put_down = {type:"block",name:"mountainSnow0"}
# 游戏主循环
while True:
    pygame.draw.rect(screen,(255,255,255),(0,0,window_x,window_y))
    mouse_x,mouse_y=pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                exit()
            if event.key == K_s:
                with open("../Data/main_chapter/chapter1_map.yaml", "w", encoding='utf-8') as f:
                    loadData["map"] = map
                    yaml.dump(loadData, f)
                exit()
        elif event.type == MOUSEBUTTONDOWN:
            block_get_click_x = int(mouse_x/green.get_width())
            block_get_click_y = int(mouse_y/green.get_height())
            if block_get_click_y < len(map) and block_get_click_x < len(map[block_get_click_y]):
                map[block_get_click_y][block_get_click_x] = new_block_type
                if new_block_type == 0:
                    img_name = "mountainSnow0"
                elif new_block_type == 1:
                    img_name = "plainsColdSnowCovered0"
                elif new_block_type == 2:
                    img_name = "forestPineSnowCovered0"
                elif new_block_type == 3:
                    img_name = "ocean0"
                map_img_list[block_get_click_y][block_get_click_x] = img_name

    #场景加载
    for i in range(len(map_img_list)):
        for a in range(len(map_img_list[i])):
            img_display = pygame.transform.scale(env_img_list[map_img_list[i][a]], (int(block_x_length), int(block_y_length*1.5)))
            screen.blit(img_display,(a*block_x_length,(i+1)*block_y_length-int(block_y_length*1.5)))
    #角色动画
    for every_chara in characters_data:
        if map[characters_data[every_chara].y][characters_data[every_chara].x] == 2:
            characters_data[every_chara].undetected = True
        else:
            characters_data[every_chara].undetected = False
        action_displayer(every_chara,"wait",characters_data[every_chara].start_position[0],characters_data[every_chara].start_position[1])
    for enemies in sangvisFerris_data:
        action_displayer(enemies,"wait",sangvisFerris_data[enemies].x,sangvisFerris_data[enemies].y)
    

    #显示所有可放置的友方角色
    i=1
    for every_chara in all_characters_img_list:
        drawImg(all_characters_img_list[every_chara],(perBlockWidth*i,window_y*0.9-perBlockHeight*0.9),screen)
        i+=2
    i=1
    for enemies in all_sangvisFerris_img_list:
        drawImg(all_sangvisFerris_img_list[enemies],(perBlockWidth*i,window_y*0.9+perBlockHeight*0.7),screen)
        i+=2

    keys = pygame.key.get_pressed()
    if keys[pygame.K_1]:
        new_block_type = 0
    elif keys[pygame.K_2]:
        new_block_type = 1
    elif keys[pygame.K_3]:
        new_block_type = 2
    elif keys[pygame.K_4]:
        new_block_type = 3

    
    img_will_be_placed = pygame.transform.scale(env_img_list[img_name_list[new_block_type]], (int(block_x_length), int(block_y_length*1.5)))
    screen.blit(img_will_be_placed,(mouse_x-block_x_length*0.5,mouse_y-block_y_length*0.5))

    pygame.display.flip()
