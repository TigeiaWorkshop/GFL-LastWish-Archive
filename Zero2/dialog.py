import glob
from sys import exit

import pygame
import yaml
from pygame.locals import *

from Zero2.basic import *
from Zero2.battle import *

def dialog(chapter_name,window_x,window_y,screen,lang,fps,part):
    #加载动画
    LoadingImgAbove = loadImg("Assets/img/loading_img/LoadingImgAbove.png",window_x+8,window_y/1.7)
    LoadingImgBelow = loadImg("Assets/img/loading_img/LoadingImgBelow.png",window_x+8,window_y/2.05)
    #帧数控制器
    fpsClock = pygame.time.Clock()

    #开始加载
    for i in range(101):
        drawImg(LoadingImgAbove,(-4,LoadingImgAbove.get_height()/100*i-LoadingImgAbove.get_height()),screen)
        drawImg(LoadingImgBelow,(-4,window_y-LoadingImgBelow.get_height()/100*i),screen)
        fpsClock.tick(fps)
        pygame.display.update()
    
    #卸载音乐
    pygame.mixer.music.unload()

    #读取章节信息
    with open("Data/main_chapter/"+chapter_name+"_dialogs_"+lang+".yaml", "r", encoding='utf-8') as f:
        dialog_content = yaml.load(f.read(),Loader=yaml.FullLoader)[part]
    
    #加载npc立绘
    all_npc_file_list = glob.glob(r'Assets/img/npc/*.png')
    npc_img_dic={}
    for i in range(len(all_npc_file_list)):
        img_name = all_npc_file_list[i].replace("Assets","").replace("img","").replace("npc","").replace(".png","").replace("\\","").replace("/","")
        npc_img_dic[img_name] = loadImg(all_npc_file_list[i],window_x/2,window_x/2)
    #加载对话的背景图片（注意是jpg）
    all_dialog_bg_file_list = glob.glob(r'Assets/img/dialog_background/*.jpg')
    dialog_bg_img_dic={}
    for i in range(len(all_dialog_bg_file_list)):
        img_name = all_dialog_bg_file_list[i].replace("Assets","").replace("img","").replace("dialog_background","").replace(".jpg","").replace("\\","").replace("/","")
        dialog_bg_img_dic[img_name] = loadImage(all_dialog_bg_file_list[i],0,0,window_x,window_y)
    
    #加载对话框
    dialoguebox = loadImage("Assets/img/UI/dialoguebox.png",(window_x-window_x/1.4)/2,window_y*0.65,window_x/1.4,window_y/4)
    #鼠标图标
    mouse_none = loadImg("Assets/img/UI/mouse_none.png",window_x/65,window_x/65)
    mouse_click = loadImg("Assets/img/UI/mouse.png",window_x/65,window_x/65)
    #黑色帘幕
    the_black = loadImg("Assets/img/UI/black.png",window_x,window_y)
    #设定初始化
    display_num = 0
    dialog_content_id = 1
    displayed_line = -1
    mouse_gif_id=1
    
    #渐入效果
    for i in range(100,-1,-1):
        drawImage(dialog_bg_img_dic[dialog_content[display_num][1][0]],screen)
        drawImg(LoadingImgAbove,(-4,LoadingImgAbove.get_height()/100*i-LoadingImgAbove.get_height()),screen)
        drawImg(LoadingImgBelow,(-4,window_y-LoadingImgBelow.get_height()/100*i),screen)
        fpsClock.tick(fps)
        pygame.display.update()
    
    the_bg_music = dialog_content[display_num][1][1]
    pygame.mixer.music.load("Assets/music/"+the_bg_music+".mp3")
    pygame.mixer.music.play(loops=9999, start=0.0)

    #主循环
    while len(dialog_content)!=0 and display_num<len(dialog_content):
        #背景
        drawImage(dialog_bg_img_dic[dialog_content[display_num][1][0]],screen)
        #加载对话任务
        if len(dialog_content[display_num][0])==2:
            drawImg(npc_img_dic[dialog_content[display_num][0][0]],(0,window_y-window_x/2),screen)
            drawImg(npc_img_dic[dialog_content[display_num][0][1]],(window_x/2,window_y-window_x/2),screen)
        elif len(dialog_content[display_num][0])==1 and dialog_content[display_num][0][0] != "NAR":
            drawImg(npc_img_dic[dialog_content[display_num][0][0]],(window_x/4,window_y-window_x/2),screen)
        # 对话框图片
        drawImage(dialoguebox,screen)
        #讲述者名称
        drawImg(fontRender(dialog_content[display_num][1][2],"white",window_x/64),(dialoguebox.x+dialoguebox.width/8,dialoguebox.y+dialoguebox.height/8),screen)
        #对话框内容
        if displayed_line >= 0:
            for i in range(displayed_line+1):
                drawImg(fontRender(dialog_content[display_num][2][i],"white",window_x/70),(dialoguebox.x+dialoguebox.width/10,dialoguebox.y+dialoguebox.height*0.35+window_x/65*i),screen)

        drawImg(fontRender(dialog_content[display_num][2][displayed_line+1][0:dialog_content_id],"white",window_x/70),(dialoguebox.x+dialoguebox.width/10,dialoguebox.y+dialoguebox.height*0.35+window_x/65*(displayed_line+1)),screen)
        #检测所有字是否都已经播出
        if dialog_content_id < len(dialog_content[display_num][2][displayed_line+1]):
            dialog_content_id +=1
        else:
            if displayed_line < len(dialog_content[display_num][2])-2:
                dialog_content_id = 1
                displayed_line += 1

        #鼠标gif
        if mouse_gif_id<=20:
            mouse_gif_id+=1
            drawImg(mouse_click,(dialoguebox.x+dialoguebox.width*0.95,dialoguebox.y+dialoguebox.height*0.7),screen)
        elif mouse_gif_id==40:
            mouse_gif_id=1
            drawImg(mouse_none,(dialoguebox.x+dialoguebox.width*0.95,dialoguebox.y+dialoguebox.height*0.7),screen)
        else:
            mouse_gif_id+=1
            drawImg(mouse_none,(dialoguebox.x+dialoguebox.width*0.95,dialoguebox.y+dialoguebox.height*0.7),screen)

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
                    if display_num<len(dialog_content):
                        if the_bg_music != dialog_content[display_num][1][1] and dialog_content[display_num][1][1] != "":
                            the_bg_music = dialog_content[display_num][1][1]
                            pygame.mixer.music.load("Assets/music/"+the_bg_music+".mp3")
                            pygame.mixer.music.play(loops=9999, start=0.0)
                elif pygame.mouse.get_pressed()[2]:
                    if display_num>0:
                        display_num -= 1
                        dialog_content_id = 1
                        displayed_line = -1
                        if the_bg_music != dialog_content[display_num][1][1] and dialog_content[display_num][1][1] != "":
                            the_bg_music = dialog_content[display_num][1][1]
                            pygame.mixer.music.load("Assets/music/"+the_bg_music+".mp3")
                            pygame.mixer.music.play(loops=9999, start=0.0)
        
        fpsClock.tick(fps)
        pygame.display.update()
    
    #淡出
    pygame.mixer.music.fadeout(1000)
    for i in range(0,55,2):
        the_black.set_alpha(i)
        drawImg(the_black,(0,0),screen)
        fpsClock.tick(fps)
        pygame.display.update()
