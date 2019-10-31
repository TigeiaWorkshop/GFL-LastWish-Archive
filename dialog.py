import pygame
from pygame.locals import *
from sys import exit
import os
import glob
import yaml
import time
pygame.init()

def dialog_display_function(chapter_name,id=""):
    #加载设置
    with open("setting.yaml", "r", encoding='utf-8') as f:
        setting = yaml.load(f.read(),Loader=yaml.FullLoader)
        window_x = setting['Screen_size_x']
        window_y =  setting['Screen_size_y']
        lang_file = setting['Language']

    # 创建窗口
    screen = pygame.display.set_mode([window_x, window_y])
    pygame.display.set_caption("Girls frontline-Last Wish") #窗口标题

    #读取章节信息
    with open("data/main_chapter/"+chapter_name+".yaml", "r", encoding='utf-8') as f:
        chapter_info = yaml.load(f.read(),Loader=yaml.FullLoader)
        dialog_display = chapter_info["dialog"+id]

    #加载npc立绘
    all_npc_file_list = glob.glob(r'img\npc\*.png')
    npc_img_dic={}
    for i in range(len(all_npc_file_list)):
        img_name = all_npc_file_list[i].replace("img","").replace("npc","").replace(".png","").replace("\\","").replace("/","")
        npc_img_dic[img_name] = pygame.image.load(os.path.join(all_npc_file_list[i])).convert_alpha()
    #加载对话的背景图片（注意是jpg）
    all_dialog_bg_file_list = glob.glob(r'img\dialog_background\*.jpg')
    dialog_bg_img_dic={}
    for i in range(len(all_dialog_bg_file_list)):
        img_name = all_dialog_bg_file_list[i].replace("img","").replace("dialog_background","").replace(".jpg","").replace("\\","").replace("/","")
        dialog_bg_img_dic[img_name] = pygame.transform.scale(pygame.image.load(os.path.join(all_dialog_bg_file_list[i])).convert_alpha(),(window_x,window_y))
    #加载对话框
    dialoguebox = pygame.transform.scale(pygame.image.load(os.path.join("img/others/dialoguebox.png")),(window_x-200,300))
    #鼠标图标
    mouse_none = pygame.transform.scale(pygame.image.load(os.path.join("img/others/mouse_none.png")),(35,35))
    mouse_click = pygame.transform.scale(pygame.image.load(os.path.join("img/others/mouse.png")),(35,35))
    #设定初始化
    display_num = 0
    my_font =pygame.font.SysFont('simsunnsimsun',25)
    dialog_content_id = 1
    mouse_gif_id=1
    while len(dialog_display)!=0 and display_num<len(dialog_display):
        #背景
        screen.blit(dialog_bg_img_dic[dialog_display[display_num][1]],(0,0))

        if len(dialog_display[display_num][0])==2:
            screen.blit(npc_img_dic[dialog_display[display_num][0][0]],(-100,100))
            screen.blit(npc_img_dic[dialog_display[display_num][0][1]],(window_x-1000,100))
        if len(dialog_display[display_num][0])==1:
            #角色
            big_img_x = (window_x - npc_img_dic[dialog_display[display_num][0][0]].get_width())/2
            screen.blit(npc_img_dic[dialog_display[display_num][0][0]],(big_img_x,100))
        #对话框内容
        screen.blit(dialoguebox,(100,window_y-dialoguebox.get_height()-50))
        if dialog_display[display_num][0][0][0:6] == "kalina":
            screen.blit(my_font.render("Kalina", True, (255,255,255)),(500,window_y-dialoguebox.get_height()))
        else:
            screen.blit(my_font.render(dialog_display[display_num][0][0], True, (255,255,255)),(500,window_y-dialoguebox.get_height()))
        screen.blit(my_font.render(dialog_display[display_num][2][0:dialog_content_id], True, (255,255,255)),(440,window_y-dialoguebox.get_height()+70))
        if mouse_gif_id<=20:
            mouse_gif_id+=1
            screen.blit(mouse_click,(dialoguebox.get_width()*0.85,window_y-dialoguebox.get_height()*0.5))
        elif mouse_gif_id==40:
            mouse_gif_id=1
            screen.blit(mouse_none,(dialoguebox.get_width()*0.85,window_y-dialoguebox.get_height()*0.5))
        else:
            mouse_gif_id+=1
            screen.blit(mouse_none,(dialoguebox.get_width()*0.85,window_y-dialoguebox.get_height()*0.5))
        #检测所有字是否都已经播出
        if dialog_content_id != len(dialog_display[display_num][2]):
            dialog_content_id +=1
        #按键判定
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    exit()
            elif event.type == MOUSEBUTTONDOWN:
                display_num += 1
                dialog_content_id = 1

        time.sleep(0.02)
        pygame.display.update()

dialog_display_function("chapter1")
