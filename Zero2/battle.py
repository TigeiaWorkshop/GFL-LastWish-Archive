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
def battle(chapter_name,window_x,window_y,screen,lang,dark_mode=True):
    #卸载音乐
    pygame.mixer.music.unload()

    #加载动作：接受角色名，动作，方位，完成对应的指令
    def action_displayer(chara_name,action,x,y,isContinue=True,ifFlip=False):
        hidden = False
        hp_img = original_UI_img["hp_green"]
        hp_empty = pygame.transform.scale(original_UI_img["hp_empty"], (int(perBlockWidth), int(perBlockHeight/5)))
        if chara_name in sangvisFerris_data:
            gif_dic = sangvisFerris_data[chara_name].gif
            if sangvisFerris_data[chara_name].current_hp < 0:
                sangvisFerris_data[chara_name].current_hp = 0
            current_hp_to_display = fontRender(str(sangvisFerris_data[chara_name].current_hp)+"/"+str(sangvisFerris_data[chara_name].max_hp),"black",10)
            percent_of_hp = sangvisFerris_data[chara_name].current_hp/sangvisFerris_data[chara_name].max_hp
            current_bullets_situation = fontRender(str(sangvisFerris_data[chara_name].current_bullets)+"/"+str(sangvisFerris_data[chara_name].maximum_bullets),"black",10)
        elif chara_name in characters_data:
            hidden = characters_data[chara_name].undetected
            gif_dic = characters_data[chara_name].gif
            if characters_data[chara_name].current_hp<=0:
                characters_data[chara_name].current_hp = 0
                if characters_data[chara_name].dying == False:
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
            current_bullets_situation = fontRender(str(characters_data[chara_name].current_bullets)+"/"+str(characters_data[chara_name].maximum_bullets),"black",10)
            printf(hp_empty,(x*perBlockWidth,y*perBlockHeight*0.98-hp_empty.get_height()),screen,local_x,local_y)
            if characters_data[chara_name].current_action_point != 0:
                printf(pygame.transform.scale(original_UI_img["action_point_blue"],(int(perBlockWidth*characters_data[chara_name].current_action_point/characters_data[chara_name].max_action_point),int(perBlockHeight/5))),(x*perBlockWidth,y*perBlockHeight*0.98-hp_empty.get_height()),screen,local_x,local_y)
        
        if percent_of_hp<0:
            percent_of_hp=0

        img_of_char = pygame.transform.scale(gif_dic[action][0][0][gif_dic[action][1]], (int(perBlockWidth*2), int(perBlockHeight*2)))
        if hidden == True:
            img_of_char.set_alpha(130)
        else:
            img_of_char.set_alpha(300)
        if ifFlip == True:
            printf(pygame.transform.flip(img_of_char,True,False),(x*perBlockWidth-perBlockWidth/2,y*perBlockHeight-perBlockHeight/2),screen,local_x,local_y)
        else:
            printf(img_of_char,(x*perBlockWidth-perBlockWidth/2,y*perBlockHeight-perBlockHeight/2),screen,local_x,local_y)
        if percent_of_hp>0:
            printf(hp_empty,(x*perBlockWidth,y*perBlockHeight*0.98),screen,local_x,local_y)
            printf(pygame.transform.scale(hp_img,(int(perBlockWidth*percent_of_hp),int(perBlockHeight/5))),(x*perBlockWidth,y*perBlockHeight*0.98),screen,local_x,local_y)
            printf(current_hp_to_display,(x*perBlockWidth,y*perBlockHeight*0.98),screen,local_x,local_y)
            printf(current_bullets_situation,(x*perBlockWidth+current_hp_to_display.get_width()-current_bullets_situation.get_width(),y*perBlockHeight*0.98-current_bullets_situation.get_height()),screen,local_x,local_y)
        
        gif_dic[action][1]+=1
        if isContinue==True:
            if gif_dic[action][1] == gif_dic[action][0][1]:
                gif_dic[action][1] = 0
        elif isContinue==False:
            if gif_dic[action][1] == gif_dic[action][0][1]:
                gif_dic[action][1]-=1

    #加载背景图片
    all_env_file_list = glob.glob(r'Assets/img/environment/*.png')
    env_img_list={}
    for i in range(len(all_env_file_list)):
        img_name = all_env_file_list[i].replace("Assets","").replace("img","").replace("environment","").replace(".png","").replace("\\","").replace("/","")
        env_img_list[img_name] = loadImg(all_env_file_list[i])

    #读取并初始化章节信息
    with open("Data/main_chapter/"+chapter_name+"_map.yaml", "r", encoding='utf-8') as f:
        chapter_info = yaml.load(f.read(),Loader=yaml.FullLoader)
        block_y = len(chapter_info["map"])
        block_x = len(chapter_info["map"][0])
        characters = chapter_info["character"]
        sangvisFerris = chapter_info["sangvisFerri"]
        theMap = chapter_info["map"]
        bg_music = chapter_info["background_music"]

    #地图方块图片随机化
    with open("Data/blocks.yaml", "r", encoding='utf-8') as f:
        chapter_info = yaml.load(f.read(),Loader=yaml.FullLoader)
        blocks_setting = chapter_info["blocks"]
    
    with open("Data/main_chapter/"+chapter_name+"_dialogs_"+lang+".yaml", "r", encoding='utf-8') as f:
        chapter_info = yaml.load(f.read(),Loader=yaml.FullLoader)
        chapter_title = chapter_info["title"]

    map_img_list = randomBlock(theMap,blocks_setting)
    #一个方块的长
    perBlockWidth = window_x/block_x
    #一个方块的高
    perBlockHeight = window_y/block_y

    #加载按钮的文字
    with open("Lang/"+lang+".yaml", "r", encoding='utf-8') as f:
        chapter_info = yaml.load(f.read(),Loader=yaml.FullLoader)
        selectMenuButtons_dic = chapter_info["select_menu"]
        your_round_txt = fontRender(chapter_info["Battle_UI"]["yourRound"], "white")
        enemy_round_txt = fontRender(chapter_info["Battle_UI"]["enemyRound"], "white")
        text_now_total_rounds_original = chapter_info["Battle_UI"]["numRound"]
        chapter_no = chapter_info["Battle_UI"]["numChapter"]
    
    #章节标题显示
    the_black = loadImg("Assets/img/UI/black.png",window_x,window_y)
    title_number_display = fontRender(chapter_no.replace("NaN",chapter_name.replace("chapter","")),"white")
    title_main_display = fontRender(chapter_title,"white")

    for i in range(0,600,1):
        printf(the_black,(0,0),screen)
        title_number_display.set_alpha(i)
        title_main_display.set_alpha(i)
        printf(title_number_display,((window_x-title_number_display.get_width())/2,400),screen)
        printf(title_main_display,((window_x-title_main_display.get_width())/2,500),screen)
        pygame.display.update()
    
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
    for jiaose in characters:
        characters_data[jiaose] = characterDataManager(jiaose,characters[jiaose]["min_damage"],characters[jiaose]["max_damage"],characters[jiaose]["max_hp"],characters[jiaose]["current_hp"],characters[jiaose]["x"],characters[jiaose]["y"],characters[jiaose]["attack_range"],characters[jiaose]["action_point"],characters[jiaose]["undetected"],character_gif_dic(jiaose,perBlockWidth,perBlockHeight),characters[jiaose]["current_bullets"],characters[jiaose]["maximum_bullets"])

    sangvisFerris_data = {}
    for enemy in sangvisFerris:
        sangvisFerris_data[enemy] = sangvisFerriDataManager(enemy,sangvisFerris[enemy]["min_damage"],sangvisFerris[enemy]["max_damage"],sangvisFerris[enemy]["max_hp"],sangvisFerris[enemy]["current_hp"],sangvisFerris[enemy]["x"],sangvisFerris[enemy]["y"],sangvisFerris[enemy]["attack_range"],sangvisFerris[enemy]["move_range"],character_gif_dic(enemy,perBlockWidth,perBlockHeight,"sangvisFerri"),sangvisFerris[enemy]["current_bullets"],sangvisFerris[enemy]["maximum_bullets"],sangvisFerris[enemy]["patrol_path"])

    #加载UI
    #加载结束回合的图片
    end_round_button = loadImage("Assets/img/UI/endRound.png",window_x*0.9,window_y*0.9,perBlockWidth*2*28/15, perBlockWidth*2)
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
        "green" : loadImg("Assets/img/UI/green.png",None,None,100),
        "red" : loadImg("Assets/img/UI/red.png",None,None,100),
        "black" : loadImg("Assets/img/UI/black.png",None,None,100),
        #计分板
        "score" : loadImage("Assets/img/UI/score.png",200,200,300,600),
    }
    green = pygame.transform.scale(original_UI_img["green"], (math.ceil(perBlockWidth), math.ceil(perBlockHeight)))
    red = pygame.transform.scale(original_UI_img["red"], (math.ceil(perBlockWidth), math.ceil(perBlockHeight)))
    black = pygame.transform.scale(original_UI_img["black"], (math.ceil(perBlockWidth), math.ceil(perBlockHeight)))

    #文字
    text_of_endround_move = 0
    text_of_endround_alpha = 400
    #章节标题淡出
    for t in range(250,200,-1):
        for i in range(len(map_img_list)):
            for a in range(len(map_img_list[i])):
                img_display = pygame.transform.scale(env_img_list[map_img_list[i][a]], (int(perBlockWidth), int(perBlockHeight*1.5)))
                img_display.set_alpha(250-t)
                printf(img_display,(a*perBlockWidth,(i+1)*perBlockHeight-int(perBlockHeight*1.5)),screen)
        title_number_display.set_alpha(i)
        title_main_display.set_alpha(i)
        printf(title_number_display,((window_x-title_number_display.get_width())/2,400),screen)
        printf(title_main_display,((window_x-title_main_display.get_width())/2,500),screen)
        pygame.display.update()
    
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
    local_x = 0
    local_y = 0
    mouse_move_temp_x = -1
    mouse_move_temp_y = -1
    total_rounds = 1
    enemies_in_control_id= 0
    #放大倍数
    zoom_in = 1
    #计算光亮区域
    light_area = calculate_darkness(characters_data)
    # 移动路径
    the_route = []
    #上个回合因为暴露被敌人发现的角色
    #格式：角色：[x,y]
    the_characters_detected_last_round = {}
    all_characters_data = dicMerge(characters_data,sangvisFerris_data)
    enemy_action = None
    result_of_round = {
        "total_kills" : 0,
        "total_time" : time.time(),
        "times_characters_down" : 0
    }
    #行走的声音
    walk_on_snow_sound = pygame.mixer.Sound("Assets/sound/snow/Snowrunning1.wav")
    #帧数控制器
    fpsClock = pygame.time.Clock()
    # 游戏主循环
    while battle==True:
        #加载地图
        for y in range(len(map_img_list)):
            for x in range(len(map_img_list[y])):
                img_display = pygame.transform.scale(env_img_list[map_img_list[y][x]], (int(perBlockWidth), int(perBlockHeight*1.5)))
                printf(img_display,(x*perBlockWidth,(y+1)*perBlockHeight-perBlockHeight*1.5),screen,local_x,local_y)
                if (x,y-1) not in light_area and dark_mode == True:
                    printf(black,(x*perBlockWidth,(y-1)*perBlockHeight),screen,local_x,local_y)
        for x in range(len(map_img_list[y])):
            if (x,y) not in light_area and dark_mode == True:
                printf(black,(x*perBlockWidth,y*perBlockHeight),screen,local_x,local_y)

        #加载UI
        if green.get_width() != math.ceil(perBlockWidth) and green.get_height() != math.ceil(perBlockHeight):
            green = pygame.transform.scale(original_UI_img["green"], (math.ceil(perBlockWidth), math.ceil(perBlockHeight)))
            red = pygame.transform.scale(original_UI_img["red"], (math.ceil(perBlockWidth), math.ceil(perBlockHeight)))
            black = pygame.transform.scale(original_UI_img["black"], (math.ceil(perBlockWidth), math.ceil(perBlockHeight)))

        #玩家输入按键判定-任何情况
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
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
        
        #玩家回合
        if whose_round == "player":
            #加载结束回合的按钮
            printIn(end_round_button,screen)
            #玩家输入按键判定-玩家回合限定
            if pygame.mouse.get_pressed()[0]:
                mouse_x,mouse_y=pygame.mouse.get_pos()
                #获取角色坐标
                block_get_click_x = int((mouse_x-local_x)/perBlockWidth)
                block_get_click_y = int((mouse_y-local_y)/perBlockHeight)
                #如果点击了回合结束的按钮
                if isHover(end_round_button):
                    whose_round = "playerToSangvisFerris"
                    the_character_get_click = ""
                    green_hide = True
                #是否在显示移动范围后点击了且点击区域在移动范围内
                elif the_route != [] and [block_get_click_x,block_get_click_y] in the_route:
                    isWaiting = "MOVING"
                    green_hide = True
                    characters_data[the_character_get_click].current_action_point -= len(the_route)
                else:
                    #控制选择菜单的显示与隐藏
                    for key in characters_data:
                        if characters_data[key].x == block_get_click_x and characters_data[key].y == block_get_click_y and isWaiting == True and action_choice != "skill":
                            if key != the_character_get_click:
                                the_character_get_click = key
                                green_hide = "SelectMenu"
                                break
                            else:
                                green_hide = True
                                the_character_get_click = ""

            #显示选择菜单
            if green_hide == "SelectMenu":
                attack_button_txt = fontRender(selectMenuButtons_dic["attack"],"black",int(perBlockWidth/2))
                move_button_txt = fontRender(selectMenuButtons_dic["move"],"black",int(perBlockWidth/2))
                skill_button_txt = fontRender(selectMenuButtons_dic["skill"],"black",int(perBlockWidth/2))
                reload_button_txt = fontRender(selectMenuButtons_dic["reload"],"black",int(perBlockWidth/2))
                select_menu_button = pygame.transform.scale(select_menu_button_original, (int(perBlockWidth*2), int(perBlockWidth/1.3)))
                displayInCenter(attack_button_txt,select_menu_button,characters_data[the_character_get_click].x*perBlockWidth-select_menu_button.get_width()-perBlockWidth*0.5,characters_data[the_character_get_click].y*perBlockHeight,screen,local_x,local_y)
                displayInCenter(move_button_txt,select_menu_button,characters_data[the_character_get_click].x*perBlockWidth+select_menu_button.get_width()-perBlockWidth*0.5,characters_data[the_character_get_click].y*perBlockHeight,screen,local_x,local_y)
                displayInCenter(skill_button_txt,select_menu_button,characters_data[the_character_get_click].x*perBlockWidth-perBlockWidth*0.5,characters_data[the_character_get_click].y*perBlockHeight-select_menu_button.get_height()-perBlockWidth*0.5,screen,local_x,local_y)
                displayInCenter(reload_button_txt,select_menu_button,characters_data[the_character_get_click].x*perBlockWidth-perBlockWidth*0.5,characters_data[the_character_get_click].y*perBlockHeight+select_menu_button.get_height()+perBlockWidth*0.5,screen,local_x,local_y)
                if pygame.mouse.get_pressed()[0]:
                    if isGetClick(select_menu_button,(characters_data[the_character_get_click].x*perBlockWidth-select_menu_button.get_width()-perBlockWidth*0.5,characters_data[the_character_get_click].y*perBlockHeight),local_x,local_y):
                        if characters_data[the_character_get_click].current_bullets > 0:
                            action_choice = "attack"
                            block_get_click_x = -100
                            block_get_click_y = -100
                            green_hide = False
                    elif isGetClick(select_menu_button,(characters_data[the_character_get_click].x*perBlockWidth+select_menu_button.get_width()-perBlockWidth*0.5,characters_data[the_character_get_click].y*perBlockHeight),local_x,local_y):
                        action_choice = "move"
                        block_get_click_x = -100
                        block_get_click_y = -100
                        green_hide = False
                    elif isGetClick(select_menu_button,(characters_data[the_character_get_click].x*perBlockWidth-perBlockWidth*0.5,characters_data[the_character_get_click].y*perBlockHeight-select_menu_button.get_height()-perBlockWidth*0.5),local_x,local_y):
                        action_choice = "skill"
                        block_get_click_x = -100
                        block_get_click_y = -100
                        green_hide = False
                    elif isGetClick(select_menu_button,(characters_data[the_character_get_click].x*perBlockWidth-perBlockWidth*0.5,characters_data[the_character_get_click].y*perBlockHeight+select_menu_button.get_height()+perBlockWidth*0.5),local_x,local_y):
                        action_choice = "reload"
                        block_get_click_x = -100
                        block_get_click_y = -100
                        green_hide = False
            #显示攻击或移动范围
            if green_hide == False and characters_data[the_character_get_click].current_action_point > 0 and the_character_get_click != "":
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
                            if blocks_setting[theMap[y][x]][1] == False:
                                map2d[x][y]=1
                    # 历遍所有角色，将角色的坐标点设置为障碍方块
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
                    
                    for i in range(len(the_route)):
                        printf(green,(the_route[i][0]*perBlockWidth,the_route[i][1]*perBlockHeight),screen,local_x,local_y)

                #显示攻击范围        
                elif action_choice == "attack":
                    attacking_range = []
                    for y in range(characters_data[the_character_get_click].y-characters_data[the_character_get_click].attack_range,characters_data[the_character_get_click].y+characters_data[the_character_get_click].attack_range):
                        if y < characters_data[the_character_get_click].y:
                            for x in range(characters_data[the_character_get_click].x-characters_data[the_character_get_click].attack_range-(y-characters_data[the_character_get_click].y)+1,characters_data[the_character_get_click].x+characters_data[the_character_get_click].attack_range+(y-characters_data[the_character_get_click].y)):
                                if blocks_setting[theMap[y][x]][1] == True:
                                    printf(green,(x*perBlockWidth,y*perBlockHeight),screen,local_x,local_y)
                                    attacking_range.append([x,y])
                        else:
                            for x in range(characters_data[the_character_get_click].x-characters_data[the_character_get_click].attack_range+(y-characters_data[the_character_get_click].y)+1,characters_data[the_character_get_click].x+characters_data[the_character_get_click].attack_range-(y-characters_data[the_character_get_click].y)):
                                if x == characters_data[the_character_get_click].x and y == characters_data[the_character_get_click].y:
                                    pass
                                else:
                                    if blocks_setting[theMap[y][x]][1] == True:
                                        printf(green,(x*perBlockWidth,y*perBlockHeight),screen,local_x,local_y)
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
                    for y in range(characters_data[the_character_get_click].y-characters_data[the_character_get_click].attack_range,characters_data[the_character_get_click].y+characters_data[the_character_get_click].attack_range):
                        if y < characters_data[the_character_get_click].y:
                            for x in range(characters_data[the_character_get_click].x-characters_data[the_character_get_click].attack_range-(y-characters_data[the_character_get_click].y)+1,characters_data[the_character_get_click].x+characters_data[the_character_get_click].attack_range+(y-characters_data[the_character_get_click].y)):
                                if blocks_setting[theMap[y][x]][1] == True:
                                    printf(green,(x*perBlockWidth,y*perBlockHeight),screen,local_x,local_y)
                                    skill_range.append([x,y])
                        else:
                            for x in range(characters_data[the_character_get_click].x-characters_data[the_character_get_click].attack_range+(y-characters_data[the_character_get_click].y)+1,characters_data[the_character_get_click].x+characters_data[the_character_get_click].attack_range-(y-characters_data[the_character_get_click].y)):
                                if x == characters_data[the_character_get_click].x and y == characters_data[the_character_get_click].y:
                                    pass
                                else:
                                    if blocks_setting[theMap[y][x]][1] == True:
                                        printf(green,(x*perBlockWidth,y*perBlockHeight),screen,local_x,local_y)
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
                    if characters_data[the_character_get_click].maximum_bullets-characters_data[the_character_get_click].current_bullets > 0:
                        #向上取整
                        characters_data[the_character_get_click].current_action_point -= math.ceil((characters_data[the_character_get_click].maximum_bullets-characters_data[the_character_get_click].current_bullets)/2)
                        characters_data[the_character_get_click].current_bullets = characters_data[the_character_get_click].maximum_bullets
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
                            walk_on_snow_sound.play()
                        if characters_data[the_character_get_click].x < the_route[0][0]:
                            characters_data[the_character_get_click].x+=0.125
                            action_displayer(the_character_get_click,"move",characters_data[the_character_get_click].x,characters_data[the_character_get_click].y)
                            if characters_data[the_character_get_click].x >= the_route[0][0]:
                                characters_data[the_character_get_click].x = the_route[0][0]
                                the_route.pop(0)
                        elif characters_data[the_character_get_click].x > the_route[0][0]:
                            characters_data[the_character_get_click].x-=0.125
                            action_displayer(characters_data[the_character_get_click].name,"move",characters_data[the_character_get_click].x,characters_data[the_character_get_click].y,True,True)
                            if characters_data[the_character_get_click].x <= the_route[0][0]:
                                characters_data[the_character_get_click].x = the_route[0][0]
                                the_route.pop(0)
                        elif characters_data[the_character_get_click].y < the_route[0][1]:
                            characters_data[the_character_get_click].y+=0.125
                            action_displayer(characters_data[the_character_get_click].name,"move",characters_data[the_character_get_click].x,characters_data[the_character_get_click].y)
                            if characters_data[the_character_get_click].y >= the_route[0][1]:
                                characters_data[the_character_get_click].y = the_route[0][1]
                                the_route.pop(0)
                        elif characters_data[the_character_get_click].y > the_route[0][1]:
                            characters_data[the_character_get_click].y-=0.125
                            action_displayer(characters_data[the_character_get_click].name,"move",characters_data[the_character_get_click].x,characters_data[the_character_get_click].y)
                            if characters_data[the_character_get_click].y <= the_route[0][1]:
                                characters_data[the_character_get_click].y = the_route[0][1]
                                the_route.pop(0)
                    else:
                        walk_on_snow_sound.stop()
                        isWaiting =True
                        the_character_get_click = ""
                    light_area = calculate_darkness(characters_data)
                elif isWaiting == "ATTACKING":
                    green_hide=True
                    if action_choice == "attack":
                        action_displayer(characters_data[the_character_get_click].name,"attack",characters_data[the_character_get_click].x,characters_data[the_character_get_click].y,False)
                        if characters_data[the_character_get_click].gif["attack"][1] == characters_data[the_character_get_click].gif["attack"][0][1]-2:
                            sangvisFerris_data[enemies_get_attack].decreaseHp(characters_data[the_character_get_click].min_damage,characters_data[the_character_get_click].max_damage)
                        the_characters_attacking = characters_data[the_character_get_click].gif
                        if the_characters_attacking["attack"][1] == the_characters_attacking["attack"][0][1]-1:
                            the_characters_attacking["attack"][1] = 0
                            characters_data[the_character_get_click].current_bullets -= 1
                            isWaiting = True
                            the_character_get_click = ""
                            action_choice = ""
                    if action_choice == "skill":
                        action_displayer(characters_data[the_character_get_click].name,"skill",characters_data[the_character_get_click].x,characters_data[the_character_get_click].y,False)
                        if characters_data[the_character_get_click].gif["skill"][1] == characters_data[the_character_get_click].gif["skill"][0][1]-2:
                            if the_character_get_click == "gsh-18":
                                characters_data[enemies_get_attack].heal(characters_data[the_character_get_click].min_damage)
                                if characters_data[enemies_get_attack].current_hp > characters_data[enemies_get_attack].max_hp:
                                    characters_data[enemies_get_attack].current_hp = characters_data[enemies_get_attack].max_hp
                            else:
                                sangvisFerris_data[enemies_get_attack].decreaseHp(characters_data[the_character_get_click].min_damage,characters_data[the_character_get_click].max_damage)
                        the_characters_attacking = characters_data[the_character_get_click].gif
                        if the_characters_attacking["skill"][1] == the_characters_attacking["skill"][0][1]-1:
                            the_characters_attacking["skill"][1] = 0
                            isWaiting =True
                            the_character_get_click = ""
                            action_choice = ""
                elif isWaiting == True:
                    action_displayer(characters_data[the_character_get_click].name,"wait",characters_data[the_character_get_click].x,characters_data[the_character_get_click].y)

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
            
            printf(text_now_total_rounds,(text_of_endround_move,(window_y-your_round_txt.get_height()*2.5)/2),screen)
            if whose_round == "sangvisFerrisToPlayer":
                printf(your_round_txt,(window_x-text_of_endround_move-your_round_txt.get_width(),(window_y-your_round_txt.get_height()*2.5)/2+your_round_txt.get_height()*1.5),screen)
            if whose_round == "playerToSangvisFerris":
                printf(enemy_round_txt,(window_x-text_of_endround_move-your_round_txt.get_width(),(window_y-your_round_txt.get_height()*2.5)/2+your_round_txt.get_height()*1.5),screen)
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
                print(enemies_in_control+"choses"+enemy_action[0]+":"+enemy_action[1])
            if enemy_action[0] == "attack":
                if (sangvisFerris_data[enemies_in_control].x,sangvisFerris_data[enemies_in_control].y) in light_area or dark_mode != True:
                    action_displayer(enemies_in_control,"attack",sangvisFerris_data[enemies_in_control].x,sangvisFerris_data[enemies_in_control].y,False)
                if sangvisFerris_data[enemies_in_control].gif["attack"][1] == sangvisFerris_data[enemies_in_control].gif["attack"][0][1]-2:
                    characters_data[enemy_action[1]].decreaseHp(sangvisFerris_data[enemies_in_control].min_damage,sangvisFerris_data[enemies_in_control].max_damage)
                the_characters_attacking = sangvisFerris_data[enemies_in_control].gif
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
                            walk_on_snow_sound.play()
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
                    walk_on_snow_sound.stop()
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
        
        #↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓角色动画展示区↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓#
        # 我方角色动画
        for every_chara in characters_data:
            if every_chara != the_character_get_click:
                if theMap[characters_data[every_chara].y][characters_data[every_chara].x] == 2:
                    characters_data[every_chara].undetected = True
                else:
                    characters_data[every_chara].undetected = False
                if characters_data[every_chara].dying == False:
                    action_displayer(characters_data[every_chara].name,"wait",characters_data[every_chara].x,characters_data[every_chara].y)
                else:
                    action_displayer(characters_data[every_chara].name,"die",characters_data[every_chara].x,characters_data[every_chara].y,False)
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
                                for y in range(sangvisFerris_data[enemies].y-sangvisFerris_data[enemies].attack_range,sangvisFerris_data[enemies].y+sangvisFerris_data[enemies].attack_range):
                                    if y < sangvisFerris_data[enemies].y:
                                        for x in range(sangvisFerris_data[enemies].x-sangvisFerris_data[enemies].attack_range-(y-sangvisFerris_data[enemies].y)+1,sangvisFerris_data[enemies].x+sangvisFerris_data[enemies].attack_range+(y-sangvisFerris_data[enemies].y)):
                                            if blocks_setting[theMap[y][x]][1] == True:
                                                printf(green,(x*perBlockWidth,y*perBlockHeight),screen,local_x,local_y)
                                            else:
                                                printf(red,(x*perBlockWidth,y*perBlockHeight),screen,local_x,local_y)
                                    else:
                                        for x in range(sangvisFerris_data[enemies].x-sangvisFerris_data[enemies].attack_range+(y-sangvisFerris_data[enemies].y)+1,sangvisFerris_data[enemies].x+sangvisFerris_data[enemies].attack_range-(y-sangvisFerris_data[enemies].y)):
                                            if x == sangvisFerris_data[enemies].x and y == sangvisFerris_data[enemies].y:
                                                pass
                                            else:
                                                if blocks_setting[theMap[y][x]][1] == True:
                                                    printf(green,(x*perBlockWidth,y*perBlockHeight),screen,local_x,local_y)
                                                else:
                                                    printf(red,(x*perBlockWidth,y*perBlockHeight),screen,local_x,local_y)
                        action_displayer(enemies,"wait",sangvisFerris_data[enemies].x,sangvisFerris_data[enemies].y)
                elif sangvisFerris_data[enemies].current_hp<=0:
                    action_displayer(enemies,"die",sangvisFerris_data[enemies].x,sangvisFerris_data[enemies].y,False)
                    the_dead_one = enemies
        if the_dead_one != "":
            the_characters_attacking = sangvisFerris_data[the_dead_one].gif
            if the_characters_attacking["die"][1] == the_characters_attacking["die"][0][1]-1:
                sangvisFerris_data.pop(the_dead_one)
                result_of_round["total_kills"]+=1
            the_dead_one=""
        #↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑角色动画展示区↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑#

        #↓↓↓↓↓↓↓↓↓↓↓↓↓↓所有回合可进行的操作↓↓↓↓↓↓↓↓↓↓↓↓↓↓#
        #移动屏幕
        if pygame.mouse.get_pressed()[1]:
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
        #↑↑↑↑↑↑↑↑↑↑↑↑↑↑所有回合可进行的操作↑↑↑↑↑↑↑↑↑↑↑↑↑↑#
        #加载雪花
        for i in range(len(all_snow_on_screen)):
            printIn(all_snow_on_screen[i],screen,local_x,local_y)
            all_snow_on_screen[i].x -= 10*zoom_in
            all_snow_on_screen[i].y += 20*zoom_in
            if all_snow_on_screen[i].x <= 0 or all_snow_on_screen[i].y+local_y >= 1080:
                all_snow_on_screen[i].y = random.randint(-100,0)
                all_snow_on_screen[i].x = random.randint(0,window_x*2)

        #加载音乐
        while pygame.mixer.music.get_busy() != 1:
            pygame.mixer.music.load("Assets/music/"+bg_music)
            pygame.mixer.music.play(loops=9999, start=0.0)
            pygame.mixer.music.set_volume(0.1)

        #结束动画
        if whose_round == "result_win":
            total_kills = fontRender("总杀敌："+str(result_of_round["total_kills"]),"white",20)
            total_time = fontRender("通关时间："+str(time.strftime('%M:%S',time.localtime(time.time()-result_of_round["total_time"]))),"white",20)
            total_rounds_txt = fontRender("通关回合数："+str(total_rounds),"white",20)
            times_characters_down = fontRender("友方角色被击倒："+str(result_of_round["times_characters_down"]),"white",20)
            player_rate = fontRender("评价：A","white",20)
            press_space = fontRender("按空格继续","white",20)
            whose_round = "result"
        
        if whose_round == "result":
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        battle = False
            printIn(original_UI_img["score"],screen)
            printf(total_kills,(250,300),screen)
            printf(total_time,(250,350),screen)
            printf(total_rounds_txt,(250,400),screen)
            printf(times_characters_down,(250,450),screen)
            printf(player_rate,(250,500),screen)
            printf(press_space,(250,700),screen)
        #画面更新
        fpsClock.tick(60)
        pygame.display.update()

