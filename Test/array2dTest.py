import os
from sys import exit
import pygame
from pygame import display
from pygame.locals import *
import yaml
pygame.init()
import linpg

flags =  pygame.DOUBLEBUF | pygame.SCALED | pygame.FULLSCREEN
screen = pygame.display.set_mode((640, 480),flags)

def cropImg(img,rect):
    cropped = pygame.Surface((rect.width, rect.height),flags=pygame.SRCALPHA).convert_alpha()
    cropped.blit(img,(-rect.x,-rect.y))
    return cropped

img_x = 10
img_y = 10
img_width = 200
img_height = 200
path = "Assets/image/character/asval/attack/asval_attack_0.png"

characterImage1 = linpg.loadImg(path,img_width,img_height)
characterImage2 = linpg.SrcalphaSurface(path,img_x,img_y,img_width,img_height)

while display:
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                exit()
    for i in range(1000):
        #screen.blit(characterImage1,(30,30))
        characterImage2.draw(screen)
    pygame.display.flip()
