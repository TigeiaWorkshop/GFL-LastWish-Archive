from Zero3.characterDataManager import *
from Zero3.map import *
from Zero3.battleUI import *
from Zero3.AI import *
from Zero3.skill import *

class BattleSystem:
    def __init__(self):
        #-----需要储存的参数-----#
        #被选中的角色
        self.characterGetClick = ""
        self.enemiesGetAttack = {}
        self.action_choice = ""
        #是否不要画出用于表示范围的方块
        self.NotDrawRangeBlocks = True
        self.areaDrawColorBlock = {"green":[],"red":[],"yellow":[],"blue":[],"orange":[]}
        #是否在战斗状态-战斗loop
        self.battle = False
        #是否在等待
        self.isWaiting = True
        #谁的回合
        self.whose_round = "sangvisFerrisToPlayer"
        #用于判断是否移动屏幕的参数
        self.mouse_move_temp_x = -1
        self.mouse_move_temp_y = -1
        self.screen_to_move_x = None
        self.screen_to_move_y = None
        #是否是死亡的那个
        self.the_dead_one = {}
        #用于检测是否有方向键被按到的字典
        self.pressKeyToMove = {"up":False,"down":False,"left":False,"right":False}
        self.rightClickCharacterAlpha = None
        #战斗系统主循环判定参数
        self.battleSystemMainLoop = True
        #技能对象
        self.skill_target = None
        #被按到的按键
        self.buttonGetHover = None
        #被救助的那个角色
        self.friendGetHelp = None
        #AI系统正在操控的地方角色ID
        self.enemy_in_control = None
        self.enemies_in_control_id = None
        #所有敌对角色的名字列表
        self.sangvisFerris_name_list = None
        #-----不需要储存的参数，每次加载都需初始化-----#
        #储存角色受到伤害的文字surface
        self.damage_do_to_characters = {}
        self.txt_alpha = None
        self.stayingTime = 0
        # 移动路径
        self.the_route = []
        #上个回合因为暴露被敌人发现的角色
        #格式：角色：[x,y]
        self.the_characters_detected_last_round = {}
        self.enemy_action = None
        self.resultInfo = {
            "total_rounds" : 1,
            "total_kills" : 0,
            "total_time" : time.time(),
            "times_characters_down" : 0
        }
        self.__pygame_events = None
        self.characters_data = None
        self.sangvisFerris_data = None
        self.theMap = None
        self.dialogData = None
        self.loadFromSave = False
    def __update_events(self):
        self.__pygame_events = pygame.event.get()
    def initialize(self,screen,chapterType,chapterName):
        #储存章节信息
        self.chapterType = chapterType
        self.chapterName = chapterName
        self.process_data(screen)
    def save_data(self):
        if pause_menu.ifSave == True:
            pause_menu.ifSave = False
            DataTmp = {}
            DataTmp["type"] = "battle"
            DataTmp["chapterType"] = self.chapterType
            DataTmp["chapterName"] = self.chapterName
            DataTmp["characters_data"] = self.characters_data
            DataTmp["sangvisFerris_data"] = self.sangvisFerris_data
            DataTmp["theMap"] = self.theMap
            DataTmp["dialogKey"] = self.dialogKey
            DataTmp["dialogData"] = self.dialogData
            with open("Save/save.yaml", "w", encoding='utf-8') as f:
                yaml.dump(DataTmp, f, allow_unicode=True)
    def load(self,screen):
        with open("Save/save.yaml", "r", encoding='utf-8') as f:
            DataTmp = yaml.load(f.read(),Loader=yaml.FullLoader)
            if DataTmp["type"] == "battle":
                self.chapterType = DataTmp["chapterType"]
                self.chapterName = DataTmp["chapterName"]
                self.characters_data = DataTmp["characters_data"]
                self.sangvisFerris_data = DataTmp["sangvisFerris_data"] 
                self.theMap = DataTmp["theMap"]
                self.dialogKey = DataTmp["dialogKey"]
                self.dialogData = DataTmp["dialogData"]
            else:
                raise Exception('ZeroEngine-Error: Cannot load the data from the "save.yaml" file because the file type does not match')
        self.loadFromSave = True
        self.process_data(screen)
    def process_data(self,screen):
        #获取屏幕的尺寸
        self.window_x,self.window_y = screen.get_size()
        #加载按钮的文字
        self.selectMenuUI = SelectMenu()
        self.battleUiTxt = get_lang("Battle_UI")
        self.warnings_to_display = WarningSystem()
        loading_info = get_lang("LoadingTxt")
        #加载剧情
        with open("Data/{0}/{1}_dialogs_{2}.yaml".format(self.chapterType,self.chapterName,get_setting('Language')), "r", encoding='utf-8') as f:
            DataTmp = yaml.load(f.read(),Loader=yaml.FullLoader)
            #章节标题显示
            self.infoToDisplayDuringLoading = LoadingTitle(self.window_x,self.window_y,self.battleUiTxt["numChapter"],self.chapterName,DataTmp["title"],DataTmp["description"])
            self.battle_info = DataTmp["battle_info"]
            self.dialog_during_battle = DataTmp["dialog_during_battle"]
        #正在加载的gif动态图标
        nowLoadingIcon = loadRealGif("Assets/image/UI/sv98_walking.gif",(self.window_x*0.7,self.window_y*0.83),(self.window_x*0.003*15,self.window_x*0.003*21))
        #渐入效果
        for i in range(1,255,2):
            self.infoToDisplayDuringLoading.display(screen,i)
            display.flip(True)
        #开始加载地图场景
        self.infoToDisplayDuringLoading.display(screen)
        now_loading = fontRender(loading_info["now_loading_map"], "white",self.window_x/76)
        drawImg(now_loading,(self.window_x*0.75,self.window_y*0.9),screen)
        nowLoadingIcon.draw(screen)
        display.flip(True)
        #读取并初始化章节信息
        with open("Data/{0}/{1}_map.yaml".format(self.chapterType,self.chapterName), "r", encoding='utf-8') as f:
            DataTmp = yaml.load(f.read(),Loader=yaml.FullLoader)
            self.zoomIn = DataTmp["zoomIn"]*100
            #储存对话数据key的字典
            self.dialogInfo = DataTmp["dialogs"]
            if self.loadFromSave == True:
                #加载对应角色所需的图片
                characterDataThread = loadCharacterDataFromSaveThread(self.characters_data,self.sangvisFerris_data)
            else:
                #初始化角色信息
                characterDataThread = initializeCharacterDataThread(DataTmp["character"],DataTmp["sangvisFerri"])
                #查看是否有战斗开始前的对话
                if self.dialogInfo["initial"] == None:
                    self.dialogKey = None
                else:
                    self.dialogKey = self.dialogInfo["initial"]
                self.dialogData = None
            self.bg_music = DataTmp["background_music"] 
            #初始化天气和环境的音效 -- 频道1
            self.environment_sound = None
            self.weatherController = None
            if DataTmp["weather"] != None:
                self.environment_sound = pygame.mixer.Sound("Assets/sound/environment/"+DataTmp["weather"]+".ogg")
                self.environment_sound.set_volume(get_setting("Sound")["sound_environment"]/100.0)
                self.weatherController = WeatherSystem(DataTmp["weather"],self.window_x,self.window_y)
        #检测self.zoomIn参数是否越界
        if self.zoomIn < 200:
            self.zoomIn = 200
        elif self.zoomIn > 400:
            self.zoomIn = 400
        self.zoomIntoBe = self.zoomIn
        self.perBlockHeight = round(self.window_y/10)
        #加载角色信息
        characterDataThread.start()
        while characterDataThread.isAlive():
            self.infoToDisplayDuringLoading.display(screen)
            now_loading = fontRender(loading_info["now_loading_characters"]+"({}/{})".format(characterDataThread.currentID,characterDataThread.totalNum), "white",self.window_x/76)
            drawImg(now_loading,(self.window_x*0.75,self.window_y*0.9),screen)
            nowLoadingIcon.draw(screen)
            display.flip(True)
        if self.loadFromSave == False:
            #获取角色数据
            self.characters_data,self.sangvisFerris_data = characterDataThread.getResult()
            #初始化地图模块
            self.theMap = MapObject(DataTmp,round(self.window_x/10),DataTmp["local_x"],DataTmp["local_y"])
        else:
            #因为地图模块已被加载，只需加载图片即可
            self.theMap.load_env_img()
        del characterDataThread
        #计算光亮区域 并初始化地图
        self.theMap.calculate_darkness(self.characters_data,self.window_x,self.window_y)
        #开始加载关卡设定
        self.infoToDisplayDuringLoading.display(screen)
        now_loading = fontRender(loading_info["now_loading_level"], "white",self.window_x/76)
        drawImg(now_loading,(self.window_x*0.75,self.window_y*0.9),screen)
        nowLoadingIcon.draw(screen)
        display.flip(True)
        #加载UI:
        #加载结束回合的图片
        self.end_round_button = loadImage("Assets/image/UI/endRound.png",(self.window_x*0.8,self.window_y*0.7),self.window_x/10, self.window_y/10)
        #加载子弹图片
        #bullet_img = loadImg("Assets/image/UI/bullet.png", perBlockWidth/6, self.perBlockHeight/12)
        #加载血条,各色方块等UI图片 size:perBlockWidth, self.perBlockHeight/5
        self.original_UI_img = {
            "hp_empty" : loadImg("Assets/image/UI/hp_empty.png"),
            "hp_red" : loadImg("Assets/image/UI/hp_red.png"),
            "hp_green" : loadImg("Assets/image/UI/hp_green.png"),
            "action_point_blue" : loadImg("Assets/image/UI/action_point.png"),
            "bullets_number_brown" : loadImg("Assets/image/UI/bullets_number.png"),
            "green" : loadImg("Assets/image/UI/green.png",None,None,150),
            "red" : loadImg("Assets/image/UI/red.png",None,None,150),
            "yellow": loadImg("Assets/image/UI/yellow.png",None,None,150),
            "blue": loadImg("Assets/image/UI/blue.png",None,None,150),
            "orange": loadImg("Assets/image/UI/orange.png",None,None,150),
            "eye_orange": loadImg("Assets/image/UI/eye_orange.png"),
            "eye_red": loadImg("Assets/image/UI/eye_red.png"),
            "supplyBoard":loadImage("Assets/image/UI/score.png",((self.window_x-self.window_x/3)/2,-self.window_y/12),self.window_x/3,self.window_y/12),
        }
        #UI - 变形后
        self.UI_img = {
            "green" : resizeImg(self.original_UI_img["green"], (self.theMap.perBlockWidth*0.8, None)),
            "red" : resizeImg(self.original_UI_img["red"], (self.theMap.perBlockWidth*0.8, None)),
            "yellow" : resizeImg(self.original_UI_img["yellow"], (self.theMap.perBlockWidth*0.8, None)),
            "blue" : resizeImg(self.original_UI_img["blue"], (self.theMap.perBlockWidth*0.8, None)),
            "orange": resizeImg(self.original_UI_img["orange"], (self.theMap.perBlockWidth*0.8, None))
        }
        #角色信息UI管理
        self.characterInfoBoardUI = CharacterInfoBoard(self.window_x,self.window_y)
        #加载对话框图片
        self.dialoguebox_up = DialogBox("Assets/image/UI/dialoguebox.png",self.window_x*0.3,self.window_y*0.15,self.window_x,self.window_y/2-self.window_y*0.35,self.window_x/80)
        self.dialoguebox_up.flip()
        self.dialoguebox_down = DialogBox("Assets/image/UI/dialoguebox.png",self.window_x*0.3,self.window_y*0.15,-self.window_x*0.3,self.window_y/2+self.window_y*0.2,self.window_x/80)
        #-----加载音效-----
        #行走的音效 -- 频道0
        self.walking_sound = []
        for walkingSound in glob.glob(r'Assets/sound/snow/*.wav'):
            self.walking_sound.append(pygame.mixer.Sound(walkingSound))
            self.walking_sound[-1].set_volume(get_setting("Sound")["sound_effects"]/100.0)
        self.the_sound_id = None
        #攻击的音效 -- 频道2
        self.attackingSounds = AttackingSoundManager(get_setting("Sound")["sound_effects"],2)
        #切换回合时的UI
        self.RoundSwitchUI = RoundSwitch(self.window_x,self.window_y,self.battleUiTxt)
        #关卡背景介绍信息文字
        for i in range(len(self.battle_info)):
            self.battle_info[i] = fontRender(self.battle_info[i],"white",self.window_x/76)
        #显示章节信息
        for a in range(0,250,2):
            self.infoToDisplayDuringLoading.display(screen)
            for i in range(len(self.battle_info)):
                self.battle_info[i].set_alpha(a)
                drawImg(self.battle_info[i],(self.window_x/20,self.window_y*0.75+self.battle_info[i].get_height()*1.2*i),screen)
                if i == 1:
                    temp_secode = fontRender(time.strftime(":%S", time.localtime()),"white",self.window_x/76)
                    temp_secode.set_alpha(a)
                    drawImg(temp_secode,(self.window_x/20+self.battle_info[i].get_width(),self.window_y*0.75+self.battle_info[i].get_height()*1.2),screen)
            display.flip(True)
    def display(self,screen):
        #战斗系统主要loop
        while self.battleSystemMainLoop == True:
            self.__update_events()
            #加载地图
            self.theMap.display_map(screen)
            #环境声音-频道1
            if pygame.mixer.Channel(1).get_busy() == False and self.environment_sound != None:
                pygame.mixer.Channel(1).play(self.environment_sound)
            if self.battle == False:
                #如果战斗有对话
                if self.dialogKey != None:
                    #设定初始化
                    if self.dialogData == None:
                        self.dialogData = {
                            "dialogId": 0,
                            "charactersPaths": None,
                            "actionOnce":None,
                            "actionLoop":{},
                            "secondsAlreadyIdle":0,
                            "secondsToIdle":None
                        }
                    dialog_to_display = self.dialog_during_battle[self.dialogKey]
                    #对话系统总循环
                    if self.dialogData["dialogId"] < len(dialog_to_display):
                        #角色动画
                        for key,value in dicMerge(self.sangvisFerris_data,self.characters_data).items():
                            if value.faction == "character" or (value.x,value.y) in self.theMap.lightArea or self.theMap.darkMode != True:
                                if self.dialogData["charactersPaths"] != None and key in self.dialogData["charactersPaths"]:
                                    value.draw("move",screen,self.theMap)
                                elif self.dialogData["actionOnce"] != None and key in self.dialogData["actionOnce"]:
                                    pass
                                elif key in self.dialogData["actionLoop"]:
                                    if self.dialogData["actionLoop"][key] != "die":
                                        value.draw(self.dialogData["actionLoop"][key],screen,self.theMap,False)
                                    else:
                                        value.draw(self.dialogData["actionLoop"][key],screen,self.theMap)
                                else:
                                    value.draw("wait",screen,self.theMap)
                        #展示设施
                        self.theMap.display_ornamentation(screen,self.characters_data,self.sangvisFerris_data)
                        #加载雪花
                        if self.weatherController != None:
                            self.weatherController.display(screen,self.theMap.perBlockWidth,self.perBlockHeight)
                        #如果操作是移动
                        if "move" in dialog_to_display[self.dialogData["dialogId"]]:
                            if self.dialogData["charactersPaths"] == None:
                                self.dialogData["charactersPaths"] = {}
                                for key,value in dicMerge(self.sangvisFerris_data,self.characters_data).items():
                                    if key in dialog_to_display[self.dialogData["dialogId"]]["move"]:
                                        #创建AStar对象,并设置起点和终点为
                                        start_x = value.x
                                        start_y = value.y
                                        end_x = dialog_to_display[self.dialogData["dialogId"]]["move"][key]["x"]
                                        end_y = dialog_to_display[self.dialogData["dialogId"]]["move"][key]["y"]
                                        self.the_route = self.theMap.findPath((start_x,start_y),(end_x,end_y),self.characters_data,self.sangvisFerris_data,None,dialog_to_display[self.dialogData["dialogId"]]["move"])
                                        if len(self.the_route)>0:
                                            self.dialogData["charactersPaths"][key] = self.the_route
                            if len(self.dialogData["charactersPaths"])>0:
                                if pygame.mixer.Channel(1).get_busy() == False and self.environment_sound != None:
                                    pygame.mixer.Channel(1).play(self.environment_sound)
                                key_to_remove = []
                                reProcessMap = False
                                for key,value in self.dialogData["charactersPaths"].items():
                                    if value != []:
                                        if pygame.mixer.Channel(0).get_busy() == False:
                                            self.the_sound_id = random.randint(0,len(self.walking_sound)-1)
                                            pygame.mixer.Channel(0).play(self.walking_sound[self.the_sound_id])
                                        if key in self.characters_data:
                                            if self.characters_data[key].x < value[0][0]:
                                                self.characters_data[key].x+=0.05
                                                self.characters_data[key].setFlip(False)
                                                if self.characters_data[key].x >= value[0][0]:
                                                    self.characters_data[key].x = value[0][0]
                                                    value.pop(0)
                                                    reProcessMap = True
                                            elif self.characters_data[key].x > value[0][0]:
                                                self.characters_data[key].x-=0.05
                                                self.characters_data[key].setFlip(True)
                                                if self.characters_data[key].x <= value[0][0]:
                                                    self.characters_data[key].x = value[0][0]
                                                    value.pop(0)
                                                    reProcessMap = True
                                            elif self.characters_data[key].y < value[0][1]:
                                                self.characters_data[key].y+=0.05
                                                self.characters_data[key].setFlip(True)
                                                if self.characters_data[key].y >= value[0][1]:
                                                    self.characters_data[key].y = value[0][1]
                                                    value.pop(0)
                                                    reProcessMap = True
                                            elif self.characters_data[key].y > value[0][1]:
                                                self.characters_data[key].y-=0.05
                                                self.characters_data[key].setFlip(False)
                                                if self.characters_data[key].y <= value[0][1]:
                                                    self.characters_data[key].y = value[0][1]
                                                    value.pop(0)
                                                    reProcessMap = True
                                        elif key in self.sangvisFerris_data:
                                            if self.sangvisFerris_data[key].x < value[0][0]:
                                                self.sangvisFerris_data[key].x+=0.05
                                                self.sangvisFerris_data[key].setFlip(True)
                                                if self.sangvisFerris_data[key].x >= value[0][0]:
                                                    self.sangvisFerris_data[key].x = value[0][0]
                                                    value.pop(0)
                                                    reProcessMap = True
                                            elif self.sangvisFerris_data[key].x > value[0][0]:
                                                self.sangvisFerris_data[key].x-=0.05
                                                self.sangvisFerris_data[key].setFlip(False)
                                                if self.sangvisFerris_data[key].x <= value[0][0]:
                                                    self.sangvisFerris_data[key].x = value[0][0]
                                                    value.pop(0)
                                                    reProcessMap = True
                                            elif self.sangvisFerris_data[key].y < value[0][1]:
                                                self.sangvisFerris_data[key].y+=0.05
                                                self.sangvisFerris_data[key].setFlip(False)
                                                if self.sangvisFerris_data[key].y >= value[0][1]:
                                                    self.sangvisFerris_data[key].y = value[0][1]
                                                    value.pop(0)
                                                    reProcessMap = True
                                            elif self.sangvisFerris_data[key].y > value[0][1]:
                                                self.sangvisFerris_data[key].y-=0.05
                                                self.sangvisFerris_data[key].setFlip(True)
                                                if self.sangvisFerris_data[key].y <= value[0][1]:
                                                    self.sangvisFerris_data[key].y = value[0][1]
                                                    value.pop(0)
                                                    reProcessMap = True
                                    else:
                                        key_to_remove.append(key)
                                if self.theMap.darkMode == True and reProcessMap == True:
                                    self.theMap.calculate_darkness(self.characters_data,self.window_x,self.window_y)
                                for i in range(len(key_to_remove)):
                                    self.dialogData["charactersPaths"].pop(key_to_remove[i])
                            else:
                                #脚步停止
                                if pygame.mixer.Channel(0).get_busy() != False:
                                    pygame.mixer.Channel(0).stop()
                                self.dialogData["dialogId"] += 1
                                self.dialogData["charactersPaths"] = None
                        #改变方向
                        elif "direction" in dialog_to_display[self.dialogData["dialogId"]]:
                            for key,value in dialog_to_display[self.dialogData["dialogId"]]["direction"].items():
                                if key in self.characters_data:
                                    self.characters_data[key].setFlip(value)
                                elif key in self.sangvisFerris_data:
                                    self.sangvisFerris_data[key].setFlip(value)
                            self.dialogData["dialogId"] += 1
                        #改变动作（一次性）
                        elif "action" in dialog_to_display[self.dialogData["dialogId"]]:
                            if self.dialogData["actionOnce"] == None:
                                self.dialogData["actionOnce"] = dialog_to_display[self.dialogData["dialogId"]]["action"]
                            else:
                                theActionNeedPop = []
                                if len(self.dialogData["actionOnce"]) > 0:
                                    for key,action in self.dialogData["actionOnce"].items():
                                        if key in self.characters_data and self.characters_data[key].draw(action,screen,self.theMap,False) == False:
                                            if action != "die":
                                                self.characters_data[key].reset_imgId(action)
                                            theActionNeedPop.append(key)
                                        elif key in self.sangvisFerris_data and self.sangvisFerris_data[key].draw(action,screen,self.theMap,False) == False:
                                            if action != "die":
                                                self.sangvisFerris_data[key].reset_imgId(action)
                                            theActionNeedPop.append(key)
                                    if len(theActionNeedPop) > 0:
                                        for i in range(len(theActionNeedPop)):
                                            self.dialogData["actionOnce"].pop(theActionNeedPop[i])
                                else:
                                    self.dialogData["dialogId"] += 1
                                    self.dialogData["actionOnce"] = None
                        #改变动作（长期）
                        elif "actionLoop" in dialog_to_display[self.dialogData["dialogId"]]:
                            for key,action in dialog_to_display[self.dialogData["dialogId"]]["actionLoop"].items():
                                self.dialogData["actionLoop"][key] = action
                            self.dialogData["dialogId"] += 1
                        #停止长期的动作改变
                        elif "actionLoopStop" in dialog_to_display[self.dialogData["dialogId"]]:
                            for i in range(len(dialog_to_display[self.dialogData["dialogId"]]["actionLoopStop"])):
                                character_key = dialog_to_display[self.dialogData["dialogId"]]["actionLoopStop"][i]
                                if character_key in self.dialogData["actionLoop"]:
                                    if character_key in self.characters_data:
                                        self.characters_data[character_key].reset_imgId(self.dialogData["actionLoop"][character_key])
                                    elif character_key in self.sangvisFerris_data:
                                        self.sangvisFerris_data[character_key].reset_imgId(self.dialogData["actionLoop"][character_key])
                                    else:
                                        raise Exception("Error: Cannot find ",character_key," while the system is trying to reset the action.")
                                    del self.dialogData["actionLoop"][character_key]
                            self.dialogData["dialogId"] += 1
                        #开始对话
                        elif "dialoguebox_up" in dialog_to_display[self.dialogData["dialogId"]] or "dialoguebox_down" in dialog_to_display[self.dialogData["dialogId"]]:
                            #对话框的移动
                            if self.dialoguebox_up.x > self.window_x/2+self.dialoguebox_up.get_width()*0.4:
                                self.dialoguebox_up.x -= 150
                            if self.dialoguebox_down.x < self.window_x/2-self.dialoguebox_down.get_width()*1.4:
                                self.dialoguebox_down.x += 150
                            #上方对话框
                            if dialog_to_display[self.dialogData["dialogId"]]["dialoguebox_up"] != None:
                                if self.dialoguebox_up.updated == False:
                                    currentTmp = dialog_to_display[self.dialogData["dialogId"]]["dialoguebox_up"]
                                    self.dialoguebox_up.update(currentTmp["content"],currentTmp["speaker"],currentTmp["speaker_icon"])
                                    del currentTmp
                                #对话框图片
                                self.dialoguebox_up.display(screen,self.characterInfoBoardUI)
                            #下方对话框
                            if dialog_to_display[self.dialogData["dialogId"]]["dialoguebox_down"] != None:
                                if self.dialoguebox_down.updated == False:
                                    currentTmp = dialog_to_display[self.dialogData["dialogId"]]["dialoguebox_down"]
                                    self.dialoguebox_down.update(currentTmp["content"],currentTmp["speaker"],currentTmp["speaker_icon"])
                                    del currentTmp
                                #对话框图片
                                self.dialoguebox_down.display(screen,self.characterInfoBoardUI)
                        #闲置一定时间（秒）
                        elif "idle" in dialog_to_display[self.dialogData["dialogId"]]:
                            if self.dialogData["secondsToIdle"] == None:
                                self.dialogData["secondsToIdle"] = dialog_to_display[self.dialogData["dialogId"]]["idle"]*display.fps
                            else:
                                if self.dialogData["secondsAlreadyIdle"] < self.dialogData["secondsToIdle"]:
                                    self.dialogData["secondsAlreadyIdle"] += 1
                                else:
                                    self.dialogData["dialogId"] += 1
                                    self.dialogData["secondsAlreadyIdle"] = 0
                                    self.dialogData["secondsToIdle"] = None
                        elif "changePos" in dialog_to_display[self.dialogData["dialogId"]]:
                            if self.screen_to_move_x == None and "x" in dialog_to_display[self.dialogData["dialogId"]]["changePos"]:
                                self.screen_to_move_x = dialog_to_display[self.dialogData["dialogId"]]["changePos"]["x"]
                            if self.screen_to_move_y == None and "y" in dialog_to_display[self.dialogData["dialogId"]]["changePos"]:
                                self.screen_to_move_y = dialog_to_display[self.dialogData["dialogId"]]["changePos"]["y"]
                            if self.screen_to_move_x != None and self.screen_to_move_x != 0:
                                temp_value = int(self.theMap.getPos_x() + self.screen_to_move_x*0.2)
                                if self.window_x-self.theMap.surface_width<=temp_value<=0:
                                    self.theMap.setPos_x(temp_value)
                                    self.screen_to_move_x*=0.8
                                    if int(self.screen_to_move_x) == 0:
                                        self.screen_to_move_x = 0
                                else:
                                    self.screen_to_move_x = 0
                            if self.screen_to_move_y != None and self.screen_to_move_y !=0:
                                temp_value = int(self.theMap.getPos_y() + self.screen_to_move_y*0.2)
                                if self.window_y-self.theMap.surface_height<=temp_value<=0:
                                    self.theMap.setPos_y(temp_value)
                                    self.screen_to_move_y*=0.8
                                    if int(self.screen_to_move_y) == 0:
                                        self.screen_to_move_y = 0
                                else:
                                    self.screen_to_move_y = 0
                            if self.screen_to_move_x == 0 and self.screen_to_move_y == 0 or self.screen_to_move_x == None and self.screen_to_move_y == None:
                                self.screen_to_move_x = None
                                self.screen_to_move_y = None
                                self.dialogData["dialogId"] += 1
                        #玩家输入按键判定
                        for event in self.__pygame_events:
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_ESCAPE:
                                    pause_menu.display(screen)
                                    self.save_data()
                                    if pause_menu.ifBackToMainMenu == True:
                                        unloadBackgroundMusic()
                                        return None
                            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 or event.type == pygame.JOYBUTTONDOWN and controller.joystick.get_button(0) == 1:
                                if "dialoguebox_up" in dialog_to_display[self.dialogData["dialogId"]] or "dialoguebox_down" in dialog_to_display[self.dialogData["dialogId"]]:
                                    self.dialogData["dialogId"] += 1
                                if self.dialogData["dialogId"] < len(dialog_to_display):
                                    if "dialoguebox_up" in dialog_to_display[self.dialogData["dialogId"]]:
                                        #检测上方对话框
                                        if dialog_to_display[self.dialogData["dialogId"]]["dialoguebox_up"] == None or "dialoguebox_up" not in dialog_to_display[self.dialogData["dialogId"]-1] or dialog_to_display[self.dialogData["dialogId"]-1]["dialoguebox_up"] == None or dialog_to_display[self.dialogData["dialogId"]]["dialoguebox_up"]["speaker"] != dialog_to_display[self.dialogData["dialogId"]-1]["dialoguebox_up"]["speaker"]:
                                            self.dialoguebox_up.reset_pos()
                                            self.dialoguebox_up.updated = False
                                        elif dialog_to_display[self.dialogData["dialogId"]]["dialoguebox_up"]["content"] != dialog_to_display[self.dialogData["dialogId"]-1]["dialoguebox_up"]["content"]:
                                            self.dialoguebox_up.updated = False
                                    else:
                                        self.dialoguebox_up.reset_pos()
                                        self.dialoguebox_up.updated = False
                                    if "dialoguebox_down" in dialog_to_display[self.dialogData["dialogId"]]:
                                        #检测下方对话框    
                                        if dialog_to_display[self.dialogData["dialogId"]]["dialoguebox_down"] == None or "dialoguebox_down" not in dialog_to_display[self.dialogData["dialogId"]-1] or dialog_to_display[self.dialogData["dialogId"]-1]["dialoguebox_down"] == None or dialog_to_display[self.dialogData["dialogId"]]["dialoguebox_down"]["speaker"] != dialog_to_display[self.dialogData["dialogId"]-1]["dialoguebox_down"]["speaker"]:
                                            self.dialoguebox_down.reset_pos()
                                            self.dialoguebox_down.updated = False
                                        elif dialog_to_display[self.dialogData["dialogId"]]["dialoguebox_down"]["content"] != dialog_to_display[self.dialogData["dialogId"]-1]["dialoguebox_down"]["content"]:
                                            self.dialoguebox_down.updated = False
                                    else:
                                        self.dialoguebox_down.reset_pos()
                                        self.dialoguebox_down.updated = False
                                else:
                                    self.dialoguebox_up.reset_pos()
                                    self.dialoguebox_up.updated = False
                                    self.dialoguebox_down.reset_pos()
                                    self.dialoguebox_down.updated = False
                                break
                    else:
                        self.dialogData = None
                        self.dialogKey = None
                        del dialog_to_display
                        self.battle = True
                #如果战斗前无·对话
                elif self.dialogKey == None:
                    #角色动画
                    for every_chara in self.characters_data:
                        self.characters_data[every_chara].draw("wait",screen,self.theMap)
                    for enemies in self.sangvisFerris_data:
                        if (self.sangvisFerris_data[enemies].x,self.sangvisFerris_data[enemies].y) in self.theMap.lightArea or self.theMap.darkMode != True:
                            self.sangvisFerris_data[enemies].draw("wait",screen,self.theMap)
                    #展示设施
                    self.theMap.display_ornamentation(screen,self.characters_data,self.sangvisFerris_data)
                    #角色动画
                    for every_chara in self.characters_data:
                        self.characters_data[every_chara].drawUI(screen,self.original_UI_img,self.theMap)
                    for enemies in self.sangvisFerris_data:
                        if (self.sangvisFerris_data[enemies].x,self.sangvisFerris_data[enemies].y) in self.theMap.lightArea or self.theMap.darkMode != True:
                            self.sangvisFerris_data[enemies].drawUI(screen,self.original_UI_img,self.theMap)
                    #加载雪花
                    if self.weatherController != None:
                        self.weatherController.display(screen,self.theMap.perBlockWidth,self.perBlockHeight)
                    if self.txt_alpha == 0:
                        self.battle = True
            # 游戏主循环
            if self.battle == True:
                right_click = False
                show_pause_menu = False
                #获取鼠标坐标
                mouse_x,mouse_y = controller.get_pos()
                for event in self.__pygame_events:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE and self.characterGetClick == "":
                            show_pause_menu = True
                        if event.key == pygame.K_ESCAPE and self.isWaiting == True:
                            self.NotDrawRangeBlocks = True
                            self.characterGetClick = ""
                            self.action_choice = ""
                            attacking_range = None
                            skill_range = None
                            self.areaDrawColorBlock = {"green":[],"red":[],"yellow":[],"blue":[],"orange":[]}
                        if event.key == pygame.K_w:
                            self.pressKeyToMove["up"]=True
                        if event.key == pygame.K_s:
                            self.pressKeyToMove["down"]=True
                        if event.key == pygame.K_a:
                            self.pressKeyToMove["left"]=True
                        if event.key == pygame.K_d:
                            self.pressKeyToMove["right"]=True
                        if event.key == pygame.K_m:
                            display.quit()
                    elif event.type == pygame.KEYUP:
                        if event.key == pygame.K_w:
                            self.pressKeyToMove["up"]=False
                        if event.key == pygame.K_s:
                            self.pressKeyToMove["down"]=False
                        if event.key == pygame.K_a:
                            self.pressKeyToMove["left"]=False
                        if event.key == pygame.K_d:
                            self.pressKeyToMove["right"]=False
                    #鼠标点击
                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 or event.type == pygame.JOYBUTTONDOWN and controller.joystick.get_button(0) == 1:
                        right_click = True
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        #上下滚轮-放大和缩小地图
                        if event.button == 4 and self.zoomIntoBe < 400:
                            self.zoomIntoBe += 20
                        elif event.button == 5 and self.zoomIntoBe > 200:
                            self.zoomIntoBe -= 20
                    if controller.joystick.get_init() == True:
                        if round(controller.joystick.get_axis(4)) == -1:
                            self.pressKeyToMove["up"]=True
                        else:
                            self.pressKeyToMove["up"]=False
                        if round(controller.joystick.get_axis(4)) == 1:
                            self.pressKeyToMove["down"]=True
                        else:
                            self.pressKeyToMove["down"]=False
                        if round(controller.joystick.get_axis(3)) == 1:
                            self.pressKeyToMove["right"]=True
                        else:
                            self.pressKeyToMove["right"]=False
                        if round(controller.joystick.get_axis(3)) == -1:
                            self.pressKeyToMove["left"]=True
                        else:
                            self.pressKeyToMove["left"]=False
                #移动屏幕
                if pygame.mouse.get_pressed()[2]:
                    if self.mouse_move_temp_x == -1 and self.mouse_move_temp_y == -1:
                        self.mouse_move_temp_x = mouse_x
                        self.mouse_move_temp_y = mouse_y
                    else:
                        if self.mouse_move_temp_x != mouse_x or self.mouse_move_temp_y != mouse_y:
                            if self.mouse_move_temp_x != mouse_x:
                                self.theMap.addPos_x(self.mouse_move_temp_x-mouse_x)
                            if self.mouse_move_temp_y != mouse_y:
                                self.theMap.addPos_y(self.mouse_move_temp_y-mouse_y)
                            self.mouse_move_temp_x = mouse_x
                            self.mouse_move_temp_y = mouse_y
                else:
                    self.mouse_move_temp_x = -1
                    self.mouse_move_temp_y = -1

                #根据self.zoomIntoBe调整self.zoomIn大小
                if self.zoomIntoBe != self.zoomIn:
                    if self.zoomIntoBe < self.zoomIn:
                        self.zoomIn -= 5
                    elif self.zoomIntoBe > self.zoomIn:
                        self.zoomIn += 5
                    newPerBlockWidth = round(self.window_x/self.theMap.column*self.zoomIn/100)
                    newPerBlockHeight = round(self.window_y/self.theMap.row*self.zoomIn/100)
                    self.theMap.addPos_x((self.theMap.perBlockWidth-newPerBlockWidth)*self.theMap.column/2)
                    self.theMap.addPos_y((self.perBlockHeight-newPerBlockHeight)*self.theMap.row/2)
                    self.theMap.perBlockWidth = newPerBlockWidth
                    self.perBlockHeight = newPerBlockHeight
                    #根据perBlockWidth和perBlockHeight重新加载对应尺寸的UI
                    self.UI_img["green"] = resizeImg(self.original_UI_img["green"], (self.theMap.perBlockWidth*0.8, None))
                    self.UI_img["red"] = resizeImg(self.original_UI_img["red"], (self.theMap.perBlockWidth*0.8, None))
                    self.UI_img["yellow"] = resizeImg(self.original_UI_img["yellow"], (self.theMap.perBlockWidth*0.8, None))
                    self.UI_img["blue"] = resizeImg(self.original_UI_img["blue"], (self.theMap.perBlockWidth*0.8, None))
                    self.UI_img["orange"] = resizeImg(self.original_UI_img["orange"], (self.theMap.perBlockWidth*0.8, None))
                    self.theMap.changePerBlockSize(self.theMap.perBlockWidth,self.window_x,self.window_y)
                    self.selectMenuUI.allButton = None
                else:
                    self.zoomIn = self.zoomIntoBe

                #根据按键情况设定要移动的数值
                if self.pressKeyToMove["up"] == True:
                    if self.screen_to_move_y == None:
                        self.screen_to_move_y = self.perBlockHeight/4
                    else:
                        self.screen_to_move_y += self.perBlockHeight/4
                if self.pressKeyToMove["down"] == True:
                    if self.screen_to_move_y == None:
                        self.screen_to_move_y = -self.perBlockHeight/4
                    else:
                        self.screen_to_move_y -= self.perBlockHeight/4
                if self.pressKeyToMove["left"] == True:
                    if self.screen_to_move_x == None:
                        self.screen_to_move_x = self.theMap.perBlockWidth/4
                    else:
                        self.screen_to_move_x += self.theMap.perBlockWidth/4
                if self.pressKeyToMove["right"] == True:
                    if self.screen_to_move_x == None:
                        self.screen_to_move_x = -self.theMap.perBlockWidth/4
                    else:
                        self.screen_to_move_x -= self.theMap.perBlockWidth/4

                #如果需要移动屏幕
                if self.screen_to_move_x != None and self.screen_to_move_x != 0:
                    temp_value = int(self.theMap.getPos_x() + self.screen_to_move_x*0.2)
                    if self.window_x-self.theMap.surface_width<=temp_value<=0:
                        self.theMap.setPos_x(temp_value)
                        self.screen_to_move_x*=0.8
                        if int(self.screen_to_move_x) == 0:
                            self.screen_to_move_x = 0
                    else:
                        self.screen_to_move_x = 0
                if self.screen_to_move_y != None and self.screen_to_move_y !=0:
                    temp_value = int(self.theMap.getPos_y() + self.screen_to_move_y*0.2)
                    if self.window_y-self.theMap.surface_height<=temp_value<=0:
                        self.theMap.setPos_y(temp_value)
                        self.screen_to_move_y*=0.8
                        if int(self.screen_to_move_y) == 0:
                            self.screen_to_move_y = 0
                    else:
                        self.screen_to_move_y = 0

                #加载地图
                self.screen_to_move_x,self.screen_to_move_y = self.theMap.display_map(screen,self.screen_to_move_x,self.screen_to_move_y)
                #画出用彩色方块表示的范围
                for area in self.areaDrawColorBlock:
                    for position in self.areaDrawColorBlock[area]:
                        xTemp,yTemp = self.theMap.calPosInMap(position[0],position[1])
                        drawImg(self.UI_img[area],(xTemp+self.theMap.perBlockWidth*0.1,yTemp),screen)

                #玩家回合
                if self.whose_round == "player":
                    if right_click == True:
                        block_get_click = self.theMap.calBlockInMap(self.UI_img["green"],mouse_x,mouse_y)
                        #如果点击了回合结束的按钮
                        if ifHover(self.end_round_button) and self.isWaiting == True:
                            self.whose_round = "playerToSangvisFerris"
                            self.characterGetClick = ""
                            self.NotDrawRangeBlocks = True
                            attacking_range = None
                            skill_range = None
                            self.areaDrawColorBlock = {"green":[],"red":[],"yellow":[],"blue":[],"orange":[]}
                        #是否在显示移动范围后点击了且点击区域在移动范围内
                        elif len(self.the_route) != 0 and block_get_click != None and (block_get_click["x"], block_get_click["y"]) in self.the_route and self.NotDrawRangeBlocks==False:
                            self.isWaiting = False
                            self.NotDrawRangeBlocks = True
                            self.characters_data[self.characterGetClick].reduce_action_point(len(self.the_route)*2)
                            self.areaDrawColorBlock = {"green":[],"red":[],"yellow":[],"blue":[],"orange":[]}
                        elif self.NotDrawRangeBlocks == "SelectMenu" and self.buttonGetHover == "attack":
                            if self.characters_data[self.characterGetClick].current_bullets > 0 and self.characters_data[self.characterGetClick].if_have_enough_action_point(5):
                                self.action_choice = "attack"
                                self.NotDrawRangeBlocks = False
                            elif self.characters_data[self.characterGetClick].current_bullets <= 0:
                                self.warnings_to_display.add("magazine_is_empty")
                            elif not self.characters_data[self.characterGetClick].if_have_enough_action_point(5):
                                self.warnings_to_display.add("no_enough_ap_to_attack")
                        elif self.NotDrawRangeBlocks == "SelectMenu" and self.buttonGetHover == "move":
                            if self.characters_data[self.characterGetClick].if_have_enough_action_point(2):
                                self.action_choice = "move"
                                self.NotDrawRangeBlocks = False
                            else:
                                self.warnings_to_display.add("no_enough_ap_to_move")
                        elif self.NotDrawRangeBlocks == "SelectMenu" and self.buttonGetHover == "skill":
                            if self.characters_data[self.characterGetClick].if_have_enough_action_point(8):
                                self.action_choice = "skill"
                                self.NotDrawRangeBlocks = False
                            else:
                                self.warnings_to_display.add("no_enough_ap_to_use_skill")
                        elif self.NotDrawRangeBlocks == "SelectMenu" and self.buttonGetHover == "reload":
                            if self.characters_data[self.characterGetClick].if_have_enough_action_point(5) and self.characters_data[self.characterGetClick].bullets_carried > 0:
                                self.action_choice = "reload"
                                self.NotDrawRangeBlocks = False
                            elif self.characters_data[self.characterGetClick].bullets_carried <= 0:
                                self.warnings_to_display.add("no_bullets_left")
                            elif not self.characters_data[self.characterGetClick].if_have_enough_action_point(5):
                                self.warnings_to_display.add("no_enough_ap_to_reload")
                        elif self.NotDrawRangeBlocks == "SelectMenu" and self.buttonGetHover == "rescue":
                            if self.characters_data[self.characterGetClick].if_have_enough_action_point(8):
                                self.action_choice = "rescue"
                                self.NotDrawRangeBlocks = False
                            else:
                                self.warnings_to_display.add("no_enough_ap_to_rescue")
                        elif self.NotDrawRangeBlocks == "SelectMenu" and self.buttonGetHover == "interact":
                            if self.characters_data[self.characterGetClick].if_have_enough_action_point(2):
                                self.action_choice = "interact"
                                self.NotDrawRangeBlocks = False
                            else:
                                self.warnings_to_display.add("no_enough_ap_to_interact")
                        #攻击判定
                        elif self.action_choice == "attack" and self.NotDrawRangeBlocks == False and self.characterGetClick != "" and len(self.enemiesGetAttack)>0:
                            self.characters_data[self.characterGetClick].reduce_action_point(5)
                            self.characters_data[self.characterGetClick].noticed()
                            self.isWaiting = False
                            self.NotDrawRangeBlocks = True
                            attacking_range = None
                            self.areaDrawColorBlock = {"green":[],"red":[],"yellow":[],"blue":[],"orange":[]}
                        elif self.action_choice == "skill" and self.NotDrawRangeBlocks == False and self.characterGetClick != "" and self.skill_target != None:
                            if self.skill_target in self.characters_data:
                                if self.characters_data[self.skill_target].x < self.characters_data[self.characterGetClick].x:
                                    self.characters_data[self.characterGetClick].setFlip(True)
                                elif self.characters_data[self.skill_target].x == self.characters_data[self.characterGetClick].x:
                                    if self.characters_data[self.skill_target].y < self.characters_data[self.characterGetClick].y:
                                        self.characters_data[self.characterGetClick].setFlip(False)
                                    else:
                                        self.characters_data[self.characterGetClick].setFlip(True)
                                else:
                                    self.characters_data[self.characterGetClick].setFlip(False)
                            elif self.skill_target in self.sangvisFerris_data:
                                self.characters_data[self.characterGetClick].noticed()
                                if self.sangvisFerris_data[self.skill_target].x < self.characters_data[self.characterGetClick].x:
                                    self.characters_data[self.characterGetClick].setFlip(True)
                                elif self.sangvisFerris_data[self.skill_target].x == self.characters_data[self.characterGetClick].x:
                                    if self.sangvisFerris_data[self.skill_target].y < self.characters_data[self.characterGetClick].y:
                                        self.characters_data[self.characterGetClick].setFlip(False)
                                    else:
                                        self.characters_data[self.characterGetClick].setFlip(True)
                                else:
                                    self.characters_data[self.characterGetClick].setFlip(False)
                            self.characters_data[self.characterGetClick].reduce_action_point(8)
                            self.characters_data[self.characterGetClick].playSound("skill")
                            self.isWaiting = False
                            self.NotDrawRangeBlocks = True
                            skill_range = None
                            self.areaDrawColorBlock = {"green":[],"red":[],"yellow":[],"blue":[],"orange":[]}
                        elif self.action_choice == "rescue" and self.NotDrawRangeBlocks == False and self.characterGetClick != "" and self.friendGetHelp != None:
                            self.characters_data[self.characterGetClick].reduce_action_point(8)
                            self.characters_data[self.characterGetClick].noticed()
                            self.characters_data[self.friendGetHelp].heal(1)
                            self.characterGetClick = ""
                            self.action_choice = ""
                            self.isWaiting = True
                            self.NotDrawRangeBlocks = True
                            attacking_range = None
                            self.areaDrawColorBlock = {"green":[],"red":[],"yellow":[],"blue":[],"orange":[]}
                        elif self.action_choice == "interact" and self.NotDrawRangeBlocks == False and self.characterGetClick != "" and self.ornamentationGetClick != None:
                            self.characters_data[self.characterGetClick].reduce_action_point(2)
                            self.theMap.ornamentationData[self.ornamentationGetClick].triggered = not self.theMap.ornamentationData[self.ornamentationGetClick].triggered
                            self.theMap.calculate_darkness(self.characters_data,self.window_x,self.window_y)
                            self.characterGetClick = ""
                            self.action_choice = ""
                            self.isWaiting = True
                            self.NotDrawRangeBlocks = True
                            attacking_range = None
                            self.areaDrawColorBlock = {"green":[],"red":[],"yellow":[],"blue":[],"orange":[]}
                        #判断是否有被点击的角色
                        elif block_get_click != None:
                            for key in self.characters_data:
                                if self.characters_data[key].x == block_get_click["x"] and self.characters_data[key].y == block_get_click["y"] and self.isWaiting == True and self.characters_data[key].dying == False and self.NotDrawRangeBlocks != False:
                                    self.screen_to_move_x = None
                                    self.screen_to_move_y = None
                                    attacking_range = None
                                    skill_range = None
                                    self.areaDrawColorBlock = {"green":[],"red":[],"yellow":[],"blue":[],"orange":[]}
                                    if self.characterGetClick != key:
                                        self.characters_data[key].playSound("get_click")
                                        self.characterGetClick = key
                                    self.characterInfoBoardUI.update()
                                    friendsCanSave = []
                                    thingsCanReact = []
                                    for key2 in self.characters_data:
                                        if self.characters_data[key2].dying != False and self.characters_data[key].near(self.characters_data[key2].dying):
                                            friendsCanSave.append(key2)
                                    for i in range(len(self.theMap.ornamentationData)):
                                        if self.theMap.ornamentationData[i].type == "campfire" and self.characters_data[key].near(self.theMap.ornamentationData[i]):
                                            thingsCanReact.append(i)
                                    self.NotDrawRangeBlocks = "SelectMenu"
                                    break
                    #选择菜单的判定，显示功能在角色动画之后
                    if self.NotDrawRangeBlocks == "SelectMenu":
                        #移动画面以使得被点击的角色可以被更好的操作
                        if self.screen_to_move_x == None:
                            tempX,tempY = self.theMap.calPosInMap(self.characters_data[self.characterGetClick].x,self.characters_data[self.characterGetClick].y)
                            if tempX < self.window_x*0.2 and self.theMap.getPos_x()<=0:
                                self.screen_to_move_x = self.window_x*0.2-tempX
                            elif tempX > self.window_x*0.8 and self.theMap.getPos_x()>=self.theMap.column*self.theMap.perBlockWidth*-1:
                                self.screen_to_move_x = self.window_x*0.8-tempX
                        if self.screen_to_move_y == None:
                            if tempY < self.window_y*0.2 and self.theMap.getPos_y()<=0:
                                self.screen_to_move_y = self.window_y*0.2-tempY
                            elif tempY > self.window_y*0.8 and self.theMap.getPos_y()>=self.theMap.row*self.perBlockHeight*-1:
                                self.screen_to_move_y = self.window_y*0.8-tempY
                            
                    #显示攻击/移动/技能范围
                    if self.NotDrawRangeBlocks == False and self.characterGetClick != "":
                        block_get_click = self.theMap.calBlockInMap(self.UI_img["green"],mouse_x,mouse_y)
                        #显示移动范围
                        if self.action_choice == "move":
                            self.areaDrawColorBlock["green"] = []
                            if block_get_click != None:
                                #创建AStar对象,并设置起点和终点为
                                start_x = self.characters_data[self.characterGetClick].x
                                start_y = self.characters_data[self.characterGetClick].y
                                end_x = block_get_click["x"]
                                end_y = block_get_click["y"]
                                max_blocks_can_move = int(self.characters_data[self.characterGetClick].get_action_point()/2)
                                if 0<abs(end_x-start_x)+abs(end_y-start_y)<=max_blocks_can_move:
                                    self.the_route = self.theMap.findPath((start_x,start_y),(end_x,end_y),self.characters_data,self.sangvisFerris_data,max_blocks_can_move)
                                    if len(self.the_route)>0:
                                        #显示路径
                                        self.areaDrawColorBlock["green"] = self.the_route
                                        xTemp,yTemp = self.theMap.calPosInMap(self.the_route[-1][0],self.the_route[-1][1])
                                        displayInCenter(fontRender("-"+str(len(self.the_route)*2)+"AP","green",self.theMap.perBlockWidth/8,True),self.UI_img["green"],xTemp,yTemp,screen)
                        #显示攻击范围        
                        elif self.action_choice == "attack":
                            if attacking_range == None:
                                attacking_range = self.characters_data[self.characterGetClick].getAttackRange(self.theMap)
                            any_character_in_attack_range = False
                            for enemies in self.sangvisFerris_data:
                                if self.sangvisFerris_data[enemies].current_hp > 0:
                                    if (self.sangvisFerris_data[enemies].x,self.sangvisFerris_data[enemies].y) in attacking_range["near"] or (self.sangvisFerris_data[enemies].x,self.sangvisFerris_data[enemies].y) in attacking_range["middle"] or (self.sangvisFerris_data[enemies].x,self.sangvisFerris_data[enemies].y) in attacking_range["far"]:
                                        any_character_in_attack_range = True
                                        break
                            if any_character_in_attack_range == True:
                                self.areaDrawColorBlock["green"] = attacking_range["near"]
                                self.areaDrawColorBlock["blue"] = attacking_range["middle"]
                                self.areaDrawColorBlock["yellow"] = attacking_range["far"]
                                if block_get_click != None:
                                    the_attacking_range_area = []
                                    for area in attacking_range:
                                        if (block_get_click["x"],block_get_click["y"]) in attacking_range[area]:
                                            for y in range(block_get_click["y"]-self.characters_data[self.characterGetClick].attack_range+1,block_get_click["y"]+self.characters_data[self.characterGetClick].attack_range):
                                                if y < block_get_click["y"]:
                                                    for x in range(block_get_click["x"]-self.characters_data[self.characterGetClick].attack_range-(y-block_get_click["y"])+1,block_get_click["x"]+self.characters_data[self.characterGetClick].attack_range+(y-block_get_click["y"])):
                                                        if self.theMap.mapData[y][x].canPassThrough == True:
                                                            the_attacking_range_area.append([x,y])
                                                else:
                                                    for x in range(block_get_click["x"]-self.characters_data[self.characterGetClick].attack_range+(y-block_get_click["y"])+1,block_get_click["x"]+self.characters_data[self.characterGetClick].attack_range-(y-block_get_click["y"])):
                                                        if self.theMap.mapData[y][x].canPassThrough == True:
                                                            the_attacking_range_area.append([x,y])
                                            break
                                    self.enemiesGetAttack = {}
                                    if len(the_attacking_range_area) > 0:
                                        self.areaDrawColorBlock["orange"] = the_attacking_range_area
                                        for enemies in self.sangvisFerris_data:
                                            if [self.sangvisFerris_data[enemies].x,self.sangvisFerris_data[enemies].y] in the_attacking_range_area and self.sangvisFerris_data[enemies].current_hp>0:
                                                if (self.sangvisFerris_data[enemies].x,self.sangvisFerris_data[enemies].y) in attacking_range["far"]:
                                                    self.enemiesGetAttack[enemies] = "far"
                                                elif (self.sangvisFerris_data[enemies].x,self.sangvisFerris_data[enemies].y) in attacking_range["middle"]:
                                                    self.enemiesGetAttack[enemies] = "middle"
                                                elif (self.sangvisFerris_data[enemies].x,self.sangvisFerris_data[enemies].y) in attacking_range["near"]:
                                                    self.enemiesGetAttack[enemies] = "near"
                            else:
                                self.warnings_to_display.add("no_enemy_in_effective_range")
                                self.action_choice = ""
                                self.NotDrawRangeBlocks = "SelectMenu"
                        #显示技能范围        
                        elif self.action_choice == "skill":
                            self.skill_target = None
                            if self.characters_data[self.characterGetClick].max_skill_range > 0:
                                if skill_range == None:
                                    skill_range = {"near":[],"middle":[],"far":[]}
                                    for y in range(self.characters_data[self.characterGetClick].y-self.characters_data[self.characterGetClick].max_skill_range,self.characters_data[self.characterGetClick].y+self.characters_data[self.characterGetClick].max_skill_range+1):
                                        if y < self.characters_data[self.characterGetClick].y:
                                            for x in range(self.characters_data[self.characterGetClick].x-self.characters_data[self.characterGetClick].max_skill_range-(y-self.characters_data[self.characterGetClick].y),self.characters_data[self.characterGetClick].x+self.characters_data[self.characterGetClick].max_skill_range+(y-self.characters_data[self.characterGetClick].y)+1):
                                                if len(self.theMap.mapData)>y>=0 and len(self.theMap.mapData[y])>x>=0:
                                                    if "far" in self.characters_data[self.characterGetClick].skill_effective_range and self.characters_data[self.characterGetClick].skill_effective_range["far"] != None and self.characters_data[self.characterGetClick].skill_effective_range["far"][0] <= abs(x-self.characters_data[self.characterGetClick].x)+abs(y-self.characters_data[self.characterGetClick].y) <= self.characters_data[self.characterGetClick].skill_effective_range["far"][1]:
                                                        skill_range["far"].append([x,y])
                                                    elif "middle" in self.characters_data[self.characterGetClick].skill_effective_range and self.characters_data[self.characterGetClick].skill_effective_range["middle"] != None and self.characters_data[self.characterGetClick].skill_effective_range["middle"][0] <= abs(x-self.characters_data[self.characterGetClick].x)+abs(y-self.characters_data[self.characterGetClick].y) <= self.characters_data[self.characterGetClick].skill_effective_range["middle"][1]:
                                                        skill_range["middle"].append([x,y])
                                                    elif "near" in self.characters_data[self.characterGetClick].skill_effective_range and self.characters_data[self.characterGetClick].skill_effective_range["near"] != None and self.characters_data[self.characterGetClick].skill_effective_range["near"][0] <= abs(x-self.characters_data[self.characterGetClick].x)+abs(y-self.characters_data[self.characterGetClick].y) <= self.characters_data[self.characterGetClick].skill_effective_range["near"][1]:
                                                        skill_range["near"].append([x,y])
                                        else:
                                            for x in range(self.characters_data[self.characterGetClick].x-self.characters_data[self.characterGetClick].max_skill_range+(y-self.characters_data[self.characterGetClick].y),self.characters_data[self.characterGetClick].x+self.characters_data[self.characterGetClick].max_skill_range-(y-self.characters_data[self.characterGetClick].y)+1):
                                                if x == self.characters_data[self.characterGetClick].x and y == self.characters_data[self.characterGetClick].y:
                                                    pass
                                                elif len(self.theMap.mapData)>y>=0 and len(self.theMap.mapData[y])>x>=0:
                                                    if "far" in self.characters_data[self.characterGetClick].skill_effective_range and self.characters_data[self.characterGetClick].skill_effective_range["far"] != None and self.characters_data[self.characterGetClick].skill_effective_range["far"][0] <= abs(x-self.characters_data[self.characterGetClick].x)+abs(y-self.characters_data[self.characterGetClick].y) <= self.characters_data[self.characterGetClick].skill_effective_range["far"][1]:
                                                        skill_range["far"].append([x,y])
                                                    elif "middle" in self.characters_data[self.characterGetClick].skill_effective_range and self.characters_data[self.characterGetClick].skill_effective_range["middle"] != None and self.characters_data[self.characterGetClick].skill_effective_range["middle"][0] <= abs(x-self.characters_data[self.characterGetClick].x)+abs(y-self.characters_data[self.characterGetClick].y) <= self.characters_data[self.characterGetClick].skill_effective_range["middle"][1]:
                                                        skill_range["middle"].append([x,y])
                                                    elif "near" in self.characters_data[self.characterGetClick].skill_effective_range and self.characters_data[self.characterGetClick].skill_effective_range["near"] != None and self.characters_data[self.characterGetClick].skill_effective_range["near"][0] <= abs(x-self.characters_data[self.characterGetClick].x)+abs(y-self.characters_data[self.characterGetClick].y) <= self.characters_data[self.characterGetClick].skill_effective_range["near"][1]:
                                                        skill_range["near"].append([x,y])
                                self.areaDrawColorBlock["green"] = skill_range["near"]
                                self.areaDrawColorBlock["blue"] = skill_range["middle"]
                                self.areaDrawColorBlock["yellow"] = skill_range["far"]
                                block_get_click = self.theMap.calBlockInMap(self.UI_img["green"],mouse_x,mouse_y)
                                if block_get_click != None:
                                    the_skill_cover_area = []
                                    for area in skill_range:
                                        if [block_get_click["x"],block_get_click["y"]] in skill_range[area]:
                                            for y in range(block_get_click["y"]-self.characters_data[self.characterGetClick].skill_cover_range,block_get_click["y"]+self.characters_data[self.characterGetClick].skill_cover_range):
                                                if y < block_get_click["y"]:
                                                    for x in range(block_get_click["x"]-self.characters_data[self.characterGetClick].skill_cover_range-(y-block_get_click["y"])+1,block_get_click["x"]+self.characters_data[self.characterGetClick].skill_cover_range+(y-block_get_click["y"])):
                                                        if len(self.theMap.mapData)>y>=0 and len(self.theMap.mapData[y])>x>=0 and self.theMap.mapData[y][x].canPassThrough == True:
                                                            the_skill_cover_area.append([x,y])
                                                else:
                                                    for x in range(block_get_click["x"]-self.characters_data[self.characterGetClick].skill_cover_range+(y-block_get_click["y"])+1,block_get_click["x"]+self.characters_data[self.characterGetClick].skill_cover_range-(y-block_get_click["y"])):
                                                        if len(self.theMap.mapData)>y>=0 and len(self.theMap.mapData[y])>x>=0 and self.theMap.mapData[y][x].canPassThrough == True:
                                                            the_skill_cover_area.append([x,y])
                                            self.areaDrawColorBlock["orange"] = the_skill_cover_area
                                            self.skill_target = skill(self.characterGetClick,{"x":block_get_click["x"],"y":block_get_click["y"]},the_skill_cover_area,self.sangvisFerris_data,self.characters_data)
                                            break
                            else:
                                self.skill_target = skill(self.characterGetClick,{"x":None,"y":None},None,self.sangvisFerris_data,self.characters_data)
                                if self.skill_target != None:
                                    self.characters_data[self.characterGetClick].reduce_action_point(8)
                                    self.isWaiting = False
                                    self.NotDrawRangeBlocks = True
                        #换弹
                        elif self.action_choice == "reload":
                            bullets_to_add = self.characters_data[self.characterGetClick].magazine_capacity-self.characters_data[self.characterGetClick].current_bullets
                            #需要换弹
                            if bullets_to_add > 0:
                                #如果角色有换弹动画
                                if self.characters_data[self.characterGetClick].get_imgId("reload") != None:
                                    self.isWaiting = False
                                #如果角色没有换弹动画
                                else:
                                    self.characters_data[self.characterGetClick].reduce_action_point(5)
                                    #当所剩子弹足够换弹的时候
                                    if bullets_to_add <= self.characters_data[self.characterGetClick].bullets_carried:
                                        self.characters_data[self.characterGetClick].bullets_carried -= bullets_to_add
                                        self.characters_data[self.characterGetClick].current_bullets += bullets_to_add
                                    #当所剩子弹不足以换弹的时候
                                    else:
                                        self.characters_data[self.characterGetClick].current_bullets += self.characters_data[self.characterGetClick].bullets_carried
                                        self.characters_data[self.characterGetClick].bullets_carried = 0
                                    self.isWaiting = True
                                    self.characterGetClick = ""
                                    self.action_choice = ""
                                    self.NotDrawRangeBlocks = True
                            #无需换弹
                            elif bullets_to_add <= 0:
                                self.warnings_to_display.add("magazine_is_full")
                                self.NotDrawRangeBlocks = "SelectMenu"
                            else:
                                print(self.characterGetClick+" is causing trouble, please double check the files or reporting this issue")
                                break
                        elif self.action_choice == "rescue":
                            self.areaDrawColorBlock["green"] = []
                            self.areaDrawColorBlock["orange"] = []
                            self.friendGetHelp = None
                            for friendNeedHelp in friendsCanSave:
                                if block_get_click != None and block_get_click["x"] == self.characters_data[friendNeedHelp].x and block_get_click["y"] == self.characters_data[friendNeedHelp].y:
                                    self.areaDrawColorBlock["orange"] = [(block_get_click["x"],block_get_click["y"])]
                                    self.friendGetHelp = friendNeedHelp
                                else:
                                    self.areaDrawColorBlock["green"].append((self.characters_data[friendNeedHelp].x,self.characters_data[friendNeedHelp].y))
                        elif self.action_choice == "interact":
                            self.areaDrawColorBlock["green"] = []
                            self.areaDrawColorBlock["orange"] = []
                            self.ornamentationGetClick = None
                            for ornamentationId in thingsCanReact:
                                if block_get_click != None and block_get_click["x"] == self.theMap.ornamentationData[ornamentationId].x and block_get_click["y"] == self.theMap.ornamentationData[ornamentationId].y:
                                    self.areaDrawColorBlock["orange"] = [(block_get_click["x"],block_get_click["y"])]
                                    self.ornamentationGetClick = ornamentationId
                                else:
                                    self.areaDrawColorBlock["green"].append((self.theMap.ornamentationData[ornamentationId].x,self.theMap.ornamentationData[ornamentationId].y))

                    #当有角色被点击时
                    if self.characterGetClick != "" and self.isWaiting == False:
                        #被点击的角色动画
                        self.NotDrawRangeBlocks=True
                        if self.action_choice == "move":
                            theCharacterMoved = False
                            if self.the_route != []:
                                if pygame.mixer.Channel(0).get_busy() == False:
                                    self.the_sound_id = random.randint(0,len(self.walking_sound)-1)
                                    pygame.mixer.Channel(0).play(self.walking_sound[self.the_sound_id])
                                if self.characters_data[self.characterGetClick].x < self.the_route[0][0]:
                                    self.characters_data[self.characterGetClick].x+=0.05
                                    self.characters_data[self.characterGetClick].setFlip(False)
                                    if self.characters_data[self.characterGetClick].x >= self.the_route[0][0]:
                                        self.characters_data[self.characterGetClick].x = self.the_route[0][0]
                                        theCharacterMoved = True
                                elif self.characters_data[self.characterGetClick].x > self.the_route[0][0]:
                                    self.characters_data[self.characterGetClick].x-=0.05
                                    self.characters_data[self.characterGetClick].setFlip(True)
                                    if self.characters_data[self.characterGetClick].x <= self.the_route[0][0]:
                                        self.characters_data[self.characterGetClick].x = self.the_route[0][0]
                                        theCharacterMoved = True
                                elif self.characters_data[self.characterGetClick].y < self.the_route[0][1]:
                                    self.characters_data[self.characterGetClick].y+=0.05
                                    self.characters_data[self.characterGetClick].setFlip(True)
                                    if self.characters_data[self.characterGetClick].y >= self.the_route[0][1]:
                                        self.characters_data[self.characterGetClick].y = self.the_route[0][1]
                                        theCharacterMoved = True
                                elif self.characters_data[self.characterGetClick].y > self.the_route[0][1]:
                                    self.characters_data[self.characterGetClick].setFlip(False)
                                    self.characters_data[self.characterGetClick].y-=0.05
                                    if self.characters_data[self.characterGetClick].y <= self.the_route[0][1]:
                                        self.characters_data[self.characterGetClick].y = self.the_route[0][1]
                                        theCharacterMoved = True
                                if theCharacterMoved == True:
                                    self.the_route.pop(0)
                                    for key,value in self.sangvisFerris_data.items():
                                        enemyAttackRange = value.getAttackRange(self.theMap)
                                        if (self.characters_data[self.characterGetClick].x,self.characters_data[self.characterGetClick].y) in enemyAttackRange["near"] or (self.characters_data[self.characterGetClick].x,self.characters_data[self.characterGetClick].y) in enemyAttackRange["middle"] or (self.characters_data[self.characterGetClick].x,self.characters_data[self.characterGetClick].y) in enemyAttackRange["far"]:
                                            self.characters_data[self.characterGetClick].noticed()
                                            break
                                    if self.theMap.darkMode == True:
                                        self.theMap.calculate_darkness(self.characters_data,self.window_x,self.window_y)
                                self.characters_data[self.characterGetClick].draw("move",screen,self.theMap)
                            else:
                                pygame.mixer.Channel(0).stop()
                                #检测是不是站在补给上
                                for i in range(len(self.theMap.ornamentationData)-1,-1,-1):
                                    if self.theMap.ornamentationData[i].type == "chest" and self.theMap.ornamentationData[i].get_pos() == self.characters_data[self.characterGetClick].get_pos():
                                        self.original_UI_img["supplyBoard"].items = []
                                        for key2,value2 in self.theMap.ornamentationData[i].items.items():
                                            if key2 == "bullet":
                                                self.characters_data[self.characterGetClick].bullets_carried += value2
                                                self.original_UI_img["supplyBoard"].items.append(fontRender(self.battleUiTxt["getBullets"]+": "+str(value2),"white",self.window_x/80))
                                            elif key2 == "hp":
                                                self.characters_data[self.characterGetClick].current_hp += value2
                                                self.original_UI_img["supplyBoard"].items.append(fontRender(self.battleUiTxt["getHealth"]+": "+str(value2),"white",self.window_x/80))
                                        if len(self.original_UI_img["supplyBoard"].items)>0:
                                            self.original_UI_img["supplyBoard"].yTogo = 10
                                        del self.theMap.ornamentationData[i]
                                        break
                                keyTemp = str(self.characters_data[self.characterGetClick].x)+"-"+str(self.characters_data[self.characterGetClick].y) 
                                #检测是否角色有set的动画
                                imgIdForSet = self.characters_data[self.characterGetClick].get_imgId("set")
                                if imgIdForSet != None:
                                    self.characters_data[self.characterGetClick].draw("set",screen,self.theMap,False)
                                    if imgIdForSet == self.characters_data[self.characterGetClick].get_imgNum("set")-1:
                                        self.characters_data[self.characterGetClick].reset_imgId("set")
                                        self.isWaiting = True
                                        self.characterGetClick = ""
                                        self.action_choice = ""
                                        if "move" in self.dialogInfo and keyTemp in self.dialogInfo["move"]:
                                            self.dialogKey = self.dialogInfo["move"][keyTemp]
                                            self.battle = False
                                else:
                                    self.isWaiting = True
                                    self.characterGetClick = ""
                                    self.action_choice = ""
                                    if "move" in self.dialogInfo and keyTemp in self.dialogInfo["move"]:
                                        self.dialogKey = self.dialogInfo["move"][keyTemp]
                                        self.battle = False
                        elif self.action_choice == "attack":
                            #根据敌我坐标判断是否需要反转角色
                            if self.characters_data[self.characterGetClick].get_imgId("attack") == 0:
                                block_get_click = self.theMap.calBlockInMap(self.UI_img["green"],mouse_x,mouse_y)
                                if block_get_click != None:
                                    if block_get_click["x"] < self.characters_data[self.characterGetClick].x:
                                        self.characters_data[self.characterGetClick].setFlip(True)
                                    elif block_get_click["x"] == self.characters_data[self.characterGetClick].x:
                                        if block_get_click["y"] < self.characters_data[self.characterGetClick].y:
                                            self.characters_data[self.characterGetClick].setFlip(False)
                                        else:
                                            self.characters_data[self.characterGetClick].setFlip(True)
                                    else:
                                        self.characters_data[self.characterGetClick].setFlip(False)
                                self.characters_data[self.characterGetClick].playSound("attack")
                            #播放射击音效
                            elif self.characters_data[self.characterGetClick].get_imgId("attack") == 3:
                                self.attackingSounds.play(self.characters_data[self.characterGetClick].kind)
                            self.characters_data[self.characterGetClick].draw("attack",screen,self.theMap,False)
                            if self.characters_data[self.characterGetClick].get_imgId("attack") == self.characters_data[self.characterGetClick].get_imgNum("attack")-2:
                                for each_enemy in self.enemiesGetAttack:
                                    if self.enemiesGetAttack[each_enemy] == "near" and random.randint(1,100) <= 95 or self.enemiesGetAttack[each_enemy] == "middle" and random.randint(1,100) <= 80 or self.enemiesGetAttack[each_enemy] == "far" and random.randint(1,100) <= 65:
                                        the_damage = random.randint(self.characters_data[self.characterGetClick].min_damage,self.characters_data[self.characterGetClick].max_damage)
                                        self.sangvisFerris_data[each_enemy].decreaseHp(the_damage)
                                        self.damage_do_to_characters[each_enemy] = fontRender("-"+str(the_damage),"red",self.window_x/76)
                                    else:
                                        self.damage_do_to_characters[each_enemy] = fontRender("Miss","red",self.window_x/76)
                            elif self.characters_data[self.characterGetClick].get_imgId("attack") == self.characters_data[self.characterGetClick].get_imgNum("attack")-1:
                                self.characters_data[self.characterGetClick].reset_imgId("attack")
                                self.characters_data[self.characterGetClick].current_bullets -= 1
                                self.isWaiting = True
                                self.characterGetClick = ""
                                self.action_choice = ""
                        elif self.action_choice == "skill":
                            self.characters_data[self.characterGetClick].draw("skill",screen,self.theMap,False)
                            if self.characters_data[self.characterGetClick].get_imgId("skill") == self.characters_data[self.characterGetClick].get_imgNum("skill")-2:
                                temp_dic = skill(self.characterGetClick,None,None,self.sangvisFerris_data,self.characters_data,"react",self.skill_target,self.damage_do_to_characters)
                                self.characters_data = temp_dic["characters_data"]
                                self.sangvisFerris_data = temp_dic["sangvisFerris_data"]
                                self.damage_do_to_characters = temp_dic["damage_do_to_characters"]
                                del temp_dic
                            elif self.characters_data[self.characterGetClick].get_imgId("skill") == self.characters_data[self.characterGetClick].get_imgNum("skill")-1:
                                self.characters_data[self.characterGetClick].reset_imgId("skill")
                                self.theMap.calculate_darkness(self.characters_data,self.window_x,self.window_y)
                                self.isWaiting =True
                                self.characterGetClick = ""
                                self.action_choice = ""
                        elif self.action_choice == "reload":
                            self.characters_data[self.characterGetClick].draw("reload",screen,self.theMap,False)
                            if self.characters_data[self.characterGetClick].get_imgNum("reload") == self.characters_data[self.characterGetClick].get_imgNum("reload")-2:
                                self.characters_data[self.characterGetClick].reset_imgId("reload")
                                self.characters_data[self.characterGetClick].reduce_action_point(5)
                                #当所剩子弹足够换弹的时候
                                if bullets_to_add <= self.characters_data[self.characterGetClick].bullets_carried:
                                    self.characters_data[self.characterGetClick].bullets_carried -= bullets_to_add
                                    self.characters_data[self.characterGetClick].current_bullets += bullets_to_add
                                #当所剩子弹不足以换弹的时候
                                else:
                                    self.characters_data[self.characterGetClick].current_bullets += self.characters_data[self.characterGetClick].bullets_carried
                                    self.characters_data[self.characterGetClick].bullets_carried = 0
                                self.isWaiting =True
                                self.characterGetClick = ""
                                self.action_choice = ""
                    elif self.characterGetClick != "" and self.isWaiting == True:
                        self.characters_data[self.characterGetClick].draw("wait",screen,self.theMap)

                #敌方回合
                if self.whose_round == "sangvisFerris":
                    self.enemy_in_control = self.sangvisFerris_name_list[self.enemies_in_control_id]
                    if self.enemy_action == None:
                        self.enemy_action = AI(self.enemy_in_control,self.theMap,self.characters_data,self.sangvisFerris_data,self.the_characters_detected_last_round)
                        print(self.enemy_in_control+" choses "+self.enemy_action["action"])
                    if self.enemy_action["action"] == "move":
                        if self.enemy_action["route"] != []:
                            if pygame.mixer.Channel(0).get_busy() == False:
                                self.the_sound_id = random.randint(0,len(self.walking_sound)-1)
                                pygame.mixer.Channel(0).play(self.walking_sound[self.the_sound_id])
                            if self.sangvisFerris_data[self.enemy_in_control].x < self.enemy_action["route"][0][0]:
                                self.sangvisFerris_data[self.enemy_in_control].x+=0.05
                                self.sangvisFerris_data[self.enemy_in_control].setFlip(True)
                                if self.sangvisFerris_data[self.enemy_in_control].x >= self.enemy_action["route"][0][0]:
                                    self.sangvisFerris_data[self.enemy_in_control].x = self.enemy_action["route"][0][0]
                                    self.enemy_action["route"].pop(0)
                            elif self.sangvisFerris_data[self.enemy_in_control].x > self.enemy_action["route"][0][0]:
                                self.sangvisFerris_data[self.enemy_in_control].x-=0.05
                                self.sangvisFerris_data[self.enemy_in_control].setFlip(False)
                                if self.sangvisFerris_data[self.enemy_in_control].x <= self.enemy_action["route"][0][0]:
                                    self.sangvisFerris_data[self.enemy_in_control].x = self.enemy_action["route"][0][0]
                                    self.enemy_action["route"].pop(0)
                            elif self.sangvisFerris_data[self.enemy_in_control].y < self.enemy_action["route"][0][1]:
                                self.sangvisFerris_data[self.enemy_in_control].y+=0.05
                                self.sangvisFerris_data[self.enemy_in_control].setFlip(False)
                                if self.sangvisFerris_data[self.enemy_in_control].y >= self.enemy_action["route"][0][1]:
                                    self.sangvisFerris_data[self.enemy_in_control].y = self.enemy_action["route"][0][1]
                                    self.enemy_action["route"].pop(0)
                            elif self.sangvisFerris_data[self.enemy_in_control].y > self.enemy_action["route"][0][1]:
                                self.sangvisFerris_data[self.enemy_in_control].y-=0.05
                                self.sangvisFerris_data[self.enemy_in_control].setFlip(True)
                                if self.sangvisFerris_data[self.enemy_in_control].y <= self.enemy_action["route"][0][1]:
                                    self.sangvisFerris_data[self.enemy_in_control].y = self.enemy_action["route"][0][1]
                                    self.enemy_action["route"].pop(0)
                            if (int(self.sangvisFerris_data[self.enemy_in_control].x),int(self.sangvisFerris_data[self.enemy_in_control].y)) in self.theMap.lightArea or self.theMap.darkMode != True:
                                self.sangvisFerris_data[self.enemy_in_control].draw("move",screen,self.theMap)
                        else:
                            if pygame.mixer.Channel(0).get_busy() == True:
                                pygame.mixer.Channel(0).stop()
                            self.enemies_in_control_id +=1
                            if self.enemies_in_control_id >= len(self.sangvisFerris_name_list):
                                self.whose_round = "sangvisFerrisToPlayer"
                                self.resultInfo["total_rounds"] += 1
                            self.enemy_action = None
                            self.enemy_in_control = ""
                    elif self.enemy_action["action"] == "attack":
                        if self.sangvisFerris_data[self.enemy_in_control].get_imgId("attack") == 3:
                            self.attackingSounds.play(self.sangvisFerris_data[self.enemy_in_control].kind)
                        if (self.sangvisFerris_data[self.enemy_in_control].x,self.sangvisFerris_data[self.enemy_in_control].y) in self.theMap.lightArea or self.theMap.darkMode != True:
                            if self.characters_data[self.enemy_action["target"]].x > self.sangvisFerris_data[self.enemy_in_control].x:
                                self.sangvisFerris_data[self.enemy_in_control].setFlip(True)
                            elif self.characters_data[self.enemy_action["target"]].x == self.sangvisFerris_data[self.enemy_in_control].x:
                                if self.characters_data[self.enemy_action["target"]].y > self.sangvisFerris_data[self.enemy_in_control].y:
                                    self.sangvisFerris_data[self.enemy_in_control].setFlip(False)
                                else:
                                    self.sangvisFerris_data[self.enemy_in_control].setFlip(True)
                            else:
                                self.sangvisFerris_data[self.enemy_in_control].setFlip(False)
                            self.sangvisFerris_data[self.enemy_in_control].draw("attack",screen,self.theMap,False)
                        else:
                            self.sangvisFerris_data[self.enemy_in_control].add_imgId("attack")
                        if self.sangvisFerris_data[self.enemy_in_control].get_imgId("attack") == self.sangvisFerris_data[self.enemy_in_control].get_imgNum("attack")-1:
                            temp_value = random.randint(0,100)
                            if self.enemy_action["target_area"] == "near" and temp_value <= 95 or self.enemy_action["target_area"] == "middle" and temp_value <= 80 or self.enemy_action["target_area"] == "far" and temp_value <= 65:
                                the_damage = random.randint(self.sangvisFerris_data[self.enemy_in_control].min_damage,self.sangvisFerris_data[self.enemy_in_control].max_damage)
                                self.resultInfo = self.characters_data[self.enemy_action["target"]].decreaseHp(the_damage,self.resultInfo)
                                self.theMap.calculate_darkness(self.characters_data,self.window_x,self.window_y)
                                self.damage_do_to_characters[self.enemy_action["target"]] = fontRender("-"+str(the_damage),"red",self.window_x/76)
                            else:
                                self.damage_do_to_characters[self.enemy_action["target"]] = fontRender("Miss","red",self.window_x/76)
                            self.sangvisFerris_data[self.enemy_in_control].reset_imgId("attack")
                            self.enemies_in_control_id +=1
                            if self.enemies_in_control_id >= len(self.sangvisFerris_name_list):
                                self.whose_round = "sangvisFerrisToPlayer"
                                self.resultInfo["total_rounds"] += 1
                            self.enemy_action = None
                            self.enemy_in_control = ""
                    elif self.enemy_action["action"] == "move&attack":
                        if len(self.enemy_action["route"]) > 0:
                            if pygame.mixer.Channel(0).get_busy() == False:
                                self.the_sound_id = random.randint(0,len(self.walking_sound)-1)
                                pygame.mixer.Channel(0).play(self.walking_sound[self.the_sound_id])
                            if self.sangvisFerris_data[self.enemy_in_control].x < self.enemy_action["route"][0][0]:
                                self.sangvisFerris_data[self.enemy_in_control].x+=0.05
                                self.sangvisFerris_data[self.enemy_in_control].setFlip(True)
                                if self.sangvisFerris_data[self.enemy_in_control].x >= self.enemy_action["route"][0][0]:
                                    self.sangvisFerris_data[self.enemy_in_control].x = self.enemy_action["route"][0][0]
                                    self.enemy_action["route"].pop(0)
                            elif self.sangvisFerris_data[self.enemy_in_control].x > self.enemy_action["route"][0][0]:
                                self.sangvisFerris_data[self.enemy_in_control].x-=0.05
                                self.sangvisFerris_data[self.enemy_in_control].setFlip(False)
                                if self.sangvisFerris_data[self.enemy_in_control].x <= self.enemy_action["route"][0][0]:
                                    self.sangvisFerris_data[self.enemy_in_control].x = self.enemy_action["route"][0][0]
                                    self.enemy_action["route"].pop(0)
                            elif self.sangvisFerris_data[self.enemy_in_control].y < self.enemy_action["route"][0][1]:
                                self.sangvisFerris_data[self.enemy_in_control].y+=0.05
                                self.sangvisFerris_data[self.enemy_in_control].setFlip(False)
                                if self.sangvisFerris_data[self.enemy_in_control].y >= self.enemy_action["route"][0][1]:
                                    self.sangvisFerris_data[self.enemy_in_control].y = self.enemy_action["route"][0][1]
                                    self.enemy_action["route"].pop(0)
                            elif self.sangvisFerris_data[self.enemy_in_control].y > self.enemy_action["route"][0][1]:
                                self.sangvisFerris_data[self.enemy_in_control].y-=0.05
                                self.sangvisFerris_data[self.enemy_in_control].setFlip(True)
                                if self.sangvisFerris_data[self.enemy_in_control].y <= self.enemy_action["route"][0][1]:
                                    self.sangvisFerris_data[self.enemy_in_control].y = self.enemy_action["route"][0][1]
                                    self.enemy_action["route"].pop(0)
                            if (int(self.sangvisFerris_data[self.enemy_in_control].x),int(self.sangvisFerris_data[self.enemy_in_control].y)) in self.theMap.lightArea or self.theMap.darkMode != True:
                                self.sangvisFerris_data[self.enemy_in_control].draw("move",screen,self.theMap)
                        else:
                            if pygame.mixer.Channel(0).get_busy() == True:
                                pygame.mixer.Channel(0).stop()
                            if self.sangvisFerris_data[self.enemy_in_control].get_imgId("attack") == 3:
                                self.attackingSounds.play(self.sangvisFerris_data[self.enemy_in_control].kind)
                            if (self.sangvisFerris_data[self.enemy_in_control].x,self.sangvisFerris_data[self.enemy_in_control].y) in self.theMap.lightArea or self.theMap.darkMode != True:
                                if self.characters_data[self.enemy_action["target"]].x > self.sangvisFerris_data[self.enemy_in_control].x:
                                    self.sangvisFerris_data[self.enemy_in_control].setFlip(True)
                                elif self.characters_data[self.enemy_action["target"]].x == self.sangvisFerris_data[self.enemy_in_control].x:
                                    if self.characters_data[self.enemy_action["target"]].y > self.sangvisFerris_data[self.enemy_in_control].y:
                                        self.sangvisFerris_data[self.enemy_in_control].setFlip(False)
                                    else:
                                        self.sangvisFerris_data[self.enemy_in_control].setFlip(True)
                                else:
                                    self.sangvisFerris_data[self.enemy_in_control].setFlip(False)
                                self.sangvisFerris_data[self.enemy_in_control].draw("attack",screen,self.theMap,False)
                            else:
                                self.sangvisFerris_data[self.enemy_in_control].add_imgId("attack")
                            if self.sangvisFerris_data[self.enemy_in_control].get_imgId("attack") == self.sangvisFerris_data[self.enemy_in_control].get_imgNum("attack")-1:
                                temp_value = random.randint(0,100)
                                if self.enemy_action["target_area"] == "near" and temp_value <= 95 or self.enemy_action["target_area"] == "middle" and temp_value <= 80 or self.enemy_action["target_area"] == "far" and temp_value <= 65:
                                    the_damage = random.randint(self.sangvisFerris_data[self.enemy_in_control].min_damage,self.sangvisFerris_data[self.enemy_in_control].max_damage)
                                    self.resultInfo = self.characters_data[self.enemy_action["target"]].decreaseHp(the_damage,self.resultInfo)
                                    self.theMap.calculate_darkness(self.characters_data,self.window_x,self.window_y)
                                    self.damage_do_to_characters[self.enemy_action["target"]] = fontRender("-"+str(the_damage),"red",self.window_x/76)
                                else:
                                    self.damage_do_to_characters[self.enemy_action["target"]] = fontRender("Miss","red",self.window_x/76)
                                self.sangvisFerris_data[self.enemy_in_control].reset_imgId("attack")
                                self.enemies_in_control_id +=1
                                if self.enemies_in_control_id >= len(self.sangvisFerris_name_list):
                                    self.whose_round = "sangvisFerrisToPlayer"
                                    self.resultInfo["total_rounds"] += 1
                                self.enemy_action = None
                                self.enemy_in_control = ""
                    elif self.enemy_action["action"] == "stay":
                        self.enemies_in_control_id +=1
                        if self.enemies_in_control_id >= len(self.sangvisFerris_name_list):
                            self.whose_round = "sangvisFerrisToPlayer"
                            self.resultInfo["total_rounds"] += 1
                        self.enemy_action = None
                        self.enemy_in_control = ""
                    else:
                        print("warning: not choice")

                #↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓角色动画展示区↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓#
                rightClickCharacterAlphaDeduct = True
                for key,value in dicMerge(self.characters_data,self.sangvisFerris_data).items():
                    #根据血量判断角色的动作
                    if value.faction == "character" and key != self.characterGetClick or value.faction == "sangvisFerri" and key != self.enemy_in_control and (value.x,value.y) in self.theMap.lightArea or value.faction == "sangvisFerri" and key != self.enemy_in_control and self.theMap.darkMode != True:
                        if value.current_hp > 0:
                            if value.faction == "character" and value.get_imgId("die") > 0:
                                value.draw("die",screen,self.theMap,False)
                                value.add_imgId("die", -2)
                                if value.get_imgId("die") <= 0:
                                    value.set_imgId("die",0)
                            else:
                                if self.NotDrawRangeBlocks == True and pygame.mouse.get_pressed()[2]:
                                    block_get_click = self.theMap.calBlockInMap(self.UI_img["green"],mouse_x,mouse_y)
                                    if block_get_click != None and block_get_click["x"] == value.x and block_get_click["y"]  == value.y:
                                        rightClickCharacterAlphaDeduct = False
                                        if self.rightClickCharacterAlpha == None:
                                            self.rightClickCharacterAlpha = 0
                                        if self.rightClickCharacterAlpha < 150:
                                            self.rightClickCharacterAlpha += 10
                                            self.UI_img["yellow"].set_alpha(self.rightClickCharacterAlpha)
                                            self.UI_img["blue"].set_alpha(self.rightClickCharacterAlpha)
                                            self.UI_img["green"].set_alpha(self.rightClickCharacterAlpha)
                                        rangeCanAttack =  value.getAttackRange(self.theMap)
                                        self.areaDrawColorBlock["yellow"] = rangeCanAttack["far"]
                                        self.areaDrawColorBlock["blue"] =  rangeCanAttack["middle"]
                                        self.areaDrawColorBlock["green"] = rangeCanAttack["near"]
                                value.draw("wait",screen,self.theMap)
                        elif value.current_hp<=0:
                            value.draw("die",screen,self.theMap,False)

                    #是否有在播放死亡角色的动画（而不是倒地状态）
                    if value.current_hp<=0 and key not in self.the_dead_one:
                        if value.faction == "character" and value.kind == "HOC" or value.faction == "sangvisFerri":
                            self.the_dead_one[key] = value.faction
                    #伤害/治理数值显示
                    if key in self.damage_do_to_characters:
                        the_alpha_to_check = self.damage_do_to_characters[key].get_alpha()
                        if the_alpha_to_check > 0:
                            xTemp,yTemp = self.theMap.calPosInMap(value.x,value.y)
                            xTemp+=self.theMap.perBlockWidth*0.05
                            yTemp-=self.theMap.perBlockWidth*0.05
                            displayInCenter(self.damage_do_to_characters[key],self.UI_img["green"],xTemp,yTemp,screen)
                            self.damage_do_to_characters[key].set_alpha(the_alpha_to_check-5)
                        else:
                            del self.damage_do_to_characters[key]
                
                if rightClickCharacterAlphaDeduct == True and self.rightClickCharacterAlpha != None:
                    if self.rightClickCharacterAlpha>0:
                        self.rightClickCharacterAlpha-=10
                        self.UI_img["yellow"].set_alpha(self.rightClickCharacterAlpha)
                        self.UI_img["blue"].set_alpha(self.rightClickCharacterAlpha)
                        self.UI_img["green"].set_alpha(self.rightClickCharacterAlpha)
                    elif self.rightClickCharacterAlpha == 0:
                        self.areaDrawColorBlock["yellow"] = []
                        self.areaDrawColorBlock["blue"] = []
                        self.areaDrawColorBlock["green"] = []
                        self.UI_img["yellow"].set_alpha(150)
                        self.UI_img["blue"].set_alpha(150)
                        self.UI_img["green"].set_alpha(150)
                        self.rightClickCharacterAlpha = None
                if len(self.the_dead_one) > 0:
                    the_dead_one_remove = []
                    for key,value in self.the_dead_one.items():
                        if value == "sangvisFerri":
                            if self.sangvisFerris_data[key].get_imgId("die") == self.sangvisFerris_data[key].get_imgNum("die")-1:
                                the_alpha = self.sangvisFerris_data[key].get_imgAlpaha("die")
                                if the_alpha > 0:
                                    self.sangvisFerris_data[key].set_imgAlpaha("die",the_alpha-5)
                                else:
                                    the_dead_one_remove.append(key)
                                    del self.sangvisFerris_data[key]
                                    self.resultInfo["total_kills"]+=1
                        elif value == "character":
                            if self.characters_data[key].get_imgId("die") == self.characters_data[key].get_imgNum("die")-1:
                                the_alpha = self.characters_data[key].get_imgAlpaha("die")
                                if the_alpha > 0:
                                    self.characters_data[key].set_imgAlpaha("die",the_alpha-5)
                                else:
                                    the_dead_one_remove.append(key)
                                    del self.characters_data[key]
                                    self.resultInfo["times_characters_down"]+=1
                                    self.theMap.calculate_darkness(self.characters_data,self.window_x,self.window_y)
                    for key in the_dead_one_remove:
                        del self.the_dead_one[key]
                #↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑角色动画展示区↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑#
                #展示设施
                self.theMap.display_ornamentation(screen,self.characters_data,self.sangvisFerris_data)
                #展示所有角色Ui
                for every_chara in self.characters_data:
                    self.characters_data[every_chara].drawUI(screen,self.original_UI_img,self.theMap)
                if self.theMap.darkMode == True:
                    for enemies in self.sangvisFerris_data:
                        if (int(self.sangvisFerris_data[enemies].x),int(self.sangvisFerris_data[enemies].y)) in self.theMap.lightArea:
                            self.sangvisFerris_data[enemies].drawUI(screen,self.original_UI_img,self.theMap)
                else:
                    for enemies in self.sangvisFerris_data:
                        self.sangvisFerris_data[enemies].drawUI(screen,self.original_UI_img,self.theMap)

                #显示选择菜单
                if self.NotDrawRangeBlocks == "SelectMenu":
                    #左下角的角色信息
                    self.characterInfoBoardUI.display(screen,self.characters_data[self.characterGetClick],self.original_UI_img)
                    #----选择菜单----
                    self.buttonGetHover = self.selectMenuUI.display(screen,round(self.theMap.perBlockWidth/10),self.theMap.getBlockExactLocation(self.characters_data[self.characterGetClick].x,self.characters_data[self.characterGetClick].y),self.characters_data[self.characterGetClick].kind,friendsCanSave,thingsCanReact)
                #加载雪花
                if self.weatherController != None:
                    self.weatherController.display(screen,self.theMap.perBlockWidth,self.perBlockHeight)
                
                #↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓中间检测区↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓#
                if self.whose_round == "playerToSangvisFerris" or self.whose_round == "sangvisFerrisToPlayer":
                    if self.RoundSwitchUI.display(screen,self.whose_round,self.resultInfo["total_rounds"]) == True:
                        if self.whose_round == "playerToSangvisFerris":
                            self.enemies_in_control_id = 0
                            self.sangvisFerris_name_list = []
                            for every_chara in self.sangvisFerris_data:
                                if self.sangvisFerris_data[every_chara].current_hp>0:
                                    self.sangvisFerris_name_list.append(every_chara)
                            for every_chara in self.characters_data:
                                if self.characters_data[every_chara].dying != False:
                                    self.characters_data[every_chara].dying -= 1
                            self.whose_round = "sangvisFerris"
                        elif self.whose_round == "sangvisFerrisToPlayer":
                            characters_detect_this_round = {}
                            for key in self.characters_data:
                                self.characters_data[key].reset_action_point()
                                if self.characters_data[key].detection == False:
                                    characters_detect_this_round[key] = [self.characters_data[key].x,self.characters_data[key].y]
                            self.whose_round = "player"
                #检测所有敌人是否都已经被消灭
                if len(self.sangvisFerris_data) == 0 and self.whose_round != "result":
                    self.characterGetClick = ""
                    self.NotDrawRangeBlocks = False
                    self.whose_round = "result_win"

                #显示获取到的物资
                if self.original_UI_img["supplyBoard"].yTogo == 10:
                    if self.original_UI_img["supplyBoard"].y < self.original_UI_img["supplyBoard"].yTogo:
                        self.original_UI_img["supplyBoard"].y += 5
                    else:
                        if self.stayingTime == 30:
                            self.original_UI_img["supplyBoard"].yTogo = -self.window_y/12
                            self.stayingTime = 0
                        else:
                            self.stayingTime += 1
                else:
                    if self.original_UI_img["supplyBoard"].y > self.original_UI_img["supplyBoard"].yTogo:
                        self.original_UI_img["supplyBoard"].y -= 5

                self.original_UI_img["supplyBoard"].draw(screen)
                if len(self.original_UI_img["supplyBoard"].items) > 0 and self.original_UI_img["supplyBoard"].y != -self.window_y/30:
                    lenTemp = 0
                    for i in range(len(self.original_UI_img["supplyBoard"].items)):
                        lenTemp += self.original_UI_img["supplyBoard"].items[i].get_width()*1.5
                    start_point = (self.window_x - lenTemp)/2
                    for i in range(len(self.original_UI_img["supplyBoard"].items)):
                        start_point += self.original_UI_img["supplyBoard"].items[i].get_width()*0.25
                        drawImg(self.original_UI_img["supplyBoard"].items[i],(start_point,(self.original_UI_img["supplyBoard"].height - self.original_UI_img["supplyBoard"].items[i].get_height())/2),screen,0,self.original_UI_img["supplyBoard"].y)
                        start_point += self.original_UI_img["supplyBoard"].items[i].get_width()*1.25

                if self.whose_round == "player":
                    #加载结束回合的按钮
                    self.end_round_button.draw(screen)

                #显示警告
                self.warnings_to_display.display(screen)

                #加载并播放音乐
                if pygame.mixer.music.get_busy() != 1:
                    pygame.mixer.music.load("Assets/music/"+self.bg_music)
                    pygame.mixer.music.play(loops=9999, start=0.0)
                    pygame.mixer.music.set_volume(get_setting("Sound")["background_music"]/100.0)

                #结束动画
                if self.whose_round == "result_win":
                    self.resultInfo["total_time"] = time.localtime(time.time()-self.resultInfo["total_time"])
                    ResultBoardUI = ResultBoard(self.resultInfo,self.window_x,self.window_y)
                    self.whose_round = "result"
                if self.whose_round == "result":
                    for event in self.__pygame_events:
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_SPACE:
                                self.battle = False
                                self.battleSystemMainLoop = False
                    ResultBoardUI.display(screen)
                #展示暂停菜单
                if show_pause_menu == True:
                    pause_menu.display(screen)
                    self.save_data()
                    if pause_menu.ifBackToMainMenu == True:
                        unloadBackgroundMusic()
                        return None
        
            #渐变效果：一次性的
            if self.txt_alpha == None:
                self.txt_alpha = 250
            if self.txt_alpha > 0:
                self.infoToDisplayDuringLoading.black_bg.set_alpha(self.txt_alpha)
                self.infoToDisplayDuringLoading.display(screen,self.txt_alpha)
                for i in range(len(self.battle_info)):
                    self.battle_info[i].set_alpha(self.txt_alpha)
                    drawImg(self.battle_info[i],(self.window_x/20,self.window_y*0.75+self.battle_info[i].get_height()*1.2*i),screen)
                    if i == 1:
                        temp_secode = fontRender(time.strftime(":%S", time.localtime()),"white",self.window_x/76)
                        temp_secode.set_alpha(self.txt_alpha)
                        drawImg(temp_secode,(self.window_x/20+self.battle_info[i].get_width(),self.window_y*0.75+self.battle_info[i].get_height()*1.2),screen)
                self.txt_alpha -= 5
            
            #刷新画面
            display.flip()