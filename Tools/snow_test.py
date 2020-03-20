import glob
import time
import sys
import random
import pygame
import yaml
from pygame.locals import *

sys.path.append('../')
from Zero2.basic import *

# 创建窗口
pygame.init()
text_title ="test"
screen = pygame.display.set_mode([1920, 1080])
pygame.display.set_caption(text_title) #窗口标题

#加载雪花
snow_list = []
for i in range(1,17):
    snow_list.append(loadImage("../Assets/img/environment/snow/"+str(i)+".png"))

snow_width = int(1920/200)

all_snow_on_screen = []
for i in range(1000):
    the_snow_add = snow_list[random.randint(0,15)]
    the_snow_add.y = random.randint(1,1080)
    the_snow_add.x = random.randint(1,1920)
    the_snow_add.img = pygame.transform.scale(the_snow_add.img, (snow_width,snow_width))
    all_snow_on_screen.append(the_snow_add)

loading_img =  pygame.transform.scale(pygame.image.load(os.path.join("../Assets/img/loading_img/img1.png")),(1920,1080))

while True:
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                exit()

    screen.blit(loading_img,(0,0))

    for i in range(len(all_snow_on_screen)):
        screen.blit(all_snow_on_screen[i].img,(all_snow_on_screen[i].x,all_snow_on_screen[i].y))
        all_snow_on_screen[i].x -= 0.01
        all_snow_on_screen[i].y += 0.02
        if all_snow_on_screen[i].x < 0 or all_snow_on_screen[i].y > 1080:
            all_snow_on_screen[i].y = 0
            all_snow_on_screen[i].x = random.randint(1,1920)
    
    pygame.display.update()
    