import glob
import math
import os
import random
import time
from sys import exit

import cv2
import pygame
import yaml
from pygame.locals import *

def cropImg(img,pos=(0,0),size=(0,0)):
    cropped = pygame.Surface((round(size[0]), round(size[1])))
    cropped.blit(img,(-pos[0],-pos[1]))
    return cropped

def loadSpine(characterImage,value):
    if value["rotate"] == True:
        img = cropImg(characterImage,value["xy"],(value["size"][1],value["size"][0]))
        img = pygame.transform.rotate(img,-90)
    else:
        img = cropImg(characterImage,value["xy"],value["size"])
    return img

screen = pygame.display.set_mode((640, 480))

characterImage = pygame.image.load(os.path.join("../Assets/image/character/asval/skel/asval.png")).convert_alpha()

with open("../Assets/image/character/asval/skel/asval.atlas.yaml", "r", encoding='utf-8') as f:
    DATA = yaml.load(f.read(),Loader=yaml.FullLoader)

characterParts = {}
for key,value in DATA.items():
    characterParts[key] = loadSpine(characterImage,value)


with open("../Assets/image/character/asval/skel/asval.skel.yaml", "r", encoding='utf-8') as f:
    DATA2 = yaml.load(f.read(),Loader=yaml.FullLoader)

newDATA2Slots = {}
for i in range(len(DATA2["slots"])):
    newDATA2Slots[DATA2["slots"][i]["name"]] = {
        "bone": DATA2["slots"][i]["bone"],
        "attachment": DATA2["slots"][i]["attachment"]
    }
DATA2["slots"] = newDATA2Slots

with open("../Assets/image/character/asval/skel/asval.skel.yaml", "w", encoding='utf-8') as f:
    yaml.dump(DATA2, f, allow_unicode=True)


while True:
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                exit()

    screen.blit(characterParts["body"],(30,30))
    pygame.display.flip()