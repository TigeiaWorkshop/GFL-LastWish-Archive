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

#生存随机方块名
with open("../Data/blocks.yaml", "r", encoding='utf-8') as f:
    reader = yaml.load(f.read(),Loader=yaml.FullLoader)
    blocks_setting = reader["blocks"]
map_img_list = randomBlock(map,blocks_setting)

#绿色方块/方块标准
green = pygame.transform.scale(pygame.image.load(os.path.join("../Assets/img/UI/green.png")), (block_x_length, int(block_y_length)))
green.set_alpha(100)
new_block_type = 0

# 游戏主循环
while True:
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                exit()
            if event.key == K_s:
                with open("../Data/main_chapter/chapter1_map.yaml", "w", encoding='utf-8') as f:
                    chapter_info["map"] = map
                    yaml.dump(chapter_info, f)
                exit()
        elif event.type == MOUSEBUTTONDOWN:
            mouse_x,mouse_y=pygame.mouse.get_pos()
            block_get_click_x = int(mouse_x/green.get_width())
            block_get_click_y = int(mouse_y/green.get_height())
            map[block_get_click_y][block_get_click_x] = new_block_type
            if new_block_type == 0:
                img_name = "mountainSnow"+str(random.randint(0,7))
            elif new_block_type == 1:
                img_name = "plainsColdSnowCovered"+str(random.randint(0,3))
            elif new_block_type == 2:
                img_name = "forestPineSnowCovered"+str(random.randint(0,4))
            elif new_block_type == 3:
                img_name = "ocean"+str(random.randint(0,4))
            map_img_list[block_get_click_y][block_get_click_x] = img_name

    #场景加载
    for i in range(len(map_img_list)):
        for a in range(len(map_img_list[i])):
            img_display = pygame.transform.scale(env_img_list[map_img_list[i][a]], (int(block_x_length), int(block_y_length*1.5)))
            screen.blit(img_display,(a*block_x_length,(i+1)*block_y_length-int(block_y_length*1.5)))
    for y in range(block_y):
        for x in range(block_x):
            screen.blit(green,(x*block_x_length,y*block_y_length))
    keys = pygame.key.get_pressed()
    if keys[pygame.K_1]:
        new_block_type = 0
    elif keys[pygame.K_2]:
        new_block_type = 1
    elif keys[pygame.K_3]:
        new_block_type = 2
    elif keys[pygame.K_4]:
        new_block_type = 3

    time.sleep(0.025)
    pygame.display.update()
