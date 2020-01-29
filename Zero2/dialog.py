import glob
import os
import time
from sys import exit

import pygame
import yaml
from pygame.locals import *

from Zero2.basic import *
from Zero2.battle import *

def dialog_display_function(chapter_name,window_x,window_y,screen,lang,id=""):
    #加载动画
    LoadingImgAbove = loadImg("Assets/img/loading_img/LoadingImgAbove.png",window_x+5,window_y/1.7)
    LoadingImgBelow = loadImg("Assets/img/loading_img/LoadingImgBelow.png",window_x+5,window_y/2.05)
    for i in range(100):
        printf(LoadingImgAbove,(-3,LoadingImgAbove.get_height()/100*i-LoadingImgAbove.get_height()),screen)
        printf(LoadingImgBelow,(-3,window_y-LoadingImgBelow.get_height()/100*i),screen)
        time.sleep(0.01)
        pygame.display.update()
    
    #卸载音乐
    pygame.mixer.music.unload()
    #读取章节信息
    with open("Data/main_chapter/"+chapter_name+"_dialogs_"+lang+".yaml", "r", encoding='utf-8') as f:
        dialog_display = yaml.load(f.read(),Loader=yaml.FullLoader)["dialog"+id]
    #加载npc立绘
    all_npc_file_list = glob.glob(r'Assets/img/npc/*.png')
    npc_img_dic={}
    for i in range(len(all_npc_file_list)):
        img_name = all_npc_file_list[i].replace("Assets","").replace("img","").replace("npc","").replace(".png","").replace("\\","").replace("/","")
        npc_img_dic[img_name] = pygame.image.load(os.path.join(all_npc_file_list[i]))
    #加载对话的背景图片（注意是jpg）
    all_dialog_bg_file_list = glob.glob(r'Assets/img/dialog_background/*.jpg')
    dialog_bg_img_dic={}
    for i in range(len(all_dialog_bg_file_list)):
        img_name = all_dialog_bg_file_list[i].replace("Assets","").replace("img","").replace("dialog_background","").replace(".jpg","").replace("\\","").replace("/","")
        dialog_bg_img_dic[img_name] = pygame.transform.scale(pygame.image.load(os.path.join(all_dialog_bg_file_list[i])),(window_x,window_y))
    #加载对话框
    dialoguebox = loadImg("Assets/img/UI/dialoguebox.png",window_x/1.2,window_y/3.6)
    #鼠标图标
    mouse_none = loadImg("Assets/img/UI/mouse_none.png",window_x/65,window_x/65)
    mouse_click = loadImg("Assets/img/UI/mouse.png",window_x/65,window_x/65)
    #黑色帘幕
    the_black = loadImg("Assets/img/UI/black.png",window_x,window_y)
    #设定初始化
    display_num = 0
    my_font =pygame.font.SysFont('simsunnsimsun',25)
    dialog_content_id = 1
    displayed_line = -1
    mouse_gif_id=1
    #渐入效果
    for i in range(0,250,2):
        img = dialog_bg_img_dic[dialog_display[display_num][1][0]]
        img.set_alpha(i)
        printf(img,(0,0),screen)
        if len(dialog_display[display_num][0])==2:
            img = npc_img_dic[dialog_display[display_num][0][0]]
            img.set_alpha(i+50)
            printf(img,(-100,100),screen)
            img = npc_img_dic[dialog_display[display_num][0][1]]
            img.set_alpha(i+50)
            printf(img,(window_x-1000,100),screen)
        elif len(dialog_display[display_num][0])==1 and dialog_display[display_num][0][0] != "NAR":
            big_img_x = (window_x - npc_img_dic[dialog_display[display_num][0][0]].get_width())/2
            img = npc_img_dic[dialog_display[display_num][0][0]]
            img.set_alpha(i+50)
            printf(img,(big_img_x,100),screen)
        printf(LoadingImgAbove, (-3,0-LoadingImgAbove.get_height()/250*i),screen)
        printf(LoadingImgBelow, (-3,window_y-LoadingImgBelow.get_height()+LoadingImgBelow.get_height()/250*i),screen)
        pygame.display.update()
    
    the_bg_music = dialog_display[display_num][1][1]
    pygame.mixer.music.load("Assets/music/"+the_bg_music+".mp3")
    pygame.mixer.music.play(loops=9999, start=0.0)

    #主循环
    while len(dialog_display)!=0 and display_num<len(dialog_display):
        
        #背景
        printf(dialog_bg_img_dic[dialog_display[display_num][1][0]],(0,0),screen)
        #加载对话任务
        if len(dialog_display[display_num][0])==2:
            printf(npc_img_dic[dialog_display[display_num][0][0]],(-100,100),screen)
            printf(npc_img_dic[dialog_display[display_num][0][1]],(window_x-1000,100),screen)
        elif len(dialog_display[display_num][0])==1:
            if dialog_display[display_num][0][0] != "NAR":
                big_img_x = (window_x - npc_img_dic[dialog_display[display_num][0][0]].get_width())/2
                printf(npc_img_dic[dialog_display[display_num][0][0]],(big_img_x,100),screen)
        # 对话框图片
        printf(dialoguebox,(100,window_y-dialoguebox.get_height()-50),screen)
        #讲述者名称
        printf(my_font.render(dialog_display[display_num][1][2], True, (255,255,255)),(500,window_y-dialoguebox.get_height()),screen)
        #对话框内容
        if displayed_line >= 0:
            for i in range(displayed_line+1):
                printf(my_font.render(dialog_display[display_num][2][i], True, (255,255,255)),(440,window_y-dialoguebox.get_height()+55+30*i),screen)

        printf(my_font.render(dialog_display[display_num][2][displayed_line+1][0:dialog_content_id], True, (255,255,255)),(440,window_y-dialoguebox.get_height()+55+30*(displayed_line+1)),screen)
        #检测所有字是否都已经播出
        if dialog_content_id < len(dialog_display[display_num][2][displayed_line+1]):
            dialog_content_id +=1
        else:
            if displayed_line < len(dialog_display[display_num][2])-2:
                dialog_content_id = 1
                displayed_line += 1

        #鼠标gif
        if mouse_gif_id<=20:
            mouse_gif_id+=1
            printf(mouse_click,(dialoguebox.get_width()*0.85,window_y-dialoguebox.get_height()*0.48),screen)
        elif mouse_gif_id==40:
            mouse_gif_id=1
            printf(mouse_none,(dialoguebox.get_width()*0.85,window_y-dialoguebox.get_height()*0.48),screen)
        else:
            mouse_gif_id+=1
            printf(mouse_none,(dialoguebox.get_width()*0.85,window_y-dialoguebox.get_height()*0.48),screen)

        #按键判定
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    exit()
            elif event.type == MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    display_num += 1
                    dialog_content_id = 1
                    displayed_line = -1
                    if display_num<len(dialog_display):
                        if dialog_display[display_num][1][1] != the_bg_music and dialog_display[display_num][1][1] != "":
                            the_bg_music = dialog_display[display_num][1][1]
                            pygame.mixer.music.load("Assets/music/"+the_bg_music+".mp3")
                            pygame.mixer.music.play(loops=9999, start=0.0)
                elif pygame.mouse.get_pressed()[2]:
                    if display_num>0:
                        display_num -= 1
                        dialog_content_id = 1
                        displayed_line = -1
                        if display_num<len(dialog_display):
                            if dialog_display[display_num][1][1] != the_bg_music and dialog_display[display_num][1][1] != "":
                                the_bg_music = dialog_display[display_num][1][1]
                                pygame.mixer.music.load("Assets/music/"+the_bg_music+".mp3")
                                pygame.mixer.music.play(loops=9999, start=0.0)
        time.sleep(0.02)
        pygame.display.update()
    
    #淡出
    for i in range(0,55,2):
        the_black.set_alpha(i)
        printf(the_black,(0,0),screen)
        pygame.display.update()
    
    #进入战斗系统
    battle(chapter_name,window_x,window_y,screen,lang)
