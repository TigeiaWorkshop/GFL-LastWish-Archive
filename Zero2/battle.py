# cython: language_level=3
from Zero2.basic import *
from Zero2.characterDataManager import *
from Zero2.map import *
from Zero2.AI import *
from Zero2.skills import *

def battle(chapter_name,screen,lang,fps):
    if pygame.joystick.get_count()>0:
        pygame.joystick.init()
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        ifJoystickInit = joystick.get_init()
    else:
        ifJoystickInit = False
    #获取屏幕的尺寸
    window_x,window_y = screen.get_size()
    #卸载音乐
    pygame.mixer.music.unload()
    #帧率控制器
    Display = DisplayController(fps)

    #加载按钮的文字
    with open("Lang/"+lang+".yaml", "r", encoding='utf-8') as f:
        loadData = yaml.load(f.read(),Loader=yaml.FullLoader)
        selectMenuButtons_dic = loadData["select_menu"]
        your_round_txt = fontRender(loadData["Battle_UI"]["yourRound"], "white",window_x/38)
        enemy_round_txt = fontRender(loadData["Battle_UI"]["enemyRound"], "white",window_x/38)
        text_now_total_rounds_original = loadData["Battle_UI"]["numRound"]
        chapter_no = loadData["Battle_UI"]["numChapter"]
        warnings_info = loadData["warnings"]
        loading_info = loadData["loading_info"]
    
    with open("Data/main_chapter/"+chapter_name+"_dialogs_"+lang+".yaml", "r", encoding='utf-8') as f:
        loadData = yaml.load(f.read(),Loader=yaml.FullLoader)
        chapter_title = loadData["title"]
        battle_info = loadData["battle_info"]
        dialog_during_battle = loadData["dialog_during_battle"]

    #章节标题显示
    black_bg = loadImage("Assets/image/UI/black.png",(0,0),window_x,window_y)
    title_number_display = fontRender(chapter_no.replace("NaN",chapter_name.replace("chapter","")),"white",window_x/38)
    title_main_display = fontRender(chapter_title,"white",window_x/38)

    #渐入效果
    for i in range(0,250,2):
        black_bg.draw(screen)
        title_number_display.set_alpha(i)
        title_main_display.set_alpha(i)
        drawImg(title_number_display,((window_x-title_number_display.get_width())/2,400),screen)
        drawImg(title_main_display,((window_x-title_main_display.get_width())/2,500),screen)
        Display.flip()

    #开始加载地图场景
    black_bg.draw(screen)
    drawImg(title_number_display,((window_x-title_number_display.get_width())/2,400),screen)
    drawImg(title_main_display,((window_x-title_main_display.get_width())/2,500),screen)
    now_loading = fontRender(loading_info["now_loading_map"], "white",window_x/76)
    drawImg(now_loading,(window_x*0.75,window_y*0.9),screen)
    Display.flip()

    #加载地图设置
    with open("Data/blocks.yaml", "r", encoding='utf-8') as f:
        loadData = yaml.load(f.read(),Loader=yaml.FullLoader)
        blocks_setting = loadData["blocks"]
    #读取并初始化章节信息
    with open("Data/main_chapter/"+chapter_name+"_map.yaml", "r", encoding='utf-8') as f:
        loadData = yaml.load(f.read(),Loader=yaml.FullLoader)
        block_y = len(loadData["map"])
        block_x = len(loadData["map"][0])
        zoomIn = loadData["zoomIn"]*100
        local_x = loadData["local_x"]
        local_y = loadData["local_y"]
        characters = loadData["character"]
        sangvisFerris = loadData["sangvisFerri"]
        bg_music = loadData["background_music"]
        theWeather = loadData["weather"]
        dialogInfo = loadData["dialogs"]
        darkMode = loadData["darkMode"]

    if zoomIn < 200:
        zoomIn = 200
    elif zoomIn > 400:
        zoomIn = 400
    zoomIntoBe = zoomIn
    perBlockWidth = round(window_x/10)
    perBlockHeight = round(window_y/10)
    #初始化地图模块
    theMap = MapObject(loadData["map"],loadData["facility"],blocks_setting,darkMode,perBlockWidth)
    
    #初始化角色信息
    i = 1
    num_of_characters = len(characters)+len(sangvisFerris)
    characters_data = {}
    for each_character in characters:
        characters_data[each_character] = CharacterDataManager(characters[each_character]["action_point"],characters[each_character]["attack_range"],characters[each_character]["current_bullets"],characters[each_character]["current_hp"],characters[each_character]["effective_range"],characters[each_character]["kind"],characters[each_character]["magazine_capacity"],characters[each_character]["max_damage"],characters[each_character]["max_hp"],characters[each_character]["min_damage"],characters[each_character]["type"],characters[each_character]["x"],characters[each_character]["y"],characters[each_character]["bullets_carried"],characters[each_character]["skill_effective_range"],characters[each_character]["skill_cover_range"],characters[each_character]["undetected"])
        black_bg.draw(screen)
        drawImg(title_number_display,((window_x-title_number_display.get_width())/2,400),screen)
        drawImg(title_main_display,((window_x-title_main_display.get_width())/2,500),screen)
        now_loading = fontRender(loading_info["now_loading_characters"]+"("+str(i)+"/"+str(num_of_characters)+")", "white",window_x/76)
        drawImg(now_loading,(window_x*0.75,window_y*0.9),screen)
        Display.flip()
        i+=1
    sangvisFerris_data = {}
    for each_character in sangvisFerris:
        sangvisFerris_data[each_character] = SangvisFerriDataManager(sangvisFerris[each_character]["action_point"],sangvisFerris[each_character]["attack_range"],sangvisFerris[each_character]["current_bullets"],sangvisFerris[each_character]["current_hp"],sangvisFerris[each_character]["effective_range"],sangvisFerris[each_character]["kind"],sangvisFerris[each_character]["magazine_capacity"],sangvisFerris[each_character]["max_damage"],sangvisFerris[each_character]["max_hp"],sangvisFerris[each_character]["min_damage"],sangvisFerris[each_character]["type"],sangvisFerris[each_character]["x"],sangvisFerris[each_character]["y"],sangvisFerris[each_character]["patrol_path"])
        black_bg.draw(screen)
        drawImg(title_number_display,((window_x-title_number_display.get_width())/2,400),screen)
        drawImg(title_main_display,((window_x-title_main_display.get_width())/2,500),screen)
        now_loading = fontRender(loading_info["now_loading_characters"]+"("+str(i)+"/"+str(num_of_characters)+")", "white",window_x/76)
        drawImg(now_loading,(window_x*0.75,window_y*0.9),screen)
        Display.flip()
        i+=1

    #计算光亮区域 并初始化地图
    theMap.lightArea = calculate_darkness(characters_data,theMap.facilityData["campfire"])
    theMap.process_map()

    #加载对话时角色的图标
    character_icon_img_list={}
    all_icon_file_list = glob.glob(r'Assets/image/npc_icon/*.png')
    for i in range(len(all_icon_file_list)):
        img_name = all_icon_file_list[i].replace("Assets","").replace("image","").replace("npc_icon","").replace(".png","").replace("\\","").replace("/","")
        character_icon_img_list[img_name] = loadImg(all_icon_file_list[i],window_y*0.08,window_y*0.08)
    del all_icon_file_list
    
    #开始加载关卡设定
    black_bg.draw(screen)
    drawImg(title_number_display,((window_x-title_number_display.get_width())/2,400),screen)
    drawImg(title_main_display,((window_x-title_main_display.get_width())/2,500),screen)
    now_loading = fontRender(loading_info["now_loading_level"], "white",window_x/76)
    drawImg(now_loading,(window_x*0.75,window_y*0.9),screen)
    Display.flip()

    #加载UI
    #加载结束回合的图片
    end_round_button = loadImage("Assets/image/UI/endRound.png",(window_x*0.8,window_y*0.7),window_x/10, window_y/10)
    #加载选择菜单的图片
    select_menu_button_original = loadImg("Assets/image/UI/menu.png")
    #加载子弹图片
    bullet_img = loadImg("Assets/image/UI/bullet.png", perBlockWidth/6, perBlockHeight/12)
    bullets_list = []
    #加载血条,各色方块等UI图片 size:perBlockWidth, perBlockHeight/5
    original_UI_img = {
        "hp_empty" : loadImg("Assets/image/UI/hp_empty.png"),
        "hp_red" : loadImg("Assets/image/UI/hp_red.png"),
        "hp_green" : loadImg("Assets/image/UI/hp_green.png"),
        "action_point_blue" : loadImg("Assets/image/UI/action_point.png"),
        "bullets_number_brown" : loadImg("Assets/image/UI/bullets_number.png"),
        "green" : loadImg("Assets/image/UI/green.png",None,None,150),
        "red" : loadImg("Assets/image/UI/red.png",None,None,150),
        "black" : loadImg("Assets/image/UI/shadow.png",None,None,150),
        "yellow": loadImg("Assets/image/UI/yellow.png",None,None,150),
        "blue": loadImg("Assets/image/UI/blue.png",None,None,150),
        "orange": loadImg("Assets/image/UI/orange.png",None,None,150),
        #计分板
        "score" : loadImage("Assets/image/UI/score.png",(200,200),300,600),
        "supplyBoard":loadImage("Assets/image/UI/score.png",((window_x-window_x/3)/2,-window_y/12),window_x/3,window_y/12),
    }
    #UI - 变形后
    UI_img = {
        "green" : resizeImg(original_UI_img["green"], (perBlockWidth*0.9, None)),
        "red" : resizeImg(original_UI_img["red"], (perBlockWidth*0.9, None)),
        "black" : resizeImg(original_UI_img["black"], (perBlockWidth*0.9, None)),
        "yellow" : resizeImg(original_UI_img["yellow"], (perBlockWidth*0.9, None)),
        "blue" : resizeImg(original_UI_img["blue"], (perBlockWidth*0.9, None)),
        "orange": resizeImg(original_UI_img["orange"], (perBlockWidth*0.9, None))
    }
    theMap.greenBlockImg = UI_img["green"]
    theMap.shadowImg = UI_img["black"]
    the_character_get_click_info_board = loadImage("Assets/image/UI/score.png",(0,window_y-window_y/6),window_x/5,window_y/6)
    #加载对话框图片
    dialoguebox_up = loadImage("Assets/image/UI/dialoguebox.png",(window_x,window_y/2-window_y*0.35),window_x*0.3,window_y*0.15)
    dialoguebox_down = loadImage(pygame.transform.flip(dialoguebox_up.img,True,False),(-window_x*0.3,window_y/2+window_y*0.2),window_x*0.3,window_y*0.15)
    #选择菜单按钮底图
    select_menu_button = resizeImg(select_menu_button_original, (round(perBlockWidth/2), round(perBlockWidth/4)))
    #-----加载音效-----
    #行走的音效 -- 频道0
    all_walking_sounds = glob.glob(r'Assets/sound/snow/*.wav')
    walking_sound = []
    for i in range(len(all_walking_sounds)):
        walking_sound.append(pygame.mixer.Sound(all_walking_sounds[i]))
    the_sound_id = None
    #加载天气和环境的音效 -- 频道1
    environment_sound = None
    weatherController = None
    if theWeather != None:
        environment_sound = pygame.mixer.Sound("Assets/sound/environment/"+theWeather+".ogg")
        weatherController = WeatherSystem(theWeather,window_x,window_y)    
    #攻击的音效 -- 频道2
    all_attacking_sounds = {
        #突击步枪
        "AR": glob.glob(r'Assets/sound/attack/ar_*.ogg'),
        #手枪
        "HG": glob.glob(r'Assets/sound/attack/hg_*.ogg'),
        #机枪
        "MG": glob.glob(r'Assets/sound/attack/mg_*.ogg'),
        #步枪
        "RF": glob.glob(r'Assets/sound/attack/rf_*.ogg'),
        #冲锋枪
        "SMG": glob.glob(r'Assets/sound/attack/smg_*.ogg'),
    }
    for key in all_attacking_sounds:
        for i in range(len(all_attacking_sounds[key])):
            all_attacking_sounds[key][i] = pygame.mixer.Sound(all_attacking_sounds[key][i])
    
    #部分设定初始化
    the_character_get_click = ""
    enemies_get_attack = {}
    enemies_in_control = ""
    action_choice =""
    green_hide = True
    battle=True
    how_many_to_move = 0
    how_many_moved = 0
    isWaiting = True
    whose_round = "sangvisFerrisToPlayer"
    mouse_move_temp_x = -1
    mouse_move_temp_y = -1
    total_rounds = 1
    warnings_to_display = WarningSystem()
    damage_do_to_character = {}
    the_dead_one = {}
    screen_to_move_x=None
    screen_to_move_y=None
    pressKeyToMove={"up":False,"down":False,"left":False,"right":False}
    rightClickCharacterAlpha = 0
    battleSystemMainLoop = True
    txt_alpha = 250
    skill_target = None
    stayingTime = 0
    buttonGetHover = None
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
    #文字
    text_of_endround_move = 0
    text_of_endround_alpha = 400

    #关卡背景介绍信息文字
    for i in range(len(battle_info)):
        battle_info[i] = fontRender(battle_info[i],"white",window_x/76)

    #显示章节信息
    for a in range(0,250,2):
        black_bg.draw(screen)
        drawImg(title_number_display,((window_x-title_number_display.get_width())/2,400),screen)
        drawImg(title_main_display,((window_x-title_main_display.get_width())/2,500),screen)
        for i in range(len(battle_info)):
            battle_info[i].set_alpha(a)
            drawImg(battle_info[i],(window_x/20,window_y*0.75+battle_info[i].get_height()*1.5*i),screen)
            if i == 1:
                temp_secode = fontRender(time.strftime(":%S", time.localtime()),"white",window_x/76)
                temp_secode.set_alpha(a)
                drawImg(temp_secode,(window_x/20+battle_info[i].get_width(),window_y*0.75+battle_info[i].get_height()*1.5*i),screen)
        Display.flip()
    
    #加载音乐
    pygame.mixer.music.load("Assets/music/"+bg_music)
    pygame.mixer.music.play(loops=9999, start=0.0)
    pygame.mixer.music.set_volume(0.5)

    if dialogInfo["initial"] == None:
        dialog_to_display = None
    else:
        dialog_to_display = dialog_during_battle[dialogInfo["initial"]]

    #加载完成，章节标题淡出
    #如果战斗前无·对话
    if dialog_to_display == None:
        if pygame.mixer.Channel(1).get_busy() == False and environment_sound != None:
            pygame.mixer.Channel(1).play(environment_sound)
        for a in range(250,0,-5):
            #加载地图
            theMap.display_map(screen,local_x,local_y)
            #展示设施
            theMap.display_facility(screen,local_x,local_y)
            #角色动画
            for every_chara in characters_data:
                if theMap.mapData[characters_data[every_chara].y][characters_data[every_chara].x] == 2:
                    characters_data[every_chara].undetected = True
                else:
                    characters_data[every_chara].undetected = False
                characters_data[every_chara].draw("wait",screen,original_UI_img,perBlockWidth,theMap.row,local_x,local_y)
            for enemies in sangvisFerris_data:
                if (sangvisFerris_data[enemies].x,sangvisFerris_data[enemies].y) in theMap.lightArea or darkMode != True:
                    sangvisFerris_data[enemies].draw("wait",screen,original_UI_img,perBlockWidth,theMap.row,local_x,local_y)
            #加载雪花
            if weatherController != None:
                weatherController.display(screen,perBlockWidth,perBlockHeight,local_x,local_y)

            black_bg.set_alpha(a)
            black_bg.draw(screen)
            drawImg(title_number_display,((window_x-title_number_display.get_width())/2,400),screen)
            drawImg(title_main_display,((window_x-title_main_display.get_width())/2,500),screen)
            for i in range(len(battle_info)):
                battle_info[i].set_alpha(a)
                drawImg(battle_info[i],(window_x/20,window_y*0.75+battle_info[i].get_height()*1.5*i),screen)
                if i == 1:
                    temp_secode = fontRender(time.strftime(":%S", time.localtime()),"white",window_x/76)
                    temp_secode.set_alpha(a)
                    drawImg(temp_secode,(window_x/20+battle_info[i].get_width(),window_y*0.75+battle_info[i].get_height()*1.5*i),screen)
            Display.flip()
    
    #战斗系统主要loop
    while battleSystemMainLoop == True:
        #如果战斗前有对话
        if dialog_to_display != None:
            #设定初始化
            display_num = 0
            dialog_up_content_id = 0
            dialog_down_content_id = 0
            dialog_up_displayed_line = 0
            dialog_down_displayed_line = 0
            all_characters_path = None
            actionLoop = {}
            theAction = None
            idle_seconde = 0
            seconde_to_idle = None
            #对话系统总循环
            while display_num < len(dialog_to_display):
                if pygame.mixer.Channel(1).get_busy() == False and environment_sound != None:
                    pygame.mixer.Channel(1).play(environment_sound)
                #加载地图
                theMap.display_map(screen,local_x,local_y)
                #展示设施
                theMap.display_facility(screen,local_x,local_y)
                #角色动画
                for key,value in dicMerge(sangvisFerris_data,characters_data).items():
                    if value.faction == "character" or (value.x,value.y) in theMap.lightArea or darkMode != True:
                        if all_characters_path != None and key in all_characters_path:
                            value.draw("move",screen,None,perBlockWidth,theMap.row,local_x,local_y)
                        elif theAction != None and key in theAction:
                            pass
                        elif key in actionLoop:
                            if actionLoop[key] != "die":
                                value.draw(actionLoop[key],screen,None,perBlockWidth,theMap.row,local_x,local_y,False)
                            else:
                                value.draw(actionLoop[key],screen,None,perBlockWidth,theMap.row,local_x,local_y)
                        else:
                            value.draw("wait",screen,None,perBlockWidth,theMap.row,local_x,local_y)
                #加载雪花
                if weatherController != None:
                    weatherController.display(screen,perBlockWidth,perBlockHeight,local_x,local_y)
                #如果操作是移动
                if "move" in dialog_to_display[display_num]:
                    if all_characters_path == None:
                        #建立地图
                        map2d=Array2D(theMap.column,theMap.row)
                        #历遍地图，设置障碍方块
                        for y in range(theMap.row):
                            for x in range(theMap.column):
                                if theMap.mapData[y][x].canPassThrough == False:
                                    map2d[x][y]=1
                        #历遍设施，设置障碍方块
                        for key1 in theMap.facilityData:
                            for key2,value2 in theMap.facilityData[key1].items():
                                map2d[value2["x"]][value2["y"]]=1
                        all_characters_path = {}
                        # 历遍所有角色，将不需要移动的角色的坐标点设置为障碍方块，为需要移动的角色生成路径
                        for key,value in dicMerge(sangvisFerris_data,characters_data).items():
                            if key not in dialog_to_display[display_num]["move"]:
                                map2d[value.x][value.y] = 1
                            else:
                                #创建AStar对象,并设置起点和终点
                                star_point_x = value.x
                                star_point_y = value.y
                                aStar=AStar(map2d,Point(star_point_x,star_point_y),Point(dialog_to_display[display_num]["move"][key]["x"],dialog_to_display[display_num]["move"][key]["y"]))
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
                                    raise Exception('Waring: '+key+" cannot find her path, please rewrite her start position!")
                                all_characters_path[key] = the_route
                    if len(all_characters_path)>0:
                        if pygame.mixer.Channel(1).get_busy() == False and environment_sound != None:
                            pygame.mixer.Channel(1).play(environment_sound)
                        key_to_remove = []
                        reProcessMap = False
                        for key,value in all_characters_path.items():
                            if value != []:
                                if pygame.mixer.Channel(0).get_busy() == False:
                                    the_sound_id = random.randint(0,len(walking_sound)-1)
                                    pygame.mixer.Channel(0).play(walking_sound[the_sound_id])
                                if key in characters_data:
                                    if characters_data[key].x < value[0][0]:
                                        characters_data[key].x+=0.05
                                        characters_data[key].setFlip(False)
                                        if characters_data[key].x >= value[0][0]:
                                            characters_data[key].x = value[0][0]
                                            value.pop(0)
                                            reProcessMap = True
                                    elif characters_data[key].x > value[0][0]:
                                        characters_data[key].x-=0.05
                                        characters_data[key].setFlip(True)
                                        if characters_data[key].x <= value[0][0]:
                                            characters_data[key].x = value[0][0]
                                            value.pop(0)
                                            reProcessMap = True
                                    elif characters_data[key].y < value[0][1]:
                                        characters_data[key].y+=0.05
                                        characters_data[key].setFlip(True)
                                        if characters_data[key].y >= value[0][1]:
                                            characters_data[key].y = value[0][1]
                                            value.pop(0)
                                            reProcessMap = True
                                    elif characters_data[key].y > value[0][1]:
                                        characters_data[key].y-=0.05
                                        characters_data[key].setFlip(False)
                                        if characters_data[key].y <= value[0][1]:
                                            characters_data[key].y = value[0][1]
                                            value.pop(0)
                                            reProcessMap = True
                                    if theMap.mapData[int(characters_data[key].y)][int(characters_data[key].x)] == 2:
                                        characters_data[key].undetected = True
                                    else:
                                        characters_data[key].undetected = False
                                elif key in sangvisFerris_data:
                                    if sangvisFerris_data[key].x < value[0][0]:
                                        sangvisFerris_data[key].x+=0.05
                                        sangvisFerris_data[key].setFlip(True)
                                        if sangvisFerris_data[key].x >= value[0][0]:
                                            sangvisFerris_data[key].x = value[0][0]
                                            value.pop(0)
                                            reProcessMap = True
                                    elif sangvisFerris_data[key].x > value[0][0]:
                                        sangvisFerris_data[key].x-=0.05
                                        sangvisFerris_data[key].setFlip(False)
                                        if sangvisFerris_data[key].x <= value[0][0]:
                                            sangvisFerris_data[key].x = value[0][0]
                                            value.pop(0)
                                            reProcessMap = True
                                    elif sangvisFerris_data[key].y < value[0][1]:
                                        sangvisFerris_data[key].y+=0.05
                                        sangvisFerris_data[key].setFlip(False)
                                        if sangvisFerris_data[key].y >= value[0][1]:
                                            sangvisFerris_data[key].y = value[0][1]
                                            value.pop(0)
                                            reProcessMap = True
                                    elif sangvisFerris_data[key].y > value[0][1]:
                                        sangvisFerris_data[key].y-=0.05
                                        sangvisFerris_data[key].setFlip(True)
                                        if sangvisFerris_data[key].y <= value[0][1]:
                                            sangvisFerris_data[key].y = value[0][1]
                                            value.pop(0)
                                            reProcessMap = True
                            else:
                                key_to_remove.append(key)
                        if darkMode == True and reProcessMap == True:
                            theMap.lightArea = calculate_darkness(characters_data,theMap.facilityData["campfire"])
                            theMap.process_map()
                        for i in range(len(key_to_remove)):
                            all_characters_path.pop(key_to_remove[i])
                    else:
                        #脚步停止
                        if pygame.mixer.Channel(0).get_busy() != False:
                            pygame.mixer.Channel(0).stop()
                        display_num += 1
                        all_characters_path = None
                #改变方向
                elif "direction" in dialog_to_display[display_num]:
                    for key,value in dialog_to_display[display_num]["direction"].items():
                        if key in characters_data:
                            characters_data[key].setFlip(value)
                        elif key in sangvisFerris_data:
                            sangvisFerris_data[key].setFlip(value)
                    display_num += 1
                #改变动作（一次性）
                elif "action" in dialog_to_display[display_num]:
                    if theAction == None:
                        theAction = dialog_to_display[display_num]["action"]
                    else:
                        theActionNeedPop = []
                        if len(theAction) > 0:
                            for key,action in theAction.items():
                                if key in characters_data and characters_data[key].draw(action,screen,None,perBlockWidth,theMap.row,local_x,local_y,False) == False:
                                    if action != "die":
                                        characters_data[key].reset_imgId(action)
                                    theActionNeedPop.append(key)
                                elif key in sangvisFerris_data and sangvisFerris_data[key].draw(action,screen,None,perBlockWidth,theMap.row,local_x,local_y,False) == False:
                                    if action != "die":
                                        sangvisFerris_data[key].reset_imgId(action)
                                    theActionNeedPop.append(key)
                            if len(theActionNeedPop) > 0:
                                for i in range(len(theActionNeedPop)):
                                    theAction.pop(theActionNeedPop[i])
                        else:
                            display_num += 1
                            theAction = None
                #改变动作（长期）
                elif "actionLoop" in dialog_to_display[display_num]:
                    for key,action in dialog_to_display[display_num]["actionLoop"].items():
                        actionLoop[key] = action
                    display_num += 1
                #停止长期的动作改变
                elif "actionLoopStop" in dialog_to_display[display_num]:
                    for i in range(len(dialog_to_display[display_num]["actionLoopStop"])):
                        character_key = dialog_to_display[display_num]["actionLoopStop"][i]
                        if character_key in actionLoop:
                            if character_key in characters_data:
                                characters_data[character_key].reset_imgId(actionLoop[character_key])
                            elif character_key in sangvisFerris_data:
                                sangvisFerris_data[character_key].reset_imgId(actionLoop[character_key])
                            else:
                                raise Exception("Warning: Cannot find",character_key," while system is trying to reset the action.")
                            del actionLoop[character_key]
                    display_num += 1
                #开始对话
                elif "dialoguebox_up" in dialog_to_display[display_num] or "dialoguebox_down" in dialog_to_display[display_num]:
                    #对话框的移动
                    if dialoguebox_up.x > window_x/2+dialoguebox_up.width*0.4:
                        dialoguebox_up.x -= 150
                    if dialoguebox_down.x < window_x/2-dialoguebox_down.width*1.4:
                        dialoguebox_down.x += 150
                    #上方对话框
                    if dialog_to_display[display_num]["dialoguebox_up"] != None:
                        #对话框图片
                        dialoguebox_up.draw(screen)
                        #名字
                        if dialog_to_display[display_num]["dialoguebox_up"]["speaker"] != None:
                            drawImg(fontRender(dialog_to_display[display_num]["dialoguebox_up"]["speaker"],"white",window_x/80),(dialoguebox_up.width/7,dialoguebox_up.height/11),screen,dialoguebox_up.x,dialoguebox_up.y)
                        #正在播放的行
                        content = fontRender(dialog_to_display[display_num]["dialoguebox_up"]["content"][dialog_up_displayed_line][:dialog_up_content_id],"white",window_x/80)
                        drawImg(content,(window_x/45,window_x/35+dialog_up_displayed_line*window_x/80),screen,dialoguebox_up.x,dialoguebox_up.y)
                        if dialog_up_content_id < len(dialog_to_display[display_num]["dialoguebox_up"]["content"][dialog_up_displayed_line]):
                            dialog_up_content_id+=1
                        elif dialog_up_displayed_line < len(dialog_to_display[display_num]["dialoguebox_up"]["content"])-1:
                            dialog_up_displayed_line += 1
                            dialog_up_content_id = 0
                        for i in range(dialog_up_displayed_line):
                            content = fontRender(dialog_to_display[display_num]["dialoguebox_up"]["content"][i],"white",window_x/80)
                            drawImg(content,(window_x/45,window_x/35+i*window_x/80),screen,dialoguebox_up.x,dialoguebox_up.y)
                        #角色图标
                        if dialog_to_display[display_num]["dialoguebox_up"]["speaker_icon"] != None:
                            drawImg(character_icon_img_list[dialog_to_display[display_num]["dialoguebox_up"]["speaker_icon"]],(window_x*0.24,window_x/40),screen,dialoguebox_up.x,dialoguebox_up.y)
                    #下方对话框
                    if dialog_to_display[display_num]["dialoguebox_down"] != None:
                        #对话框图片
                        dialoguebox_down.draw(screen)
                        #名字
                        if dialog_to_display[display_num]["dialoguebox_down"]["speaker"] != None:
                            drawImg(fontRender(dialog_to_display[display_num]["dialoguebox_down"]["speaker"],"white",window_x/80),(dialoguebox_down.width*0.75,dialoguebox_down.height/10),screen,dialoguebox_down.x,dialoguebox_down.y)
                        #正在播放的行
                        content = fontRender(dialog_to_display[display_num]["dialoguebox_down"]["content"][dialog_down_displayed_line][:dialog_down_content_id],"white",window_x/80)
                        drawImg(content,(window_x/15,window_x/35+dialog_down_displayed_line*window_x/80),screen,dialoguebox_down.x,dialoguebox_down.y)
                        if dialog_down_content_id < len(dialog_to_display[display_num]["dialoguebox_down"]["content"][dialog_down_displayed_line]):
                            dialog_down_content_id+=1
                        elif dialog_down_displayed_line < len(dialog_to_display[display_num]["dialoguebox_down"]["content"])-1:
                            dialog_down_displayed_line += 1
                            dialog_down_content_id = 0
                        for i in range(dialog_down_displayed_line):
                            content = fontRender(dialog_to_display[display_num]["dialoguebox_down"]["content"][i],"white",window_x/80)
                            drawImg(content,(window_x/15,window_x/35+i*window_x/80),screen,dialoguebox_down.x,dialoguebox_down.y)
                        #角色图标
                        if dialog_to_display[display_num]["dialoguebox_down"]["speaker_icon"] != None:
                            drawImg(character_icon_img_list[dialog_to_display[display_num]["dialoguebox_down"]["speaker_icon"]],(window_x*0.01,window_x/40),screen,dialoguebox_down.x,dialoguebox_down.y)
                #闲置一定时间（秒）
                elif "idle" in dialog_to_display[display_num]:
                    if seconde_to_idle == None:
                        seconde_to_idle = dialog_to_display[display_num]["idle"]*fps
                    else:
                        if idle_seconde < seconde_to_idle:
                            idle_seconde += 1
                        else:
                            display_num += 1
                            idle_seconde = 0
                            seconde_to_idle = None
                #玩家输入按键判定
                for event in pygame.event.get():
                    if event.type == KEYDOWN:
                        if event.key == K_ESCAPE:
                            exit()
                    elif event.type == MOUSEBUTTONDOWN and event.button == 1 or ifJoystickInit and event.type == pygame.JOYBUTTONDOWN and joystick.get_button(0) == 1:
                        if "dialoguebox_up" in dialog_to_display[display_num] or "dialoguebox_down" in dialog_to_display[display_num]:
                            display_num +=1
                            if display_num < len(dialog_to_display):
                                if "dialoguebox_up" in dialog_to_display[display_num] or "dialoguebox_down" in dialog_to_display[display_num]:
                                    #检测上方对话框
                                    if dialog_to_display[display_num]["dialoguebox_up"] != None and dialog_to_display[display_num-1]["dialoguebox_up"] != None and dialog_to_display[display_num]["dialoguebox_up"]["speaker"] == dialog_to_display[display_num-1]["dialoguebox_up"]["speaker"]:
                                        if dialog_to_display[display_num]["dialoguebox_up"]["content"] != dialog_to_display[display_num]["dialoguebox_up"]["content"]:
                                            dialog_up_content_id = 0
                                            dialog_up_displayed_line = 0
                                        else:
                                            pass
                                    else:
                                        dialoguebox_up.x = window_x
                                        dialog_up_content_id = 0
                                        dialog_up_displayed_line = 0
                                    #检测下方对话框    
                                    if dialog_to_display[display_num]["dialoguebox_down"] != None and dialog_to_display[display_num-1]["dialoguebox_down"] != None and dialog_to_display[display_num]["dialoguebox_down"]["speaker"] == dialog_to_display[display_num-1]["dialoguebox_down"]["speaker"]:
                                        if dialog_to_display[display_num]["dialoguebox_down"]["content"] != dialog_to_display[display_num-1]["dialoguebox_down"]["content"]:
                                            dialog_down_content_id = 0
                                            dialog_down_displayed_line = 0
                                        else:
                                            pass
                                    else:
                                        dialoguebox_down.x = -window_x*0.3
                                        dialog_down_content_id = 0
                                        dialog_down_displayed_line = 0
                                else:
                                    dialoguebox_up.x = window_x
                                    dialog_up_content_id = 0
                                    dialog_up_displayed_line = 0
                                    dialoguebox_down.x = -window_x*0.3
                                    dialog_down_content_id = 0
                                    dialog_down_displayed_line = 0
                        break
                #渐变效果：一次性的
                if txt_alpha >= 0:
                    black_bg.set_alpha(txt_alpha)
                    black_bg.draw(screen)
                    title_number_display.set_alpha(txt_alpha)
                    title_main_display.set_alpha(txt_alpha)
                    drawImg(title_number_display,((window_x-title_number_display.get_width())/2,400),screen)
                    drawImg(title_main_display,((window_x-title_main_display.get_width())/2,500),screen)
                    for i in range(len(battle_info)):
                        battle_info[i].set_alpha(txt_alpha)
                        drawImg(battle_info[i],(window_x/20,window_y*0.75+battle_info[i].get_height()*1.5*i),screen)
                        if i == 1:
                            temp_secode = fontRender(time.strftime(":%S", time.localtime()),"white",window_x/76)
                            temp_secode.set_alpha(txt_alpha)
                            drawImg(temp_secode,(window_x/20+battle_info[i].get_width(),window_y*0.75+battle_info[i].get_height()*1.5*i),screen)
                    txt_alpha -= 5
                Display.flip()
            dialog_to_display = None
            battle = True

        # 游戏主循环
        while battle==True:
            #环境声音-频道1
            if pygame.mixer.Channel(1).get_busy() == False and environment_sound != None:
                pygame.mixer.Channel(1).play(environment_sound)
            right_click = False
            #获取鼠标坐标
            mouse_x,mouse_y=pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE and isWaiting == True:
                        green_hide = True
                        the_character_get_click = ""
                        action_choice = ""
                        attacking_range = None
                        skill_range = None
                        theMap.greenBlockImgArea = []
                    if event.key == K_w:
                        pressKeyToMove["up"]=True
                    if event.key == K_s:
                        pressKeyToMove["down"]=True
                    if event.key == K_a:
                        pressKeyToMove["left"]=True
                    if event.key == K_d:
                        pressKeyToMove["right"]=True
                    if event.key == K_m:
                        exit()
                    break
                elif event.type == KEYUP:
                    if event.key == K_w:
                        pressKeyToMove["up"]=False
                    if event.key == K_s:
                        pressKeyToMove["down"]=False
                    if event.key == K_a:
                        pressKeyToMove["left"]=False
                    if event.key == K_d:
                        pressKeyToMove["right"]=False
                    break
                #鼠标点击
                elif event.type == MOUSEBUTTONDOWN:
                    #上下滚轮-放大和缩小地图
                    if event.button == 1 and whose_round == "player":
                        right_click = True
                    if event.button == 4 and zoomIntoBe < 400:
                        zoomIntoBe += 20
                    elif event.button == 5 and zoomIntoBe > 200:
                        zoomIntoBe -= 20
                    break
                if ifJoystickInit:
                    if round(joystick.get_axis(1)) == -1:
                        pressKeyToMove["up"]=True
                    else:
                        pressKeyToMove["up"]=False
                    if round(joystick.get_axis(1)) == 1:
                        pressKeyToMove["down"]=True
                    else:
                        pressKeyToMove["down"]=False
                    if round(joystick.get_axis(0)) == 1:
                        pressKeyToMove["right"]=True
                    else:
                        pressKeyToMove["right"]=False
                    if round(joystick.get_axis(0)) == -1:
                        pressKeyToMove["left"]=True
                    else:
                        pressKeyToMove["left"]=False
            #移动屏幕
            if pygame.mouse.get_pressed()[2]:
                if mouse_move_temp_x == -1 and mouse_move_temp_y == -1:
                    mouse_move_temp_x = mouse_x
                    mouse_move_temp_y = mouse_y
                else:
                    if mouse_move_temp_x != mouse_x or mouse_move_temp_y != mouse_y:
                        if mouse_move_temp_x > mouse_x:
                            local_x += mouse_move_temp_x-mouse_x
                        elif mouse_move_temp_x < mouse_x:
                            local_x -= mouse_x-mouse_move_temp_x
                        if mouse_move_temp_y > mouse_y:
                            local_y += mouse_move_temp_y-mouse_y
                        elif mouse_move_temp_y < mouse_y:
                            local_y -= mouse_y-mouse_move_temp_y
                        mouse_move_temp_x = mouse_x
                        mouse_move_temp_y = mouse_y
            else:
                mouse_move_temp_x = -1
                mouse_move_temp_y = -1
            
            #根据zoomIntoBe调整zoomIn大小
            if zoomIntoBe != zoomIn:
                if zoomIntoBe < zoomIn:
                    zoomIn -= 5
                elif zoomIntoBe > zoomIn:
                    zoomIn += 5
                newPerBlockWidth = round(window_x/block_x*zoomIn/100)
                newPerBlockHeight = round(window_y/block_y*zoomIn/100)
                local_x += (perBlockWidth-newPerBlockWidth)*theMap.column/2
                local_y += (perBlockHeight-newPerBlockHeight)*theMap.row/2
                perBlockWidth = newPerBlockWidth
                perBlockHeight = newPerBlockHeight
                #根据perBlockWidth和perBlockHeight重新加载对应尺寸的UI
                UI_img["green"] = resizeImg(original_UI_img["green"], (perBlockWidth*0.9, None))
                UI_img["red"] = resizeImg(original_UI_img["red"], (perBlockWidth*0.9, None))
                UI_img["black"] = resizeImg(original_UI_img["black"], (perBlockWidth*0.9, None))
                UI_img["yellow"] = resizeImg(original_UI_img["yellow"], (perBlockWidth*0.9, None))
                UI_img["blue"] = resizeImg(original_UI_img["blue"], (perBlockWidth*0.9, None))
                UI_img["orange"] = resizeImg(original_UI_img["orange"], (perBlockWidth*0.9, None))
                select_menu_button =  resizeImg(select_menu_button_original, (round(perBlockWidth/2), round(perBlockWidth/4)))
                theMap.changePerBlockSize(perBlockWidth)
            else:
                zoomIn = zoomIntoBe

            #根据按键情况设定要移动的数值
            if pressKeyToMove["up"] == True:
                if screen_to_move_y== None:
                    screen_to_move_y = perBlockHeight
                else:
                    screen_to_move_y += perBlockHeight
            if pressKeyToMove["down"] == True:
                if screen_to_move_y== None:
                    screen_to_move_y = -perBlockHeight
                else:
                    screen_to_move_y -= perBlockHeight
            if pressKeyToMove["left"] == True:
                if screen_to_move_x== None:
                    screen_to_move_x = perBlockWidth
                else:
                    screen_to_move_x += perBlockWidth
            if pressKeyToMove["right"] == True:
                if screen_to_move_x== None:
                    screen_to_move_x = -perBlockWidth
                else:
                    screen_to_move_x -= perBlockWidth

            #如果需要移动屏幕
            if screen_to_move_x != None and screen_to_move_x != 0:
                temp_value = local_x + screen_to_move_x*0.2
                if -1*theMap.column*perBlockWidth<=temp_value<=0:
                    local_x = temp_value
                    screen_to_move_x*=0.8
                    if int(screen_to_move_x) == 0:
                        screen_to_move_x = 0
                else:
                    screen_to_move_x = 0
            if screen_to_move_y != None and screen_to_move_y !=0:
                temp_value = local_y + screen_to_move_y*0.2
                if -1*theMap.row*perBlockHeight<=temp_value<=0:
                    local_y = temp_value
                    screen_to_move_y*=0.8
                    if int(screen_to_move_y) == 0:
                        screen_to_move_y = 0
                else:
                    screen_to_move_y = 0
            
            #加载地图
            theMap.display_map(screen,local_x,local_y)
            block_get_click = theMap.calBlockInMap(UI_img["green"],local_x,local_y)
            #玩家回合
            if whose_round == "player":
                if right_click == True:
                    #如果点击了回合结束的按钮
                    if isHover(end_round_button) and isWaiting == True:
                        whose_round = "playerToSangvisFerris"
                        the_character_get_click = ""
                        green_hide = True
                    #是否在显示移动范围后点击了且点击区域在移动范围内
                    elif len(the_route) != 0 and block_get_click != None and (block_get_click["x"], block_get_click["y"]) in the_route and green_hide==False:
                        isWaiting = False
                        green_hide = True
                        characters_data[the_character_get_click].current_action_point -= len(the_route)*2
                    elif green_hide == "SelectMenu" and buttonGetHover == "attack":
                        if characters_data[the_character_get_click].current_bullets > 0 and characters_data[the_character_get_click].current_action_point >= 5:
                            action_choice = "attack"
                            green_hide = False
                        if characters_data[the_character_get_click].current_bullets <= 0:
                            warnings_to_display.add(warnings_info["magazine_is_empty"])
                        if characters_data[the_character_get_click].current_action_point < 5:
                            warnings_to_display.add(warnings_info["no_enough_ap_to_attack"])
                    elif green_hide == "SelectMenu" and buttonGetHover == "move":
                        if characters_data[the_character_get_click].current_action_point >= 2:
                            action_choice = "move"
                            green_hide = False
                        else:
                            warnings_to_display.add(warnings_info["no_enough_ap_to_move"])
                    elif green_hide == "SelectMenu" and buttonGetHover == "skill":
                        if characters_data[the_character_get_click].current_action_point >= 8:
                            action_choice = "skill"
                            green_hide = False
                        else:
                            warnings_to_display.add(warnings_info["no_enough_ap_to_use_skill"])
                    elif green_hide == "SelectMenu" and buttonGetHover == "reload":
                        if characters_data[the_character_get_click].current_action_point >= 5 and characters_data[the_character_get_click].bullets_carried > 0:
                            action_choice = "reload"
                            green_hide = False
                        if characters_data[the_character_get_click].bullets_carried <= 0:
                            warnings_to_display.add(warnings_info["no_bullets_left"])
                        if characters_data[the_character_get_click].current_action_point < 5:
                            warnings_to_display.add(warnings_info["no_enough_ap_to_reload"])
                    #攻击判定
                    elif action_choice == "attack" and green_hide == False and the_character_get_click != "" and len(enemies_get_attack)>0:
                        characters_data[the_character_get_click].current_action_point -= 5
                        isWaiting = False
                        green_hide = True
                        attacking_range = None
                    elif action_choice == "skill" and green_hide == False and the_character_get_click != "" and skill_target != None:
                        if skill_target in characters_data:
                            if characters_data[skill_target].x < characters_data[the_character_get_click].x:
                                characters_data[the_character_get_click].setFlip(True)
                            else:
                                characters_data[the_character_get_click].setFlip(False)
                        elif skill_target in sangvisFerris_data:
                            if sangvisFerris_data[skill_target].x < characters_data[the_character_get_click].x:
                                characters_data[the_character_get_click].setFlip(True)
                            else:
                                characters_data[the_character_get_click].setFlip(False)
                        characters_data[the_character_get_click].current_action_point -= 8
                        isWaiting = False
                        green_hide = True
                        skill_range = None
                    #判断是否有被点击的角色
                    elif block_get_click != None:
                        for key in characters_data:
                            if characters_data[key].x == block_get_click["x"] and characters_data[key].y == block_get_click["y"] and isWaiting == True and characters_data[key].dying == False and green_hide != False:
                                screen_to_move_x = None
                                screen_to_move_y = None
                                attacking_range = None
                                skill_range = None
                                the_character_get_click = key
                                green_hide = "SelectMenu"
                                break
                        
                #选择菜单的判定，显示功能在角色动画之后
                if green_hide == "SelectMenu":
                    #移动画面以使得被点击的角色可以被更好的操作
                    if screen_to_move_x == None:
                        tempX,tempY = calPosInMap(theMap.row,perBlockWidth,characters_data[the_character_get_click].x,characters_data[the_character_get_click].y,local_x,local_y)
                        if tempX < window_x*0.2 and local_x<=0:
                            screen_to_move_x = window_x*0.2-tempX
                        elif tempX > window_x*0.8 and local_x>=theMap.column*perBlockWidth*-1:
                            screen_to_move_x = window_x*0.8-tempX
                    if screen_to_move_y == None:
                        if tempY < window_y*0.2 and local_y<=0:
                            screen_to_move_y = window_y*0.2-tempY
                        elif tempY > window_y*0.8 and local_y>=theMap.row*perBlockHeight*-1:
                            screen_to_move_y = window_y*0.8-tempY
                        
                #显示攻击/移动/技能范围
                if green_hide == False and the_character_get_click != "":
                    #显示移动范围
                    if action_choice == "move" and block_get_click != None:
                        #创建AStar对象,并设置起点和终点为
                        star_point_x = characters_data[the_character_get_click].x
                        star_point_y = characters_data[the_character_get_click].y
                        end_point_x = block_get_click["x"]
                        end_point_y = block_get_click["y"]
                        max_blocks_can_move = int(characters_data[the_character_get_click].current_action_point/2)
                        if abs(end_point_x-star_point_x)+abs(end_point_y-star_point_y)<=max_blocks_can_move:
                            #建立地图
                            map2d=Array2D(theMap.column,theMap.row)
                            #历遍地图，设置障碍方块
                            for y in range(theMap.row):
                                for x in range(theMap.column):
                                    if theMap.mapData[y][x].canPassThrough == False:
                                        map2d[x][y]=1
                            #历遍设施，设置障碍方块
                            for key1 in theMap.facilityData:
                                if key1 != "chest":
                                    for key2,value2 in theMap.facilityData[key1].items():
                                        map2d[value2["x"]][value2["y"]]=1
                            # 历遍所有角色，将角色的坐标点设置为障碍方块
                            for key,value in dicMerge(characters_data,sangvisFerris_data).items():
                                map2d[value.x][value.y] = 1
                            aStar=AStar(map2d,Point(star_point_x,star_point_y),Point(end_point_x,end_point_y))
                            #开始寻路
                            pathList=aStar.start()
                            #遍历路径点,讲指定数量的点放到路径列表中
                            the_route = []
                            if pathList != None:
                                if len(pathList)>max_blocks_can_move:
                                    route_len = max_blocks_can_move
                                else:
                                    route_len = len(pathList)
                                for i in range(route_len):
                                    if Point(star_point_x+1,star_point_y) in pathList and (star_point_x+1,star_point_y) not in the_route:
                                        star_point_x+=1
                                    elif Point(star_point_x-1,star_point_y) in pathList and (star_point_x-1,star_point_y) not in the_route:
                                        star_point_x-=1
                                    elif Point(star_point_x,star_point_y+1) in pathList and (star_point_x,star_point_y+1) not in the_route:
                                        star_point_y+=1
                                    elif Point(star_point_x,star_point_y-1) in pathList and (star_point_x,star_point_y-1) not in the_route:
                                        star_point_y-=1
                                    else:
                                        #快速跳出
                                        break
                                    the_route.append((star_point_x,star_point_y))
                                #显示路径
                                for i in range(len(the_route)):
                                    xTemp,yTemp = calPosInMap(theMap.row,perBlockWidth,the_route[i][0],the_route[i][1],local_x,local_y)
                                    screen.blit(UI_img["green"],(xTemp+perBlockWidth*0.05,yTemp))
                                    if i == len(the_route)-1:
                                        displayInCenter(fontRender("-"+str((i+1)*2)+"AP","green",perBlockWidth/8,True),UI_img["green"],xTemp,yTemp,screen)
                    #显示攻击范围        
                    elif action_choice == "attack":
                        if attacking_range == None:
                            attacking_range = {"near":[],"middle":[],"far":[]}
                            for y in range(characters_data[the_character_get_click].y-characters_data[the_character_get_click].max_effective_range,characters_data[the_character_get_click].y+characters_data[the_character_get_click].max_effective_range+1):
                                if y < characters_data[the_character_get_click].y:
                                    for x in range(characters_data[the_character_get_click].x-characters_data[the_character_get_click].max_effective_range-(y-characters_data[the_character_get_click].y),characters_data[the_character_get_click].x+characters_data[the_character_get_click].max_effective_range+(y-characters_data[the_character_get_click].y)+1):
                                        if len(theMap.mapData)>y>=0 and len(theMap.mapData[y])>x>=0:
                                            if "far" in characters_data[the_character_get_click].effective_range and characters_data[the_character_get_click].effective_range["far"] != None and characters_data[the_character_get_click].effective_range["far"][0] <= abs(x-characters_data[the_character_get_click].x)+abs(y-characters_data[the_character_get_click].y) <= characters_data[the_character_get_click].effective_range["far"][1]:
                                                attacking_range["far"].append([x,y])
                                            elif "middle" in characters_data[the_character_get_click].effective_range and characters_data[the_character_get_click].effective_range["middle"] != None and characters_data[the_character_get_click].effective_range["middle"][0] <= abs(x-characters_data[the_character_get_click].x)+abs(y-characters_data[the_character_get_click].y) <= characters_data[the_character_get_click].effective_range["middle"][1]:
                                                attacking_range["middle"].append([x,y])
                                            elif "near" in characters_data[the_character_get_click].effective_range and characters_data[the_character_get_click].effective_range["near"] != None and characters_data[the_character_get_click].effective_range["near"][0] <= abs(x-characters_data[the_character_get_click].x)+abs(y-characters_data[the_character_get_click].y) <= characters_data[the_character_get_click].effective_range["near"][1]:
                                                attacking_range["near"].append([x,y])
                                else:
                                    for x in range(characters_data[the_character_get_click].x-characters_data[the_character_get_click].max_effective_range+(y-characters_data[the_character_get_click].y),characters_data[the_character_get_click].x+characters_data[the_character_get_click].max_effective_range-(y-characters_data[the_character_get_click].y)+1):
                                        if x == characters_data[the_character_get_click].x and y == characters_data[the_character_get_click].y:
                                            pass
                                        elif len(theMap.mapData)>y>=0 and len(theMap.mapData[y])>x>=0:
                                            if characters_data[the_character_get_click].effective_range["far"] != None and characters_data[the_character_get_click].effective_range["far"][0] <= abs(x-characters_data[the_character_get_click].x)+abs(y-characters_data[the_character_get_click].y) <= characters_data[the_character_get_click].effective_range["far"][1]:
                                                attacking_range["far"].append([x,y])
                                            elif characters_data[the_character_get_click].effective_range["middle"] != None and characters_data[the_character_get_click].effective_range["middle"][0] <= abs(x-characters_data[the_character_get_click].x)+abs(y-characters_data[the_character_get_click].y) <= characters_data[the_character_get_click].effective_range["middle"][1]:
                                                attacking_range["middle"].append([x,y])
                                            elif characters_data[the_character_get_click].effective_range["near"] != None and characters_data[the_character_get_click].effective_range["near"][0] <= abs(x-characters_data[the_character_get_click].x)+abs(y-characters_data[the_character_get_click].y) <= characters_data[the_character_get_click].effective_range["near"][1]:
                                                attacking_range["near"].append([x,y])
                        any_character_in_attack_range = False
                        for enemies in sangvisFerris_data:
                            if [sangvisFerris_data[enemies].x,sangvisFerris_data[enemies].y] in attacking_range["near"] or [sangvisFerris_data[enemies].x,sangvisFerris_data[enemies].y] in attacking_range["middle"] or [sangvisFerris_data[enemies].x,sangvisFerris_data[enemies].y] in attacking_range["far"]:
                                any_character_in_attack_range = True
                                break
                        if any_character_in_attack_range == True:
                            for potion in attacking_range["near"]:
                                xTemp,yTemp = calPosInMap(theMap.row,perBlockWidth,potion[0],potion[1],local_x,local_y)
                                drawImg(UI_img["green"],(xTemp+perBlockWidth*0.05,yTemp),screen)
                            for potion in attacking_range["middle"]:
                                xTemp,yTemp = calPosInMap(theMap.row,perBlockWidth,potion[0],potion[1],local_x,local_y)
                                drawImg(UI_img["blue"],(xTemp+perBlockWidth*0.05,yTemp),screen)
                            for potion in attacking_range["far"]:
                                xTemp,yTemp = calPosInMap(theMap.row,perBlockWidth,potion[0],potion[1],local_x,local_y)
                                drawImg(UI_img["yellow"],(xTemp+perBlockWidth*0.05,yTemp),screen)
                            if block_get_click != None:
                                the_attacking_range_area = []
                                for area in attacking_range:
                                    if [block_get_click["x"],block_get_click["y"]] in attacking_range[area]:
                                        for y in range(block_get_click["y"]-characters_data[the_character_get_click].attack_range+1,block_get_click["y"]+characters_data[the_character_get_click].attack_range):
                                            if y < block_get_click["y"]:
                                                for x in range(block_get_click["x"]-characters_data[the_character_get_click].attack_range-(y-block_get_click["y"])+1,block_get_click["x"]+characters_data[the_character_get_click].attack_range+(y-block_get_click["y"])):
                                                    if theMap.mapData[y][x].canPassThrough == True:
                                                        xTemp,yTemp = calPosInMap(theMap.row,perBlockWidth,x,y,local_x,local_y)
                                                        drawImg(UI_img["orange"],(xTemp+perBlockWidth*0.05,yTemp),screen)
                                                        the_attacking_range_area.append([x,y])
                                            else:
                                                for x in range(block_get_click["x"]-characters_data[the_character_get_click].attack_range+(y-block_get_click["y"])+1,block_get_click["x"]+characters_data[the_character_get_click].attack_range-(y-block_get_click["y"])):
                                                    if theMap.mapData[y][x].canPassThrough == True:
                                                        xTemp,yTemp = calPosInMap(theMap.row,perBlockWidth,x,y,local_x,local_y)
                                                        drawImg(UI_img["orange"],(xTemp+perBlockWidth*0.05,yTemp),screen)
                                                        the_attacking_range_area.append([x,y])
                                        break
                                enemies_get_attack = {}
                                if len(the_attacking_range_area) > 0:
                                    for enemies in sangvisFerris_data:
                                        if [sangvisFerris_data[enemies].x,sangvisFerris_data[enemies].y] in the_attacking_range_area and sangvisFerris_data[enemies].current_hp>0:
                                            if [sangvisFerris_data[enemies].x,sangvisFerris_data[enemies].y] in attacking_range["far"]:
                                                enemies_get_attack[enemies] = "far"
                                            elif [sangvisFerris_data[enemies].x,sangvisFerris_data[enemies].y] in attacking_range["middle"]:
                                                enemies_get_attack[enemies] = "middle"
                                            elif [sangvisFerris_data[enemies].x,sangvisFerris_data[enemies].y] in attacking_range["near"]:
                                                enemies_get_attack[enemies] = "near"
                        else:
                            warnings_to_display.add(warnings_info["no_enemy_in_effective_range"])
                            action_choice = ""
                            green_hide = "SelectMenu"
                    #显示技能范围        
                    elif action_choice == "skill":
                        skill_target = None
                        if characters_data[the_character_get_click].max_skill_range > 0:
                            if skill_range == None:
                                skill_range = {"near":[],"middle":[],"far":[]}
                                for y in range(characters_data[the_character_get_click].y-characters_data[the_character_get_click].max_skill_range,characters_data[the_character_get_click].y+characters_data[the_character_get_click].max_skill_range+1):
                                    if y < characters_data[the_character_get_click].y:
                                        for x in range(characters_data[the_character_get_click].x-characters_data[the_character_get_click].max_skill_range-(y-characters_data[the_character_get_click].y),characters_data[the_character_get_click].x+characters_data[the_character_get_click].max_skill_range+(y-characters_data[the_character_get_click].y)+1):
                                            if len(theMap.mapData)>y>=0 and len(theMap.mapData[y])>x>=0:
                                                if "far" in characters_data[the_character_get_click].skill_effective_range and characters_data[the_character_get_click].skill_effective_range["far"] != None and characters_data[the_character_get_click].skill_effective_range["far"][0] <= abs(x-characters_data[the_character_get_click].x)+abs(y-characters_data[the_character_get_click].y) <= characters_data[the_character_get_click].skill_effective_range["far"][1]:
                                                    skill_range["far"].append([x,y])
                                                elif "middle" in characters_data[the_character_get_click].skill_effective_range and characters_data[the_character_get_click].skill_effective_range["middle"] != None and characters_data[the_character_get_click].skill_effective_range["middle"][0] <= abs(x-characters_data[the_character_get_click].x)+abs(y-characters_data[the_character_get_click].y) <= characters_data[the_character_get_click].skill_effective_range["middle"][1]:
                                                    skill_range["middle"].append([x,y])
                                                elif "near" in characters_data[the_character_get_click].skill_effective_range and characters_data[the_character_get_click].skill_effective_range["near"] != None and characters_data[the_character_get_click].skill_effective_range["near"][0] <= abs(x-characters_data[the_character_get_click].x)+abs(y-characters_data[the_character_get_click].y) <= characters_data[the_character_get_click].skill_effective_range["near"][1]:
                                                    skill_range["near"].append([x,y])
                                    else:
                                        for x in range(characters_data[the_character_get_click].x-characters_data[the_character_get_click].max_skill_range+(y-characters_data[the_character_get_click].y),characters_data[the_character_get_click].x+characters_data[the_character_get_click].max_skill_range-(y-characters_data[the_character_get_click].y)+1):
                                            if x == characters_data[the_character_get_click].x and y == characters_data[the_character_get_click].y:
                                                pass
                                            elif len(theMap.mapData)>y>=0 and len(theMap.mapData[y])>x>=0:
                                                if "far" in characters_data[the_character_get_click].skill_effective_range and characters_data[the_character_get_click].skill_effective_range["far"] != None and characters_data[the_character_get_click].skill_effective_range["far"][0] <= abs(x-characters_data[the_character_get_click].x)+abs(y-characters_data[the_character_get_click].y) <= characters_data[the_character_get_click].skill_effective_range["far"][1]:
                                                    skill_range["far"].append([x,y])
                                                elif "middle" in characters_data[the_character_get_click].skill_effective_range and characters_data[the_character_get_click].skill_effective_range["middle"] != None and characters_data[the_character_get_click].skill_effective_range["middle"][0] <= abs(x-characters_data[the_character_get_click].x)+abs(y-characters_data[the_character_get_click].y) <= characters_data[the_character_get_click].skill_effective_range["middle"][1]:
                                                    skill_range["middle"].append([x,y])
                                                elif "near" in characters_data[the_character_get_click].skill_effective_range and characters_data[the_character_get_click].skill_effective_range["near"] != None and characters_data[the_character_get_click].skill_effective_range["near"][0] <= abs(x-characters_data[the_character_get_click].x)+abs(y-characters_data[the_character_get_click].y) <= characters_data[the_character_get_click].skill_effective_range["near"][1]:
                                                    skill_range["near"].append([x,y])
                            for position in skill_range["near"]:
                                xTemp,yTemp = calPosInMap(theMap.row,perBlockWidth,position[0],position[1],local_x,local_y)
                                drawImg(UI_img["green"],(xTemp+perBlockWidth*0.05,yTemp),screen)
                            for position in skill_range["middle"]:
                                xTemp,yTemp = calPosInMap(theMap.row,perBlockWidth,position[0],position[1],local_x,local_y)
                                drawImg(UI_img["yellow"],(xTemp+perBlockWidth*0.05,yTemp),screen)
                            for position in skill_range["far"]:
                                xTemp,yTemp = calPosInMap(theMap.row,perBlockWidth,position[0],position[1],local_x,local_y)
                                drawImg(UI_img["blue"],(xTemp+perBlockWidth*0.05,yTemp),screen)
                            if block_get_click != None:
                                the_skill_cover_area = []
                                for area in skill_range:
                                    if [block_get_click["x"],block_get_click["y"]] in skill_range[area]:
                                        for y in range(block_get_click["y"]-characters_data[the_character_get_click].skill_cover_range,block_get_click["y"]+characters_data[the_character_get_click].skill_cover_range):
                                            if y < block_get_click["y"]:
                                                for x in range(block_get_click["x"]-characters_data[the_character_get_click].skill_cover_range-(y-block_get_click["y"])+1,block_get_click["x"]+characters_data[the_character_get_click].skill_cover_range+(y-block_get_click["y"])):
                                                    if theMap.mapData[y][x].canPassThrough == True:
                                                        xTemp,yTemp = calPosInMap(theMap.row,perBlockWidth,x,y,local_x,local_y)
                                                        drawImg(UI_img["orange"],(xTemp+perBlockWidth*0.05,yTemp),screen)
                                                        the_skill_cover_area.append([x,y])
                                            else:
                                                for x in range(block_get_click["x"]-characters_data[the_character_get_click].skill_cover_range+(y-block_get_click["y"])+1,block_get_click["x"]+characters_data[the_character_get_click].skill_cover_range-(y-block_get_click["y"])):
                                                    if theMap.mapData[y][x].canPassThrough == True:
                                                        xTemp,yTemp = calPosInMap(theMap.row,perBlockWidth,x,y,local_x,local_y)
                                                        drawImg(UI_img["orange"],(xTemp+perBlockWidth*0.05,yTemp),screen)
                                                        the_skill_cover_area.append([x,y])
                                            skill_target = skill(the_character_get_click,{"x":block_get_click["x"],"y":block_get_click["y"]},the_skill_cover_area,sangvisFerris_data,characters_data)
                                        break
                        else:
                            skill_target = skill(the_character_get_click,{"x":None,"y":None},None,sangvisFerris_data,characters_data)
                            if skill_target != None:
                                characters_data[the_character_get_click].current_action_point -= 8
                                isWaiting = False
                                green_hide = True
                    #换弹
                    elif action_choice == "reload":
                        bullets_to_add = characters_data[the_character_get_click].magazine_capacity-characters_data[the_character_get_click].current_bullets
                        #需要换弹
                        if bullets_to_add > 0:
                            #如果角色有换弹动画
                            if characters_data[the_character_get_click].gif_dic["reload"] != None:
                                isWaiting = False
                            #如果角色没有换弹动画
                            else:
                                characters_data[the_character_get_click].current_action_point -= 5
                                #当所剩子弹足够换弹的时候
                                if bullets_to_add <= characters_data[the_character_get_click].bullets_carried:
                                    characters_data[the_character_get_click].bullets_carried -= bullets_to_add
                                    characters_data[the_character_get_click].current_bullets += bullets_to_add
                                #当所剩子弹不足以换弹的时候
                                else:
                                    characters_data[the_character_get_click].current_bullets += characters_data[the_character_get_click].bullets_carried
                                    characters_data[the_character_get_click].bullets_carried = 0
                                action_choice = ""
                        #无需换弹
                        elif bullets_to_add <= 0:
                            warnings_to_display.add(warnings_info["magazine_is_full"])
                            green_hide = "SelectMenu"
                        else:
                            print(the_character_get_click+" is causing trouble, please double check the files or reporting this issue")
                            break
                        
                #当有角色被点击时
                if the_character_get_click != "" and isWaiting == False:
                    #被点击的角色动画
                    green_hide=True
                    if action_choice == "move":
                        theCharacterMoved = False
                        if the_route != []:
                            if theMap.mapData[int(characters_data[the_character_get_click].y)][int(characters_data[the_character_get_click].x)] == 2:
                                characters_data[the_character_get_click].undetected = True
                            else:
                                characters_data[the_character_get_click].undetected = False
                            if pygame.mixer.Channel(0).get_busy() == False:
                                the_sound_id = random.randint(0,len(walking_sound)-1)
                                pygame.mixer.Channel(0).play(walking_sound[the_sound_id])
                            if characters_data[the_character_get_click].x < the_route[0][0]:
                                characters_data[the_character_get_click].x+=0.05
                                characters_data[the_character_get_click].setFlip(False)
                                if characters_data[the_character_get_click].x >= the_route[0][0]:
                                    characters_data[the_character_get_click].x = the_route[0][0]
                                    theCharacterMoved = True
                            elif characters_data[the_character_get_click].x > the_route[0][0]:
                                characters_data[the_character_get_click].x-=0.05
                                characters_data[the_character_get_click].setFlip(True)
                                if characters_data[the_character_get_click].x <= the_route[0][0]:
                                    characters_data[the_character_get_click].x = the_route[0][0]
                                    theCharacterMoved = True
                            elif characters_data[the_character_get_click].y < the_route[0][1]:
                                characters_data[the_character_get_click].y+=0.05
                                characters_data[the_character_get_click].setFlip(True)
                                if characters_data[the_character_get_click].y >= the_route[0][1]:
                                    characters_data[the_character_get_click].y = the_route[0][1]
                                    theCharacterMoved = True
                            elif characters_data[the_character_get_click].y > the_route[0][1]:
                                characters_data[the_character_get_click].setFlip(False)
                                characters_data[the_character_get_click].y-=0.05
                                if characters_data[the_character_get_click].y <= the_route[0][1]:
                                    characters_data[the_character_get_click].y = the_route[0][1]
                                    theCharacterMoved = True
                            if theCharacterMoved == True:
                                the_route.pop(0)
                                if darkMode == True:
                                    theMap.lightArea = calculate_darkness(characters_data,theMap.facilityData["campfire"])
                                    theMap.process_map()
                            characters_data[the_character_get_click].draw("move",screen,original_UI_img,perBlockWidth,theMap.row,local_x,local_y)
                        else:
                            pygame.mixer.Channel(0).stop()
                            #检测是不是站在补给上
                            chest_need_to_remove = None
                            for key,value in theMap.facilityData["chest"].items():
                                if value["x"] == characters_data[the_character_get_click].x and value["y"] == characters_data[the_character_get_click].y:
                                    original_UI_img["supplyBoard"].items = []
                                    for key2,value2 in value["item"].items():
                                        if key2 == "bullet":
                                            characters_data[the_character_get_click].bullets_carried += value2
                                            original_UI_img["supplyBoard"].items.append(fontRender("获得子弹: "+str(value2),"white",window_x/80))
                                        elif key2 == "hp":
                                            characters_data[the_character_get_click].current_hp += value2
                                            original_UI_img["supplyBoard"].items.append(fontRender("获得血量: "+str(value2),"white",window_x/80))
                                    if len(original_UI_img["supplyBoard"].items)>0:
                                        original_UI_img["supplyBoard"].yTogo = 10
                                    chest_need_to_remove = key
                                    break
                            if chest_need_to_remove != None:
                                del theMap.facilityData["chest"][chest_need_to_remove]
                            keyTemp = str(characters_data[the_character_get_click].x)+"-"+str(characters_data[the_character_get_click].y) 
                            #检测是否角色有set的动画
                            if characters_data[the_character_get_click].gif_dic["set"] != None:
                                characters_data[the_character_get_click].draw("set",screen,original_UI_img,perBlockWidth,theMap.row,local_x,local_y,False)
                                if characters_data[the_character_get_click].gif_dic["set"]["imgId"] == characters_data[the_character_get_click].gif_dic["set"]["imgNum"]-1:
                                    characters_data[the_character_get_click].gif_dic["set"]["imgId"]=0
                                    #当角色走到草丛中时
                                    if theMap.mapData[characters_data[the_character_get_click].y][characters_data[the_character_get_click].x] == 2:
                                        characters_data[the_character_get_click].undetected = True
                                    else:
                                        characters_data[the_character_get_click].undetected = False
                                    isWaiting = True
                                    the_character_get_click = ""
                                    action_choice = ""
                            else:
                                #当角色走到草丛中时
                                if theMap.mapData[characters_data[the_character_get_click].y][characters_data[the_character_get_click].x] == 2:
                                    characters_data[the_character_get_click].undetected = True
                                else:
                                    characters_data[the_character_get_click].undetected = False
                                isWaiting = True
                                the_character_get_click = ""
                                action_choice = ""
                            if keyTemp in dialogInfo["move"]:
                                dialog_to_display = dialog_during_battle[dialogInfo["move"][keyTemp]]
                                break
                    elif action_choice == "attack":
                        if characters_data[the_character_get_click].gif_dic["attack"]["imgId"] == 3 and characters_data[the_character_get_click].kind !="HOC":
                            pygame.mixer.Channel(2).play(all_attacking_sounds[characters_data[the_character_get_click].kind][random.randint(0,len(all_attacking_sounds[characters_data[the_character_get_click].kind])-1)])
                        if block_get_click["x"] < characters_data[the_character_get_click].x:
                            characters_data[the_character_get_click].setFlip(True)
                        else:
                            characters_data[the_character_get_click].setFlip(False)
                        characters_data[the_character_get_click].draw("attack",screen,original_UI_img,perBlockWidth,theMap.row,local_x,local_y,False)
                        if characters_data[the_character_get_click].gif_dic["attack"]["imgId"] == characters_data[the_character_get_click].gif_dic["attack"]["imgNum"]-2:
                            for each_enemy in enemies_get_attack:
                                if enemies_get_attack[each_enemy] == "near" and random.randint(1,100) <= 95 or enemies_get_attack[each_enemy] == "middle" and random.randint(1,100) <= 80 or enemies_get_attack[each_enemy] == "far" and random.randint(1,100) <= 65:
                                    the_damage = random.randint(characters_data[the_character_get_click].min_damage,characters_data[the_character_get_click].max_damage)
                                    sangvisFerris_data[each_enemy].decreaseHp(the_damage)
                                    damage_do_to_character[each_enemy] = fontRender("-"+str(the_damage),"red",window_x/76)
                                else:
                                    damage_do_to_character[each_enemy] = fontRender("Miss","red",window_x/76)
                        if characters_data[the_character_get_click].gif_dic["attack"]["imgId"] == characters_data[the_character_get_click].gif_dic["attack"]["imgNum"]-1:
                            characters_data[the_character_get_click].gif_dic["attack"]["imgId"] = 0
                            characters_data[the_character_get_click].current_bullets -= 1
                            isWaiting = True
                            the_character_get_click = ""
                            action_choice = ""
                    elif action_choice == "skill":
                        characters_data[the_character_get_click].draw("skill",screen,original_UI_img,perBlockWidth,theMap.row,local_x,local_y,False)
                        if characters_data[the_character_get_click].gif_dic["skill"]["imgId"] == characters_data[the_character_get_click].gif_dic["skill"]["imgNum"]-2:
                            temp_dic = skill(the_character_get_click,None,None,sangvisFerris_data,characters_data,"react",skill_target,damage_do_to_character)
                            characters_data = temp_dic["characters_data"]
                            sangvisFerris_data = temp_dic["sangvisFerris_data"]
                            damage_do_to_character = temp_dic["damage_do_to_character"]
                            del temp_dic
                        if characters_data[the_character_get_click].gif_dic["skill"]["imgId"] == characters_data[the_character_get_click].gif_dic["skill"]["imgNum"]-1:
                            characters_data[the_character_get_click].gif_dic["skill"]["imgId"] = 0
                            theMap.lightArea = calculate_darkness(characters_data,theMap.facilityData["campfire"])
                            theMap.process_map()
                            isWaiting =True
                            the_character_get_click = ""
                            action_choice = ""
                    elif action_choice == "reload":
                        characters_data[the_character_get_click].draw("reload",screen,original_UI_img,perBlockWidth,theMap.row,local_x,local_y,False)
                        if characters_data[the_character_get_click].gif_dic["reload"]["imgId"] == characters_data[the_character_get_click].gif_dic["reload"]["imgNum"]-2:
                            characters_data[the_character_get_click].gif_dic["reload"]["imgId"] = 0
                            characters_data[the_character_get_click].current_action_point -= 5
                            #当所剩子弹足够换弹的时候
                            if bullets_to_add <= characters_data[the_character_get_click].bullets_carried:
                                characters_data[the_character_get_click].bullets_carried -= bullets_to_add
                                characters_data[the_character_get_click].current_bullets += bullets_to_add
                            #当所剩子弹不足以换弹的时候
                            else:
                                characters_data[the_character_get_click].current_bullets += characters_data[the_character_get_click].bullets_carried
                                characters_data[the_character_get_click].bullets_carried = 0
                            isWaiting =True
                            the_character_get_click = ""
                            action_choice = ""
                elif the_character_get_click != "" and isWaiting == True:
                    characters_data[the_character_get_click].draw("wait",screen,original_UI_img,perBlockWidth,theMap.row,local_x,local_y)

            #↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓中间检测区↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓#
            if whose_round == "playerToSangvisFerris" or whose_round == "sangvisFerrisToPlayer":
                text_now_total_rounds = text_now_total_rounds_original
                text_now_total_rounds = fontRender(text_now_total_rounds.replace("NaN",str(total_rounds)), "white",window_x/38)
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
                        enemies_in_control_id = 0
                        sangvisFerris_name_list = []
                        for every_chara in sangvisFerris_data:
                            if sangvisFerris_data[every_chara].current_hp>0:
                                sangvisFerris_name_list.append(every_chara)
                        for every_chara in characters_data:
                            if characters_data[every_chara].dying != False:
                                characters_data[every_chara].dying -= 1
                        whose_round = "sangvisFerris"
                    elif whose_round == "sangvisFerrisToPlayer":
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
                the_character_get_click = ""
                green_hide = False
                whose_round = "result_win"
            
            #↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑中间检测区↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑#
            #敌方回合
            if whose_round == "sangvisFerris":
                enemies_in_control = sangvisFerris_name_list[enemies_in_control_id]
                if enemy_action == None:
                    enemy_action = AI(enemies_in_control,theMap,characters_data,sangvisFerris_data,the_characters_detected_last_round,blocks_setting)
                    print(enemies_in_control+" choses "+enemy_action["action"])
                if enemy_action["action"] == "move":
                    if enemy_action["route"] != []:
                        if pygame.mixer.Channel(0).get_busy() == False:
                            the_sound_id = random.randint(0,len(walking_sound)-1)
                            pygame.mixer.Channel(0).play(walking_sound[the_sound_id])
                        if sangvisFerris_data[enemies_in_control].x < enemy_action["route"][0][0]:
                            sangvisFerris_data[enemies_in_control].x+=0.05
                            sangvisFerris_data[enemies_in_control].setFlip(True)
                            if sangvisFerris_data[enemies_in_control].x >= enemy_action["route"][0][0]:
                                sangvisFerris_data[enemies_in_control].x = enemy_action["route"][0][0]
                                enemy_action["route"].pop(0)
                        elif sangvisFerris_data[enemies_in_control].x > enemy_action["route"][0][0]:
                            sangvisFerris_data[enemies_in_control].x-=0.05
                            sangvisFerris_data[enemies_in_control].setFlip(False)
                            if sangvisFerris_data[enemies_in_control].x <= enemy_action["route"][0][0]:
                                sangvisFerris_data[enemies_in_control].x = enemy_action["route"][0][0]
                                enemy_action["route"].pop(0)
                        elif sangvisFerris_data[enemies_in_control].y < enemy_action["route"][0][1]:
                            sangvisFerris_data[enemies_in_control].y+=0.05
                            sangvisFerris_data[enemies_in_control].setFlip(False)
                            if sangvisFerris_data[enemies_in_control].y >= enemy_action["route"][0][1]:
                                sangvisFerris_data[enemies_in_control].y = enemy_action["route"][0][1]
                                enemy_action["route"].pop(0)
                        elif sangvisFerris_data[enemies_in_control].y > enemy_action["route"][0][1]:
                            sangvisFerris_data[enemies_in_control].y-=0.05
                            sangvisFerris_data[enemies_in_control].setFlip(True)
                            if sangvisFerris_data[enemies_in_control].y <= enemy_action["route"][0][1]:
                                sangvisFerris_data[enemies_in_control].y = enemy_action["route"][0][1]
                                enemy_action["route"].pop(0)
                        if (int(sangvisFerris_data[enemies_in_control].x),int(sangvisFerris_data[enemies_in_control].y)) in theMap.lightArea or darkMode != True:
                            sangvisFerris_data[enemies_in_control].draw("move",screen,original_UI_img,perBlockWidth,theMap.row,local_x,local_y)
                    else:
                        if pygame.mixer.Channel(0).get_busy() == True:
                            pygame.mixer.Channel(0).stop()
                        enemies_in_control_id +=1
                        if enemies_in_control_id >= len(sangvisFerris_name_list):
                            whose_round = "sangvisFerrisToPlayer"
                            total_rounds += 1
                        enemy_action = None
                        enemies_in_control = ""
                elif enemy_action["action"] == "attack":
                    if (sangvisFerris_data[enemies_in_control].x,sangvisFerris_data[enemies_in_control].y) in theMap.lightArea or darkMode != True:
                        if characters_data[enemy_action["target"]].x > sangvisFerris_data[enemies_in_control].x:
                            sangvisFerris_data[enemies_in_control].setFlip(True)
                        else:
                            sangvisFerris_data[enemies_in_control].setFlip(False)
                        sangvisFerris_data[enemies_in_control].draw("attack",screen,original_UI_img,perBlockWidth,theMap.row,local_x,local_y,False)
                    else:
                        sangvisFerris_data[enemies_in_control].gif_dic["attack"]["imgId"] += 1
                    if sangvisFerris_data[enemies_in_control].gif_dic["attack"]["imgId"] == sangvisFerris_data[enemies_in_control].gif_dic["attack"]["imgNum"]-1:
                        temp_value = random.randint(0,100)
                        if enemy_action["target_area"] == "near" and temp_value <= 95 or enemy_action["target_area"] == "middle" and temp_value <= 80 or enemy_action["target_area"] == "far" and temp_value <= 65:
                            the_damage = random.randint(sangvisFerris_data[enemies_in_control].min_damage,sangvisFerris_data[enemies_in_control].max_damage)
                            result_of_round = characters_data[enemy_action["target"]].decreaseHp(the_damage,result_of_round)
                            theMap.lightArea = calculate_darkness(characters_data,theMap.facilityData["campfire"])
                            theMap.process_map()
                            damage_do_to_character[enemy_action["target"]] = fontRender("-"+str(the_damage),"red",window_x/76)
                        else:
                            damage_do_to_character[enemy_action["target"]] = fontRender("Miss","red",window_x/76)
                        sangvisFerris_data[enemies_in_control].gif_dic["attack"]["imgId"] = 0
                        enemies_in_control_id +=1
                        if enemies_in_control_id >= len(sangvisFerris_name_list):
                            whose_round = "sangvisFerrisToPlayer"
                            total_rounds += 1
                        enemy_action = None
                        enemies_in_control = ""
                elif enemy_action["action"] == "move&attack":
                    if len(enemy_action["route"]) > 0:
                        if pygame.mixer.Channel(0).get_busy() == False:
                            the_sound_id = random.randint(0,len(walking_sound)-1)
                            pygame.mixer.Channel(0).play(walking_sound[the_sound_id])
                        if sangvisFerris_data[enemies_in_control].x < enemy_action["route"][0][0]:
                            sangvisFerris_data[enemies_in_control].x+=0.05
                            sangvisFerris_data[enemies_in_control].setFlip(True)
                            if sangvisFerris_data[enemies_in_control].x >= enemy_action["route"][0][0]:
                                sangvisFerris_data[enemies_in_control].x = enemy_action["route"][0][0]
                                enemy_action["route"].pop(0)
                        elif sangvisFerris_data[enemies_in_control].x > enemy_action["route"][0][0]:
                            sangvisFerris_data[enemies_in_control].x-=0.05
                            sangvisFerris_data[enemies_in_control].setFlip(False)
                            if sangvisFerris_data[enemies_in_control].x <= enemy_action["route"][0][0]:
                                sangvisFerris_data[enemies_in_control].x = enemy_action["route"][0][0]
                                enemy_action["route"].pop(0)
                        elif sangvisFerris_data[enemies_in_control].y < enemy_action["route"][0][1]:
                            sangvisFerris_data[enemies_in_control].y+=0.05
                            sangvisFerris_data[enemies_in_control].setFlip(False)
                            if sangvisFerris_data[enemies_in_control].y >= enemy_action["route"][0][1]:
                                sangvisFerris_data[enemies_in_control].y = enemy_action["route"][0][1]
                                enemy_action["route"].pop(0)
                        elif sangvisFerris_data[enemies_in_control].y > enemy_action["route"][0][1]:
                            sangvisFerris_data[enemies_in_control].y-=0.05
                            sangvisFerris_data[enemies_in_control].setFlip(True)
                            if sangvisFerris_data[enemies_in_control].y <= enemy_action["route"][0][1]:
                                sangvisFerris_data[enemies_in_control].y = enemy_action["route"][0][1]
                                enemy_action["route"].pop(0)
                        if (int(sangvisFerris_data[enemies_in_control].x),int(sangvisFerris_data[enemies_in_control].y)) in theMap.lightArea or darkMode != True:
                            sangvisFerris_data[enemies_in_control].draw("move",screen,original_UI_img,perBlockWidth,theMap.row,local_x,local_y)
                    else:
                        if pygame.mixer.Channel(0).get_busy() == True:
                            pygame.mixer.Channel(0).stop()
                        if (sangvisFerris_data[enemies_in_control].x,sangvisFerris_data[enemies_in_control].y) in theMap.lightArea or darkMode != True:
                            if characters_data[enemy_action["target"]].x > sangvisFerris_data[enemies_in_control].x:
                                sangvisFerris_data[enemies_in_control].setFlip(True)
                            else:
                                sangvisFerris_data[enemies_in_control].setFlip(False)
                            sangvisFerris_data[enemies_in_control].draw("attack",screen,original_UI_img,perBlockWidth,theMap.row,local_x,local_y,False)
                        else:
                            sangvisFerris_data[enemies_in_control].gif_dic["attack"]["imgId"] += 1
                        if sangvisFerris_data[enemies_in_control].gif_dic["attack"]["imgId"] == sangvisFerris_data[enemies_in_control].gif_dic["attack"]["imgNum"]-1:
                            temp_value = random.randint(0,100)
                            if enemy_action["target_area"] == "near" and temp_value <= 95 or enemy_action["target_area"] == "middle" and temp_value <= 80 or enemy_action["target_area"] == "far" and temp_value <= 65:
                                the_damage = random.randint(sangvisFerris_data[enemies_in_control].min_damage,sangvisFerris_data[enemies_in_control].max_damage)
                                result_of_round = characters_data[enemy_action["target"]].decreaseHp(the_damage,result_of_round)
                                theMap.lightArea = calculate_darkness(characters_data,theMap.facilityData["campfire"])
                                theMap.process_map()
                                damage_do_to_character[enemy_action["target"]] = fontRender("-"+str(the_damage),"red",window_x/76)
                            else:
                                damage_do_to_character[enemy_action["target"]] = fontRender("Miss","red",window_x/76)
                            sangvisFerris_data[enemies_in_control].gif_dic["attack"]["imgId"] = 0
                            enemies_in_control_id +=1
                            if enemies_in_control_id >= len(sangvisFerris_name_list):
                                whose_round = "sangvisFerrisToPlayer"
                                total_rounds += 1
                            enemy_action = None
                            enemies_in_control = ""
                elif enemy_action["action"] == "stay":
                    enemies_in_control_id +=1
                    if enemies_in_control_id >= len(sangvisFerris_name_list):
                        whose_round = "sangvisFerrisToPlayer"
                        total_rounds += 1
                    enemy_action = None
                    enemies_in_control = ""
                else:
                    print("warning: not choice")

            #↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓角色动画展示区↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓#
            rightClickCharacterAlphaDeduct = True
            for key,value in dicMerge(characters_data,sangvisFerris_data).items():
                #根据血量判断角色的动作
                if value.faction == "character" and key != the_character_get_click or value.faction == "sangvisFerri" and key != enemies_in_control and (value.x,value.y) in theMap.lightArea or value.faction == "sangvisFerri" and key != enemies_in_control and darkMode != True:
                    if value.current_hp > 0:
                        if green_hide == True and pygame.mouse.get_pressed()[2]:
                            if block_get_click != None and block_get_click["x"] == value.x and block_get_click["y"]  == value.y:
                                rightClickCharacterAlphaDeduct = False
                                if rightClickCharacterAlpha < 150:
                                    rightClickCharacterAlpha += 10
                                UI_img["yellow"].set_alpha(rightClickCharacterAlpha)
                                UI_img["blue"].set_alpha(rightClickCharacterAlpha)
                                UI_img["green"].set_alpha(rightClickCharacterAlpha)
                                for y in range(value.y-value.max_effective_range,value.y+value.max_effective_range+1):
                                    if y < value.y:
                                        for x in range(value.x-value.max_effective_range-(y-value.y),value.x+value.max_effective_range+(y-value.y)+1):
                                            if len(theMap.mapData)>y>=0 and len(theMap.mapData[y])>x>=0:
                                                if value.effective_range["far"] != None and value.effective_range["far"][0] <= abs(x-value.x)+abs(y-value.y) <= value.effective_range["far"][1]:
                                                    xTemp,yTemp = calPosInMap(theMap.row,perBlockWidth,x,y,local_x,local_y)
                                                    drawImg(UI_img["yellow"],(xTemp+perBlockWidth*0.05,yTemp),screen)
                                                elif value.effective_range["middle"] != None and value.effective_range["middle"][0] <= abs(x-value.x)+abs(y-value.y) <= value.effective_range["middle"][1]:
                                                    xTemp,yTemp = calPosInMap(theMap.row,perBlockWidth,x,y,local_x,local_y)
                                                    drawImg(UI_img["blue"],(xTemp+perBlockWidth*0.05,yTemp),screen)
                                                elif value.effective_range["near"] != None and value.effective_range["near"][0] <= abs(x-value.x)+abs(y-value.y) <= value.effective_range["near"][1]:
                                                    xTemp,yTemp = calPosInMap(theMap.row,perBlockWidth,x,y,local_x,local_y)
                                                    drawImg(UI_img["green"],(xTemp+perBlockWidth*0.05,yTemp),screen)
                                    else:
                                        for x in range(value.x-value.max_effective_range+(y-value.y),value.x+value.max_effective_range-(y-value.y)+1):
                                            if x == value.x and y == value.y:
                                                pass
                                            elif len(theMap.mapData)>y>=0 and len(theMap.mapData[y])>x>=0:
                                                if value.effective_range["far"] != None and value.effective_range["far"][0] <= abs(x-value.x)+abs(y-value.y) <= value.effective_range["far"][1]:
                                                    xTemp,yTemp = calPosInMap(theMap.row,perBlockWidth,x,y,local_x,local_y)
                                                    drawImg(UI_img["yellow"],(xTemp+perBlockWidth*0.05,yTemp),screen)
                                                elif value.effective_range["middle"] != None and value.effective_range["middle"][0] <= abs(x-value.x)+abs(y-value.y) <= value.effective_range["middle"][1]:
                                                    xTemp,yTemp = calPosInMap(theMap.row,perBlockWidth,x,y,local_x,local_y)
                                                    drawImg(UI_img["blue"],(xTemp+perBlockWidth*0.05,yTemp),screen)
                                                elif value.effective_range["near"] != None and value.effective_range["near"][0] <= abs(x-value.x)+abs(y-value.y) <= value.effective_range["near"][1]:
                                                    xTemp,yTemp = calPosInMap(theMap.row,perBlockWidth,x,y,local_x,local_y)
                                                    drawImg(UI_img["green"],(xTemp+perBlockWidth*0.05,yTemp),screen)
                                UI_img["yellow"].set_alpha(150)
                                UI_img["blue"].set_alpha(150)
                                UI_img["green"].set_alpha(150)
                        value.draw("wait",screen,original_UI_img,perBlockWidth,theMap.row,local_x,local_y)
                    elif value.current_hp<=0:
                        value.draw("die",screen,original_UI_img,perBlockWidth,theMap.row,local_x,local_y,False)
                #是否有在播放死亡角色的动画（而不是倒地状态）
                if value.current_hp<=0 and key not in the_dead_one:
                    if value.faction == "character" and value.kind == "HOC" or value.faction == "sangvisFerri":
                        the_dead_one[key] = value.faction
                #伤害/治理数值显示
                if key in damage_do_to_character:
                    the_alpha_to_check = damage_do_to_character[key].get_alpha()
                    if the_alpha_to_check > 0:
                        xTemp,yTemp = calPosInMap(theMap.row,perBlockWidth,value.x,value.y,local_x,local_y)
                        xTemp+=perBlockWidth*0.05
                        yTemp-=perBlockWidth*0.05
                        displayInCenter(damage_do_to_character[key],UI_img["green"],xTemp,yTemp,screen)
                        damage_do_to_character[key].set_alpha(the_alpha_to_check-5)
                    else:
                        del damage_do_to_character[key]
            
            if rightClickCharacterAlphaDeduct == True and rightClickCharacterAlpha>0:
                rightClickCharacterAlpha-=10

            the_dead_one_remove = []
            for key,value in the_dead_one.items():
                if value == "sangvisFerri":
                    if sangvisFerris_data[key].gif_dic["die"]["imgId"] == sangvisFerris_data[key].gif_dic["die"]["imgNum"]-1:
                        the_alpha = sangvisFerris_data[key].gif_dic["die"]["img"][-1].get_alpha()
                        if the_alpha > 0:
                            sangvisFerris_data[key].gif_dic["die"]["img"][-1].set_alpha(the_alpha-5)
                        else:
                            the_dead_one_remove.append(key)
                            del sangvisFerris_data[key]
                            result_of_round["total_kills"]+=1
                elif value == "character":
                    if characters_data[key].gif_dic["die"]["imgId"] == characters_data[key].gif_dic["die"]["imgNum"]-1:
                        the_alpha = characters_data[key].gif_dic["die"]["img"][-1].get_alpha()
                        if the_alpha > 0:
                            characters_data[key].gif_dic["die"]["img"][-1].set_alpha(the_alpha-5)
                        else:
                            the_dead_one_remove.append(key)
                            del characters_data[key]
                            result_of_round["times_characters_down"]+=1
                            theMap.lightArea = calculate_darkness(characters_data,theMap.facilityData["campfire"])
                            theMap.process_map()
            for key in the_dead_one_remove:
                del the_dead_one[key]
            #↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑角色动画展示区↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑#
            #展示设施
            theMap.display_facility(screen,local_x,local_y)
            #显示选择菜单
            if green_hide == "SelectMenu":
                buttonGetHover = None
                #左下角的角色信息
                text_size = 20
                the_character_get_click_info_board.draw(screen)
                padding = (the_character_get_click_info_board.height-character_icon_img_list[characters_data[the_character_get_click].type].get_height())/2
                drawImg(character_icon_img_list[characters_data[the_character_get_click].type],(padding,padding),screen,the_character_get_click_info_board.x,the_character_get_click_info_board.y)
                tcgc_hp1 = fontRender("HP: ","white",window_x/96)
                tcgc_hp2 = fontRender(str(characters_data[the_character_get_click].current_hp)+"/"+str(characters_data[the_character_get_click].max_hp),"black",window_x/96)
                tcgc_action_point1 = fontRender("AP: ","white",window_x/96)
                tcgc_action_point2 = fontRender(str(characters_data[the_character_get_click].current_action_point)+"/"+str(characters_data[the_character_get_click].max_action_point),"black",window_x/96)
                tcgc_bullets_situation1 = fontRender("BP: ","white",window_x/96)
                tcgc_bullets_situation2 = fontRender(str(characters_data[the_character_get_click].current_bullets)+"/"+str(characters_data[the_character_get_click].bullets_carried),"black",window_x/96)
                drawImg(tcgc_hp1,(character_icon_img_list[characters_data[the_character_get_click].type].get_width()*2,padding),screen,the_character_get_click_info_board.x,the_character_get_click_info_board.y)
                drawImg(tcgc_action_point1,(character_icon_img_list[characters_data[the_character_get_click].type].get_width()*2,padding+text_size*1.5),screen,the_character_get_click_info_board.x,the_character_get_click_info_board.y)
                drawImg(tcgc_bullets_situation1,(character_icon_img_list[characters_data[the_character_get_click].type].get_width()*2,padding+text_size*3),screen,the_character_get_click_info_board.x,the_character_get_click_info_board.y)
                hp_empty = resizeImg(original_UI_img["hp_empty"],(int(the_character_get_click_info_board.width/3),int(text_size)))
                drawImg(hp_empty,(character_icon_img_list[characters_data[the_character_get_click].type].get_width()*2.4,padding),screen,the_character_get_click_info_board.x,the_character_get_click_info_board.y)
                drawImg(hp_empty,(character_icon_img_list[characters_data[the_character_get_click].type].get_width()*2.4,padding+text_size*1.5),screen,the_character_get_click_info_board.x,the_character_get_click_info_board.y)
                drawImg(hp_empty,(character_icon_img_list[characters_data[the_character_get_click].type].get_width()*2.4,padding+text_size*3),screen,the_character_get_click_info_board.x,the_character_get_click_info_board.y)
                drawImg(resizeImg(original_UI_img["hp_green"],(int(hp_empty.get_width()*characters_data[the_character_get_click].current_hp/characters_data[the_character_get_click].max_hp),int(text_size))),(character_icon_img_list[characters_data[the_character_get_click].type].get_width()*2.4,padding),screen,the_character_get_click_info_board.x,the_character_get_click_info_board.y)
                drawImg(resizeImg(original_UI_img["action_point_blue"],(int(hp_empty.get_width()*characters_data[the_character_get_click].current_action_point/characters_data[the_character_get_click].max_action_point),int(text_size))),(character_icon_img_list[characters_data[the_character_get_click].type].get_width()*2.4,padding+text_size*1.5),screen,the_character_get_click_info_board.x,the_character_get_click_info_board.y)
                drawImg(resizeImg(original_UI_img["bullets_number_brown"],(int(hp_empty.get_width()*characters_data[the_character_get_click].current_bullets/characters_data[the_character_get_click].magazine_capacity),int(text_size))),(character_icon_img_list[characters_data[the_character_get_click].type].get_width()*2.4,padding+text_size*3),screen,the_character_get_click_info_board.x,the_character_get_click_info_board.y)
                displayInCenter(tcgc_hp2,hp_empty,character_icon_img_list[characters_data[the_character_get_click].type].get_width()*2.4,padding,screen,the_character_get_click_info_board.x,the_character_get_click_info_board.y)
                displayInCenter(tcgc_action_point2,hp_empty,character_icon_img_list[characters_data[the_character_get_click].type].get_width()*2.4,padding+text_size*1.5,screen,the_character_get_click_info_board.x,the_character_get_click_info_board.y)
                displayInCenter(tcgc_bullets_situation2,hp_empty,character_icon_img_list[characters_data[the_character_get_click].type].get_width()*2.4,padding+text_size*3,screen,the_character_get_click_info_board.x,the_character_get_click_info_board.y)
                #----选择菜单----
                tempLocation = theMap.getBlockExactLocation(characters_data[the_character_get_click].x,characters_data[the_character_get_click].y,local_x,local_y)
                #攻击按钮 - 左
                txt_temp = fontRender(selectMenuButtons_dic["attack"],"black",round(perBlockWidth/10))
                txt_temp2 = fontRender("5 AP","black",round(perBlockWidth/13))
                txt_tempX = tempLocation["xStart"]-select_menu_button.get_width()*0.6
                txt_tempY = tempLocation["yStart"]+select_menu_button.get_height()*0.6
                if isHoverOn(select_menu_button,(txt_tempX,txt_tempY)):
                    buttonGetHover = "attack"
                drawImg(select_menu_button,(txt_tempX,txt_tempY),screen)
                drawImg(txt_temp,((select_menu_button.get_width()-txt_temp.get_width())/2,txt_temp.get_height()*0.4),screen,txt_tempX,txt_tempY)
                drawImg(txt_temp2,((select_menu_button.get_width()-txt_temp2.get_width())/2,txt_temp.get_height()*1.5),screen,txt_tempX,txt_tempY)
                #移动按钮 - 右
                txt_temp = fontRender(selectMenuButtons_dic["move"],"black",round(perBlockWidth/10))
                txt_temp2 = fontRender("2N AP","black",round(perBlockWidth/13))
                txt_tempX = tempLocation["xEnd"]-select_menu_button.get_width()*0.4
                txt_tempY = tempLocation["yStart"]+select_menu_button.get_height()*0.6
                if isHoverOn(select_menu_button,(txt_tempX,txt_tempY)):
                    buttonGetHover = "move"
                drawImg(select_menu_button,(txt_tempX,txt_tempY),screen)
                drawImg(txt_temp,((select_menu_button.get_width()-txt_temp.get_width())/2,txt_temp.get_height()*0.4),screen,txt_tempX,txt_tempY)
                drawImg(txt_temp2,((select_menu_button.get_width()-txt_temp2.get_width())/2,txt_temp.get_height()*1.5),screen,txt_tempX,txt_tempY)
                #技能按钮 - 上
                if characters_data[the_character_get_click].kind != "HOC":
                    txt_temp = fontRender(selectMenuButtons_dic["skill"],"black",round(perBlockWidth/10))
                    txt_temp2 = fontRender("8 AP","black",round(perBlockWidth/13))
                    txt_tempX = tempLocation["xStart"]+perBlockWidth/4
                    txt_tempY = tempLocation["yStart"]-perBlockWidth*0.3
                    if isHoverOn(select_menu_button,(txt_tempX,txt_tempY)):
                        buttonGetHover = "skill"
                    drawImg(select_menu_button,(txt_tempX,txt_tempY),screen)
                    drawImg(txt_temp,((select_menu_button.get_width()-txt_temp.get_width())/2,txt_temp.get_height()*0.4),screen,txt_tempX,txt_tempY)
                    drawImg(txt_temp2,((select_menu_button.get_width()-txt_temp2.get_width())/2,txt_temp.get_height()*1.5),screen,txt_tempX,txt_tempY)
                #换弹按钮 - 下
                txt_temp = fontRender(selectMenuButtons_dic["reload"],"black",round(perBlockWidth/10))
                txt_temp2 = fontRender("5 AP","black",round(perBlockWidth/13))
                txt_tempX = tempLocation["xStart"]+perBlockWidth/4
                txt_tempY = tempLocation["yStart"]+perBlockWidth*0.55
                if isHoverOn(select_menu_button,(txt_tempX,txt_tempY)):
                    buttonGetHover = "reload"
                drawImg(select_menu_button,(txt_tempX,txt_tempY),screen)
                drawImg(txt_temp,((select_menu_button.get_width()-txt_temp.get_width())/2,txt_temp.get_height()*0.4),screen,txt_tempX,txt_tempY)
                drawImg(txt_temp2,((select_menu_button.get_width()-txt_temp2.get_width())/2,txt_temp.get_height()*1.5),screen,txt_tempX,txt_tempY)

            #加载雪花
            if weatherController != None:
                weatherController.display(screen,perBlockWidth,perBlockHeight,local_x,local_y)
            
            #显示获取到的物资
            if original_UI_img["supplyBoard"].yTogo == 10:
                if original_UI_img["supplyBoard"].y < original_UI_img["supplyBoard"].yTogo:
                    original_UI_img["supplyBoard"].y += 5
                else:
                    if stayingTime == 30:
                        original_UI_img["supplyBoard"].yTogo = -window_y/12
                        stayingTime = 0
                    else:
                        stayingTime += 1
            else:
                if original_UI_img["supplyBoard"].y > original_UI_img["supplyBoard"].yTogo:
                    original_UI_img["supplyBoard"].y -= 5

            original_UI_img["supplyBoard"].draw(screen)
            if len(original_UI_img["supplyBoard"].items) > 0 and original_UI_img["supplyBoard"].y != -window_y/30:
                lenTemp = 0
                for i in range(len(original_UI_img["supplyBoard"].items)):
                    lenTemp += original_UI_img["supplyBoard"].items[i].get_width()*1.5
                start_point = (window_x - lenTemp)/2
                for i in range(len(original_UI_img["supplyBoard"].items)):
                    start_point += original_UI_img["supplyBoard"].items[i].get_width()*0.25
                    drawImg(original_UI_img["supplyBoard"].items[i],(start_point,(original_UI_img["supplyBoard"].height - original_UI_img["supplyBoard"].items[i].get_height())/2),screen,0,original_UI_img["supplyBoard"].y)
                    start_point += original_UI_img["supplyBoard"].items[i].get_width()*1.25

            if whose_round == "player":
                #加载结束回合的按钮
                end_round_button.draw(screen)

            #显示警告
            warnings_to_display.display(screen,window_x,window_y)

            #加载音乐
            while pygame.mixer.music.get_busy() != 1:
                pygame.mixer.music.load("Assets/music/"+bg_music)
                pygame.mixer.music.play(loops=9999, start=0.0)
                pygame.mixer.music.set_volume(0.5)

            #结束动画
            if whose_round == "result_win":
                total_kills = fontRender("总杀敌："+str(result_of_round["total_kills"]),"white",window_x/96)
                result_of_round["total_time"] = time.localtime(time.time()-result_of_round["total_time"])
                total_time = fontRender("通关时间："+str(time.strftime('%M:%S',result_of_round["total_time"])),"white",window_x/96)
                result_of_round["total_rounds"] = total_rounds
                total_rounds_txt = fontRender("通关回合数："+str(result_of_round["total_rounds"]),"white",window_x/96)
                times_characters_down = fontRender("友方角色被击倒："+str(result_of_round["times_characters_down"]),"white",window_x/96)
                player_rate = fontRender("评价：A","white",window_x/96)
                press_space = fontRender("按空格继续","white",window_x/96)
                whose_round = "result"
            
            if whose_round == "result":
                for event in pygame.event.get():
                    if event.type == KEYDOWN:
                        if event.key == K_SPACE:
                            battle = False
                            battleSystemMainLoop = False
                original_UI_img["score"].draw(screen)
                drawImg(total_kills,(250,300),screen)
                drawImg(total_time,(250,350),screen)
                drawImg(total_rounds_txt,(250,400),screen)
                drawImg(times_characters_down,(250,450),screen)
                drawImg(player_rate,(250,500),screen)
                drawImg(press_space,(250,700),screen)
            Display.flip()

    return result_of_round    
