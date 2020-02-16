import glob
import math
import time
from sys import exit

import pygame
import yaml
from pygame.locals import *
import gc

from Zero2.basic import *
from Zero2.characterDataManager import *
from Zero2.characterAnimation import *
from Zero2.map import *
from Zero2.AI import *

def battle(chapter_name,window_x,window_y,screen,lang,fps,dark_mode=True):
    #卸载音乐
    pygame.mixer.music.unload()
    #帧数控制器
    fpsClock = pygame.time.Clock()

    #加载动作：接受角色名，动作，方位，完成对应的指令
    def action_displayer(chara_name,action,x,y,isContinue=True,ifFlip=False):
        hidden = False
        hp_img = original_UI_img["hp_green"]
        hp_empty = pygame.transform.scale(original_UI_img["hp_empty"], (int(perBlockWidth), int(perBlockHeight/5)))
        if chara_name in sangvisFerris_data:
            gif_dic = sangvisFerris_data[chara_name].gif_dic
            if sangvisFerris_data[chara_name].current_hp < 0:
                sangvisFerris_data[chara_name].current_hp = 0
            current_hp_to_display = fontRender(str(sangvisFerris_data[chara_name].current_hp)+"/"+str(sangvisFerris_data[chara_name].max_hp),"black",10)
            percent_of_hp = sangvisFerris_data[chara_name].current_hp/sangvisFerris_data[chara_name].max_hp
            current_bullets_situation = fontRender(str(sangvisFerris_data[chara_name].current_bullets)+"/"+str(sangvisFerris_data[chara_name].max_bullets),"black",10)
        elif chara_name in characters_data:
            hidden = characters_data[chara_name].undetected
            gif_dic = characters_data[chara_name].gif_dic
            if characters_data[chara_name].current_hp<=0:
                characters_data[chara_name].current_hp = 0
                if characters_data[chara_name].dying == False:
                    result_of_round["times_characters_down"] += 1
                    characters_data[chara_name].dying = 3
                current_hp_to_display = fontRender(str(characters_data[chara_name].dying)+"/3","black",10)
                percent_of_hp = characters_data[chara_name].dying/3
                hp_img = original_UI_img["hp_red"]
            else:
                if characters_data[chara_name].dying != False:
                    characters_data[chara_name].dying = False
                    gif_dic["die"][1] = 0
                current_hp_to_display = fontRender(str(characters_data[chara_name].current_hp)+"/"+str(characters_data[chara_name].max_hp),"black",10)
                percent_of_hp = characters_data[chara_name].current_hp/characters_data[chara_name].max_hp
            
        if percent_of_hp<0:
            percent_of_hp=0

        img_of_char = pygame.transform.scale(gif_dic[action][0][0][gif_dic[action][1]], (int(perBlockWidth*2), int(perBlockHeight*2)))
        if hidden == True:
            img_of_char.set_alpha(130)
        else:
            img_of_char.set_alpha(300)
        if ifFlip == True:
            drawImg(pygame.transform.flip(img_of_char,True,False),(x*perBlockWidth-perBlockWidth/2,y*perBlockHeight-perBlockHeight/2),screen,local_x,local_y)
        else:
            drawImg(img_of_char,(x*perBlockWidth-perBlockWidth/2,y*perBlockHeight-perBlockHeight/2),screen,local_x,local_y)
        if percent_of_hp>0:
            drawImg(hp_empty,(x*perBlockWidth,y*perBlockHeight*0.98),screen,local_x,local_y)
            drawImg(pygame.transform.scale(hp_img,(int(perBlockWidth*percent_of_hp),int(perBlockHeight/5))),(x*perBlockWidth,y*perBlockHeight*0.98),screen,local_x,local_y)
            drawImg(current_hp_to_display,(x*perBlockWidth,y*perBlockHeight*0.98),screen,local_x,local_y)
            
        gif_dic[action][1]+=1
        if isContinue==True:
            if gif_dic[action][1] == gif_dic[action][0][1]:
                gif_dic[action][1] = 0
        elif isContinue==False:
            if gif_dic[action][1] == gif_dic[action][0][1]:
                gif_dic[action][1]-=1

    #加载按钮的文字
    with open("Lang/"+lang+".yaml", "r", encoding='utf-8') as f:
        loadData = yaml.load(f.read(),Loader=yaml.FullLoader)
        selectMenuButtons_dic = loadData["select_menu"]
        your_round_txt = fontRender(loadData["Battle_UI"]["yourRound"], "white")
        enemy_round_txt = fontRender(loadData["Battle_UI"]["enemyRound"], "white")
        text_now_total_rounds_original = loadData["Battle_UI"]["numRound"]
        chapter_no = loadData["Battle_UI"]["numChapter"]
    
    with open("Data/main_chapter/"+chapter_name+"_dialogs_"+lang+".yaml", "r", encoding='utf-8') as f:
        loadData = yaml.load(f.read(),Loader=yaml.FullLoader)
        chapter_title = loadData["title"]
        battle_info = loadData["battle_info"]
        dialog_during_battle = loadData["dialog_during_battle"]

    #章节标题显示
    the_black = loadImg("Assets/img/UI/black.png",window_x,window_y)
    title_number_display = fontRender(chapter_no.replace("NaN",chapter_name.replace("chapter","")),"white")
    title_main_display = fontRender(chapter_title,"white")

    #渐入效果
    for i in range(0,250,2):
        drawImg(the_black,(0,0),screen)
        title_number_display.set_alpha(i)
        title_main_display.set_alpha(i)
        drawImg(title_number_display,((window_x-title_number_display.get_width())/2,400),screen)
        drawImg(title_main_display,((window_x-title_main_display.get_width())/2,500),screen)
        fpsClock.tick(fps)
        pygame.display.update()

    #加载背景图片
    all_env_file_list = glob.glob(r'Assets/img/environment/*.png')
    env_img_list={}
    for i in range(len(all_env_file_list)):
        img_name = all_env_file_list[i].replace("Assets","").replace("img","").replace("environment","").replace(".png","").replace("\\","").replace("/","")
        env_img_list[img_name] = loadImg(all_env_file_list[i])

    #读取并初始化章节信息
    with open("Data/main_chapter/"+chapter_name+"_map.yaml", "r", encoding='utf-8') as f:
        loadData = yaml.load(f.read(),Loader=yaml.FullLoader)
        block_y = len(loadData["map"])
        block_x = len(loadData["map"][0])
        zoom_in = loadData["zoom_in"]
        local_x = loadData["local_x"]
        local_y = loadData["local_y"]
        characters = loadData["character"]
        sangvisFerris = loadData["sangvisFerri"]
        theMap = loadData["map"]
        bg_music = loadData["background_music"]

    if zoom_in < 1:
        zoom_in = 1
    elif zoom_in > 2:
        zoom_in = 2
    perBlockWidth = window_x/block_x*zoom_in
    perBlockHeight = window_y/block_y*zoom_in

    if local_x+window_x/block_x*0.25*len(theMap[0]) >0:
        local_x=0
    if local_y+window_y/block_y*0.25*len(theMap)>0:
        local_y=0
    
    #地图方块图片随机化
    with open("Data/blocks.yaml", "r", encoding='utf-8') as f:
        loadData = yaml.load(f.read(),Loader=yaml.FullLoader)
        blocks_setting = loadData["blocks"]
    
    map_img_list = randomBlock(theMap,blocks_setting)
    
    #加载雪花
    all_snow_img = glob.glob(r'Assets/img/environment/snow/*.png')
    snow_list = []
    for snowflake in all_snow_img:
        snow_list.append(loadImg(snowflake))

    all_snow_img_len = len(snow_list)-1
    all_snow_on_screen = []
    for i in range(100):
        the_snow_add_y = random.randint(1,window_y)
        the_snow_add_x = random.randint(1,window_x*1.5)
        the_snow_add_img = snow_list[random.randint(0,all_snow_img_len)]
        all_snow_on_screen.append(loadImage(the_snow_add_img,the_snow_add_x,the_snow_add_y,int(window_x/200),int(window_x/200)))

    del all_snow_img,snow_list,all_snow_img_len
    gc.collect()

    #初始化角色信息
    #hpManager(名字, 最小攻击力, 最大攻击力, 血量上限 , 当前血量, x轴位置，y轴位置，攻击范围，移动范围,gif字典)
    characters_data = {}
    for each_character in characters:
        characters_data[each_character] = characterDataManager(characters[each_character]["action_point"],characters[each_character]["attack_range"],characters[each_character]["current_bullets"],characters[each_character]["current_hp"],characters[each_character]["effective_range"],character_gif_dic(each_character,perBlockWidth,perBlockHeight),characters[each_character]["max_bullets"],characters[each_character]["max_damage"],characters[each_character]["max_hp"],characters[each_character]["min_damage"],characters[each_character]["x"],characters[each_character]["y"],characters[each_character]["start_position"],characters[each_character]["undetected"])

    sangvisFerris_data = {}
    for each_character in sangvisFerris:
        sangvisFerris_data[each_character] = sangvisFerriDataManager(sangvisFerris[each_character]["action_point"],sangvisFerris[each_character]["attack_range"],sangvisFerris[each_character]["current_bullets"],sangvisFerris[each_character]["current_hp"],sangvisFerris[each_character]["effective_range"],character_gif_dic(sangvisFerris[each_character]["type"],perBlockWidth,perBlockHeight,"sangvisFerri"),sangvisFerris[each_character]["max_bullets"],sangvisFerris[each_character]["max_damage"],sangvisFerris[each_character]["max_hp"],sangvisFerris[each_character]["min_damage"],sangvisFerris[each_character]["x"],sangvisFerris[each_character]["y"],sangvisFerris[each_character]["patrol_path"])

    #加载对话时角色的图标
    all_icon_file_list = glob.glob(r'Assets/img/npc_icon/*.png')
    character_icon_img_list={}
    for i in range(len(all_icon_file_list)):
        img_name = all_icon_file_list[i].replace("Assets","").replace("img","").replace("npc_icon","").replace(".png","").replace("\\","").replace("/","")
        character_icon_img_list[img_name] = loadImg(all_icon_file_list[i],window_y*0.08,window_y*0.08)

    #加载UI
    #加载结束回合的图片
    end_round_button = loadImage("Assets/img/UI/endRound.png",window_x*0.8,window_y*0.7,window_x/10, window_y/10)
    #加载选择菜单的图片
    select_menu_button_original = loadImg("Assets/img/UI/menu.png")
    #加载子弹图片
    bullet_img = loadImg("Assets/img/UI/bullet.png", perBlockWidth/6, perBlockHeight/12)
    bullets_list = []
    #加载血条,各色方块等UI图片 size:perBlockWidth, perBlockHeight/5
    original_UI_img = {
        "hp_empty" : loadImg("Assets/img/UI/hp_empty.png"),
        "hp_red" : loadImg("Assets/img/UI/hp_red.png"),
        "hp_green" : loadImg("Assets/img/UI/hp_green.png"),
        "action_point_blue" : loadImg("Assets/img/UI/action_point.png"),
        "bullets_number_brown" : loadImg("Assets/img/UI/bullets_number.png"),
        "green" : loadImg("Assets/img/UI/green.png",None,None,100),
        "red" : loadImg("Assets/img/UI/red.png",None,None,100),
        "black" : loadImg("Assets/img/UI/black.png",None,None,100),
        #计分板
        "score" : loadImage("Assets/img/UI/score.png",200,200,300,600),
    }
    the_character_get_click_info_board = loadImage("Assets/img/UI/score.png",0,window_y-window_y/6,window_x/5,window_y/6)
    green = pygame.transform.scale(original_UI_img["green"], (math.ceil(perBlockWidth), math.ceil(perBlockHeight)))
    red = pygame.transform.scale(original_UI_img["red"], (math.ceil(perBlockWidth), math.ceil(perBlockHeight)))
    black = pygame.transform.scale(original_UI_img["black"], (math.ceil(perBlockWidth), math.ceil(perBlockHeight)))

    #文字
    text_of_endround_move = 0
    text_of_endround_alpha = 400
    
    #部分设定初始化
    the_character_get_click = ""
    enemies_get_attack = ""
    enemies_in_control = ""
    action_choice =""
    green_hide = True
    battle=True
    how_many_to_move = 0
    how_many_moved = 0
    isWaiting = True
    the_dead_one = ""
    whose_round = "sangvisFerrisToPlayer"
    mouse_move_temp_x = -1
    mouse_move_temp_y = -1
    total_rounds = 1
    enemies_in_control_id= 0
    #计算光亮区域
    light_area = calculate_darkness(characters_data)
    # 移动路径
    the_route = []
    #上个回合因为暴露被敌人发现的角色
    #格式：角色：[x,y]
    the_characters_detected_last_round = {}
    enemy_action = None
    result_of_round = {
        "total_kills" : 0,
        "total_time" : time.time(),
        "times_characters_down" : 0
    }
    #行走的声音
    all_walking_sounds = glob.glob(r'Assets/sound/snow/*.wav')
    walk_on_snow_sound = []
    for i in range(len(all_walking_sounds)):
        walk_on_snow_sound.append(pygame.mixer.Sound(all_walking_sounds[i]))
    the_sound_id = None
    
    battle_info_line1 = fontRender(battle_info[0],"white",25)
    battle_info_line2 = fontRender(battle_info[1],"white",25)
    #显示章节信息
    for i in range(0,250,2):
        drawImg(the_black,(0,0),screen)
        battle_info_line1.set_alpha(i)
        battle_info_line2.set_alpha(i)
        drawImg(title_number_display,((window_x-title_number_display.get_width())/2,400),screen)
        drawImg(title_main_display,((window_x-title_main_display.get_width())/2,500),screen)
        drawImg(battle_info_line1,(perBlockWidth,window_y*0.8),screen)
        drawImg(battle_info_line2,(perBlockWidth,window_y*0.8+battle_info_line1.get_height()*2),screen)
        fpsClock.tick(fps)
        pygame.display.update()
    
    #加载音乐
    pygame.mixer.music.load("Assets/music/"+bg_music)
    pygame.mixer.music.play(loops=9999, start=0.0)
    pygame.mixer.music.set_volume(0.5)

    #加载完成，章节标题淡出
    if dialog_during_battle == None:
        for a in range(250,0,-5):
            #加载地图
            for y in range(len(map_img_list)):
                for x in range(len(map_img_list[y])):
                    if -perBlockWidth<=x*perBlockWidth+local_x <= window_x and -perBlockHeight*1.5<=(y-0.5)*perBlockHeight+local_y<= window_y:
                        img_display = pygame.transform.scale(env_img_list[map_img_list[y][x]], (int(perBlockWidth), int(perBlockHeight*1.5)))
                        drawImg(img_display,(x*perBlockWidth,(y-0.5)*perBlockHeight),screen,local_x,local_y)
            #加载阴影区
            for y in range(len(map_img_list)):
                for x in range(len(map_img_list[y])):
                    if -perBlockWidth<=x*perBlockWidth+local_x <= window_x and -perBlockHeight<=y*perBlockHeight+local_y<= window_y and (x,y) not in light_area and dark_mode == True:
                        drawImg(black,(x*perBlockWidth,y*perBlockHeight),screen,local_x,local_y)
            #角色动画
            for every_chara in characters_data:
                if theMap[characters_data[every_chara].y][characters_data[every_chara].x] == 2:
                    characters_data[every_chara].undetected = True
                else:
                    characters_data[every_chara].undetected = False
                action_displayer(every_chara,"wait",characters_data[every_chara].x,characters_data[every_chara].y)
            for enemies in sangvisFerris_data:
                if (sangvisFerris_data[enemies].x,sangvisFerris_data[enemies].y) in light_area or dark_mode != True:
                    action_displayer(enemies,"wait",sangvisFerris_data[enemies].x,sangvisFerris_data[enemies].y)
            #加载雪花
            for i in range(len(all_snow_on_screen)):
                drawImage(all_snow_on_screen[i],screen,local_x,local_y)
                all_snow_on_screen[i].x -= 10*zoom_in
                all_snow_on_screen[i].y += 20*zoom_in
                if all_snow_on_screen[i].x <= 0 or all_snow_on_screen[i].y+local_y >= 1080:
                    all_snow_on_screen[i].y = random.randint(-100,0)
                    all_snow_on_screen[i].x = random.randint(0,window_x*2)
            the_black.set_alpha(a)
            drawImg(the_black,(0,0),screen)
            title_number_display.set_alpha(a)
            title_main_display.set_alpha(a)
            drawImg(title_number_display,((window_x-title_number_display.get_width())/2,400),screen)
            drawImg(title_main_display,((window_x-title_main_display.get_width())/2,500),screen)
            battle_info_line1.set_alpha(a)
            battle_info_line2.set_alpha(a)
            drawImg(battle_info_line1,(perBlockWidth,window_y*0.8),screen)
            drawImg(battle_info_line2,(perBlockWidth,window_y*0.8+battle_info_line1.get_height()*2),screen)
            fpsClock.tick(fps)
            pygame.display.flip()
    elif dialog_during_battle != None:
        #建立地图
        map2d=Array2D(len(theMap[0]),len(theMap))
        #历遍地图，设置障碍方块
        for y in range(len(theMap)):
            for x in range(len(theMap[y])):
                if blocks_setting[theMap[y][x]]["canPassThrough"] == False:
                    map2d[x][y]=1
        # 历遍所有角色，将角色的坐标点设置为障碍方块
        for every_chara in sangvisFerris_data:
            map2d[sangvisFerris_data[every_chara].x][sangvisFerris_data[every_chara].y] = 1
        all_characters_path = {}
        for every_chara in characters_data:
            #创建AStar对象,并设置起点和终点为
            star_point_x = characters_data[every_chara].start_position[0]
            star_point_y = characters_data[every_chara].start_position[1]
            aStar=AStar(map2d,Point(star_point_x,star_point_y),Point(characters_data[every_chara].x,characters_data[every_chara].y))
            #开始寻路
            pathList=aStar.start()
            #遍历路径点,讲指定数量的点放到路径列表中
            the_route = []
            if pathList != None:
                for i in range(len(pathList)):
                    if Point(star_point_x+1,star_point_y) in pathList and [star_point_x+1,star_point_y] not in the_route:
                        star_point_x+=1
                    elif Point(star_point_x-1,star_point_y) in pathList and [star_point_x-1,star_point_y] not in the_route:
                        star_point_x-=1
                    elif Point(star_point_x,star_point_y+1) in pathList and [star_point_x,star_point_y+1] not in the_route:
                        star_point_y+=1
                    elif Point(star_point_x,star_point_y-1) in pathList and [star_point_x,star_point_y-1] not in the_route:
                        star_point_y-=1
                    the_route.append([star_point_x,star_point_y])
            else:
                raise Exception('Waring: '+every_chara+" cannot find her path, please rewrite her start position!")
            all_characters_path[every_chara] = the_route

        txt_alpha = 250
        while len(all_characters_path)>0:
            #加载地图
            for y in range(len(map_img_list)):
                for x in range(len(map_img_list[y])):
                    if -perBlockWidth<=x*perBlockWidth+local_x <= window_x and -perBlockHeight*1.5<=(y-0.5)*perBlockHeight+local_y<= window_y:
                        img_display = pygame.transform.scale(env_img_list[map_img_list[y][x]], (int(perBlockWidth), int(perBlockHeight*1.5)))
                        drawImg(img_display,(x*perBlockWidth,(y-0.5)*perBlockHeight),screen,local_x,local_y)
            #加载阴影区
            for y in range(len(map_img_list)):
                for x in range(len(map_img_list[y])):
                    if -perBlockWidth<=x*perBlockWidth+local_x <= window_x and -perBlockHeight<=y*perBlockHeight+local_y<= window_y and (x,y) not in light_area and dark_mode == True:
                        drawImg(black,(x*perBlockWidth,y*perBlockHeight),screen,local_x,local_y)

            key_to_remove = []
            for every_chara in all_characters_path:
                if all_characters_path[every_chara] != []:
                    if pygame.mixer.get_busy() == False:
                        the_sound_id = random.randint(0,len(walk_on_snow_sound)-1)
                        walk_on_snow_sound[the_sound_id].play()
                    if characters_data[every_chara].start_position[0] < all_characters_path[every_chara][0][0]:
                        characters_data[every_chara].start_position[0]+=0.125
                        action_displayer(every_chara,"move",characters_data[every_chara].start_position[0],characters_data[every_chara].start_position[1])
                        if characters_data[every_chara].start_position[0] >= all_characters_path[every_chara][0][0]:
                            characters_data[every_chara].start_position[0] = all_characters_path[every_chara][0][0]
                            all_characters_path[every_chara].pop(0)
                    elif characters_data[every_chara].start_position[0] > all_characters_path[every_chara][0][0]:
                        characters_data[every_chara].start_position[0]-=0.125
                        action_displayer(every_chara,"move",characters_data[every_chara].start_position[0],characters_data[every_chara].start_position[1],True,True)
                        if characters_data[every_chara].start_position[0] <= all_characters_path[every_chara][0][0]:
                            characters_data[every_chara].start_position[0] = all_characters_path[every_chara][0][0]
                            all_characters_path[every_chara].pop(0)
                    elif characters_data[every_chara].start_position[1] < all_characters_path[every_chara][0][1]:
                        characters_data[every_chara].start_position[1]+=0.125
                        action_displayer(every_chara,"move",characters_data[every_chara].start_position[0],characters_data[every_chara].start_position[1])
                        if characters_data[every_chara].start_position[1] >= all_characters_path[every_chara][0][1]:
                            characters_data[every_chara].start_position[1] = all_characters_path[every_chara][0][1]
                            all_characters_path[every_chara].pop(0)
                    elif characters_data[every_chara].start_position[1] > all_characters_path[every_chara][0][1]:
                        characters_data[every_chara].start_position[1]-=0.125
                        action_displayer(every_chara,"move",characters_data[every_chara].start_position[0],characters_data[every_chara].start_position[1])
                        if characters_data[every_chara].start_position[1] <= all_characters_path[every_chara][0][1]:
                            characters_data[every_chara].start_position[1] = all_characters_path[every_chara][0][1]
                            all_characters_path[every_chara].pop(0)
                else:
                    key_to_remove.append(every_chara)
            light_area = calculate_darkness_before_battle(characters_data)
            for i in range(len(key_to_remove)):
                all_characters_path.pop(key_to_remove[i])
            #角色动画
            for every_chara in characters_data:
                if every_chara not in all_characters_path:
                    if theMap[characters_data[every_chara].y][characters_data[every_chara].x] == 2:
                        characters_data[every_chara].undetected = True
                    else:
                        characters_data[every_chara].undetected = False
                    action_displayer(every_chara,"wait",characters_data[every_chara].start_position[0],characters_data[every_chara].start_position[1])
            for enemies in sangvisFerris_data:
                if (sangvisFerris_data[enemies].x,sangvisFerris_data[enemies].y) in light_area or dark_mode != True:
                    action_displayer(enemies,"wait",sangvisFerris_data[enemies].x,sangvisFerris_data[enemies].y)

            #加载雪花
            for i in range(len(all_snow_on_screen)):
                drawImage(all_snow_on_screen[i],screen,local_x,local_y)
                all_snow_on_screen[i].x -= 10*zoom_in
                all_snow_on_screen[i].y += 20*zoom_in
                if all_snow_on_screen[i].x <= 0 or all_snow_on_screen[i].y+local_y >= 1080:
                    all_snow_on_screen[i].y = random.randint(-100,0)
                    all_snow_on_screen[i].x = random.randint(0,window_x*2)
            
            if txt_alpha >= 0:
                the_black.set_alpha(txt_alpha)
                drawImg(the_black,(0,0),screen)
                title_number_display.set_alpha(txt_alpha)
                title_main_display.set_alpha(txt_alpha)
                drawImg(title_number_display,((window_x-title_number_display.get_width())/2,400),screen)
                drawImg(title_main_display,((window_x-title_main_display.get_width())/2,500),screen)
                battle_info_line1.set_alpha(txt_alpha)
                battle_info_line2.set_alpha(txt_alpha)
                drawImg(battle_info_line1,(perBlockWidth,window_y*0.8),screen)
                drawImg(battle_info_line2,(perBlockWidth,window_y*0.8+battle_info_line1.get_height()*2),screen)
                txt_alpha -= 5
            #画面更新
            fpsClock.tick(fps)
            pygame.display.update()
        #脚步停止
        walk_on_snow_sound[the_sound_id].stop()
        #加载对话框图片
        dialoguebox_up = loadImage("Assets/img/UI/dialoguebox.png",window_x,window_y/2-window_y*0.35,window_x*0.3,window_y*0.15)
        dialoguebox_down = loadImage(pygame.transform.flip(dialoguebox_up.img,True,False),-window_x*0.3,window_y/2+window_y*0.2,window_x*0.3,window_y*0.15)
        #设定初始化
        display_num = 0
        dialog_up_content_id = 0
        dialog_down_content_id = 0
        dialog_up_displayed_line = 0
        dialog_down_displayed_line = 0
        dialog = True
        #开始对话
        while dialog == True:
            #玩家输入按键判定
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        exit()
                elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                    if display_num < len(dialog_during_battle)-1:
                        display_num += 1
                        #检测上方对话框
                        if dialog_during_battle[display_num]["dialoguebox_up"] != None:
                            if dialog_during_battle[display_num-1]["dialoguebox_up"] != None:
                                if dialog_during_battle[display_num]["dialoguebox_up"]["speaker"] != dialog_during_battle[display_num-1]["dialoguebox_up"]["speaker"]:
                                    dialoguebox_up.x = window_x
                                    dialog_up_content_id = 0
                                    dialog_up_displayed_line = 0
                                elif dialog_during_battle[display_num]["dialoguebox_up"]["content"] != dialog_during_battle[display_num-1]["dialoguebox_up"]["content"]:
                                    dialog_up_content_id = 0
                                    dialog_up_displayed_line = 0
                            else:
                                dialoguebox_up.x = window_x
                                dialog_up_content_id = 0
                                dialog_up_displayed_line = 0
                        else:
                            dialoguebox_up.x = window_x
                            dialog_up_content_id = 0
                            dialog_up_displayed_line = 0
                        #检测下方对话框    
                        if dialog_during_battle[display_num]["dialoguebox_down"] != None:
                            if dialog_during_battle[display_num-1]["dialoguebox_down"] != None:
                                if dialog_during_battle[display_num]["dialoguebox_down"]["speaker"] != dialog_during_battle[display_num-1]["dialoguebox_down"]["speaker"]:
                                    dialoguebox_down.x = -window_x*0.3
                                    dialog_down_content_id = 0
                                    dialog_down_displayed_line = 0
                                elif dialog_during_battle[display_num]["dialoguebox_down"]["content"] != dialog_during_battle[display_num-1]["dialoguebox_down"]["content"]:
                                    dialog_down_content_id = 0
                                    dialog_down_displayed_line = 0
                            else:
                                dialoguebox_down.x = -window_x*0.3
                                dialog_down_content_id = 0
                                dialog_down_displayed_line = 0
                        else:
                            dialoguebox_down.x = -window_x*0.3
                            dialog_down_content_id = 0
                            dialog_down_displayed_line = 0
                    else:
                        dialog = False

            #加载地图
            for y in range(len(map_img_list)):
                for x in range(len(map_img_list[y])):
                    if -perBlockWidth<=x*perBlockWidth+local_x <= window_x and -perBlockHeight*1.5<=(y-0.5)*perBlockHeight+local_y<= window_y:
                        img_display = pygame.transform.scale(env_img_list[map_img_list[y][x]], (int(perBlockWidth), int(perBlockHeight*1.5)))
                        drawImg(img_display,(x*perBlockWidth,(y-0.5)*perBlockHeight),screen,local_x,local_y)
            #加载阴影区
            for y in range(len(map_img_list)):
                for x in range(len(map_img_list[y])):
                    if -perBlockWidth<=x*perBlockWidth+local_x <= window_x and -perBlockHeight<=y*perBlockHeight+local_y<= window_y and (x,y) not in light_area and dark_mode == True:
                        drawImg(black,(x*perBlockWidth,y*perBlockHeight),screen,local_x,local_y)
                
            #角色动画
            for every_chara in characters_data:
                if theMap[characters_data[every_chara].y][characters_data[every_chara].x] == 2:
                    characters_data[every_chara].undetected = True
                else:
                    characters_data[every_chara].undetected = False
                action_displayer(every_chara,"wait",characters_data[every_chara].start_position[0],characters_data[every_chara].start_position[1])
            for enemies in sangvisFerris_data:
                if (sangvisFerris_data[enemies].x,sangvisFerris_data[enemies].y) in light_area or dark_mode != True:
                    action_displayer(enemies,"wait",sangvisFerris_data[enemies].x,sangvisFerris_data[enemies].y)

            #加载雪花
            for i in range(len(all_snow_on_screen)):
                drawImage(all_snow_on_screen[i],screen,local_x,local_y)
                all_snow_on_screen[i].x -= 10*zoom_in
                all_snow_on_screen[i].y += 20*zoom_in
                if all_snow_on_screen[i].x <= 0 or all_snow_on_screen[i].y+local_y >= 1080:
                    all_snow_on_screen[i].y = random.randint(-100,0)
                    all_snow_on_screen[i].x = random.randint(0,window_x*2)
                
            if dialoguebox_up.x > window_x/2+dialoguebox_up.width*0.4:
                dialoguebox_up.x -= 150
            if dialoguebox_down.x < window_x/2-dialoguebox_down.width*1.4:
                dialoguebox_down.x += 150

            #上方对话框
            if dialog_during_battle[display_num]["dialoguebox_up"] != None:
                #对话框图片
                drawImage(dialoguebox_up,screen)
                #名字
                if dialog_during_battle[display_num]["dialoguebox_up"]["speaker"] != None:
                    drawImg(fontRender(dialog_during_battle[display_num]["dialoguebox_up"]["speaker"],"white",window_x/80),(dialoguebox_up.width/7,dialoguebox_up.height/11),screen,dialoguebox_up.x,dialoguebox_up.y)
                #正在播放的行
                content = fontRender(dialog_during_battle[display_num]["dialoguebox_up"]["content"][dialog_up_displayed_line][:dialog_up_content_id],"white",window_x/80)
                drawImg(content,(window_x/45,window_x/35+dialog_up_displayed_line*window_x/80),screen,dialoguebox_up.x,dialoguebox_up.y)
                if dialog_up_content_id < len(dialog_during_battle[display_num]["dialoguebox_up"]["content"][dialog_up_displayed_line]):
                    dialog_up_content_id+=1
                elif dialog_up_displayed_line < len(dialog_during_battle[display_num]["dialoguebox_up"]["content"])-1:
                    dialog_up_displayed_line += 1
                    dialog_up_content_id = 0
                for i in range(dialog_up_displayed_line):
                    content = fontRender(dialog_during_battle[display_num]["dialoguebox_up"]["content"][i],"white",window_x/80)
                    drawImg(content,(window_x/45,window_x/35+i*window_x/80),screen,dialoguebox_up.x,dialoguebox_up.y)
                #角色图标
                if dialog_during_battle[display_num]["dialoguebox_up"]["speaker_icon"] != None:
                    drawImg(character_icon_img_list[dialog_during_battle[display_num]["dialoguebox_up"]["speaker_icon"]],(window_x*0.24,window_x/40),screen,dialoguebox_up.x,dialoguebox_up.y)
            #下方对话框
            if dialog_during_battle[display_num]["dialoguebox_down"] != None:
                #对话框图片
                drawImage(dialoguebox_down,screen)
                #名字
                if dialog_during_battle[display_num]["dialoguebox_down"]["speaker"] != None:
                    drawImg(fontRender(dialog_during_battle[display_num]["dialoguebox_down"]["speaker"],"white",window_x/80),(dialoguebox_down.width*0.75,dialoguebox_down.height/10),screen,dialoguebox_down.x,dialoguebox_down.y)
                #正在播放的行
                content = fontRender(dialog_during_battle[display_num]["dialoguebox_down"]["content"][dialog_down_displayed_line][:dialog_down_content_id],"white",window_x/80)
                drawImg(content,(window_x/15,window_x/35+dialog_down_displayed_line*window_x/80),screen,dialoguebox_down.x,dialoguebox_down.y)
                if dialog_down_content_id < len(dialog_during_battle[display_num]["dialoguebox_down"]["content"][dialog_down_displayed_line]):
                    dialog_down_content_id+=1
                elif dialog_down_displayed_line < len(dialog_during_battle[display_num]["dialoguebox_down"]["content"])-1:
                    dialog_down_displayed_line += 1
                    dialog_down_content_id = 0
                for i in range(dialog_down_displayed_line):
                    content = fontRender(dialog_during_battle[display_num]["dialoguebox_down"]["content"][i],"white",window_x/80)
                    drawImg(content,(window_x/15,window_x/35+i*window_x/80),screen,dialoguebox_down.x,dialoguebox_down.y)
                #角色图标
                if dialog_during_battle[display_num]["dialoguebox_down"]["speaker_icon"] != None:
                    drawImg(character_icon_img_list[dialog_during_battle[display_num]["dialoguebox_down"]["speaker_icon"]],(window_x*0.01,window_x/40),screen,dialoguebox_down.x,dialoguebox_down.y)

            #画面更新
            fpsClock.tick(fps)
            pygame.display.update()

    # 游戏主循环
    while battle==True:
        #玩家输入按键判定-任何情况
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    green_hide = True
                    the_character_get_click = ""
                    isWaiting = True
                    action_choice = ""
                if event.key == K_m:
                    exit()
            elif event.type == MOUSEBUTTONDOWN:
                #上下滚轮-放大和缩小图片
                if event.button == 4:
                    if zoom_in < 2:
                        zoom_in += 0.25
                        perBlockWidth = window_x/block_x*zoom_in
                        perBlockHeight = window_y/block_y*zoom_in
                        local_x -= window_x/block_x*0.25*len(map_img_list[0])
                        local_y -= window_y/block_y*0.25*len(map_img_list)
                elif event.button == 5:
                    if zoom_in > 1:
                        zoom_in -= 0.25
                        perBlockWidth = window_x/block_x*zoom_in
                        perBlockHeight = window_y/block_y*zoom_in
                        local_x += window_x/block_x*0.25*len(map_img_list[0])
                        if local_x >0:
                            local_x=0
                        local_y += window_y/block_y*0.25*len(map_img_list)
                        if local_y>0:
                            local_y = 0
            #移动屏幕
            if pygame.mouse.get_pressed()[2]:
                mouse_x,mouse_y=pygame.mouse.get_pos()
                if mouse_move_temp_x == -1 and mouse_move_temp_y == -1:
                    mouse_move_temp_x = mouse_x
                    mouse_move_temp_y = mouse_y
                else:
                    if mouse_move_temp_x != mouse_x or mouse_move_temp_y != mouse_y:
                        if mouse_move_temp_x > mouse_x:
                            if local_x+mouse_move_temp_x-mouse_x <= 0:
                                local_x += mouse_move_temp_x-mouse_x
                        elif mouse_move_temp_x < mouse_x:
                            if local_x-(mouse_x - mouse_move_temp_x) >= 0 - perBlockWidth*len(map_img_list[0]) + window_x:
                                local_x -= mouse_x-mouse_move_temp_x
                        if mouse_move_temp_y > mouse_y:
                            if local_y+mouse_move_temp_y-mouse_y <= 0:
                                local_y += mouse_move_temp_y-mouse_y
                        elif mouse_move_temp_y < mouse_y:
                            if local_y-(mouse_y-mouse_move_temp_y) >= 0 - perBlockHeight*len(map_img_list) + window_y:
                                local_y -= mouse_y-mouse_move_temp_y
                        mouse_move_temp_x = mouse_x
                        mouse_move_temp_y = mouse_y
            else:
                mouse_move_temp_x = -1
                mouse_move_temp_y = -1
        
        #加载UI
        if green.get_width() != math.ceil(perBlockWidth) and green.get_height() != math.ceil(perBlockHeight):
            green = pygame.transform.scale(original_UI_img["green"], (math.ceil(perBlockWidth), math.ceil(perBlockHeight)))
            red = pygame.transform.scale(original_UI_img["red"], (math.ceil(perBlockWidth), math.ceil(perBlockHeight)))
            black = pygame.transform.scale(original_UI_img["black"], (math.ceil(perBlockWidth), math.ceil(perBlockHeight)))
        
        #加载地图
        for y in range(len(map_img_list)):
            for x in range(len(map_img_list[y])):
                if -perBlockWidth<=x*perBlockWidth+local_x <= window_x and -perBlockHeight*1.5<=(y-0.5)*perBlockHeight+local_y<= window_y:
                    img_display = pygame.transform.scale(env_img_list[map_img_list[y][x]], (int(perBlockWidth), int(perBlockHeight*1.5)))
                    drawImg(img_display,(x*perBlockWidth,(y-0.5)*perBlockHeight),screen,local_x,local_y)
        #加载阴影区
        for y in range(len(map_img_list)):
            for x in range(len(map_img_list[y])):
                if -perBlockWidth<=x*perBlockWidth+local_x <= window_x and -perBlockHeight<=y*perBlockHeight+local_y<= window_y and (x,y) not in light_area and dark_mode == True:
                    drawImg(black,(x*perBlockWidth,y*perBlockHeight),screen,local_x,local_y)

        #↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓角色动画展示区↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓#
        # 我方角色动画
        for every_chara in characters_data:
            if every_chara != the_character_get_click:
                if theMap[characters_data[every_chara].y][characters_data[every_chara].x] == 2:
                    characters_data[every_chara].undetected = True
                else:
                    characters_data[every_chara].undetected = False
                if characters_data[every_chara].dying == False:
                    action_displayer(every_chara,"wait",characters_data[every_chara].x,characters_data[every_chara].y)
                else:
                    action_displayer(every_chara,"die",characters_data[every_chara].x,characters_data[every_chara].y,False)
        #敌方动画
        for enemies in sangvisFerris_data:
            if enemies != enemies_in_control:
                if sangvisFerris_data[enemies].current_hp>0:
                    if (sangvisFerris_data[enemies].x,sangvisFerris_data[enemies].y) in light_area or dark_mode != True:
                        if green_hide == True and pygame.mouse.get_pressed()[2]:
                            mouse_x,mouse_y=pygame.mouse.get_pos()
                            block_get_click_x2 = int((mouse_x-local_x)/perBlockWidth)
                            block_get_click_y2 = int((mouse_y-local_y)/perBlockHeight)
                            if block_get_click_x2 == sangvisFerris_data[enemies].x and block_get_click_y2 == sangvisFerris_data[enemies].y:
                                for y in range(sangvisFerris_data[enemies].y-sangvisFerris_data[enemies].effective_range,sangvisFerris_data[enemies].y+sangvisFerris_data[enemies].effective_range):
                                    if y < sangvisFerris_data[enemies].y:
                                        for x in range(sangvisFerris_data[enemies].x-sangvisFerris_data[enemies].effective_range-(y-sangvisFerris_data[enemies].y)+1,sangvisFerris_data[enemies].x+sangvisFerris_data[enemies].effective_range+(y-sangvisFerris_data[enemies].y)):
                                            if blocks_setting[theMap[y][x]]["canPassThrough"] == True:
                                                drawImg(green,(x*perBlockWidth,y*perBlockHeight),screen,local_x,local_y)
                                            else:
                                                drawImg(red,(x*perBlockWidth,y*perBlockHeight),screen,local_x,local_y)
                                    else:
                                        for x in range(sangvisFerris_data[enemies].x-sangvisFerris_data[enemies].effective_range+(y-sangvisFerris_data[enemies].y)+1,sangvisFerris_data[enemies].x+sangvisFerris_data[enemies].effective_range-(y-sangvisFerris_data[enemies].y)):
                                            if x == sangvisFerris_data[enemies].x and y == sangvisFerris_data[enemies].y:
                                                pass
                                            else:
                                                if blocks_setting[theMap[y][x]]["canPassThrough"] == True:
                                                    drawImg(green,(x*perBlockWidth,y*perBlockHeight),screen,local_x,local_y)
                                                else:
                                                    drawImg(red,(x*perBlockWidth,y*perBlockHeight),screen,local_x,local_y)
                        action_displayer(enemies,"wait",sangvisFerris_data[enemies].x,sangvisFerris_data[enemies].y)
                elif sangvisFerris_data[enemies].current_hp<=0:
                    action_displayer(enemies,"die",sangvisFerris_data[enemies].x,sangvisFerris_data[enemies].y,False)
                    the_dead_one = enemies
        if the_dead_one != "":
            the_characters_attacking = sangvisFerris_data[the_dead_one].gif_dic
            if the_characters_attacking["die"][1] == the_characters_attacking["die"][0][1]-1:
                sangvisFerris_data.pop(the_dead_one)
                result_of_round["total_kills"]+=1
            the_dead_one=""
        #↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑角色动画展示区↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑#

        #玩家回合
        if whose_round == "player":
            #加载结束回合的按钮
            drawImage(end_round_button,screen)
            #玩家输入按键判定-玩家回合限定
            if pygame.mouse.get_pressed()[0]:
                mouse_x,mouse_y=pygame.mouse.get_pos()
                #获取角色坐标
                block_get_click_x = int((mouse_x-local_x)/perBlockWidth)
                block_get_click_y = int((mouse_y-local_y)/perBlockHeight)
                #如果点击了回合结束的按钮
                if isHover(end_round_button) and isWaiting == True:
                    whose_round = "playerToSangvisFerris"
                    the_character_get_click = ""
                    green_hide = True
                #是否在显示移动范围后点击了且点击区域在移动范围内
                elif the_route != [] and [block_get_click_x,block_get_click_y] in the_route and green_hide==False:
                    isWaiting = "MOVING"
                    green_hide = True
                    characters_data[the_character_get_click].current_action_point -= len(the_route)
                else:
                    #控制选择菜单的显示与隐藏
                    for key in characters_data:
                        if characters_data[key].x == block_get_click_x and characters_data[key].y == block_get_click_y and isWaiting == True and action_choice != "skill" and characters_data[key].dying == False:
                            the_character_get_click = key
                            green_hide = "SelectMenu"
                            break

            #显示选择菜单
            if green_hide == "SelectMenu":
                #左下角的角色信息
                text_size = 20
                drawImage(the_character_get_click_info_board,screen)
                padding = (the_character_get_click_info_board.height-character_icon_img_list[the_character_get_click].get_height())/2
                drawImg(character_icon_img_list[the_character_get_click],(padding,padding),screen,the_character_get_click_info_board.x,the_character_get_click_info_board.y)
                tcgc_hp1 = fontRender("HP: ","white",20)
                tcgc_hp2 = fontRender(str(characters_data[the_character_get_click].current_hp)+"/"+str(characters_data[the_character_get_click].max_hp),"black",20)
                tcgc_action_point1 = fontRender("AP: ","white",20)
                tcgc_action_point2 = fontRender(str(characters_data[the_character_get_click].current_action_point)+"/"+str(characters_data[the_character_get_click].max_action_point),"black",20)
                tcgc_bullets_situation1 = fontRender("BP: ","white",20)
                tcgc_bullets_situation2 = fontRender(str(characters_data[the_character_get_click].current_bullets)+"/"+str(characters_data[the_character_get_click].max_bullets),"black",20)
                drawImg(tcgc_hp1,(character_icon_img_list[the_character_get_click].get_width()*2,padding),screen,the_character_get_click_info_board.x,the_character_get_click_info_board.y)
                drawImg(tcgc_action_point1,(character_icon_img_list[the_character_get_click].get_width()*2,padding+text_size*1.5),screen,the_character_get_click_info_board.x,the_character_get_click_info_board.y)
                drawImg(tcgc_bullets_situation1,(character_icon_img_list[the_character_get_click].get_width()*2,padding+text_size*3),screen,the_character_get_click_info_board.x,the_character_get_click_info_board.y)
                hp_empty = pygame.transform.scale(original_UI_img["hp_empty"],(int(the_character_get_click_info_board.width/3),int(text_size)))
                drawImg(hp_empty,(character_icon_img_list[the_character_get_click].get_width()*2.4,padding),screen,the_character_get_click_info_board.x,the_character_get_click_info_board.y)
                drawImg(hp_empty,(character_icon_img_list[the_character_get_click].get_width()*2.4,padding+text_size*1.5),screen,the_character_get_click_info_board.x,the_character_get_click_info_board.y)
                drawImg(hp_empty,(character_icon_img_list[the_character_get_click].get_width()*2.4,padding+text_size*3),screen,the_character_get_click_info_board.x,the_character_get_click_info_board.y)
                drawImg(pygame.transform.scale(original_UI_img["hp_green"],(int(hp_empty.get_width()*characters_data[the_character_get_click].current_hp/characters_data[the_character_get_click].max_hp),int(text_size))),(character_icon_img_list[the_character_get_click].get_width()*2.4,padding),screen,the_character_get_click_info_board.x,the_character_get_click_info_board.y)
                drawImg(pygame.transform.scale(original_UI_img["action_point_blue"],(int(hp_empty.get_width()*characters_data[the_character_get_click].current_action_point/characters_data[the_character_get_click].max_action_point),int(text_size))),(character_icon_img_list[the_character_get_click].get_width()*2.4,padding+text_size*1.5),screen,the_character_get_click_info_board.x,the_character_get_click_info_board.y)
                drawImg(pygame.transform.scale(original_UI_img["bullets_number_brown"],(int(hp_empty.get_width()*characters_data[the_character_get_click].current_bullets/characters_data[the_character_get_click].max_bullets),int(text_size))),(character_icon_img_list[the_character_get_click].get_width()*2.4,padding+text_size*3),screen,the_character_get_click_info_board.x,the_character_get_click_info_board.y)
                displayInCenter(tcgc_hp2,hp_empty,character_icon_img_list[the_character_get_click].get_width()*2.4,padding,screen,the_character_get_click_info_board.x,the_character_get_click_info_board.y)
                displayInCenter(tcgc_action_point2,hp_empty,character_icon_img_list[the_character_get_click].get_width()*2.4,padding+text_size*1.5,screen,the_character_get_click_info_board.x,the_character_get_click_info_board.y)
                displayInCenter(tcgc_bullets_situation2,hp_empty,character_icon_img_list[the_character_get_click].get_width()*2.4,padding+text_size*3,screen,the_character_get_click_info_board.x,the_character_get_click_info_board.y)
                select_menu_button = pygame.transform.scale(select_menu_button_original, (int(perBlockWidth*2), int(perBlockWidth/1.3)))
                #选择菜单
                displayWithInCenter(fontRender(selectMenuButtons_dic["attack"],"black",int(perBlockWidth/2)),select_menu_button,characters_data[the_character_get_click].x*perBlockWidth-select_menu_button.get_width()-perBlockWidth*0.5,characters_data[the_character_get_click].y*perBlockHeight,screen,local_x,local_y)
                displayWithInCenter(fontRender(selectMenuButtons_dic["move"],"black",int(perBlockWidth/2)),select_menu_button,characters_data[the_character_get_click].x*perBlockWidth+select_menu_button.get_width()-perBlockWidth*0.5,characters_data[the_character_get_click].y*perBlockHeight,screen,local_x,local_y)
                displayWithInCenter(fontRender(selectMenuButtons_dic["skill"],"black",int(perBlockWidth/2)),select_menu_button,characters_data[the_character_get_click].x*perBlockWidth-perBlockWidth*0.5,characters_data[the_character_get_click].y*perBlockHeight-select_menu_button.get_height()-perBlockWidth*0.5,screen,local_x,local_y)
                displayWithInCenter(fontRender(selectMenuButtons_dic["reload"],"black",int(perBlockWidth/2)),select_menu_button,characters_data[the_character_get_click].x*perBlockWidth-perBlockWidth*0.5,characters_data[the_character_get_click].y*perBlockHeight+select_menu_button.get_height()+perBlockWidth*0.5,screen,local_x,local_y)
                if pygame.mouse.get_pressed()[0]:
                    if isHoverOn(select_menu_button,(characters_data[the_character_get_click].x*perBlockWidth-select_menu_button.get_width()-perBlockWidth*0.5,characters_data[the_character_get_click].y*perBlockHeight),local_x,local_y):
                        if characters_data[the_character_get_click].current_bullets > 0:
                            time.sleep(0.05)
                            action_choice = "attack"
                            block_get_click_x = -100
                            block_get_click_y = -100
                            green_hide = False
                    elif isHoverOn(select_menu_button,(characters_data[the_character_get_click].x*perBlockWidth+select_menu_button.get_width()-perBlockWidth*0.5,characters_data[the_character_get_click].y*perBlockHeight),local_x,local_y):
                        action_choice = "move"
                        time.sleep(0.05)
                        block_get_click_x = -100
                        block_get_click_y = -100
                        green_hide = False
                    elif isHoverOn(select_menu_button,(characters_data[the_character_get_click].x*perBlockWidth-perBlockWidth*0.5,characters_data[the_character_get_click].y*perBlockHeight-select_menu_button.get_height()-perBlockWidth*0.5),local_x,local_y):
                        action_choice = "skill"
                        time.sleep(0.05)
                        block_get_click_x = -100
                        block_get_click_y = -100
                        green_hide = False
                    elif isHoverOn(select_menu_button,(characters_data[the_character_get_click].x*perBlockWidth-perBlockWidth*0.5,characters_data[the_character_get_click].y*perBlockHeight+select_menu_button.get_height()+perBlockWidth*0.5),local_x,local_y):
                        action_choice = "reload"
                        block_get_click_x = -100
                        block_get_click_y = -100
                        green_hide = False
            #显示攻击或移动范围
            elif green_hide == False and characters_data[the_character_get_click].current_action_point > 0 and the_character_get_click != "":
                #显示移动范围
                if action_choice == "move":
                    mouse_x,mouse_y=pygame.mouse.get_pos()
                    block_get_click_x = int((mouse_x-local_x)/perBlockWidth)
                    block_get_click_y = int((mouse_y-local_y)/perBlockHeight)
                    #建立地图
                    map2d=Array2D(len(theMap[0]),len(theMap))
                    #历遍地图，设置障碍方块
                    for y in range(len(theMap)):
                        for x in range(len(theMap[y])):
                            if blocks_setting[theMap[y][x]]["canPassThrough"] == False:
                                map2d[x][y]=1
                    # 历遍所有角色，将角色的坐标点设置为障碍方块
                    all_characters_data = dicMerge(characters_data,sangvisFerris_data)
                    for every_chara in all_characters_data:
                        map2d[all_characters_data[every_chara].x][all_characters_data[every_chara].y] = 1
                    #创建AStar对象,并设置起点和终点为
                    star_point_x = characters_data[the_character_get_click].x
                    star_point_y = characters_data[the_character_get_click].y
                    aStar=AStar(map2d,Point(star_point_x,star_point_y),Point(block_get_click_x,block_get_click_y))
                    #开始寻路
                    pathList=aStar.start()
                    #遍历路径点,讲指定数量的点放到路径列表中
                    the_route = []
                    if pathList != None:
                        if len(pathList)>characters_data[the_character_get_click].current_action_point:
                            route_len = characters_data[the_character_get_click].current_action_point
                        else:
                            route_len = len(pathList)
                        for i in range(route_len):
                            if Point(star_point_x+1,star_point_y) in pathList and [star_point_x+1,star_point_y] not in the_route:
                                star_point_x+=1
                            elif Point(star_point_x-1,star_point_y) in pathList and [star_point_x-1,star_point_y] not in the_route:
                                star_point_x-=1
                            elif Point(star_point_x,star_point_y+1) in pathList and [star_point_x,star_point_y+1] not in the_route:
                                star_point_y+=1
                            elif Point(star_point_x,star_point_y-1) in pathList and [star_point_x,star_point_y-1] not in the_route:
                                star_point_y-=1
                            else:
                                #快速跳出
                                break
                            the_route.append([star_point_x,star_point_y])
                    #显示路径
                    for i in range(len(the_route)):
                        drawImg(green,(the_route[i][0]*perBlockWidth,the_route[i][1]*perBlockHeight),screen,local_x,local_y)

                #显示攻击范围        
                if action_choice == "attack":
                    attacking_range = []
                    for y in range(characters_data[the_character_get_click].y-characters_data[the_character_get_click].effective_range,characters_data[the_character_get_click].y+characters_data[the_character_get_click].effective_range):
                        if y < characters_data[the_character_get_click].y:
                            for x in range(characters_data[the_character_get_click].x-characters_data[the_character_get_click].effective_range-(y-characters_data[the_character_get_click].y)+1,characters_data[the_character_get_click].x+characters_data[the_character_get_click].effective_range+(y-characters_data[the_character_get_click].y)):
                                if blocks_setting[theMap[y][x]]["canPassThrough"] == True:
                                    drawImg(green,(x*perBlockWidth,y*perBlockHeight),screen,local_x,local_y)
                                    attacking_range.append([x,y])
                        else:
                            for x in range(characters_data[the_character_get_click].x-characters_data[the_character_get_click].effective_range+(y-characters_data[the_character_get_click].y)+1,characters_data[the_character_get_click].x+characters_data[the_character_get_click].effective_range-(y-characters_data[the_character_get_click].y)):
                                if x == characters_data[the_character_get_click].x and y == characters_data[the_character_get_click].y:
                                    pass
                                else:
                                    if blocks_setting[theMap[y][x]]["canPassThrough"] == True:
                                        drawImg(green,(x*perBlockWidth,y*perBlockHeight),screen,local_x,local_y)
                                        attacking_range.append([x,y])
                    if [block_get_click_x,block_get_click_y] in attacking_range:
                        for enemies in sangvisFerris_data:
                            if block_get_click_x == sangvisFerris_data[enemies].x and  block_get_click_y == sangvisFerris_data[enemies].y:
                                isWaiting = "ATTACKING"
                                enemies_get_attack = enemies
                                green_hide = True
                                break
                #显示技能范围        
                elif action_choice == "skill":
                    skill_range = []
                    for y in range(characters_data[the_character_get_click].y-characters_data[the_character_get_click].effective_range,characters_data[the_character_get_click].y+characters_data[the_character_get_click].effective_range):
                        if y < characters_data[the_character_get_click].y:
                            for x in range(characters_data[the_character_get_click].x-characters_data[the_character_get_click].effective_range-(y-characters_data[the_character_get_click].y)+1,characters_data[the_character_get_click].x+characters_data[the_character_get_click].effective_range+(y-characters_data[the_character_get_click].y)):
                                if blocks_setting[theMap[y][x]]["canPassThrough"] == True:
                                    drawImg(green,(x*perBlockWidth,y*perBlockHeight),screen,local_x,local_y)
                                    skill_range.append([x,y])
                        else:
                            for x in range(characters_data[the_character_get_click].x-characters_data[the_character_get_click].effective_range+(y-characters_data[the_character_get_click].y)+1,characters_data[the_character_get_click].x+characters_data[the_character_get_click].effective_range-(y-characters_data[the_character_get_click].y)):
                                if x == characters_data[the_character_get_click].x and y == characters_data[the_character_get_click].y:
                                    pass
                                else:
                                    if blocks_setting[theMap[y][x]]["canPassThrough"] == True:
                                        drawImg(green,(x*perBlockWidth,y*perBlockHeight),screen,local_x,local_y)
                                        skill_range.append([x,y])
                    if [block_get_click_x,block_get_click_y] in skill_range:
                        if the_character_get_click == "gsh-18":
                            for character in characters_data:
                                if block_get_click_x == characters_data[character].x and  block_get_click_y == characters_data[character].y:
                                    isWaiting = "ATTACKING"
                                    enemies_get_attack = character
                                    green_hide = True
                                    break
                        else:
                            for enemies in sangvisFerris_data:
                                if block_get_click_x == sangvisFerris_data[enemies].x and  block_get_click_y == sangvisFerris_data[enemies].y:
                                    isWaiting = "ATTACKING"
                                    enemies_get_attack = enemies
                                    green_hide = True
                                    break
                elif action_choice == "reload":
                    if characters_data[the_character_get_click].max_bullets-characters_data[the_character_get_click].current_bullets > 0:
                        #向上取整
                        characters_data[the_character_get_click].current_action_point -= math.ceil((characters_data[the_character_get_click].max_bullets-characters_data[the_character_get_click].current_bullets)/2)
                        characters_data[the_character_get_click].current_bullets = characters_data[the_character_get_click].max_bullets
                    else:
                        #无需换弹                                      
                        pass
            
            #当有角色被点击时
            if the_character_get_click != "":
                #被点击的角色动画
                if isWaiting == "MOVING":
                    green_hide=True
                    if the_route != []:
                        if pygame.mixer.get_busy() == False:
                            the_sound_id = random.randint(0,len(walk_on_snow_sound)-1)
                            walk_on_snow_sound[the_sound_id].play()
                        if characters_data[the_character_get_click].x < the_route[0][0]:
                            characters_data[the_character_get_click].x+=0.125
                            action_displayer(the_character_get_click,"move",characters_data[the_character_get_click].x,characters_data[the_character_get_click].y)
                            if characters_data[the_character_get_click].x >= the_route[0][0]:
                                characters_data[the_character_get_click].x = the_route[0][0]
                                the_route.pop(0)
                        elif characters_data[the_character_get_click].x > the_route[0][0]:
                            characters_data[the_character_get_click].x-=0.125
                            action_displayer(the_character_get_click,"move",characters_data[the_character_get_click].x,characters_data[the_character_get_click].y,True,True)
                            if characters_data[the_character_get_click].x <= the_route[0][0]:
                                characters_data[the_character_get_click].x = the_route[0][0]
                                the_route.pop(0)
                        elif characters_data[the_character_get_click].y < the_route[0][1]:
                            characters_data[the_character_get_click].y+=0.125
                            action_displayer(the_character_get_click,"move",characters_data[the_character_get_click].x,characters_data[the_character_get_click].y)
                            if characters_data[the_character_get_click].y >= the_route[0][1]:
                                characters_data[the_character_get_click].y = the_route[0][1]
                                the_route.pop(0)
                        elif characters_data[the_character_get_click].y > the_route[0][1]:
                            characters_data[the_character_get_click].y-=0.125
                            action_displayer(the_character_get_click,"move",characters_data[the_character_get_click].x,characters_data[the_character_get_click].y)
                            if characters_data[the_character_get_click].y <= the_route[0][1]:
                                characters_data[the_character_get_click].y = the_route[0][1]
                                the_route.pop(0)
                    else:
                        walk_on_snow_sound[the_sound_id].stop()
                        isWaiting =True
                        the_character_get_click = ""
                    light_area = calculate_darkness(characters_data)
                elif isWaiting == "ATTACKING":
                    green_hide=True
                    if action_choice == "attack":
                        if sangvisFerris_data[enemies_get_attack].x < characters_data[the_character_get_click].x:
                            action_displayer(the_character_get_click,"attack",characters_data[the_character_get_click].x,characters_data[the_character_get_click].y,False,True)
                        else:
                            action_displayer(the_character_get_click,"attack",characters_data[the_character_get_click].x,characters_data[the_character_get_click].y,False)
                        if characters_data[the_character_get_click].gif_dic["attack"][1] == characters_data[the_character_get_click].gif_dic["attack"][0][1]-2:
                            sangvisFerris_data[enemies_get_attack].decreaseHp(characters_data[the_character_get_click].min_damage,characters_data[the_character_get_click].max_damage)
                        the_characters_attacking = characters_data[the_character_get_click].gif_dic
                        if the_characters_attacking["attack"][1] == the_characters_attacking["attack"][0][1]-1:
                            the_characters_attacking["attack"][1] = 0
                            characters_data[the_character_get_click].current_bullets -= 1
                            isWaiting = True
                            the_character_get_click = ""
                            action_choice = ""
                    if action_choice == "skill":
                        action_displayer(the_character_get_click,"skill",characters_data[the_character_get_click].x,characters_data[the_character_get_click].y,False)
                        if characters_data[the_character_get_click].gif_dic["skill"][1] == characters_data[the_character_get_click].gif_dic["skill"][0][1]-2:
                            if the_character_get_click == "gsh-18":
                                characters_data[enemies_get_attack].heal(characters_data[the_character_get_click].min_damage)
                                if characters_data[enemies_get_attack].current_hp > characters_data[enemies_get_attack].max_hp:
                                    characters_data[enemies_get_attack].current_hp = characters_data[enemies_get_attack].max_hp
                            else:
                                sangvisFerris_data[enemies_get_attack].decreaseHp(characters_data[the_character_get_click].min_damage,characters_data[the_character_get_click].max_damage)
                        the_characters_attacking = characters_data[the_character_get_click].gif_dic
                        if the_characters_attacking["skill"][1] == the_characters_attacking["skill"][0][1]-1:
                            the_characters_attacking["skill"][1] = 0
                            isWaiting =True
                            the_character_get_click = ""
                            action_choice = ""
                elif isWaiting == True:
                    action_displayer(the_character_get_click,"wait",characters_data[the_character_get_click].x,characters_data[the_character_get_click].y)

        #↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓中间检测区↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓#
        if whose_round == "playerToSangvisFerris" or whose_round == "sangvisFerrisToPlayer":
            text_now_total_rounds = text_now_total_rounds_original
            text_now_total_rounds = fontRender(text_now_total_rounds.replace("NaN",str(total_rounds)), "white")
            if text_of_endround_move < (window_x-your_round_txt.get_width()*2)/2:
                text_of_endround_move += perBlockWidth*2
            if text_of_endround_move >= (window_x-your_round_txt.get_width()*2)/2-30:
                text_now_total_rounds.set_alpha(text_of_endround_alpha)
                your_round_txt.set_alpha(text_of_endround_alpha)
                enemy_round_txt.set_alpha(text_of_endround_alpha)
                text_of_endround_alpha -= 5
            
            drawImg(text_now_total_rounds,(text_of_endround_move,(window_y-your_round_txt.get_height()*2.5)/2),screen)
            if whose_round == "sangvisFerrisToPlayer":
                drawImg(your_round_txt,(window_x-text_of_endround_move-your_round_txt.get_width(),(window_y-your_round_txt.get_height()*2.5)/2+your_round_txt.get_height()*1.5),screen)
            if whose_round == "playerToSangvisFerris":
                drawImg(enemy_round_txt,(window_x-text_of_endround_move-your_round_txt.get_width(),(window_y-your_round_txt.get_height()*2.5)/2+your_round_txt.get_height()*1.5),screen)
            if text_of_endround_alpha <=0:
                if whose_round == "playerToSangvisFerris":
                    sangvisFerris_name_list = []
                    for every_chara in sangvisFerris_data:
                        sangvisFerris_name_list.append(every_chara)
                    for every_chara in characters_data:
                        if characters_data[every_chara].dying != False:
                            characters_data[every_chara].dying -= 1
                    whose_round = "sangvisFerris"
                elif whose_round == "sangvisFerrisToPlayer":
                    enemies_in_control_id = 0
                    characters_detect_this_round = {}
                    for key in characters_data:
                        characters_data[key].current_action_point = characters_data[key].max_action_point
                        if characters_data[key].undetected == False:
                            characters_detect_this_round[key] = [characters_data[key].x,characters_data[key].y]
                    whose_round = "player"
                text_of_endround_alpha = 400
                text_of_endround_move = 0
                text_now_total_rounds.set_alpha(text_of_endround_alpha)
                your_round_txt.set_alpha(text_of_endround_alpha)
                enemy_round_txt.set_alpha(text_of_endround_alpha)

        #检测所有敌人是否都已经被消灭
        if len(sangvisFerris_data) == 0 and whose_round != "result":
            whose_round = "result_win"
        
        #↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑中间检测区↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑#
        #敌方回合
        if whose_round == "sangvisFerris":
            enemies_in_control = sangvisFerris_name_list[enemies_in_control_id]
            if enemy_action == None:
                enemy_action = AI(enemies_in_control,theMap,characters_data,sangvisFerris_data,the_characters_detected_last_round,blocks_setting)
                print(enemies_in_control+" choses "+enemy_action[0])
            if enemy_action[0] == "attack":
                if (sangvisFerris_data[enemies_in_control].x,sangvisFerris_data[enemies_in_control].y) in light_area or dark_mode != True:
                    action_displayer(enemies_in_control,"attack",sangvisFerris_data[enemies_in_control].x,sangvisFerris_data[enemies_in_control].y,False)
                if sangvisFerris_data[enemies_in_control].gif_dic["attack"][1] == sangvisFerris_data[enemies_in_control].gif_dic["attack"][0][1]-2:
                    characters_data[enemy_action[1]].decreaseHp(sangvisFerris_data[enemies_in_control].min_damage,sangvisFerris_data[enemies_in_control].max_damage)
                the_characters_attacking = sangvisFerris_data[enemies_in_control].gif_dic
                if the_characters_attacking["attack"][1] == the_characters_attacking["attack"][0][1]-1:
                    the_characters_attacking["attack"][1] = 0
                    enemies_in_control_id +=1
                    if enemies_in_control_id == len(sangvisFerris_data):
                        whose_round = "sangvisFerrisToPlayer"
                        total_rounds += 1
                    enemy_action = None
                    enemies_in_control = ""
            elif enemy_action[0] == "move":
                the_route = enemy_action[1]
                if the_route != []:
                    if pygame.mixer.get_busy() == False:
                        the_sound_id = random.randint(0,len(walk_on_snow_sound)-1)
                        walk_on_snow_sound[the_sound_id].play()
                    if sangvisFerris_data[enemies_in_control].x < the_route[0][0]:
                        sangvisFerris_data[enemies_in_control].x+=0.125
                        if (int(sangvisFerris_data[enemies_in_control].x),int(sangvisFerris_data[enemies_in_control].y)) in light_area or dark_mode != True:
                            action_displayer(enemies_in_control,"move",sangvisFerris_data[enemies_in_control].x,sangvisFerris_data[enemies_in_control].y)
                        if sangvisFerris_data[enemies_in_control].x >= the_route[0][0]:
                            sangvisFerris_data[enemies_in_control].x = the_route[0][0]
                            the_route.pop(0)
                    elif sangvisFerris_data[enemies_in_control].x > the_route[0][0]:
                        sangvisFerris_data[enemies_in_control].x-=0.125
                        if (int(sangvisFerris_data[enemies_in_control].x),int(sangvisFerris_data[enemies_in_control].y)) in light_area or dark_mode != True:
                            action_displayer(enemies_in_control,"move",sangvisFerris_data[enemies_in_control].x,sangvisFerris_data[enemies_in_control].y)
                        if sangvisFerris_data[enemies_in_control].x <= the_route[0][0]:
                            sangvisFerris_data[enemies_in_control].x = the_route[0][0]
                            the_route.pop(0)
                    elif sangvisFerris_data[enemies_in_control].y < the_route[0][1]:
                        sangvisFerris_data[enemies_in_control].y+=0.125
                        if (int(sangvisFerris_data[enemies_in_control].x),int(sangvisFerris_data[enemies_in_control].y)) in light_area or dark_mode != True:
                            action_displayer(enemies_in_control,"move",sangvisFerris_data[enemies_in_control].x,sangvisFerris_data[enemies_in_control].y)
                        if sangvisFerris_data[enemies_in_control].y >= the_route[0][1]:
                            sangvisFerris_data[enemies_in_control].y = the_route[0][1]
                            the_route.pop(0)
                    elif sangvisFerris_data[enemies_in_control].y > the_route[0][1]:
                        sangvisFerris_data[enemies_in_control].y-=0.125
                        if (int(sangvisFerris_data[enemies_in_control].x),int(sangvisFerris_data[enemies_in_control].y)) in light_area or dark_mode != True:
                            action_displayer(enemies_in_control,"move",sangvisFerris_data[enemies_in_control].x,sangvisFerris_data[enemies_in_control].y,True,True)
                        if sangvisFerris_data[enemies_in_control].y <= the_route[0][1]:
                            sangvisFerris_data[enemies_in_control].y = the_route[0][1]
                            the_route.pop(0)
                else:
                    walk_on_snow_sound[the_sound_id].stop()
                    enemies_in_control_id +=1
                    if enemies_in_control_id == len(sangvisFerris_data):
                        whose_round = "sangvisFerrisToPlayer"
                        total_rounds += 1
                    enemy_action = None
                    enemies_in_control = ""
            elif enemy_action[0] == "stay":
                enemies_in_control_id +=1
                if enemies_in_control_id == len(sangvisFerris_data):
                    whose_round = "sangvisFerrisToPlayer"
                    total_rounds += 1
                enemy_action = None
                enemies_in_control = ""
            else:
                print("warning: not choice")

        #加载雪花
        for i in range(len(all_snow_on_screen)):
            drawImage(all_snow_on_screen[i],screen,local_x,local_y)
            all_snow_on_screen[i].x -= 10*zoom_in
            all_snow_on_screen[i].y += 20*zoom_in
            if all_snow_on_screen[i].x <= 0 or all_snow_on_screen[i].y+local_y >= 1080:
                all_snow_on_screen[i].y = random.randint(-100,0)
                all_snow_on_screen[i].x = random.randint(0,window_x*2)

        #加载音乐
        while pygame.mixer.music.get_busy() != 1:
            pygame.mixer.music.load("Assets/music/"+bg_music)
            pygame.mixer.music.play(loops=9999, start=0.0)
            pygame.mixer.music.set_volume(0.5)

        #结束动画
        if whose_round == "result_win":
            total_kills = fontRender("总杀敌："+str(result_of_round["total_kills"]),"white",20)
            result_of_round["total_time"] = time.localtime(time.time()-result_of_round["total_time"])
            total_time = fontRender("通关时间："+str(time.strftime('%M:%S',result_of_round["total_time"])),"white",20)
            result_of_round["total_rounds"] = total_rounds
            total_rounds_txt = fontRender("通关回合数："+str(result_of_round["total_rounds"]),"white",20)
            times_characters_down = fontRender("友方角色被击倒："+str(result_of_round["times_characters_down"]),"white",20)
            player_rate = fontRender("评价：A","white",20)
            press_space = fontRender("按空格继续","white",20)
            whose_round = "result"
        
        if whose_round == "result":
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        battle = False
            drawImage(original_UI_img["score"],screen)
            drawImg(total_kills,(250,300),screen)
            drawImg(total_time,(250,350),screen)
            drawImg(total_rounds_txt,(250,400),screen)
            drawImg(times_characters_down,(250,450),screen)
            drawImg(player_rate,(250,500),screen)
            drawImg(press_space,(250,700),screen)
        #画面更新
        fpsClock.tick(fps)
        pygame.display.update()

    return result_of_round    
