from sys import exit
import pygame
from pygame.locals import *
pygame.init()


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
path = "../Assets/image/character/asval/attack/asval_attack_0.png"

characterImage1 = pygame.image.load(path)
characterImage1_array = pygame.surfarray.array3d(cropImg(characterImage1,characterImage1.get_bounding_rect()))


darker = 1
for pixel_line in characterImage1_array:
    for pixel_rgb in pixel_line:
        for i in range(3):
            pixel_rgb[i] -= darker
            if pixel_rgb[i] < 0:
                pixel_rgb[i] = 0
        darker += 1

characterImage1 = pygame.surfarray.make_surface(characterImage1_array)

while True:
    screen.fill((255,255,255))
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                exit()
    
    screen.blit(characterImage1,(0,0))
    pygame.display.flip()
