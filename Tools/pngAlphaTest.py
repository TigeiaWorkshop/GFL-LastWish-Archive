import pygame
from pygame.locals import *
from sys import exit
import os

pygame.init()

# 创建窗口
screen = pygame.display.set_mode((1920, 1080),pygame.SCALED)
path = "../Assets\image\character/2b14/attack/2b14_attack_0.png"
newimage = pygame.image.load(os.path.join(path)).convert_alpha()

newimage.set_alpha(100)
newimage2 = pygame.transform.scale(newimage,(100,100))

while True:
    pygame.draw.rect(screen,(0,0,0),(0,0,600,400))
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                exit()

    screen.blit(newimage,(100,100))
    screen.blit(newimage2,(100,200))

    pygame.display.update()
