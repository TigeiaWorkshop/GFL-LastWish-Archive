import pygame
from pygame.locals import *
from sys import exit

pygame.init()
pygame.mixer.init()
# 创建窗口
screen = pygame.display.set_mode((600, 400),pygame.SCALED)

fontId = 0
allSysFonts = pygame.font.get_fonts()

the_txt = "攻击 技能 开始游戏"
id_can_go = [27, 28, 29, 34, 35, 36, 40, 56, 74, 75, 76, 77, 79,200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213]
new_check = []
for i in range(len(id_can_go)):
    new_check.append(allSysFonts[id_can_go[i]])
print(new_check)
['microsoftjhengheimicrosoftjhengheiui', 'microsoftjhengheimicrosoftjhengheiuibold', 'microsoftjhengheimicrosoftjhengheiuilight', 'microsoftyaheimicrosoftyaheiui','microsoftyaheimicrosoftyaheiuibold', 'microsoftyaheimicrosoftyaheiuilight', 'msgothicmsuigothicmspgothic', 'simsunnsimsun', 'dengxian', 'fangsong', 'kaiti', 'simhei', '方正兰亭超细黑简体', '方正舒体', '方正姚体', '隶书', '幼圆', '华文彩云', '华文仿宋', '华文琥珀', '华文楷体', '华文隶书', '华文宋体', '华文细黑', '华文行楷', '华文新魏', '华文中宋']
"""
while True:
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_s:
                fontId+=1
                print(allSysFonts[fontId],fontId)
                pygame.draw.rect(screen,(0,0,0),(0,0,600,400))
            elif event.key == K_SPACE:
                id_can_go.append(fontId)
                fontId+=1
                print(allSysFonts[fontId],fontId)
                pygame.draw.rect(screen,(0,0,0),(0,0,600,400))
            elif event.key == K_ESCAPE:
                print(id_can_go)
                exit()
    normal_font = pygame.font.SysFont(allSysFonts[fontId],30)
    text_out = normal_font.render(the_txt, True, (255, 255, 255))

    screen.blit(text_out,(100,100))
    
    pygame.display.update()
"""