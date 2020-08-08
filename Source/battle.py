# cython: language_level=3
from Source.skills import *
import Zero3 as Zero
import pygame
import yaml
import glob
import time
import random

def battle(chapter_name,screen,setting):
    """初始化基础数据"""
    #控制器输入组件
    InputController = Zero.GameController(setting["MouseIconWidth"],setting["MouseMoveSpeed"])
    #获取屏幕的尺寸
    window_x,window_y = screen.get_size()
    #卸载音乐
    pygame.mixer.music.unload()
    #帧率控制器
    Display = Zero.DisplayController(setting['FPS'])
    #加载按钮的文字
    with open("Lang/"+setting['Language']+".yaml", "r", encoding='utf-8') as f:
        loadData = yaml.load(f.read(),Loader=yaml.FullLoader)
        selectMenuUI = Zero.SelectMenu(loadData["SelectMenu"])
        battleUiTxt = loadData["Battle_UI"]
        warnings_to_display = Zero.WarningSystem(loadData["Warnings"])
        loading_info = loadData["LoadingTxt"]
        resultTxt = loadData["ResultBoard"]
    #加载剧情
    with open("Data/main_chapter/"+chapter_name+"_dialogs_"+setting['Language']+".yaml", "r", encoding='utf-8') as f:
        loadData = yaml.load(f.read(),Loader=yaml.FullLoader)
        chapter_title = loadData["title"]
        battle_info = loadData["battle_info"]
        dialog_during_battle = loadData["dialog_during_battle"]
        chapterDesc = loadData["description"]
    #章节标题显示
    infoToDisplayDuringLoading = Zero.LoadingTitle(window_x,window_y,battleUiTxt["numChapter"],chapter_name,chapter_title,chapterDesc)

    #渐入效果
    for i in range(1,255,2):
        infoToDisplayDuringLoading.display(screen,i)
        Display.flip()

    #开始加载地图场景
    infoToDisplayDuringLoading.display(screen)
    now_loading = Zero.fontRender(loading_info["now_loading_map"], "white",window_x/76)
    Zero.drawImg(now_loading,(window_x*0.75,window_y*0.9),screen)
    Display.flip()

    #读取并初始化章节信息
    with open("Data/main_chapter/"+chapter_name+"_map.yaml", "r", encoding='utf-8') as f:
        loadData = yaml.load(f.read(),Loader=yaml.FullLoader)
        zoomIn = loadData["zoomIn"]*100
        #初始化角色信息
        characterDataThread = Zero.initializeCharacterDataThread(loadData["character"],loadData["sangvisFerri"],setting)
        bg_music = loadData["background_music"]
        theWeather = loadData["weather"]
        dialogInfo = loadData["dialogs"]

    if zoomIn < 200:
        zoomIn = 200
    elif zoomIn > 400:
        zoomIn = 400
    zoomIntoBe = zoomIn
    perBlockHeight = round(window_y/10)

    #加载角色信息
    characterDataThread.start()
    while characterDataThread.isAlive():
        infoToDisplayDuringLoading.display(screen)
        now_loading = Zero.fontRender(loading_info["now_loading_characters"]+"({}/{})".format(characterDataThread.currentID,characterDataThread.totalNum), "white",window_x/76)
        Zero.drawImg(now_loading,(window_x*0.75,window_y*0.9),screen)
        Display.flip()
    characters_data,sangvisFerris_data = characterDataThread.getResult()

    #初始化地图模块
    theMap = Zero.MapObject(loadData,round(window_x/10),loadData["local_x"],loadData["local_y"])

    #计算光亮区域 并初始化地图
    theMap.calculate_darkness(characters_data,window_x,window_y)
    
    #开始加载关卡设定
    infoToDisplayDuringLoading.display(screen)
    now_loading = Zero.fontRender(loading_info["now_loading_level"], "white",window_x/76)
    Zero.drawImg(now_loading,(window_x*0.75,window_y*0.9),screen)
    Display.flip()

    #加载UI:
    #加载结束回合的图片
    end_round_button = Zero.loadImage("Assets/image/UI/endRound.png",(window_x*0.8,window_y*0.7),window_x/10, window_y/10)
    #加载子弹图片
    #bullet_img = Zero.loadImg("Assets/image/UI/bullet.png", perBlockWidth/6, perBlockHeight/12)
    bullets_list = []
    #加载血条,各色方块等UI图片 size:perBlockWidth, perBlockHeight/5
    original_UI_img = {
        "hp_empty" : Zero.loadImg("Assets/image/UI/hp_empty.png"),
        "hp_red" : Zero.loadImg("Assets/image/UI/hp_red.png"),
        "hp_green" : Zero.loadImg("Assets/image/UI/hp_green.png"),
        "action_point_blue" : Zero.loadImg("Assets/image/UI/action_point.png"),
        "bullets_number_brown" : Zero.loadImg("Assets/image/UI/bullets_number.png"),
        "green" : Zero.loadImg("Assets/image/UI/green.png",None,None,150),
        "red" : Zero.loadImg("Assets/image/UI/red.png",None,None,150),
        "yellow": Zero.loadImg("Assets/image/UI/yellow.png",None,None,150),
        "blue": Zero.loadImg("Assets/image/UI/blue.png",None,None,150),
        "orange": Zero.loadImg("Assets/image/UI/orange.png",None,None,150),
        "eye_orange": Zero.loadImg("Assets/image/UI/eye_orange.png"),
        "eye_red": Zero.loadImg("Assets/image/UI/eye_red.png"),
        "supplyBoard":Zero.loadImage("Assets/image/UI/score.png",((window_x-window_x/3)/2,-window_y/12),window_x/3,window_y/12),
    }
    #UI - 变形后
    UI_img = {
        "green" : Zero.resizeImg(original_UI_img["green"], (theMap.perBlockWidth*0.8, None)),
        "red" : Zero.resizeImg(original_UI_img["red"], (theMap.perBlockWidth*0.8, None)),
        "yellow" : Zero.resizeImg(original_UI_img["yellow"], (theMap.perBlockWidth*0.8, None)),
        "blue" : Zero.resizeImg(original_UI_img["blue"], (theMap.perBlockWidth*0.8, None)),
        "orange": Zero.resizeImg(original_UI_img["orange"], (theMap.perBlockWidth*0.8, None))
    }
    #角色信息UI管理
    characterInfoBoardUI = Zero.CharacterInfoBoard(window_x,window_y)
    #加载对话框图片
    dialoguebox_up = Zero.loadImage("Assets/image/UI/dialoguebox.png",(window_x,window_y/2-window_y*0.35),window_x*0.3,window_y*0.15)
    dialoguebox_down = Zero.loadImage(pygame.transform.flip(dialoguebox_up.img,True,False),(-window_x*0.3,window_y/2+window_y*0.2),window_x*0.3,window_y*0.15)
    #-----加载音效-----
    #行走的音效 -- 频道0
    all_walking_sounds = glob.glob(r'Assets/sound/snow/*.wav')
    walking_sound = []
    for i in range(len(all_walking_sounds)):
        walking_sound.append(pygame.mixer.Sound(all_walking_sounds[i]))
        walking_sound[-1].set_volume(setting["Sound"]["sound_effects"]/100.0)
    the_sound_id = None
    #加载天气和环境的音效 -- 频道1
    environment_sound = None
    weatherController = None
    if theWeather != None:
        environment_sound = pygame.mixer.Sound("Assets/sound/environment/"+theWeather+".ogg")
        environment_sound.set_volume(setting["Sound"]["sound_environment"]/100.0)
        weatherController = Zero.WeatherSystem(theWeather,window_x,window_y)    
    #攻击的音效 -- 频道2
    attackingSounds = Zero.AttackingSoundManager(2,setting["Sound"]["sound_effects"])
    #部分设定初始化
    the_character_get_click = ""
    enemies_get_attack = {}
    enemies_in_control = ""
    action_choice =""
    green_hide = True
    battle=False
    isWaiting = True
    whose_round = "sangvisFerrisToPlayer"
    mouse_move_temp_x = -1
    mouse_move_temp_y = -1
    damage_do_to_character = {}
    the_dead_one = {}
    screen_to_move_x=None
    screen_to_move_y=None
    pressKeyToMove={"up":False,"down":False,"left":False,"right":False}
    rightClickCharacterAlpha = None
    battleSystemMainLoop = True
    txt_alpha = None
    skill_target = None
    stayingTime = 0
    buttonGetHover = None
    theFriendGetHelp = None
    areaDrawColorBlock = {"green":[],"red":[],"yellow":[],"blue":[],"orange":[]}
    RoundSwitchUI = Zero.RoundSwitch(window_x,window_y,battleUiTxt)
    enemies_in_control_id = None
    sangvisFerris_name_list = None
    dialog_valuable_initialized = False
    # 移动路径
    the_route = []
    #上个回合因为暴露被敌人发现的角色
    #格式：角色：[x,y]
    the_characters_detected_last_round = {}
    enemy_action = None
    resultInfo = {
        "total_rounds" : 1,
        "total_kills" : 0,
        "total_time" : time.time(),
        "times_characters_down" : 0
    }

    #关卡背景介绍信息文字
    for i in range(len(battle_info)):
        battle_info[i] = Zero.fontRender(battle_info[i],"white",window_x/76)

    #显示章节信息
    for a in range(0,250,2):
        infoToDisplayDuringLoading.display(screen)
        for i in range(len(battle_info)):
            battle_info[i].set_alpha(a)
            Zero.drawImg(battle_info[i],(window_x/20,window_y*0.75+battle_info[i].get_height()*1.2*i),screen)
            if i == 1:
                temp_secode = Zero.fontRender(time.strftime(":%S", time.localtime()),"white",window_x/76)
                temp_secode.set_alpha(a)
                Zero.drawImg(temp_secode,(window_x/20+battle_info[i].get_width(),window_y*0.75+battle_info[i].get_height()*1.2),screen)
        Display.flip()

    if dialogInfo["initial"] == None:
        dialog_to_display = None
    else:
        dialog_to_display = dialog_during_battle[dialogInfo["initial"]]

    #战斗系统主要loop
    while battleSystemMainLoop == True:
        #加载地图
        theMap.display_map(screen)
        #环境声音-频道1
        if pygame.mixer.Channel(1).get_busy() == False and environment_sound != None:
            pygame.mixer.Channel(1).play(environment_sound)
        if battle == False:
            #如果战斗有对话
            if dialog_to_display != None:
                #设定初始化
                if dialog_valuable_initialized == False:
                    dialog_valuable_initialized = True
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
                if display_num < len(dialog_to_display):
                    #角色动画
                    for key,value in Zero.dicMerge(sangvisFerris_data,characters_data).items():
                        if value.faction == "character" or (value.x,value.y) in theMap.lightArea or theMap.darkMode != True:
                            if all_characters_path != None and key in all_characters_path:
                                value.draw("move",screen,theMap)
                            elif theAction != None and key in theAction:
                                pass
                            elif key in actionLoop:
                                if actionLoop[key] != "die":
                                    value.draw(actionLoop[key],screen,theMap,False)
                                else:
                                    value.draw(actionLoop[key],screen,theMap)
                            else:
                                value.draw("wait",screen,theMap)
                    #展示设施
                    theMap.display_facility(screen,characters_data,sangvisFerris_data)
                    #加载雪花
                    if weatherController != None:
                        weatherController.display(screen,theMap.perBlockWidth,perBlockHeight)
                    #如果操作是移动
                    if "move" in dialog_to_display[display_num]:
                        if all_characters_path == None:
                            all_characters_path = {}
                            for key,value in Zero.dicMerge(sangvisFerris_data,characters_data).items():
                                if key in dialog_to_display[display_num]["move"]:
                                    #创建AStar对象,并设置起点和终点为
                                    start_x = value.x
                                    start_y = value.y
                                    end_x = dialog_to_display[display_num]["move"][key]["x"]
                                    end_y = dialog_to_display[display_num]["move"][key]["y"]
                                    the_route = theMap.findPath((start_x,start_y),(end_x,end_y),characters_data,sangvisFerris_data,None,dialog_to_display[display_num]["move"])
                                    if len(the_route)>0:
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
                            if theMap.darkMode == True and reProcessMap == True:
                                theMap.calculate_darkness(characters_data,window_x,window_y)
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
                                    if key in characters_data and characters_data[key].draw(action,screen,theMap,False) == False:
                                        if action != "die":
                                            characters_data[key].reset_imgId(action)
                                        theActionNeedPop.append(key)
                                    elif key in sangvisFerris_data and sangvisFerris_data[key].draw(action,screen,theMap,False) == False:
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
                                    raise Exception("Error: Cannot find ",character_key," while the system is trying to reset the action.")
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
                                Zero.drawImg(Zero.fontRender(dialog_to_display[display_num]["dialoguebox_up"]["speaker"],"white",window_x/80),(dialoguebox_up.width/7,dialoguebox_up.height/11),screen,dialoguebox_up.x,dialoguebox_up.y)
                            #正在播放的行
                            content = Zero.fontRender(dialog_to_display[display_num]["dialoguebox_up"]["content"][dialog_up_displayed_line][:dialog_up_content_id],"white",window_x/80)
                            Zero.drawImg(content,(window_x/45,window_x/35+dialog_up_displayed_line*window_x/80),screen,dialoguebox_up.x,dialoguebox_up.y)
                            if dialog_up_content_id < len(dialog_to_display[display_num]["dialoguebox_up"]["content"][dialog_up_displayed_line]):
                                dialog_up_content_id+=1
                            elif dialog_up_displayed_line < len(dialog_to_display[display_num]["dialoguebox_up"]["content"])-1:
                                dialog_up_displayed_line += 1
                                dialog_up_content_id = 0
                            for i in range(dialog_up_displayed_line):
                                content = Zero.fontRender(dialog_to_display[display_num]["dialoguebox_up"]["content"][i],"white",window_x/80)
                                Zero.drawImg(content,(window_x/45,window_x/35+i*window_x/80),screen,dialoguebox_up.x,dialoguebox_up.y)
                            #角色图标
                            if dialog_to_display[display_num]["dialoguebox_up"]["speaker_icon"] != None:
                                Zero.drawImg(characterInfoBoardUI.characterIconImages[dialog_to_display[display_num]["dialoguebox_up"]["speaker_icon"]],(window_x*0.24,window_x/40),screen,dialoguebox_up.x,dialoguebox_up.y)
                        #下方对话框
                        if dialog_to_display[display_num]["dialoguebox_down"] != None:
                            #对话框图片
                            dialoguebox_down.draw(screen)
                            #名字
                            if dialog_to_display[display_num]["dialoguebox_down"]["speaker"] != None:
                                Zero.drawImg(Zero.fontRender(dialog_to_display[display_num]["dialoguebox_down"]["speaker"],"white",window_x/80),(dialoguebox_down.width*0.75,dialoguebox_down.height/10),screen,dialoguebox_down.x,dialoguebox_down.y)
                            #正在播放的行
                            content = Zero.fontRender(dialog_to_display[display_num]["dialoguebox_down"]["content"][dialog_down_displayed_line][:dialog_down_content_id],"white",window_x/80)
                            Zero.drawImg(content,(window_x/15,window_x/35+dialog_down_displayed_line*window_x/80),screen,dialoguebox_down.x,dialoguebox_down.y)
                            if dialog_down_content_id < len(dialog_to_display[display_num]["dialoguebox_down"]["content"][dialog_down_displayed_line]):
                                dialog_down_content_id+=1
                            elif dialog_down_displayed_line < len(dialog_to_display[display_num]["dialoguebox_down"]["content"])-1:
                                dialog_down_displayed_line += 1
                                dialog_down_content_id = 0
                            for i in range(dialog_down_displayed_line):
                                content = Zero.fontRender(dialog_to_display[display_num]["dialoguebox_down"]["content"][i],"white",window_x/80)
                                Zero.drawImg(content,(window_x/15,window_x/35+i*window_x/80),screen,dialoguebox_down.x,dialoguebox_down.y)
                            #角色图标
                            if dialog_to_display[display_num]["dialoguebox_down"]["speaker_icon"] != None:
                                Zero.drawImg(characterInfoBoardUI.characterIconImages[dialog_to_display[display_num]["dialoguebox_down"]["speaker_icon"]],(window_x*0.01,window_x/40),screen,dialoguebox_down.x,dialoguebox_down.y)
                    #闲置一定时间（秒）
                    elif "idle" in dialog_to_display[display_num]:
                        if seconde_to_idle == None:
                            seconde_to_idle = dialog_to_display[display_num]["idle"]*Display.fps
                        else:
                            if idle_seconde < seconde_to_idle:
                                idle_seconde += 1
                            else:
                                display_num += 1
                                idle_seconde = 0
                                seconde_to_idle = None
                    elif "changePos" in dialog_to_display[display_num]:
                        if screen_to_move_x == None and "x" in dialog_to_display[display_num]["changePos"]:
                            screen_to_move_x = dialog_to_display[display_num]["changePos"]["x"]
                        if screen_to_move_y == None and "y" in dialog_to_display[display_num]["changePos"]:
                            screen_to_move_y = dialog_to_display[display_num]["changePos"]["y"]
                        if screen_to_move_x != None and screen_to_move_x != 0:
                            temp_value = int(theMap.getPos_x() + screen_to_move_x*0.2)
                            if window_x-theMap.surface_width<=temp_value<=0:
                                theMap.setPos_x(temp_value)
                                screen_to_move_x*=0.8
                                if int(screen_to_move_x) == 0:
                                    screen_to_move_x = 0
                            else:
                                screen_to_move_x = 0
                        if screen_to_move_y != None and screen_to_move_y !=0:
                            temp_value = int(theMap.getPos_y() + screen_to_move_y*0.2)
                            if window_y-theMap.surface_height<=temp_value<=0:
                                theMap.setPos_y(temp_value)
                                screen_to_move_y*=0.8
                                if int(screen_to_move_y) == 0:
                                    screen_to_move_y = 0
                            else:
                                screen_to_move_y = 0
                        if screen_to_move_x == 0 and screen_to_move_y == 0 or screen_to_move_x == None and screen_to_move_y == None:
                            screen_to_move_x = None
                            screen_to_move_y = None
                            display_num += 1
                    #玩家输入按键判定
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                Display.quit()
                        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 or event.type == pygame.JOYBUTTONDOWN and InputController.joystick.get_button(0) == 1:
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
                else:
                    dialog_valuable_initialized = False
                    dialog_to_display = None
                    battle = True
            #如果战斗前无·对话
            elif dialog_to_display == None:
                #角色动画
                for every_chara in characters_data:
                    characters_data[every_chara].draw("wait",screen,theMap)
                for enemies in sangvisFerris_data:
                    if (sangvisFerris_data[enemies].x,sangvisFerris_data[enemies].y) in theMap.lightArea or theMap.darkMode != True:
                        sangvisFerris_data[enemies].draw("wait",screen,theMap)
                #展示设施
                theMap.display_facility(screen,characters_data,sangvisFerris_data)
                #角色动画
                for every_chara in characters_data:
                    characters_data[every_chara].drawUI(screen,original_UI_img,theMap)
                for enemies in sangvisFerris_data:
                    if (sangvisFerris_data[enemies].x,sangvisFerris_data[enemies].y) in theMap.lightArea or theMap.darkMode != True:
                        sangvisFerris_data[enemies].drawUI(screen,original_UI_img,theMap)
                #加载雪花
                if weatherController != None:
                    weatherController.display(screen,theMap.perBlockWidth,perBlockHeight)
                if txt_alpha == 0:
                    battle = True
        # 游戏主循环
        elif battle == True:
            right_click = False
            #获取鼠标坐标
            mouse_x,mouse_y=InputController.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE and isWaiting == True:
                        green_hide = True
                        the_character_get_click = ""
                        action_choice = ""
                        attacking_range = None
                        skill_range = None
                        areaDrawColorBlock = {"green":[],"red":[],"yellow":[],"blue":[],"orange":[]}
                    if event.key == pygame.K_w:
                        pressKeyToMove["up"]=True
                    if event.key == pygame.K_s:
                        pressKeyToMove["down"]=True
                    if event.key == pygame.K_a:
                        pressKeyToMove["left"]=True
                    if event.key == pygame.K_d:
                        pressKeyToMove["right"]=True
                    if event.key == pygame.K_m:
                        Display.quit()
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_w:
                        pressKeyToMove["up"]=False
                    if event.key == pygame.K_s:
                        pressKeyToMove["down"]=False
                    if event.key == pygame.K_a:
                        pressKeyToMove["left"]=False
                    if event.key == pygame.K_d:
                        pressKeyToMove["right"]=False
                #鼠标点击
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 or event.type == pygame.JOYBUTTONDOWN and InputController.joystick.get_button(0) == 1:
                    right_click = True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    #上下滚轮-放大和缩小地图
                    if event.button == 4 and zoomIntoBe < 400:
                        zoomIntoBe += 20
                    elif event.button == 5 and zoomIntoBe > 200:
                        zoomIntoBe -= 20
                if InputController.joystick.get_init() == True:
                    if round(InputController.joystick.get_axis(4)) == -1:
                        pressKeyToMove["up"]=True
                    else:
                        pressKeyToMove["up"]=False
                    if round(InputController.joystick.get_axis(4)) == 1:
                        pressKeyToMove["down"]=True
                    else:
                        pressKeyToMove["down"]=False
                    if round(InputController.joystick.get_axis(3)) == 1:
                        pressKeyToMove["right"]=True
                    else:
                        pressKeyToMove["right"]=False
                    if round(InputController.joystick.get_axis(3)) == -1:
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
                        if mouse_move_temp_x != mouse_x:
                            theMap.addPos_x(mouse_move_temp_x-mouse_x)
                        if mouse_move_temp_y != mouse_y:
                            theMap.addPos_y(mouse_move_temp_y-mouse_y)
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
                newPerBlockWidth = round(window_x/theMap.column*zoomIn/100)
                newPerBlockHeight = round(window_y/theMap.row*zoomIn/100)
                theMap.addPos_x((theMap.perBlockWidth-newPerBlockWidth)*theMap.column/2)
                theMap.addPos_y((perBlockHeight-newPerBlockHeight)*theMap.row/2)
                theMap.perBlockWidth = newPerBlockWidth
                perBlockHeight = newPerBlockHeight
                #根据perBlockWidth和perBlockHeight重新加载对应尺寸的UI
                UI_img["green"] = resizeImg(original_UI_img["green"], (theMap.perBlockWidth*0.8, None))
                UI_img["red"] = resizeImg(original_UI_img["red"], (theMap.perBlockWidth*0.8, None))
                UI_img["yellow"] = resizeImg(original_UI_img["yellow"], (theMap.perBlockWidth*0.8, None))
                UI_img["blue"] = resizeImg(original_UI_img["blue"], (theMap.perBlockWidth*0.8, None))
                UI_img["orange"] = resizeImg(original_UI_img["orange"], (theMap.perBlockWidth*0.8, None))
                theMap.changePerBlockSize(theMap.perBlockWidth,window_x,window_y)
                selectMenuUI.allButton = None
            else:
                zoomIn = zoomIntoBe

            #根据按键情况设定要移动的数值
            if pressKeyToMove["up"] == True:
                if screen_to_move_y == None:
                    screen_to_move_y = perBlockHeight/4
                else:
                    screen_to_move_y += perBlockHeight/4
            if pressKeyToMove["down"] == True:
                if screen_to_move_y == None:
                    screen_to_move_y = -perBlockHeight/4
                else:
                    screen_to_move_y -= perBlockHeight/4
            if pressKeyToMove["left"] == True:
                if screen_to_move_x == None:
                    screen_to_move_x = theMap.perBlockWidth/4
                else:
                    screen_to_move_x += theMap.perBlockWidth/4
            if pressKeyToMove["right"] == True:
                if screen_to_move_x == None:
                    screen_to_move_x = -theMap.perBlockWidth/4
                else:
                    screen_to_move_x -= theMap.perBlockWidth/4

            #如果需要移动屏幕
            if screen_to_move_x != None and screen_to_move_x != 0:
                temp_value = int(theMap.getPos_x() + screen_to_move_x*0.2)
                if window_x-theMap.surface_width<=temp_value<=0:
                    theMap.setPos_x(temp_value)
                    screen_to_move_x*=0.8
                    if int(screen_to_move_x) == 0:
                        screen_to_move_x = 0
                else:
                    screen_to_move_x = 0
            if screen_to_move_y != None and screen_to_move_y !=0:
                temp_value = int(theMap.getPos_y() + screen_to_move_y*0.2)
                if window_y-theMap.surface_height<=temp_value<=0:
                    theMap.setPos_y(temp_value)
                    screen_to_move_y*=0.8
                    if int(screen_to_move_y) == 0:
                        screen_to_move_y = 0
                else:
                    screen_to_move_y = 0

            #加载地图
            screen_to_move_x,screen_to_move_y = theMap.display_map(screen,screen_to_move_x,screen_to_move_y)
            #画出用彩色方块表示的范围
            for area in areaDrawColorBlock:
                for position in areaDrawColorBlock[area]:
                    xTemp,yTemp = theMap.calPosInMap(position[0],position[1])
                    Zero.drawImg(UI_img[area],(xTemp+theMap.perBlockWidth*0.1,yTemp),screen)
            #显示设施
            theMap.display_facility_ahead(screen)

            #玩家回合
            if whose_round == "player":
                if right_click == True:
                    block_get_click = theMap.calBlockInMap(UI_img["green"],mouse_x,mouse_y)
                    #如果点击了回合结束的按钮
                    if Zero.ifHover(end_round_button) and isWaiting == True:
                        whose_round = "playerToSangvisFerris"
                        the_character_get_click = ""
                        green_hide = True
                        attacking_range = None
                        skill_range = None
                        areaDrawColorBlock = {"green":[],"red":[],"yellow":[],"blue":[],"orange":[]}
                    #是否在显示移动范围后点击了且点击区域在移动范围内
                    elif len(the_route) != 0 and block_get_click != None and (block_get_click["x"], block_get_click["y"]) in the_route and green_hide==False:
                        isWaiting = False
                        green_hide = True
                        characters_data[the_character_get_click].current_action_point -= len(the_route)*2
                        areaDrawColorBlock = {"green":[],"red":[],"yellow":[],"blue":[],"orange":[]}
                    elif green_hide == "SelectMenu" and buttonGetHover == "attack":
                        if characters_data[the_character_get_click].current_bullets > 0 and characters_data[the_character_get_click].current_action_point >= 5:
                            action_choice = "attack"
                            green_hide = False
                        if characters_data[the_character_get_click].current_bullets <= 0:
                            warnings_to_display.add("magazine_is_empty")
                        if characters_data[the_character_get_click].current_action_point < 5:
                            warnings_to_display.add("no_enough_ap_to_attack")
                    elif green_hide == "SelectMenu" and buttonGetHover == "move":
                        if characters_data[the_character_get_click].current_action_point >= 2:
                            action_choice = "move"
                            green_hide = False
                        else:
                            warnings_to_display.add("no_enough_ap_to_move")
                    elif green_hide == "SelectMenu" and buttonGetHover == "skill":
                        if characters_data[the_character_get_click].current_action_point >= 8:
                            action_choice = "skill"
                            green_hide = False
                        else:
                            warnings_to_display.add("no_enough_ap_to_use_skill")
                    elif green_hide == "SelectMenu" and buttonGetHover == "reload":
                        if characters_data[the_character_get_click].current_action_point >= 5 and characters_data[the_character_get_click].bullets_carried > 0:
                            action_choice = "reload"
                            green_hide = False
                        elif characters_data[the_character_get_click].bullets_carried <= 0:
                            warnings_to_display.add("no_bullets_left")
                        elif characters_data[the_character_get_click].current_action_point < 5:
                            warnings_to_display.add("no_enough_ap_to_reload")
                    elif green_hide == "SelectMenu" and buttonGetHover == "rescue":
                        if characters_data[the_character_get_click].current_action_point >= 8:
                            action_choice = "rescue"
                            green_hide = False
                        else:
                            warnings_to_display.add("no_enough_ap_to_rescue")
                    #攻击判定
                    elif action_choice == "attack" and green_hide == False and the_character_get_click != "" and len(enemies_get_attack)>0:
                        characters_data[the_character_get_click].current_action_point -= 5
                        characters_data[the_character_get_click].noticed()
                        isWaiting = False
                        green_hide = True
                        attacking_range = None
                        areaDrawColorBlock = {"green":[],"red":[],"yellow":[],"blue":[],"orange":[]}
                    elif action_choice == "skill" and green_hide == False and the_character_get_click != "" and skill_target != None:
                        if skill_target in characters_data:
                            if characters_data[skill_target].x < characters_data[the_character_get_click].x:
                                characters_data[the_character_get_click].setFlip(True)
                            elif characters_data[skill_target].x == characters_data[the_character_get_click].x:
                                if characters_data[skill_target].y < characters_data[the_character_get_click].y:
                                    characters_data[the_character_get_click].setFlip(False)
                                else:
                                    characters_data[the_character_get_click].setFlip(True)
                            else:
                                characters_data[the_character_get_click].setFlip(False)
                        elif skill_target in sangvisFerris_data:
                            characters_data[the_character_get_click].noticed()
                            if sangvisFerris_data[skill_target].x < characters_data[the_character_get_click].x:
                                characters_data[the_character_get_click].setFlip(True)
                            elif sangvisFerris_data[skill_target].x == characters_data[the_character_get_click].x:
                                if sangvisFerris_data[skill_target].y < characters_data[the_character_get_click].y:
                                    characters_data[the_character_get_click].setFlip(False)
                                else:
                                    characters_data[the_character_get_click].setFlip(True)
                            else:
                                characters_data[the_character_get_click].setFlip(False)
                        characters_data[the_character_get_click].current_action_point -= 8
                        isWaiting = False
                        green_hide = True
                        skill_range = None
                        areaDrawColorBlock = {"green":[],"red":[],"yellow":[],"blue":[],"orange":[]}
                    elif action_choice == "rescue" and green_hide == False and the_character_get_click != "" and theFriendGetHelp != None:
                        characters_data[the_character_get_click].current_action_point -= 8
                        characters_data[the_character_get_click].noticed()
                        characters_data[theFriendGetHelp].heal(1)
                        the_character_get_click = ""
                        action_choice = ""
                        isWaiting = True
                        green_hide = True
                        attacking_range = None
                        areaDrawColorBlock = {"green":[],"red":[],"yellow":[],"blue":[],"orange":[]}
                    #判断是否有被点击的角色
                    elif block_get_click != None:
                        for key in characters_data:
                            if characters_data[key].x == block_get_click["x"] and characters_data[key].y == block_get_click["y"] and isWaiting == True and characters_data[key].dying == False and green_hide != False:
                                screen_to_move_x = None
                                screen_to_move_y = None
                                attacking_range = None
                                skill_range = None
                                areaDrawColorBlock = {"green":[],"red":[],"yellow":[],"blue":[],"orange":[]}
                                the_character_get_click = key
                                characterInfoBoardUI.update()
                                friendsCanSave = []
                                for key2 in characters_data:
                                    if characters_data[key2].dying != False:
                                        if characters_data[key2].x == characters_data[key].x:
                                            if characters_data[key2].y+1 == characters_data[key].y or characters_data[key2].y-1 == characters_data[key].y:
                                                friendsCanSave.append(key2)
                                        elif characters_data[key2].y == characters_data[key].y:
                                            if characters_data[key2].x+1 == characters_data[key].x or characters_data[key2].x-1 == characters_data[key].x:
                                                friendsCanSave.append(key2)
                                green_hide = "SelectMenu"
                                break
                        
                #选择菜单的判定，显示功能在角色动画之后
                if green_hide == "SelectMenu":
                    #移动画面以使得被点击的角色可以被更好的操作
                    if screen_to_move_x == None:
                        tempX,tempY = theMap.calPosInMap(characters_data[the_character_get_click].x,characters_data[the_character_get_click].y)
                        if tempX < window_x*0.2 and theMap.getPos_x()<=0:
                            screen_to_move_x = window_x*0.2-tempX
                        elif tempX > window_x*0.8 and theMap.getPos_x()>=theMap.column*theMap.perBlockWidth*-1:
                            screen_to_move_x = window_x*0.8-tempX
                    if screen_to_move_y == None:
                        if tempY < window_y*0.2 and theMap.getPos_y()<=0:
                            screen_to_move_y = window_y*0.2-tempY
                        elif tempY > window_y*0.8 and theMap.getPos_y()>=theMap.row*perBlockHeight*-1:
                            screen_to_move_y = window_y*0.8-tempY
                        
                #显示攻击/移动/技能范围
                if green_hide == False and the_character_get_click != "":
                    block_get_click = theMap.calBlockInMap(UI_img["green"],mouse_x,mouse_y)
                    #显示移动范围
                    if action_choice == "move":
                        areaDrawColorBlock["green"] = []
                        if block_get_click != None:
                            #创建AStar对象,并设置起点和终点为
                            start_x = characters_data[the_character_get_click].x
                            start_y = characters_data[the_character_get_click].y
                            end_x = block_get_click["x"]
                            end_y = block_get_click["y"]
                            max_blocks_can_move = int(characters_data[the_character_get_click].current_action_point/2)
                            if 0<abs(end_x-start_x)+abs(end_y-start_y)<=max_blocks_can_move:
                                the_route = theMap.findPath((start_x,start_y),(end_x,end_y),characters_data,sangvisFerris_data,max_blocks_can_move)
                                if len(the_route)>0:
                                    #显示路径
                                    areaDrawColorBlock["green"] = the_route
                                    xTemp,yTemp = theMap.calPosInMap(the_route[-1][0],the_route[-1][1])
                                    Zero.displayInCenter(Zero.fontRender("-"+str(len(the_route)*2)+"AP","green",theMap.perBlockWidth/8,True),UI_img["green"],xTemp,yTemp,screen)
                    #显示攻击范围        
                    elif action_choice == "attack":
                        if attacking_range == None:
                            attacking_range = characters_data[the_character_get_click].getAttackRange(theMap)
                        any_character_in_attack_range = False
                        for enemies in sangvisFerris_data:
                            if sangvisFerris_data[enemies].current_hp > 0:
                                if (sangvisFerris_data[enemies].x,sangvisFerris_data[enemies].y) in attacking_range["near"] or (sangvisFerris_data[enemies].x,sangvisFerris_data[enemies].y) in attacking_range["middle"] or (sangvisFerris_data[enemies].x,sangvisFerris_data[enemies].y) in attacking_range["far"]:
                                    any_character_in_attack_range = True
                                    break
                        if any_character_in_attack_range == True:
                            areaDrawColorBlock["green"] = attacking_range["near"]
                            areaDrawColorBlock["blue"] = attacking_range["middle"]
                            areaDrawColorBlock["yellow"] = attacking_range["far"]
                            if block_get_click != None:
                                the_attacking_range_area = []
                                for area in attacking_range:
                                    if (block_get_click["x"],block_get_click["y"]) in attacking_range[area]:
                                        for y in range(block_get_click["y"]-characters_data[the_character_get_click].attack_range+1,block_get_click["y"]+characters_data[the_character_get_click].attack_range):
                                            if y < block_get_click["y"]:
                                                for x in range(block_get_click["x"]-characters_data[the_character_get_click].attack_range-(y-block_get_click["y"])+1,block_get_click["x"]+characters_data[the_character_get_click].attack_range+(y-block_get_click["y"])):
                                                    if theMap.mapData[y][x].canPassThrough == True:
                                                        the_attacking_range_area.append([x,y])
                                            else:
                                                for x in range(block_get_click["x"]-characters_data[the_character_get_click].attack_range+(y-block_get_click["y"])+1,block_get_click["x"]+characters_data[the_character_get_click].attack_range-(y-block_get_click["y"])):
                                                    if theMap.mapData[y][x].canPassThrough == True:
                                                        the_attacking_range_area.append([x,y])
                                        break
                                enemies_get_attack = {}
                                if len(the_attacking_range_area) > 0:
                                    areaDrawColorBlock["orange"] = the_attacking_range_area
                                    for enemies in sangvisFerris_data:
                                        if [sangvisFerris_data[enemies].x,sangvisFerris_data[enemies].y] in the_attacking_range_area and sangvisFerris_data[enemies].current_hp>0:
                                            if (sangvisFerris_data[enemies].x,sangvisFerris_data[enemies].y) in attacking_range["far"]:
                                                enemies_get_attack[enemies] = "far"
                                            elif (sangvisFerris_data[enemies].x,sangvisFerris_data[enemies].y) in attacking_range["middle"]:
                                                enemies_get_attack[enemies] = "middle"
                                            elif (sangvisFerris_data[enemies].x,sangvisFerris_data[enemies].y) in attacking_range["near"]:
                                                enemies_get_attack[enemies] = "near"
                        else:
                            warnings_to_display.add("no_enemy_in_effective_range")
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
                            areaDrawColorBlock["green"] = skill_range["near"]
                            areaDrawColorBlock["blue"] = skill_range["middle"]
                            areaDrawColorBlock["yellow"] = skill_range["far"]
                            block_get_click = theMap.calBlockInMap(UI_img["green"],mouse_x,mouse_y)
                            if block_get_click != None:
                                the_skill_cover_area = []
                                for area in skill_range:
                                    if [block_get_click["x"],block_get_click["y"]] in skill_range[area]:
                                        for y in range(block_get_click["y"]-characters_data[the_character_get_click].skill_cover_range,block_get_click["y"]+characters_data[the_character_get_click].skill_cover_range):
                                            if y < block_get_click["y"]:
                                                for x in range(block_get_click["x"]-characters_data[the_character_get_click].skill_cover_range-(y-block_get_click["y"])+1,block_get_click["x"]+characters_data[the_character_get_click].skill_cover_range+(y-block_get_click["y"])):
                                                    if theMap.mapData[y][x].canPassThrough == True:
                                                        the_skill_cover_area.append([x,y])
                                            else:
                                                for x in range(block_get_click["x"]-characters_data[the_character_get_click].skill_cover_range+(y-block_get_click["y"])+1,block_get_click["x"]+characters_data[the_character_get_click].skill_cover_range-(y-block_get_click["y"])):
                                                    if theMap.mapData[y][x].canPassThrough == True:
                                                        the_skill_cover_area.append([x,y])
                                        areaDrawColorBlock["orange"] = the_skill_cover_area
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
                                isWaiting = True
                                the_character_get_click = ""
                                action_choice = ""
                                green_hide = True
                        #无需换弹
                        elif bullets_to_add <= 0:
                            warnings_to_display.add("magazine_is_full")
                            green_hide = "SelectMenu"
                        else:
                            print(the_character_get_click+" is causing trouble, please double check the files or reporting this issue")
                            break
                    elif action_choice == "rescue":
                        areaDrawColorBlock["green"] = []
                        areaDrawColorBlock["orange"] = []
                        theFriendGetHelp = None
                        for friendNeedHelp in friendsCanSave:
                            if block_get_click != None and block_get_click["x"] == characters_data[friendNeedHelp].x and block_get_click["y"] == characters_data[friendNeedHelp].y:
                                areaDrawColorBlock["orange"] = [(block_get_click["x"],block_get_click["y"])]
                                theFriendGetHelp = friendNeedHelp
                            else:
                                areaDrawColorBlock["green"].append((characters_data[friendNeedHelp].x,characters_data[friendNeedHelp].y))

                #当有角色被点击时
                if the_character_get_click != "" and isWaiting == False:
                    #被点击的角色动画
                    green_hide=True
                    if action_choice == "move":
                        theCharacterMoved = False
                        if the_route != []:
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
                                for key,value in sangvisFerris_data.items():
                                    enemyAttackRange = value.getAttackRange(theMap)
                                    if (characters_data[the_character_get_click].x,characters_data[the_character_get_click].y) in enemyAttackRange["near"] or (characters_data[the_character_get_click].x,characters_data[the_character_get_click].y) in enemyAttackRange["middle"] or (characters_data[the_character_get_click].x,characters_data[the_character_get_click].y) in enemyAttackRange["far"]:
                                        characters_data[the_character_get_click].noticed()
                                        break
                                if theMap.darkMode == True:
                                    theMap.calculate_darkness(characters_data,window_x,window_y)
                            characters_data[the_character_get_click].draw("move",screen,theMap)
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
                                            original_UI_img["supplyBoard"].items.append(Zero.fontRender(battleUiTxt["getBullets"]+": "+str(value2),"white",window_x/80))
                                        elif key2 == "hp":
                                            characters_data[the_character_get_click].current_hp += value2
                                            original_UI_img["supplyBoard"].items.append(Zero.fontRender(battleUiTxt["getHealth"]+": "+str(value2),"white",window_x/80))
                                    if len(original_UI_img["supplyBoard"].items)>0:
                                        original_UI_img["supplyBoard"].yTogo = 10
                                    chest_need_to_remove = key
                                    break
                            if chest_need_to_remove != None:
                                del theMap.facilityData["chest"][chest_need_to_remove]
                            keyTemp = str(characters_data[the_character_get_click].x)+"-"+str(characters_data[the_character_get_click].y) 
                            #检测是否角色有set的动画
                            if characters_data[the_character_get_click].gif_dic["set"] != None:
                                characters_data[the_character_get_click].draw("set",screen,theMap,False)
                                if characters_data[the_character_get_click].gif_dic["set"]["imgId"] == characters_data[the_character_get_click].gif_dic["set"]["imgNum"]-1:
                                    characters_data[the_character_get_click].gif_dic["set"]["imgId"]=0
                                    isWaiting = True
                                    the_character_get_click = ""
                                    action_choice = ""
                                    if "move" in dialogInfo and keyTemp in dialogInfo["move"]:
                                        dialog_to_display = dialog_during_battle[dialogInfo["move"][keyTemp]]
                                        battle = False
                            else:
                                isWaiting = True
                                the_character_get_click = ""
                                action_choice = ""
                                if "move" in dialogInfo and keyTemp in dialogInfo["move"]:
                                    dialog_to_display = dialog_during_battle[dialogInfo["move"][keyTemp]]
                                    battle = False
                    elif action_choice == "attack":
                        if characters_data[the_character_get_click].gif_dic["attack"]["imgId"] == 3:
                            attackingSounds.play(characters_data[the_character_get_click].kind)
                        if characters_data[the_character_get_click].gif_dic["attack"]["imgId"] == 0:
                            block_get_click = theMap.calBlockInMap(UI_img["green"],mouse_x,mouse_y)
                            if block_get_click != None:
                                if block_get_click["x"] < characters_data[the_character_get_click].x:
                                    characters_data[the_character_get_click].setFlip(True)
                                elif block_get_click["x"] == characters_data[the_character_get_click].x:
                                    if block_get_click["y"] < characters_data[the_character_get_click].y:
                                        characters_data[the_character_get_click].setFlip(False)
                                    else:
                                        characters_data[the_character_get_click].setFlip(True)
                                else:
                                    characters_data[the_character_get_click].setFlip(False)
                        characters_data[the_character_get_click].draw("attack",screen,theMap,False)
                        if characters_data[the_character_get_click].gif_dic["attack"]["imgId"] == characters_data[the_character_get_click].gif_dic["attack"]["imgNum"]-2:
                            for each_enemy in enemies_get_attack:
                                if enemies_get_attack[each_enemy] == "near" and random.randint(1,100) <= 95 or enemies_get_attack[each_enemy] == "middle" and random.randint(1,100) <= 80 or enemies_get_attack[each_enemy] == "far" and random.randint(1,100) <= 65:
                                    the_damage = random.randint(characters_data[the_character_get_click].min_damage,characters_data[the_character_get_click].max_damage)
                                    sangvisFerris_data[each_enemy].decreaseHp(the_damage)
                                    damage_do_to_character[each_enemy] = Zero.fontRender("-"+str(the_damage),"red",window_x/76)
                                else:
                                    damage_do_to_character[each_enemy] = Zero.fontRender("Miss","red",window_x/76)
                        if characters_data[the_character_get_click].gif_dic["attack"]["imgId"] == characters_data[the_character_get_click].gif_dic["attack"]["imgNum"]-1:
                            characters_data[the_character_get_click].gif_dic["attack"]["imgId"] = 0
                            characters_data[the_character_get_click].current_bullets -= 1
                            isWaiting = True
                            the_character_get_click = ""
                            action_choice = ""
                    elif action_choice == "skill":
                        characters_data[the_character_get_click].draw("skill",screen,theMap,False)
                        if characters_data[the_character_get_click].gif_dic["skill"]["imgId"] == characters_data[the_character_get_click].gif_dic["skill"]["imgNum"]-2:
                            temp_dic = skill(the_character_get_click,None,None,sangvisFerris_data,characters_data,"react",skill_target,damage_do_to_character)
                            characters_data = temp_dic["characters_data"]
                            sangvisFerris_data = temp_dic["sangvisFerris_data"]
                            damage_do_to_character = temp_dic["damage_do_to_character"]
                            del temp_dic
                        if characters_data[the_character_get_click].gif_dic["skill"]["imgId"] == characters_data[the_character_get_click].gif_dic["skill"]["imgNum"]-1:
                            characters_data[the_character_get_click].gif_dic["skill"]["imgId"] = 0
                            theMap.calculate_darkness(characters_data,window_x,window_y)
                            isWaiting =True
                            the_character_get_click = ""
                            action_choice = ""
                    elif action_choice == "reload":
                        characters_data[the_character_get_click].draw("reload",screen,theMap,False)
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
                    characters_data[the_character_get_click].draw("wait",screen,theMap)

            
            #↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑中间检测区↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑#
            #敌方回合
            if whose_round == "sangvisFerris":
                enemies_in_control = sangvisFerris_name_list[enemies_in_control_id]
                if enemy_action == None:
                    enemy_action = Zero.AI(enemies_in_control,theMap,characters_data,sangvisFerris_data,the_characters_detected_last_round)
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
                        if (int(sangvisFerris_data[enemies_in_control].x),int(sangvisFerris_data[enemies_in_control].y)) in theMap.lightArea or theMap.darkMode != True:
                            sangvisFerris_data[enemies_in_control].draw("move",screen,theMap)
                    else:
                        if pygame.mixer.Channel(0).get_busy() == True:
                            pygame.mixer.Channel(0).stop()
                        enemies_in_control_id +=1
                        if enemies_in_control_id >= len(sangvisFerris_name_list):
                            whose_round = "sangvisFerrisToPlayer"
                            resultInfo["total_rounds"] += 1
                        enemy_action = None
                        enemies_in_control = ""
                elif enemy_action["action"] == "attack":
                    if sangvisFerris_data[enemies_in_control].gif_dic["attack"]["imgId"] == 3:
                        attackingSounds.play(sangvisFerris_data[enemies_in_control].kind)
                    if (sangvisFerris_data[enemies_in_control].x,sangvisFerris_data[enemies_in_control].y) in theMap.lightArea or theMap.darkMode != True:
                        if characters_data[enemy_action["target"]].x > sangvisFerris_data[enemies_in_control].x:
                            sangvisFerris_data[enemies_in_control].setFlip(True)
                        elif characters_data[enemy_action["target"]].x == sangvisFerris_data[enemies_in_control].x:
                            if characters_data[enemy_action["target"]].y > sangvisFerris_data[enemies_in_control].y:
                                sangvisFerris_data[enemies_in_control].setFlip(False)
                            else:
                                sangvisFerris_data[enemies_in_control].setFlip(True)
                        else:
                            sangvisFerris_data[enemies_in_control].setFlip(False)
                        sangvisFerris_data[enemies_in_control].draw("attack",screen,theMap,False)
                    else:
                        sangvisFerris_data[enemies_in_control].gif_dic["attack"]["imgId"] += 1
                    if sangvisFerris_data[enemies_in_control].gif_dic["attack"]["imgId"] == sangvisFerris_data[enemies_in_control].gif_dic["attack"]["imgNum"]-1:
                        temp_value = random.randint(0,100)
                        if enemy_action["target_area"] == "near" and temp_value <= 95 or enemy_action["target_area"] == "middle" and temp_value <= 80 or enemy_action["target_area"] == "far" and temp_value <= 65:
                            the_damage = random.randint(sangvisFerris_data[enemies_in_control].min_damage,sangvisFerris_data[enemies_in_control].max_damage)
                            resultInfo = characters_data[enemy_action["target"]].decreaseHp(the_damage,resultInfo)
                            theMap.calculate_darkness(characters_data,window_x,window_y)
                            damage_do_to_character[enemy_action["target"]] = Zero.fontRender("-"+str(the_damage),"red",window_x/76)
                        else:
                            damage_do_to_character[enemy_action["target"]] = Zero.fontRender("Miss","red",window_x/76)
                        sangvisFerris_data[enemies_in_control].gif_dic["attack"]["imgId"] = 0
                        enemies_in_control_id +=1
                        if enemies_in_control_id >= len(sangvisFerris_name_list):
                            whose_round = "sangvisFerrisToPlayer"
                            resultInfo["total_rounds"] += 1
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
                        if (int(sangvisFerris_data[enemies_in_control].x),int(sangvisFerris_data[enemies_in_control].y)) in theMap.lightArea or theMap.darkMode != True:
                            sangvisFerris_data[enemies_in_control].draw("move",screen,theMap)
                    else:
                        if pygame.mixer.Channel(0).get_busy() == True:
                            pygame.mixer.Channel(0).stop()
                        if sangvisFerris_data[enemies_in_control].gif_dic["attack"]["imgId"] == 3:
                            attackingSounds.play(sangvisFerris_data[enemies_in_control].kind)
                        if (sangvisFerris_data[enemies_in_control].x,sangvisFerris_data[enemies_in_control].y) in theMap.lightArea or theMap.darkMode != True:
                            if characters_data[enemy_action["target"]].x > sangvisFerris_data[enemies_in_control].x:
                                sangvisFerris_data[enemies_in_control].setFlip(True)
                            elif characters_data[enemy_action["target"]].x == sangvisFerris_data[enemies_in_control].x:
                                if characters_data[enemy_action["target"]].y > sangvisFerris_data[enemies_in_control].y:
                                    sangvisFerris_data[enemies_in_control].setFlip(False)
                                else:
                                    sangvisFerris_data[enemies_in_control].setFlip(True)
                            else:
                                sangvisFerris_data[enemies_in_control].setFlip(False)
                            sangvisFerris_data[enemies_in_control].draw("attack",screen,theMap,False)
                        else:
                            sangvisFerris_data[enemies_in_control].gif_dic["attack"]["imgId"] += 1
                        if sangvisFerris_data[enemies_in_control].gif_dic["attack"]["imgId"] == sangvisFerris_data[enemies_in_control].gif_dic["attack"]["imgNum"]-1:
                            temp_value = random.randint(0,100)
                            if enemy_action["target_area"] == "near" and temp_value <= 95 or enemy_action["target_area"] == "middle" and temp_value <= 80 or enemy_action["target_area"] == "far" and temp_value <= 65:
                                the_damage = random.randint(sangvisFerris_data[enemies_in_control].min_damage,sangvisFerris_data[enemies_in_control].max_damage)
                                resultInfo = characters_data[enemy_action["target"]].decreaseHp(the_damage,resultInfo)
                                theMap.calculate_darkness(characters_data,window_x,window_y)
                                damage_do_to_character[enemy_action["target"]] = Zero.fontRender("-"+str(the_damage),"red",window_x/76)
                            else:
                                damage_do_to_character[enemy_action["target"]] = Zero.fontRender("Miss","red",window_x/76)
                            sangvisFerris_data[enemies_in_control].gif_dic["attack"]["imgId"] = 0
                            enemies_in_control_id +=1
                            if enemies_in_control_id >= len(sangvisFerris_name_list):
                                whose_round = "sangvisFerrisToPlayer"
                                resultInfo["total_rounds"] += 1
                            enemy_action = None
                            enemies_in_control = ""
                elif enemy_action["action"] == "stay":
                    enemies_in_control_id +=1
                    if enemies_in_control_id >= len(sangvisFerris_name_list):
                        whose_round = "sangvisFerrisToPlayer"
                        resultInfo["total_rounds"] += 1
                    enemy_action = None
                    enemies_in_control = ""
                else:
                    print("warning: not choice")

            #↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓角色动画展示区↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓#
            rightClickCharacterAlphaDeduct = True
            for key,value in Zero.dicMerge(characters_data,sangvisFerris_data).items():
                #根据血量判断角色的动作
                if value.faction == "character" and key != the_character_get_click or value.faction == "sangvisFerri" and key != enemies_in_control and (value.x,value.y) in theMap.lightArea or value.faction == "sangvisFerri" and key != enemies_in_control and theMap.darkMode != True:
                    if value.current_hp > 0:
                        if value.faction == "character" and value.get_imgId("die") > 0:
                            value.draw("die",screen,theMap,False)
                            value.gif_dic["die"]["imgId"] -= 2
                            if value.get_imgId("die") <= 0:
                                value.set_imgId("die",0)
                        else:
                            if green_hide == True and pygame.mouse.get_pressed()[2]:
                                block_get_click = theMap.calBlockInMap(UI_img["green"],mouse_x,mouse_y)
                                if block_get_click != None and block_get_click["x"] == value.x and block_get_click["y"]  == value.y:
                                    rightClickCharacterAlphaDeduct = False
                                    if rightClickCharacterAlpha == None:
                                        rightClickCharacterAlpha = 0
                                    if rightClickCharacterAlpha < 150:
                                        rightClickCharacterAlpha += 10
                                        UI_img["yellow"].set_alpha(rightClickCharacterAlpha)
                                        UI_img["blue"].set_alpha(rightClickCharacterAlpha)
                                        UI_img["green"].set_alpha(rightClickCharacterAlpha)
                                    rangeCanAttack =  value.getAttackRange(theMap)
                                    areaDrawColorBlock["yellow"] = rangeCanAttack["far"]
                                    areaDrawColorBlock["blue"] =  rangeCanAttack["middle"]
                                    areaDrawColorBlock["green"] = rangeCanAttack["near"]
                            value.draw("wait",screen,theMap)
                    elif value.current_hp<=0:
                        value.draw("die",screen,theMap,False)

                #是否有在播放死亡角色的动画（而不是倒地状态）
                if value.current_hp<=0 and key not in the_dead_one:
                    if value.faction == "character" and value.kind == "HOC" or value.faction == "sangvisFerri":
                        the_dead_one[key] = value.faction
                #伤害/治理数值显示
                if key in damage_do_to_character:
                    the_alpha_to_check = damage_do_to_character[key].get_alpha()
                    if the_alpha_to_check > 0:
                        xTemp,yTemp = theMap.calPosInMap(value.x,value.y)
                        xTemp+=theMap.perBlockWidth*0.05
                        yTemp-=theMap.perBlockWidth*0.05
                        Zero.displayInCenter(damage_do_to_character[key],UI_img["green"],xTemp,yTemp,screen)
                        damage_do_to_character[key].set_alpha(the_alpha_to_check-5)
                    else:
                        del damage_do_to_character[key]
            
            if rightClickCharacterAlphaDeduct == True and rightClickCharacterAlpha != None:
                if rightClickCharacterAlpha>0:
                    rightClickCharacterAlpha-=10
                    UI_img["yellow"].set_alpha(rightClickCharacterAlpha)
                    UI_img["blue"].set_alpha(rightClickCharacterAlpha)
                    UI_img["green"].set_alpha(rightClickCharacterAlpha)
                elif rightClickCharacterAlpha == 0:
                    areaDrawColorBlock["yellow"] = []
                    areaDrawColorBlock["blue"] = []
                    areaDrawColorBlock["green"] = []
                    UI_img["yellow"].set_alpha(150)
                    UI_img["blue"].set_alpha(150)
                    UI_img["green"].set_alpha(150)
                    rightClickCharacterAlpha = None
                
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
                            resultInfo["total_kills"]+=1
                elif value == "character":
                    if characters_data[key].gif_dic["die"]["imgId"] == characters_data[key].gif_dic["die"]["imgNum"]-1:
                        the_alpha = characters_data[key].gif_dic["die"]["img"][-1].get_alpha()
                        if the_alpha > 0:
                            characters_data[key].gif_dic["die"]["img"][-1].set_alpha(the_alpha-5)
                        else:
                            the_dead_one_remove.append(key)
                            del characters_data[key]
                            resultInfo["times_characters_down"]+=1
                            theMap.calculate_darkness(characters_data,window_x,window_y)
            for key in the_dead_one_remove:
                del the_dead_one[key]
            #↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑角色动画展示区↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑#
            #展示设施
            theMap.display_facility(screen,characters_data,sangvisFerris_data)
            #展示所有角色Ui
            for every_chara in characters_data:
                characters_data[every_chara].drawUI(screen,original_UI_img,theMap)
            if theMap.darkMode == True:
                for enemies in sangvisFerris_data:
                    if (int(sangvisFerris_data[enemies].x),int(sangvisFerris_data[enemies].y)) in theMap.lightArea:
                        sangvisFerris_data[enemies].drawUI(screen,original_UI_img,theMap)
            else:
                for enemies in sangvisFerris_data:
                    sangvisFerris_data[enemies].drawUI(screen,original_UI_img,theMap)

            #显示选择菜单
            if green_hide == "SelectMenu":
                #左下角的角色信息
                characterInfoBoardUI.display(screen,characters_data[the_character_get_click],original_UI_img)
                #----选择菜单----
                buttonGetHover = selectMenuUI.display(screen,round(theMap.perBlockWidth/10),theMap.getBlockExactLocation(characters_data[the_character_get_click].x,characters_data[the_character_get_click].y),characters_data[the_character_get_click].kind,friendsCanSave)
            #加载雪花
            if weatherController != None:
                weatherController.display(screen,theMap.perBlockWidth,perBlockHeight)
            
            #↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓中间检测区↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓#
            if whose_round == "playerToSangvisFerris" or whose_round == "sangvisFerrisToPlayer":
                if RoundSwitchUI.display(screen,whose_round,resultInfo["total_rounds"]) == True:
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
                            if characters_data[key].detection == False:
                                characters_detect_this_round[key] = [characters_data[key].x,characters_data[key].y]
                        whose_round = "player"
            #检测所有敌人是否都已经被消灭
            if len(sangvisFerris_data) == 0 and whose_round != "result":
                the_character_get_click = ""
                green_hide = False
                whose_round = "result_win"

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
                    Zero.drawImg(original_UI_img["supplyBoard"].items[i],(start_point,(original_UI_img["supplyBoard"].height - original_UI_img["supplyBoard"].items[i].get_height())/2),screen,0,original_UI_img["supplyBoard"].y)
                    start_point += original_UI_img["supplyBoard"].items[i].get_width()*1.25

            if whose_round == "player":
                #加载结束回合的按钮
                end_round_button.draw(screen)

            #显示警告
            warnings_to_display.display(screen)

            #加载并播放音乐
            if pygame.mixer.music.get_busy() != 1:
                pygame.mixer.music.load("Assets/music/"+bg_music)
                pygame.mixer.music.play(loops=9999, start=0.0)
                pygame.mixer.music.set_volume(setting["Sound"]["background_music"]/100.0)

            #结束动画
            if whose_round == "result_win":
                resultInfo["total_time"] = time.localtime(time.time()-resultInfo["total_time"])
                ResultBoardUI = ResultBoard(resultTxt,resultInfo,window_x,window_y)

                whose_round = "result"
            
            if whose_round == "result":
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            battle = False
                            battleSystemMainLoop = False
                ResultBoardUI.display(screen)
    
        #渐变效果：一次性的
        if txt_alpha == None:
            txt_alpha = 250
        if txt_alpha > 0:
            infoToDisplayDuringLoading.black_bg.set_alpha(txt_alpha)
            infoToDisplayDuringLoading.display(screen,txt_alpha)
            for i in range(len(battle_info)):
                battle_info[i].set_alpha(txt_alpha)
                Zero.drawImg(battle_info[i],(window_x/20,window_y*0.75+battle_info[i].get_height()*1.2*i),screen)
                if i == 1:
                    temp_secode = Zero.fontRender(time.strftime(":%S", time.localtime()),"white",window_x/76)
                    temp_secode.set_alpha(txt_alpha)
                    Zero.drawImg(temp_secode,(window_x/20+battle_info[i].get_width(),window_y*0.75+battle_info[i].get_height()*1.2),screen)
            txt_alpha -= 5
        
        #刷新画面
        InputController.display(screen)
        Display.flip()
    
    #暂停声效 - 尤其是环境声
    pygame.mixer.stop()
    
    return resultInfo    
