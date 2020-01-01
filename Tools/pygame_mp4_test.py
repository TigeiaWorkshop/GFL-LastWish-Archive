import pygame
import cv2
from pygame.locals import *
import os
import yaml
from sys import exit

#加载主菜单背景

background_img_list=[]

for i in range(10):
    print("now is loading:"+str(i))
    path = "../Assets/img/main_menu/bgImg"+str(i)+".jpg"
    img = pygame.image.load(os.path.join(path))
    background_img_list.append(pygame.image.tostring(img,"RGB"))


with open("img_list.yaml", "r", encoding='utf-8') as f:
    chapter_info = yaml.load(f.read(),Loader=yaml.FullLoader)

with open("img_list.yaml", "w", encoding='utf-8') as f:
    chapter_info["data"] = background_img_list
    yaml.dump(chapter_info, f)

print("Done!")
exit()
