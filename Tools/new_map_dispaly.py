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
block_x_length = int(window_x*4/5/block_x)
block_y_length = int(window_y*4/5/block_y)
bg_img_test = pygame.transform.scale(pygame.image.load(os.path.join("../Assets/img/loading_img/test.png")),(int(1920),int(1080)))

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

#生存随机方块名
with open("../Data/blocks.yaml", "r", encoding='utf-8') as f:
    reader = yaml.load(f.read(),Loader=yaml.FullLoader)
    blocks_setting = reader["blocks"]
map_img_list = randomBlock(map,blocks_setting)

to_left = (1920 - len(map_img_list[0])*block_x_length)/2
dirt_void = pygame.transform.scale(pygame.image.load(os.path.join("../Assets/img/environment/below_dirt.png")),(int(block_x_length),int(block_x_length)))

# 游戏主循环
while True:
    screen.blit(bg_img_test,(0,0))
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                exit()

    #场景加载
    for i in range(len(map_img_list)):
        for a in range(len(map_img_list[i])):
            img_display = pygame.transform.scale(env_img_list[map_img_list[i][a]], (int(block_x_length), int(block_y_length*1.5)))
            screen.blit(img_display,(to_left+a*block_x_length,100+(i+1)*block_y_length-int(block_y_length*1.5)))
    
    for k in range(len(map_img_list[0])):
        screen.blit(dirt_void,(to_left+k*block_x_length,100+(len(map_img_list)+1.5)*block_y_length-int(block_y_length*1.5)))
    
    pygame.display.update()
