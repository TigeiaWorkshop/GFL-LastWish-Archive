import glob
from sys import exit

import pygame
import yaml
from pygame.locals import *

from Zero2.basic import *
from Zero2.battle import *


def dialog(chapter_name,screen,lang,fps,part):
    #获取屏幕的尺寸
    window_x,window_y = screen.get_size()
    #加载动画
    LoadingImgAbove = loadImg("Assets/image/loading_img/LoadingImgAbove.png",window_x+8,window_y/1.7)
    LoadingImgBelow = loadImg("Assets/image/loading_img/LoadingImgBelow.png",window_x+8,window_y/2.05)
    #帧数控制器
    fpsClock = pygame.time.Clock()

    #开始加载-渐入效果
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
    all_npc_file_list = glob.glob(r'Assets/image/npc/*.png')
    npc_img_dic={}
    for i in range(len(all_npc_file_list)):
        img_name = all_npc_file_list[i].replace("Assets","").replace("image","").replace("npc","").replace(".png","").replace("\\","").replace("/","")
        npc_img_dic[img_name] = loadImg(all_npc_file_list[i],window_x/2,window_x/2)
    #加载对话的背景图片（注意是jpg）
    all_dialog_bg_file_list = glob.glob(r'Assets/image/dialog_background/*.jpg')
    dialog_bg_img_dic={}
    for i in range(len(all_dialog_bg_file_list)):
        img_name = all_dialog_bg_file_list[i].replace("Assets","").replace("image","").replace("dialog_background","").replace(".jpg","").replace("\\","").replace("/","")
        dialog_bg_img_dic[img_name] = loadImage(all_dialog_bg_file_list[i],(0,0),window_x,window_y)
    
    #加载对话框
    dialoguebox_max_height = window_y/4
    dialoguebox = loadImage("Assets/image/UI/dialoguebox.png",((window_x-window_x/1.4)/2,window_y*0.65+dialoguebox_max_height/2),window_x/1.4,0)
    #鼠标图标
    mouse_none = loadImg("Assets/image/UI/mouse_none.png",window_x/65,window_x/65)
    mouse_click = loadImg("Assets/image/UI/mouse.png",window_x/65,window_x/65)
    #选项栏
    optionBox = loadImg("Assets/image/UI/option.png")
    #跳过按钮
    skip_button = loadImage("Assets/image/UI/skip.png",(window_x*0.92,window_y*0.05),window_x*0.055,window_x*0.025)
    if_skip = False
    #黑色帘幕
    black_bg = loadImage("Assets/image/UI/black.png",(0,0),window_x,window_y)
    #设定初始化
    dialogId = "head"
    dialog_content_id = 1
    displayed_line = 0
    mouse_gif_id = 1
    videoCapture = None
    surface = pygame.surface.Surface((window_x,window_y))
    the_FPS = fps

    #加载完成-淡出效果
    for i in range(100,-1,-1):
        if dialog_content[dialogId]["background_img"] == None:
            black_bg.draw(screen)
        elif dialog_content[dialogId]["background_img"] in dialog_bg_img_dic:
            dialog_bg_img_dic[dialog_content[dialogId]["background_img"]].draw(screen)
        else:
            if videoCapture == None:
                if os.path.exists("Assets/movie/"+dialog_content[dialogId]["background_img"]) == False:
                    raise Exception('The video file is not exist')
                videoCapture = VideoObject("Assets/movie/"+dialog_content[dialogId]["background_img"],True)
                frames_num = videoCapture.getFrameNum()
                the_FPS = videoCapture.getFPS()
            else:
                videoCapture.display(surface,screen)
        drawImg(LoadingImgAbove,(-4,LoadingImgAbove.get_height()/100*i-LoadingImgAbove.get_height()),screen)
        drawImg(LoadingImgBelow,(-4,window_y-LoadingImgBelow.get_height()/100*i),screen)
        fpsClock.tick(the_FPS)
        pygame.display.update()
    
    #音效
    pygame.mixer.music.load("Assets/music/"+dialog_content[dialogId]["background_music"]+".mp3")
    pygame.mixer.music.play(loops=9999, start=0.0)
    dialog_is_playing_sound = pygame.mixer.Sound("Assets/sound/ui/dialog_words_playing.ogg")

    #玩家在对话时做出的选择
    dialog_options = {}
    the_FPS = fps
    #主循环
    while len(dialog_content)!=0 and if_skip == False:
        #背景
        if dialog_content[dialogId]["background_img"] == None:
            black_bg.draw(screen)
        elif dialog_content[dialogId]["background_img"] in dialog_bg_img_dic:
            dialog_bg_img_dic[dialog_content[dialogId]["background_img"]].draw(screen)
        else:
            if videoCapture == None:
                if os.path.exists("Assets/movie/"+dialog_content[dialogId]["background_img"]) == False:
                    raise Exception('The video file is not exist')
                videoCapture = VideoObject("Assets/movie/"+dialog_content[dialogId]["background_img"],True)
                frames_num = videoCapture.getFrameNum()
                the_FPS = videoCapture.getFPS()
            else:
                videoCapture.display(surface,screen)

        #加载对话人物立绘
        if dialog_content[dialogId]["characters_img"] != None:
            if len(dialog_content[dialogId]["characters_img"])==2:
                drawImg(npc_img_dic[dialog_content[dialogId]["characters_img"][0]],(0,window_y-window_x/2),screen)
                drawImg(npc_img_dic[dialog_content[dialogId]["characters_img"][1]],(window_x/2,window_y-window_x/2),screen)
            elif len(dialog_content[dialogId]["characters_img"])==1:
                drawImg(npc_img_dic[dialog_content[dialogId]["characters_img"][0]],(window_x/4,window_y-window_x/2),screen)
        # 对话框图片
        dialoguebox.draw(screen)
        #跳过按钮
        skip_button.draw(screen)

        if dialoguebox.height < dialoguebox_max_height:
            dialoguebox.height += dialoguebox_max_height/12
            dialoguebox.y -= dialoguebox_max_height/24
        else:
            #讲述者名称
            if dialog_content[dialogId]["narrator"] != None:
                drawImg(fontRender(dialog_content[dialogId]["narrator"],"white",window_x*0.017),(dialoguebox.width*0.1,dialoguebox.height/8),screen,dialoguebox.x,dialoguebox.y)
            #对话框已播放的内容
            for i in range(displayed_line):
                drawImg(fontRender(dialog_content[dialogId]["content"][i],"white",window_x*0.015),(dialoguebox.width*0.075,dialoguebox.height*0.33+window_x*0.02*i),screen,dialoguebox.x,dialoguebox.y)
            #对话框正在播放的内容
            drawImg(fontRender(dialog_content[dialogId]["content"][displayed_line][0:dialog_content_id],"white",window_x*0.015),(dialoguebox.width*0.075,dialoguebox.height*0.33+window_x*0.02*displayed_line),screen,dialoguebox.x,dialoguebox.y)
            #检测所有字是否都已经播出
            if dialog_content_id < len(dialog_content[dialogId]["content"][displayed_line]):
                if pygame.mixer.get_busy() == False:
                    dialog_is_playing_sound.play()
                dialog_content_id +=1
            #当前行的所有字都播出后，播出下一行
            elif displayed_line < len(dialog_content[dialogId]["content"])-1:
                if pygame.mixer.get_busy() == False:
                    dialog_is_playing_sound.play()
                dialog_content_id = 1
                displayed_line += 1
            #当所有行都播出后
            else:
                if pygame.mixer.get_busy() == True:
                    dialog_is_playing_sound.stop()
                if dialog_content[dialogId]["next_dialog_id"] != None and dialog_content[dialogId]["next_dialog_id"][0] == "option":
                    optionBox_y_base = (window_y*3/4-(len(dialog_content[dialogId]["next_dialog_id"])-1)*2*window_x*0.03)/4
                    for i in range(1,len(dialog_content[dialogId]["next_dialog_id"])):
                        option_txt = fontRender(dialog_content[dialogId]["next_dialog_id"][i][0],"white",window_x*0.025)
                        optionBox_scaled = pygame.transform.scale(optionBox,(int(option_txt.get_width()*2),int(window_x*0.05)))
                        optionBox_x = (window_x-optionBox_scaled.get_width())/2
                        optionBox_y = i*2*window_x*0.03+optionBox_y_base
                        displayWithInCenter(option_txt,optionBox_scaled,optionBox_x,optionBox_y,screen)
                        if pygame.mouse.get_pressed()[0] and isHoverOn(optionBox_scaled,(optionBox_x,optionBox_y)):
                            dialog_content_id = 1
                            displayed_line = 0
                            if dialog_content[dialog_content[dialogId]["next_dialog_id"][i][1]]["background_img"] != dialog_content[dialogId]["background_img"]:
                                videoCapture = None
                                the_FPS = fps
                            if dialog_content[dialog_content[dialogId]["next_dialog_id"][i][1]]["background_music"] != dialog_content[dialogId]["background_music"]:
                                pygame.mixer.music.load("Assets/music/"+dialog_content[dialog_content[dialogId]["next_dialog_id"][i][1]]["background_music"]+".mp3")
                                pygame.mixer.music.play(loops=9999, start=0.0)
                            if dialog_content[dialog_content[dialogId]["next_dialog_id"][i][1]]["narrator"] != dialog_content[dialogId]["narrator"]:
                                dialoguebox.height = 0
                                dialoguebox.y = window_y*0.65+dialoguebox_max_height/2
                            dialog_options[len(dialog_options)] = i
                            dialogId = dialog_content[dialogId]["next_dialog_id"][i][1]
                            break

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
                #如果接来下没有文档了或者玩家按到了跳过按钮
                if pygame.mouse.get_pressed()[0]:
                    if isHover(skip_button) or dialog_content[dialogId]["next_dialog_id"] == None:
                        if_skip = True
                    elif displayed_line < len(dialog_content[dialogId]["content"])-1:
                        displayed_line = len(dialog_content[dialogId]["content"])-1
                        dialog_content_id = len(dialog_content[dialogId]["content"][displayed_line])-1
                    elif dialog_content[dialogId]["next_dialog_id"][0] == "default":
                        dialog_content_id = 1
                        displayed_line = 0
                        if dialog_content[dialog_content[dialogId]["next_dialog_id"][1]]["background_img"] != dialog_content[dialogId]["background_img"]:
                            videoCapture = None
                            the_FPS = fps
                        if dialog_content[dialog_content[dialogId]["next_dialog_id"][1]]["background_music"] != dialog_content[dialogId]["background_music"]:
                            pygame.mixer.music.load("Assets/music/"+dialog_content[dialog_content[dialogId]["next_dialog_id"][1]]["background_music"]+".mp3")
                            pygame.mixer.music.play(loops=9999, start=0.0)
                        if dialog_content[dialog_content[dialogId]["next_dialog_id"][1]]["narrator"] != dialog_content[dialogId]["narrator"]:
                            dialoguebox.height = 0
                            dialoguebox.y = window_y*0.65+dialoguebox_max_height/2
                        dialogId = dialog_content[dialogId]["next_dialog_id"][1]
                        dialog_is_playing_sound.stop()
                elif pygame.mouse.get_pressed()[2]:
                    if dialog_content[dialogId]["last_dialog_id"] != None:
                        dialog_content_id = 1
                        displayed_line = 0
                        if dialog_content[dialog_content[dialogId]["last_dialog_id"]]["background_img"] != dialog_content[dialogId]["background_img"]:
                            videoCapture = None
                            the_FPS = fps
                        if dialog_content[dialog_content[dialogId]["last_dialog_id"]]["background_music"] != dialog_content[dialogId]["background_music"]:
                            pygame.mixer.music.load("Assets/music/"+dialog_content[dialog_content[dialogId]["last_dialog_id"]]["background_music"]+".mp3")
                            pygame.mixer.music.play(loops=9999, start=0.0)
                        dialogId = dialog_content[dialogId]["last_dialog_id"]
                        dialog_is_playing_sound.stop()
        
        fpsClock.tick(the_FPS)
        pygame.display.update()
    
    #淡出
    pygame.mixer.music.fadeout(1000)
    for i in range(0,55,2):
        black_bg.set_alpha(i)
        black_bg.draw(screen)
        fpsClock.tick(fps)
        pygame.display.update()

    if len(dialog_options) == 0:
        return True
    else:
        return dialog_options
