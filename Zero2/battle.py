import glob
import os
import time
from sys import exit

import pygame
import yaml
from pygame.locals import *

from Zero2.basic import *
from Zero2.map import *
from Zero2.characterDataManager import *


def battle(chapter_name,window_x,window_y,screen,lang):
    #卸载音乐
    pygame.mixer.music.unload()

    #加载动作：接受角色名，动作，方位，完成对应的指令
    def action_displayer(name,action,x,y,isContinue=True):
        if name in sangvisFerris_name_list:
            gif_dic = sangvisFerris_data[name].gif
            if sangvisFerris_data[name].current_hp < 0:
                sangvisFerris_data[name].current_hp = 0
            current_hp_to_display = hp_font.render(str(sangvisFerris_data[name].current_hp)+"/"+str(sangvisFerris_data[name].max_hp), True, (0,0,0))
            percent_of_hp = sangvisFerris_data[name].current_hp/sangvisFerris_data[name].max_hp
        else:
            gif_dic = characters_data[name].gif
            if characters_data[name].current_hp<0:
                characters_data[name].current_hp = 0
            current_hp_to_display = hp_font.render(str(characters_data[name].current_hp)+"/"+str(characters_data[name].max_hp), True, (0,0,0))
            percent_of_hp = characters_data[name].current_hp/characters_data[name].max_hp
        if percent_of_hp<0:
            percent_of_hp=0

        img_of_char = gif_dic[action][0][0][gif_dic[action][1]]
        screen.blit(img_of_char,(x*green.get_width()-green.get_width()/2,y*green.get_height()-green.get_height()/2))
        if percent_of_hp>0:
            screen.blit(hp_empty,(x*green.get_width(),y*green.get_height()*0.98))
            screen.blit(pygame.transform.scale(hp_red,(int(block_x_length*percent_of_hp),int(block_y_length/5))),(x*green.get_width(),y*green.get_height()*0.98))
            screen.blit(current_hp_to_display,(x*green.get_width(),y*green.get_height()*0.98))
        gif_dic[action][1]+=1
        if gif_dic[action][1] == 5 and action == "attack":
            pass
            #bullets_list.append(Bullet(characters_data.x+img_of_char.get_width()-20,characters_data.y+img_of_char.get_height()/2-5,300))
        if isContinue==True:
            if gif_dic[action][1] == gif_dic[action][0][1]:
                gif_dic[action][1] = 0
        if isContinue=="die":
            if gif_dic[action][1] == gif_dic[action][0][1]:
                gif_dic[action][1] -= 1

    #加载背景图片
    all_env_file_list = glob.glob(r'Assets/img/environment/*.png')
    env_img_list={}
    for i in range(len(all_env_file_list)):
        img_name = all_env_file_list[i].replace("Assets","").replace("img","").replace("environment","").replace(".png","").replace("\\","").replace("/","")
        env_img_list[img_name] = pygame.image.load(os.path.join(all_env_file_list[i])).convert_alpha()

    my_font =pygame.font.SysFont('simsunnsimsun',25)
    #读取并初始化章节信息
    with open("Data/main_chapter/"+chapter_name+"_map.yaml", "r", encoding='utf-8') as f:
        chapter_info = yaml.load(f.read(),Loader=yaml.FullLoader)
        chapter_title = chapter_info["title"]
        block_y = len(chapter_info["map"])
        block_x = len(chapter_info["map"][0])
        characters = chapter_info["character"]
        sangvisFerris = chapter_info["sangvisFerri"]
        theMap = chapter_info["map"]
        bg_music = chapter_info["background_music"]

    #地图方块图片随机化
    with open("Data/blocks.yaml", "r", encoding='utf-8') as f:
        reader = yaml.load(f.read(),Loader=yaml.FullLoader)
        blocks_setting = reader["blocks"]
    map_img_list = randomBlock(theMap,blocks_setting)
    #一个方块的长
    block_x_length = window_x/block_x
    #一个方块的高
    block_y_length = window_y/block_y

    #初始化角色信息
    #hpManager(名字, 最小攻击力, 最大攻击力, 血量上限 , 当前血量, x轴位置，y轴位置，攻击范围，移动范围,gif字典)
    characters_name_list = []
    characters_data = {}
    for jiaose in characters:
        characters_data[jiaose] = characterDataManager(jiaose,characters[jiaose]["min_damage"],characters[jiaose]["max_damage"],characters[jiaose]["max_hp"],characters[jiaose]["current_hp"],characters[jiaose]["x"],characters[jiaose]["y"],characters[jiaose]["attack_range"],characters[jiaose]["move_range"],character_gif_dic(jiaose,block_x_length,block_y_length))
        characters_name_list.append(jiaose)

    sangvisFerris_name_list = []
    sangvisFerris_data = {}
    for enemy in sangvisFerris:
        sangvisFerris_data[enemy] = characterDataManager(enemy,sangvisFerris[enemy]["min_damage"],sangvisFerris[enemy]["max_damage"],sangvisFerris[enemy]["max_hp"],sangvisFerris[enemy]["current_hp"],sangvisFerris[enemy]["x"],sangvisFerris[enemy]["y"],sangvisFerris[enemy]["attack_range"],sangvisFerris[enemy]["move_range"],character_gif_dic(enemy,block_x_length,block_y_length,"sangvisFerri"))
        sangvisFerris_name_list.append(enemy)

    hp_font =pygame.font.SysFont('simsunnsimsun',10)

    #加载UI
    #加载按钮
    with open("Lang/"+lang+".yaml", "r", encoding='utf-8') as f:
        chapter_info = yaml.load(f.read(),Loader=yaml.FullLoader)
        selectMenuButtons_dic = chapter_info["select_menu"]
    selectMenuFont = pygame.font.SysFont('simsunnsimsun',int(block_x_length/2))
    attack_button_txt = selectMenuFont.render(selectMenuButtons_dic["attack"], True, (105,105,105))
    move_button_txt = selectMenuFont.render(selectMenuButtons_dic["move"], True, (105,105,105))
    skill_button_txt = selectMenuFont.render(selectMenuButtons_dic["skill"], True, (105,105,105))
    pass_button_txt = selectMenuFont.render(selectMenuButtons_dic["pass"], True, (105,105,105))
    select_menu_button = pygame.transform.scale(pygame.image.load(os.path.join("Assets/img/UI/menu.png")), (int(block_x_length*2), int(block_x_length/1.3)))
    #加载子弹图片
    bullet_img = pygame.transform.scale(pygame.image.load(os.path.join("Assets/img/UI/bullet.png")), (int(block_x_length/6), int(block_y_length/12)))
    bullets_list = []
    #加载血条
    hp_empty = pygame.transform.scale(pygame.image.load(os.path.join("Assets/img/UI/hp_empty.png")), (int(block_x_length), int(block_y_length/5)))
    hp_red = pygame.transform.scale(pygame.image.load(os.path.join("Assets/img/UI/hp_red.png")), (int(block_x_length), int(block_y_length/5)))
    #绿色方块/方块标准
    green = pygame.transform.scale(pygame.image.load(os.path.join("Assets/img/UI/green.png")), (int(block_x_length), int(block_y_length)))
    green.set_alpha(100)
    red = pygame.transform.scale(pygame.image.load(os.path.join("Assets/img/UI/red.png")), (int(block_x_length), int(block_y_length)))
    red.set_alpha(100)
    the_black = pygame.transform.scale(pygame.image.load(os.path.join("Assets/img/UI/black.png")),(window_x,window_y))
    new_block_type = 0
    per_block_width = green.get_width()
    per_block_height = green.get_height()
    """
    #章节标题
    title_number_display = pygame.font.SysFont('simsunnsimsun',50).render("Chapter1", True, (255,255,255))
    title_main_display = pygame.font.SysFont('simsunnsimsun',50).render(chapter_title, True, (255,255,255))
    for i in range(0,600,1):
        screen.blit(the_black,(0,0))
        title_number_display.set_alpha(i)
        title_main_display.set_alpha(i)
        screen.blit(title_number_display,((window_x-title_number_display.get_width())/2,400))
        screen.blit(title_main_display,((window_x-title_main_display.get_width())/2,500))
        pygame.display.update()
    for i in range(600,0,-1):
        screen.blit(the_black,(0,0))
        title_number_display.set_alpha(i)
        title_main_display.set_alpha(i)
        screen.blit(title_number_display,((window_x-title_number_display.get_width())/2,400))
        screen.blit(title_main_display,((window_x-title_main_display.get_width())/2,500))
        pygame.display.update()
    """
    #部分设定初始化
    the_character_get_click = ""
    enemies_get_attack = ""
    action_choice =""
    green_hide = True
    action_point = len(characters_name_list)#行动值
    battle=True
    how_many_to_move = 0
    how_many_moved = 0

    # 游戏主循环
    while battle==True:
        #加载地图
        for i in range(len(map_img_list)):
            for a in range(len(map_img_list[i])):
                img_display = pygame.transform.scale(env_img_list[map_img_list[i][a]], (int(block_x_length), int(block_y_length*1.5)))
                screen.blit(img_display,(a*block_x_length,(i+1)*block_y_length-int(block_y_length*1.5)))
        #显示选择菜单
        if green_hide == "SelectMenu":
            displayInCenter(attack_button_txt,select_menu_button,characters_data[the_character_get_click].x*green.get_width()-select_menu_button.get_width()-block_x_length*0.5,characters_data[the_character_get_click].y*green.get_height(),screen)
            displayInCenter(move_button_txt,select_menu_button,characters_data[the_character_get_click].x*green.get_width()+select_menu_button.get_width()-block_x_length*0.5,characters_data[the_character_get_click].y*green.get_height(),screen)
            displayInCenter(skill_button_txt,select_menu_button,characters_data[the_character_get_click].x*green.get_width()-block_x_length*0.5,characters_data[the_character_get_click].y*green.get_height()-select_menu_button.get_height()-block_x_length*0.5,screen)
            displayInCenter(pass_button_txt,select_menu_button,characters_data[the_character_get_click].x*green.get_width()-block_x_length*0.5,characters_data[the_character_get_click].y*green.get_height()+select_menu_button.get_height()+block_x_length*0.5,screen)
        #显示攻击或移动范围
        if green_hide == False:
            if action_choice == "move":
                the_moving_range=[]
                for x in range(characters_data[the_character_get_click].x+1,characters_data[the_character_get_click].x+characters_data[the_character_get_click].move_range+1):
                    if blocks_setting[theMap[characters_data[the_character_get_click].y][x]][1] == True:
                        screen.blit(green,(x*green.get_width(),characters_data[the_character_get_click].y*green.get_height()))
                    else:
                        the_moving_range.append(x)
                        for x_red in range(x,characters_data[the_character_get_click].x+characters_data[the_character_get_click].move_range+1):
                            screen.blit(red,(x_red*green.get_width(),characters_data[the_character_get_click].y*green.get_height()))
                        break
                    if(x == characters_data[the_character_get_click].x+characters_data[the_character_get_click].move_range+1):
                        the_moving_range.append(x)
                for x in range(characters_data[the_character_get_click].x-1,characters_data[the_character_get_click].x-characters_data[the_character_get_click].move_range-1,-1):
                    if blocks_setting[theMap[characters_data[the_character_get_click].y][x]][1] == True:
                        screen.blit(green,(x*green.get_width(),characters_data[the_character_get_click].y*green.get_height()))
                    else:
                        the_moving_range.append(x)
                        for x_red in range(x,characters_data[the_character_get_click].x-characters_data[the_character_get_click].move_range-1,-1):
                            screen.blit(red,(x_red*green.get_width(),characters_data[the_character_get_click].y*green.get_height()))
                        break
                    if(x == characters_data[the_character_get_click].x-characters_data[the_character_get_click].move_range-1):
                        the_moving_range.append(x)
                for y in range(characters_data[the_character_get_click].y+1,characters_data[the_character_get_click].y+characters_data[the_character_get_click].move_range+1):
                    if blocks_setting[theMap[y][characters_data[the_character_get_click].x]][1] == True:
                        screen.blit(green,(characters_data[the_character_get_click].x*green.get_width(),y*green.get_height()))
                    else:
                        the_moving_range.append(y)
                        for y_red in range(y,characters_data[the_character_get_click].y+characters_data[the_character_get_click].move_range+1):
                            screen.blit(red,(characters_data[the_character_get_click].x*green.get_width(),y_red*green.get_height()))
                        break
                    if(y == characters_data[the_character_get_click].y+characters_data[the_character_get_click].move_range+1):
                        the_moving_range.append(y)
                for y in range(characters_data[the_character_get_click].y-1,characters_data[the_character_get_click].y-characters_data[the_character_get_click].move_range-1,-1):
                    if blocks_setting[theMap[y][characters_data[the_character_get_click].x]][1] == True:
                        screen.blit(green,(characters_data[the_character_get_click].x*green.get_width(),y*green.get_height()))
                    else:
                        the_moving_range.append(y)
                        for y_red in range(y,characters_data[the_character_get_click].y-characters_data[the_character_get_click].move_range-1,-1):
                            screen.blit(red,(characters_data[the_character_get_click].x*green.get_width(),y_red*green.get_height()))
                        break
                    if(y == characters_data[the_character_get_click].y-characters_data[the_character_get_click].move_range-1):
                        the_moving_range.append(y)
            elif action_choice == "attack":
                attacking_range = []
                for y in range(characters_data[the_character_get_click].y-characters_data[the_character_get_click].attack_range,characters_data[the_character_get_click].y+characters_data[the_character_get_click].attack_range):
                    if y < characters_data[the_character_get_click].y:
                        for x in range(characters_data[the_character_get_click].x-characters_data[the_character_get_click].attack_range-(y-characters_data[the_character_get_click].y)+1,characters_data[the_character_get_click].x+characters_data[the_character_get_click].attack_range+(y-characters_data[the_character_get_click].y)):
                            if blocks_setting[theMap[y][x]][1] == True:
                                    screen.blit(green,(x*green.get_width(),y*green.get_height()))
                                    attacking_range.append([x,y])
                            else:
                                screen.blit(red,(x*green.get_width(),y*green.get_height()))
                    else:
                        for x in range(characters_data[the_character_get_click].x-characters_data[the_character_get_click].attack_range+(y-characters_data[the_character_get_click].y)+1,characters_data[the_character_get_click].x+characters_data[the_character_get_click].attack_range-(y-characters_data[the_character_get_click].y)):
                            if x == characters_data[the_character_get_click].x and y == characters_data[the_character_get_click].y:
                                pass
                            else:
                                if blocks_setting[theMap[y][x]][1] == True:
                                        screen.blit(green,(x*green.get_width(),y*green.get_height()))
                                        attacking_range.append([x,y])
                                else:
                                    screen.blit(red,(x*green.get_width(),y*green.get_height()))
        #玩家输入按键判定
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    exit()
            elif event.type == MOUSEBUTTONDOWN:
                #获取角色坐标
                mouse_x,mouse_y=pygame.mouse.get_pos()
                block_get_click_x = int(mouse_x/green.get_width())
                block_get_click_y = int(mouse_y/green.get_height())
                for key in characters_data:
                    if characters_data[key].x == block_get_click_x and characters_data[key].y == block_get_click_y:
                        if key != the_character_get_click:
                            the_character_get_click = key
                            green_hide = "SelectMenu"
                            break
                        else:
                            green_hide = False
                            the_character_get_click = ""

                """
                if green_hide ==False:
                    if action_choice == "move":
                        if the_moving_range[0]>block_get_click_x>the_moving_range[1] and characters_data[the_character_get_click].y == block_get_click_y:
                                temp_x = characters_data[the_character_get_click].x
                                temp_max = block_get_click_x
                                isWaiting = "LEFTANDRIGHT"
                        elif the_moving_range[2]>block_get_click_y>the_moving_range[3] and characters_data[the_character_get_click].x == block_get_click_x:
                                temp_y = characters_data[the_character_get_click].y
                                temp_max = block_get_click_y
                                isWaiting = "TOPANDBOTTOM"
                    elif action_choice == "attack":
                        pass
                        
                        if characters_data[the_character_get_click].x-characters_data[the_character_get_click].attack_range-1<block_get_click_x<characters_data[the_character_get_click].x+characters_data[the_character_get_click].attack_range+1 and characters_data[the_character_get_click].y == block_get_click_y:
                            for enemies in sangvisFerris_data:
                                if block_get_click_x == sangvisFerris_data[enemies].x and  block_get_click_y == sangvisFerris_data[enemies].y:
                                    isWaiting = "ATTACKING"
                                    enemies_get_attack = enemies
                        elif characters_data[the_character_get_click].y-characters_data[the_character_get_click].attack_range-1<block_get_click_y<characters_data[the_character_get_click].y+characters_data[the_character_get_click].attack_range+1 and characters_data[the_character_get_click].x == block_get_click_x:
                            for enemies in sangvisFerris_data:
                                if block_get_click_x == sangvisFerris_data[enemies].x and  block_get_click_y == sangvisFerris_data[enemies].y:
                                    isWaiting = "ATTACKING"
                                    enemies_get_attack = enemies
                """

        #角色动画
        for every_chara in characters:
            action_displayer(characters_data[every_chara].name,"wait",characters_data[every_chara].x,characters_data[every_chara].y,)
        for enemies in sangvisFerris_data:
            if sangvisFerris_data[enemies].current_hp>0:
                action_displayer(enemies,"wait",sangvisFerris_data[enemies].x,sangvisFerris_data[enemies].y)
            elif sangvisFerris_data[enemies].current_hp<=0:
                action_displayer(enemies,"die",sangvisFerris_data[enemies].x,sangvisFerris_data[enemies].y,"die")

        while pygame.mixer.music.get_busy() != 1:
            pygame.mixer.music.load('Assets/music/'+bg_music)
            pygame.mixer.music.play(loops=9999, start=0.0)

        #画面更新
        time.sleep(0.025)
        pygame.display.update()
