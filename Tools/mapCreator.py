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
        gif_dic = sangvisFerris_data[chara_name].gif_dic
    elif chara_name in characters_data:
        gif_dic = characters_data[chara_name].gif_dic
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

#读取地图
with open("../Data/main_chapter/chapter1_map.yaml", "r", encoding='utf-8') as f:
    loadData = yaml.load(f.read(),Loader=yaml.FullLoader)
    map = loadData["map"]
    characters = loadData["character"]
    sangvisFerris = loadData["sangvisFerri"]

#初始化地图
if len(map) == 0:
    block_y = 36
    block_x = 64
    default_map = []
    for i in range(block_y):
        map_per_line = []
        for a in range(block_x):
            if i == 0 or i == block_y-1:
                map_per_line.append(0)
            else:
                if a == 0 or a == block_x-1:
                    map_per_line.append(0)
                else:
                    map_per_line.append(1)
        default_map.append(map_per_line)

    with open("../Data/main_chapter/chapter1_map.yaml", "w", encoding='utf-8') as f:
        loadData["map"] = default_map
        yaml.dump(loadData, f)

    with open("../Data/main_chapter/chapter1_map.yaml", "r", encoding='utf-8') as f:
        map = loadData["map"]
else:
    block_x = len(map[0])
    block_y = len(map)

block_x_length = int(window_x/block_x*0.9)
block_y_length = int(window_y/block_y*0.9)

#加载背景图片
all_env_file_list = glob.glob(r'../Assets/img/environment/*.png')
env_img_list={}
for i in range(len(all_env_file_list)):
    img_name = all_env_file_list[i].replace(".","").replace("Assets","").replace("img","").replace("environment","").replace("png","").replace("\\","").replace("/","")
    env_img_list[img_name] = loadImg(all_env_file_list[i],int(block_x_length), int(block_y_length*1.5))

perBlockWidth = block_x_length
perBlockHeight = block_y_length
#初始化角色信息
characters_data = {}
for each_character in characters:
    characters_data[each_character] = characterDataManager(characters[each_character]["action_point"],characters[each_character]["attack_range"],characters[each_character]["current_bullets"],characters[each_character]["current_hp"],characters[each_character]["effective_range"],character_gif_dic(characters[each_character]["type"],perBlockWidth,perBlockHeight),characters[each_character]["magazine_capacity"],characters[each_character]["max_damage"],characters[each_character]["max_hp"],characters[each_character]["min_damage"],characters[each_character]["x"],characters[each_character]["y"],characters[each_character]["bullets_carried"],characters[each_character]["start_position"],characters[each_character]["undetected"])

sangvisFerris_data = {}
for each_character in sangvisFerris:
    sangvisFerris_data[each_character] = sangvisFerriDataManager(sangvisFerris[each_character]["action_point"],sangvisFerris[each_character]["attack_range"],sangvisFerris[each_character]["current_bullets"],sangvisFerris[each_character]["current_hp"],sangvisFerris[each_character]["effective_range"],character_gif_dic(sangvisFerris[each_character]["type"],perBlockWidth,perBlockHeight,"sangvisFerri"),sangvisFerris[each_character]["magazine_capacity"],sangvisFerris[each_character]["max_damage"],sangvisFerris[each_character]["max_hp"],sangvisFerris[each_character]["min_damage"],sangvisFerris[each_character]["x"],sangvisFerris[each_character]["y"],sangvisFerris[each_character]["patrol_path"])

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

#生存随机方块名
with open("../Data/blocks.yaml", "r", encoding='utf-8') as f:
    reader = yaml.load(f.read(),Loader=yaml.FullLoader)
    blocks_setting = reader["blocks"]
map_img_list = randomBlock(map,blocks_setting)

#绿色方块/方块标准
green = pygame.transform.scale(pygame.image.load(os.path.join("../Assets/img/UI/green.png")), (block_x_length, int(block_y_length)))
green.set_alpha(100)
object_to_put_down = None
#帧数控制器
fpsClock = pygame.time.Clock()

data_to_edit = None

# 游戏主循环
while True:
    pygame.draw.rect(screen,(255,255,255),(0,0,window_x,window_y))
    mouse_x,mouse_y=pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                object_to_put_down = None
                data_to_edit = None
            elif event.key == K_m:
                exit()    
            elif event.key == K_s:
                with open("../Data/main_chapter/chapter1_map.yaml", "w", encoding='utf-8') as f:
                    loadData["map"] = map
                    loadData["character"] = characters
                    loadData["sangvisFerri"] = sangvisFerris
                    yaml.dump(loadData, f)
                exit()
        elif event.type == MOUSEBUTTONDOWN:
            all_characters_data = dicMerge(characters_data,sangvisFerris_data)
            block_get_click_x = int(mouse_x/green.get_width())
            block_get_click_y = int(mouse_y/green.get_height())
            if block_get_click_y < len(map) and block_get_click_x < len(map[block_get_click_y]):
                if pygame.mouse.get_pressed()[0]:
                    if object_to_put_down != None:
                        if object_to_put_down["type"] == "block":
                            map[block_get_click_y][block_get_click_x] = object_to_put_down["id"]
                            map_img_list[block_get_click_y][block_get_click_x] = object_to_put_down["name"]
                        elif object_to_put_down["type"] == "character" or object_to_put_down["type"] == "sangvisFerri":
                            any_chara_replace = None
                            for chara in all_characters_data:
                                if all_characters_data[chara].x == block_get_click_x and all_characters_data[chara].y == block_get_click_y:
                                    any_chara_replace = chara
                                    break
                            if any_chara_replace != None:
                                if any_chara_replace in characters_data:
                                    characters_data.pop(any_chara_replace)
                                    characters.pop(any_chara_replace)
                                elif any_chara_replace in sangvisFerris_data:
                                    sangvisFerris_data.pop(any_chara_replace)
                                    sangvisFerris.pop(any_chara_replace)
                            the_id = 0
                            if object_to_put_down["type"] == "character":
                                while object_to_put_down["id"]+"_"+str(the_id) in characters_data:
                                    the_id+=1
                                characters_data[object_to_put_down["id"]+"_"+str(the_id)] = characterDataManager(1,1,1,1,1,character_gif_dic(object_to_put_down["id"],perBlockWidth,perBlockHeight),1,1,1,1,block_get_click_x,block_get_click_y,[],False)
                                characters[object_to_put_down["id"]+"_"+str(the_id)] = {"action_point": 1,"attack_range": 1,"bullets_carried": 1,"current_bullets": 1,"current_hp": 1,"effective_range": 1,"magazine_capacity": 1,"max_damage": 1,"max_hp": 1,"min_damage": 1,"start_position": [],"type": object_to_put_down["id"],"undetected": False,"x": block_get_click_x,"y": block_get_click_y}
                            elif object_to_put_down["type"] == "sangvisFerri":
                                while object_to_put_down["id"]+"_"+str(the_id) in sangvisFerris_data:
                                    the_id+=1
                                sangvisFerris_data[object_to_put_down["id"]+"_"+str(the_id)] = sangvisFerriDataManager(1,1,1,1,1,character_gif_dic(object_to_put_down["id"],perBlockWidth,perBlockHeight,"sangvisFerri"),1,1,1,1,block_get_click_x,block_get_click_y,[])
                                sangvisFerris[object_to_put_down["id"]+"_"+str(the_id)] = {"action_point": 1,"attack_range": 1,"current_bullets": 1,"current_hp": 1,"effective_range": 1,"max_bullets": 1,"max_damage": 1,"max_hp": 1,"min_damage": 1,"type": object_to_put_down["id"],"patrol_path": [],"x": block_get_click_x,"y": block_get_click_y}
                if pygame.mouse.get_pressed()[2]:
                    any_chara_replace = None
                    for chara in all_characters_data:
                        if all_characters_data[chara].x == block_get_click_x and all_characters_data[chara].y == block_get_click_y:
                            any_chara_replace = chara
                            break
                    if any_chara_replace != None:
                        if any_chara_replace in characters_data:
                            characters_data.pop(any_chara_replace)
                            characters.pop(any_chara_replace)
                        elif any_chara_replace in sangvisFerris_data:
                            sangvisFerris_data.pop(any_chara_replace)
                            sangvisFerris.pop(any_chara_replace)
    #场景加载
    for i in range(len(map_img_list)):
        for a in range(len(map_img_list[i])):
            screen.blit(env_img_list[map_img_list[i][a]],(a*block_x_length,(i+1)*block_y_length-int(block_y_length*1.5)))
    #角色动画
    for every_chara in characters_data:
        if map[characters_data[every_chara].y][characters_data[every_chara].x] == 2:
            characters_data[every_chara].undetected = True
        else:
            characters_data[every_chara].undetected = False
        action_displayer(every_chara,"wait",characters_data[every_chara].x,characters_data[every_chara].y)
        if object_to_put_down == None and pygame.mouse.get_pressed()[0] and isHoverOn(all_characters_img_list[characters[every_chara]["type"]],(characters_data[every_chara].x*perBlockWidth-perBlockWidth/2,characters_data[every_chara].y*perBlockHeight-perBlockHeight/2)):
            data_to_edit = characters_data[every_chara]
    for enemies in sangvisFerris_data:
        action_displayer(enemies,"wait",sangvisFerris_data[enemies].x,sangvisFerris_data[enemies].y)
        if object_to_put_down == None and pygame.mouse.get_pressed()[0] and isHoverOn(all_sangvisFerris_img_list[sangvisFerris[enemies]["type"]],(sangvisFerris_data[enemies].x*perBlockWidth-perBlockWidth/2,sangvisFerris_data[enemies].y*perBlockHeight-perBlockHeight/2)):
            data_to_edit = sangvisFerris_data[enemies]
    
    #显示所有可放置的友方角色
    i=1
    for every_chara in all_characters_img_list:
        drawImg(all_characters_img_list[every_chara],(perBlockWidth*i,window_y*0.9-perBlockHeight*0.9),screen)
        if pygame.mouse.get_pressed()[0] and isHoverOn(all_characters_img_list[every_chara],(perBlockWidth*i,window_y*0.9-perBlockHeight*0.9)):
            object_to_put_down = {"type":"character","id":every_chara}
        i+=2
    i=1
    for enemies in all_sangvisFerris_img_list:
        drawImg(all_sangvisFerris_img_list[enemies],(perBlockWidth*i,window_y*0.9+perBlockHeight*0.7),screen)
        if pygame.mouse.get_pressed()[0] and isHoverOn(all_sangvisFerris_img_list[enemies],(perBlockWidth*i,window_y*0.9+perBlockHeight*0.7)):
            object_to_put_down = {"type":"sangvisFerri","id":enemies}
        i+=2
    
    #显示所有可放置的环境方块
    i=0
    for the_block_id in blocks_setting:
        if blocks_setting[the_block_id]["imgNum"] > 1:
            img_name = blocks_setting[the_block_id]["name"]+"0"
        else:
            img_name = blocks_setting[the_block_id]["name"]
        drawImg(env_img_list[img_name],(window_x*0.92+perBlockWidth*1.5*(i%3),perBlockHeight*1.5*int(i/3)),screen)
        if pygame.mouse.get_pressed()[0] and isHoverOn(env_img_list[img_name],(window_x*0.92+perBlockWidth*1.5*(i%3),perBlockHeight*1.5*int(i/3))):
            object_to_put_down = {"type":"block","id":the_block_id,"name":img_name}
        i+=1
    
    #跟随鼠标显示即将被放下的物品
    if object_to_put_down != None:
        if object_to_put_down["type"] == "block":
            drawImg(env_img_list[object_to_put_down["name"]],(mouse_x-block_x_length*0.5,mouse_y-block_y_length),screen)
        elif object_to_put_down["type"] == "character":
            drawImg(all_characters_img_list[object_to_put_down["id"]],(mouse_x-block_x_length,mouse_y-block_y_length),screen)
        elif object_to_put_down["type"] == "sangvisFerri":
            drawImg(all_sangvisFerris_img_list[object_to_put_down["id"]],(mouse_x-block_x_length,mouse_y-block_y_length),screen)

    #显示即将被编辑的数据
    object_edit_id = 0
    if data_to_edit != None:
        drawImg(fontRender("action points: "+str(data_to_edit.max_action_point),"black",15),(window_x*0.91,window_y*0.8),screen)
        drawImg(fontRender("attack range: "+str(data_to_edit.attack_range),"black",15),(window_x*0.91,window_y*0.8+20),screen)
        drawImg(fontRender("current bullets: "+str(data_to_edit.current_bullets),"black",15),(window_x*0.91,window_y*0.8+20*2),screen)
        drawImg(fontRender("magazine capacity: "+str(data_to_edit.magazine_capacity),"black",15),(window_x*0.91,window_y*0.8+20*3),screen)
        drawImg(fontRender("max hp: "+str(data_to_edit.max_hp),"black",15),(window_x*0.91,window_y*0.8+20*4),screen)
        drawImg(fontRender("effective range: "+str(data_to_edit.effective_range),"black",15),(window_x*0.91,window_y*0.8+20*5),screen)
        drawImg(fontRender("max damage: "+str(data_to_edit.max_damage),"black",15),(window_x*0.91,window_y*0.8+20*6),screen)
        drawImg(fontRender("min damage: "+str(data_to_edit.min_damage),"black",15),(window_x*0.91,window_y*0.8+20*7),screen)
        drawImg(fontRender("x: "+str(data_to_edit.x),"black",15),(window_x*0.91,window_y*0.8+20*8),screen)
        drawImg(fontRender("y: "+str(data_to_edit.y),"black",15),(window_x*0.91,window_y*0.8+20*9),screen)

    fpsClock.tick(60)
    pygame.display.flip()
