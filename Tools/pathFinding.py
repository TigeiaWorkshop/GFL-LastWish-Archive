#image purchased from unity store and internet
import pygame
import time
from pygame.locals import *
from sys import exit
import os
import glob
import yaml
from map import *
pygame.init()
import sys
sys.setrecursionlimit(1000000) #例如这里设置为一百万
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
    chapter_info = yaml.load(f.read(),Loader=yaml.FullLoader)
    map = chapter_info["map"]
block_x = 48
block_y = 24
block_x_length = int(window_x/block_x)
block_y_length = int(window_y/block_y)

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
        chapter_info["map"] = default_map
        yaml.dump(chapter_info, f)

    with open("../Data/main_chapter/chapter1_map.yaml", "r", encoding='utf-8') as f:
        map = chapter_info["map"]

#生成随机方块名
with open("../Data/blocks.yaml", "r", encoding='utf-8') as f:
    reader = yaml.load(f.read(),Loader=yaml.FullLoader)
    blocks_setting = reader["blocks"]
map_img_list = randomBlock(map,blocks_setting)

#绿色方块/方块标准
green = pygame.transform.scale(pygame.image.load(os.path.join("../Assets/img/UI/green.png")), (block_x_length, int(block_y_length)))
green.set_alpha(100)

first_point = None
second_point = None

def create_map_with_path(x_start,y_start,map_in):
    map_out = []
    for y in range(len(map_in)):
        map_out_line = []
        for x in range(len(map_in[y])):
            if blocks_setting[map_in[y][x]][1] == True:
                if y <= y_start and x <= x_start:
                    map_out_line.append(x_start+y_start-x-y)
                elif y <= y_start and x >= x_start:
                    map_out_line.append(x+y_start-x_start-y)
                elif y >= y_start and x <= x_start:
                    map_out_line.append(x_start+y-x-y_start)
                elif y >= y_start and x >= x_start:
                    map_out_line.append(x+y-x_start-y_start)
            else:
                map_out_line.append("disable")
        map_out.append(map_out_line)
    return map_out

def findPath(x_togo,y_togo,theMapWithRoute):
    route_move = []
    pathlist.append([x,y])
    if x == x_togo and y == y_togo:
        return pathlist
    else:
        if [x+1,y] not in pathlist and x<len(map_in[y])-2:
            to_add = findPath(x+1,y,x_togo,y_togo,map_in,pathlist)
            if to_add != None:
                all_path_to_compare.append(to_add)
        if [x-1,y] not in pathlist and x>1:
            to_add = findPath(x-1,y,x_togo,y_togo,map_in,pathlist)
            if to_add != None:
                all_path_to_compare.append(to_add)
        if [x,y+1] not in pathlist and y<len(map_in)-2:
            to_add = findPath(x,y+1,x_togo,y_togo,map_in,pathlist)
            if to_add != None:
                all_path_to_compare.append(to_add)
        if [x,y-1] not in pathlist and y>1:
            to_add = findPath(x,y-1,x_togo,y_togo,map_in,pathlist)
            if to_add != None:
                all_path_to_compare.append(to_add)
        if len(all_path_to_compare) == 0:
            return None
        elif len(all_path_to_compare) == 1:
            return all_path_to_compare[0]
        elif len(all_path_to_compare) > 1:
            min_len = all_path_to_compare[0]
            for i in range(1,len(all_path_to_compare)):
                if len(all_path_to_compare[i]) <= len(min_len):
                    min_len = all_path_to_compare[i]
            return min_len

all_list = []
all_list = create_map_with_path(3,2,3,5,map)
for i in range(len(all_list)):
    print(all_list[i])
exit()
"""
# 游戏主循环
while True:
    mouse_x,mouse_y=pygame.mouse.get_pos()
    block_get_click_x = int(mouse_x/green.get_width())
    block_get_click_y = int(mouse_y/green.get_height())
                
    second_point = [block_get_click_x,block_get_click_y]
    #场景加载
    for i in range(len(map_img_list)):
        for a in range(len(map_img_list[i])):
            img_display = pygame.transform.scale(env_img_list[map_img_list[i][a]], (int(block_x_length), int(block_y_length*1.5)))
            screen.blit(img_display,(a*block_x_length,(i+1)*block_y_length-int(block_y_length*1.5)))
    
    for i in range(len(all_list)):
        screen.blit(green,(all_list[i][0]*block_x_length,all_list[i][1]*block_y_length))
        time.sleep(0.025)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    exit()
                if event.key == K_s:
                    first_point = None
                    second_point = None
            elif event.type == MOUSEBUTTONDOWN:
                first_point = [block_get_click_x,block_get_click_y]
"""