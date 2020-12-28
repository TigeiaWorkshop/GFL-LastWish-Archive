# cython: language_level=3
from Zero3.battleSystemInterface import *

class BattleSystem(BattleSystemInterface):
    def __init__(self,chapterType=None,chapterId=None):
        BattleSystemInterface.__init__(self,chapterType,chapterId)
        #被选中的角色
        self.characterGetClick = None
        self.enemiesGetAttack = {}
        self.action_choice = None
        #是否不要画出用于表示范围的方块
        self.NotDrawRangeBlocks = True
        self.areaDrawColorBlock = {"green":[],"red":[],"yellow":[],"blue":[],"orange":[]}
        #是否在战斗状态-战斗loop
        self.battleMode = False
        #是否在等待
        self.isWaiting = True
        #谁的回合
        self.whose_round = "sangvisFerrisToPlayer"
        self.rightClickCharacterAlpha = None
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
        #战斗状态数据
        self.resultInfo = {
            "total_rounds" : 1,
            "total_kills" : 0,
            "total_time" : time.time(),
            "times_characters_down" : 0
        }
        #储存角色受到伤害的文字surface
        self.damage_do_to_characters = {}
        self.txt_alpha = None
        self.stayingTime = 0
        # 移动路径
        self.the_route = []
        #上个回合因为暴露被敌人发现的角色
        #格式：角色：[x,y]
        self.the_characters_detected_last_round = {}
        #敌人的状态
        self.enemy_action = None
        #积分栏的UI模块
        self.ResultBoardUI = None
        #对话-动作是否被设置
        self.dialog_ifPathSet = False
    #储存章节信息
    def __save_data(self):
        if pause_menu.ifSave == True:
            pause_menu.ifSave = False
            DataTmp = {}
            DataTmp["type"] = "battle"
            DataTmp["chapterType"] = self.chapterType
            DataTmp["chapterId"] = self.chapterId
            DataTmp["characters_data"] = self.characters_data
            DataTmp["sangvisFerris_data"] = self.sangvisFerris_data
            DataTmp["MAP"] = self.MAP
            DataTmp["dialogKey"] = self.dialogKey
            DataTmp["dialogData"] = self.dialogData
            DataTmp["resultInfo"] = self.resultInfo
            saveConfig("Save/save.yaml",DataTmp)
    #从存档中加载游戏进程
    def load(self,screen):
        DataTmp = loadConfig("Save/save.yaml")
        if DataTmp["type"] == "battle":
            self.chapterType = DataTmp["chapterType"]
            self.chapterId = DataTmp["chapterId"]
            self.characters_data = DataTmp["characters_data"]
            self.sangvisFerris_data = DataTmp["sangvisFerris_data"] 
            self.MAP = DataTmp["MAP"]
            self.dialogKey = DataTmp["dialogKey"]
            self.dialogData = DataTmp["dialogData"]
            self.resultInfo = DataTmp["resultInfo"]
        else:
            raise Exception('ZeroEngine-Error: Cannot load the data from the "save.yaml" file because the file type does not match')
        self.loadFromSave = True
        self.initialize(screen)
    #加载游戏进程
    def initialize(self,screen):
        #获取屏幕的尺寸
        self.window_x,self.window_y = screen.get_size()
        #生成标准文字渲染器
        self.FONTSIZE = int(self.window_x/76)
        self.FONT = createFont(self.FONTSIZE)
        #加载按钮的文字
        self.selectMenuUI = SelectMenu()
        self.battleModeUiTxt = get_lang("Battle_UI")
        self.warnings_to_display = WarningSystem()
        loading_info = get_lang("LoadingTxt")
        #加载剧情
        DataTmp = loadConfig("Data/{0}/chapter{1}_dialogs_{2}.yaml".format(self.chapterType,self.chapterId,get_setting('Language')))
        #章节标题显示
        self.infoToDisplayDuringLoading = LoadingTitle(self.window_x,self.window_y,self.battleModeUiTxt["numChapter"],self.chapterId,DataTmp["title"],DataTmp["description"])
        self.battleMode_info = DataTmp["battle_info"]
        self.dialog_during_battle = DataTmp["dialog_during_battle"]
        #正在加载的gif动态图标
        nowLoadingIcon = loadRealGif("Assets/image/UI/sv98_walking.gif",(self.window_x*0.7,self.window_y*0.83),(self.window_x*0.003*15,self.window_x*0.003*21))
        #渐入效果
        for i in range(1,255,2):
            self.infoToDisplayDuringLoading.display(screen,i)
            display.flip(True)
        #开始加载地图场景
        self.infoToDisplayDuringLoading.display(screen)
        now_loading = self.FONT.render(loading_info["now_loading_map"],get_fontMode(),(255,255,255))
        drawImg(now_loading,(self.window_x*0.75,self.window_y*0.9),screen)
        nowLoadingIcon.draw(screen)
        display.flip(True)
        #读取并初始化章节信息
        DataTmp = loadConfig("Data/{0}/chapter{1}_map.yaml".format(self.chapterType,self.chapterId))
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
            if "initial" not in self.dialogInfo or self.dialogInfo["initial"] == None:
                self.dialogKey = None
            else:
                self.dialogKey = self.dialogInfo["initial"]
            self.dialogData = None
        self.bg_music = DataTmp["background_music"] 
        #初始化天气和环境的音效 -- 频道1
        self.environment_sound = SoundManagement(1)
        self.weatherController = None
        if DataTmp["weather"] != None:
            self.environment_sound.add("Assets/sound/environment/{}.ogg".format(DataTmp["weather"]))
            self.environment_sound.set_volume(get_setting("Sound","sound_environment")/100.0)
            self.weatherController = WeatherSystem(DataTmp["weather"],self.window_x,self.window_y)
        #检测self.zoomIn参数是否越界
        if self.zoomIn < 200:
            self.zoomIn = 200
        elif self.zoomIn > 400:
            self.zoomIn = 400
        self.zoomIntoBe = self.zoomIn
        #加载角色信息
        characterDataThread.start()
        while characterDataThread.isAlive():
            self.infoToDisplayDuringLoading.display(screen)
            now_loading = self.FONT.render(loading_info["now_loading_characters"]+"({}/{})".format(characterDataThread.currentID,characterDataThread.totalNum),get_fontMode(),(255,255,255))
            drawImg(now_loading,(self.window_x*0.75,self.window_y*0.9),screen)
            nowLoadingIcon.draw(screen)
            display.flip(True)
        if self.loadFromSave == False:
            #获取角色数据
            self.characters_data,self.sangvisFerris_data = characterDataThread.getResult()
            #初始化地图模块
            self._create_map(DataTmp)
        else:
            #因为地图模块已被加载，只需加载图片即可
            self.MAP.load_env_img()
        del characterDataThread
        #计算光亮区域 并初始化地图
        self.MAP.calculate_darkness(self.characters_data)
        #开始加载关卡设定
        self.infoToDisplayDuringLoading.display(screen)
        now_loading = self.FONT.render(loading_info["now_loading_level"],get_fontMode(),findColorRGBA("white"))
        drawImg(now_loading,(self.window_x*0.75,self.window_y*0.9),screen)
        nowLoadingIcon.draw(screen)
        display.flip(True)
        #加载UI:
        #加载结束回合的图片
        self.end_round_txt = self.FONT.render(get_lang("Battle_UI","endRound"),get_fontMode(),findColorRGBA("white"))
        self.end_round_button = loadImage("Assets/image/UI/end_round_button.png",(self.window_x*0.8,self.window_y*0.7),self.end_round_txt.get_width()*2,self.end_round_txt.get_height()*2.5)
        #加载子弹图片
        #bullet_img = loadImg("Assets/image/UI/bullet.png", perBlockWidth/6, self.MAP.perBlockHeight/12)
        #加载血条,各色方块等UI图片 size:perBlockWidth, self.MAP.perBlockHeight/5
        self.original_UI_img = {
            "hp_empty" : loadImg("Assets/image/UI/hp_empty.png"),
            "hp_red" : loadImg("Assets/image/UI/hp_red.png"),
            "hp_green" : loadImg("Assets/image/UI/hp_green.png"),
            "action_point_blue" : loadImg("Assets/image/UI/action_point.png"),
            "bullets_number_brown" : loadImg("Assets/image/UI/bullets_number.png"),
            "green" : loadImg("Assets/image/UI/range/green.png"),
            "red" : loadImg("Assets/image/UI/range/red.png"),
            "yellow": loadImg("Assets/image/UI/range/yellow.png"),
            "blue": loadImg("Assets/image/UI/range/blue.png"),
            "orange": loadImg("Assets/image/UI/range/orange.png"),
            "eye_orange": loadImg("Assets/image/UI/eye_orange.png"),
            "eye_red": loadImg("Assets/image/UI/eye_red.png"),
            "supplyBoard":loadImage("Assets/image/UI/score.png",((self.window_x-self.window_x/3)/2,-self.window_y/12),self.window_x/3,self.window_y/12),
        }
        #UI - 变形后
        self.UI_img = {
            "green" : resizeImg(self.original_UI_img["green"], (self.MAP.perBlockWidth*0.8, None)),
            "red" : resizeImg(self.original_UI_img["red"], (self.MAP.perBlockWidth*0.8, None)),
            "yellow" : resizeImg(self.original_UI_img["yellow"], (self.MAP.perBlockWidth*0.8, None)),
            "blue" : resizeImg(self.original_UI_img["blue"], (self.MAP.perBlockWidth*0.8, None)),
            "orange": resizeImg(self.original_UI_img["orange"], (self.MAP.perBlockWidth*0.8, None))
        }
        #角色信息UI管理
        self.characterInfoBoardUI = CharacterInfoBoard(self.window_x,self.window_y)
        #加载对话框图片
        self.dialoguebox_up = DialogBox("Assets/image/UI/dialoguebox.png",self.window_x*0.3,self.window_y*0.15,self.window_x,self.window_y/2-self.window_y*0.35,self.FONTSIZE)
        self.dialoguebox_up.flip()
        self.dialoguebox_down = DialogBox("Assets/image/UI/dialoguebox.png",self.window_x*0.3,self.window_y*0.15,-self.window_x*0.3,self.window_y/2+self.window_y*0.2,self.FONTSIZE)
        #-----加载音效-----
        #行走的音效 -- 频道0
        self.footstep_sounds = SoundManagement(0)
        for walkingSoundPath in glob.glob(r'Assets/sound/snow/*.wav'):
            self.footstep_sounds.add(walkingSoundPath)
        self.footstep_sounds.set_volume(get_setting("Sound","sound_effects")/100)
        #攻击的音效 -- 频道2
        self.attackingSounds = AttackingSoundManager(get_setting("Sound","sound_effects"),2)
        #切换回合时的UI
        self.RoundSwitchUI = RoundSwitch(self.window_x,self.window_y,self.battleModeUiTxt)
        #关卡背景介绍信息文字
        for i in range(len(self.battleMode_info)):
            self.battleMode_info[i] = self.FONT.render(self.battleMode_info[i],get_fontMode(),(255,255,255))
        #显示章节信息
        for a in range(0,250,2):
            self.infoToDisplayDuringLoading.display(screen)
            for i in range(len(self.battleMode_info)):
                self.battleMode_info[i].set_alpha(a)
                drawImg(self.battleMode_info[i],(self.window_x/20,self.window_y*0.75+self.battleMode_info[i].get_height()*1.2*i),screen)
                if i == 1:
                    temp_secode = self.FONT.render(time.strftime(":%S", time.localtime()),get_fontMode(),(255,255,255))
                    temp_secode.set_alpha(a)
                    drawImg(temp_secode,(self.window_x/20+self.battleMode_info[i].get_width(),self.window_y*0.75+self.battleMode_info[i].get_height()*1.2),screen)
            display.flip(True)
    #把战斗系统的画面画到screen上
    def display(self,screen):
        #更新输入事件
        self._update_event()
        #环境声音-频道1
        self.environment_sound.play()
        # 游戏主循环
        if self.battleMode:
            self.__play_battle(screen)
        #在战斗状态
        else:
            self.__play_dialog(screen)
        #渐变效果：一次性的
        if self.txt_alpha == None:
            self.txt_alpha = 250
        if self.txt_alpha > 0:
            self.infoToDisplayDuringLoading.black_bg.set_alpha(self.txt_alpha)
            self.infoToDisplayDuringLoading.display(screen,self.txt_alpha)
            for i in range(len(self.battleMode_info)):
                self.battleMode_info[i].set_alpha(self.txt_alpha)
                drawImg(self.battleMode_info[i],(self.window_x/20,self.window_y*0.75+self.battleMode_info[i].get_height()*1.2*i),screen)
                if i == 1:
                    temp_secode = self.FONT.render(time.strftime(":%S", time.localtime()),get_fontMode(),(255,255,255))
                    temp_secode.set_alpha(self.txt_alpha)
                    drawImg(temp_secode,(self.window_x/20+self.battleMode_info[i].get_width(),self.window_y*0.75+self.battleMode_info[i].get_height()*1.2),screen)
            self.txt_alpha -= 5
        #刷新画面
        display.flip()
    #对话模块
    def __play_dialog(self,screen):
        #画出地图
        self.MAP.display_map(screen)
        #角色动画
        for every_chara in self.characters_data:
            self.characters_data[every_chara].draw(screen,self.MAP)
        for enemies in self.sangvisFerris_data:
            if self.MAP.inLightArea(self.sangvisFerris_data[enemies]):
                self.sangvisFerris_data[enemies].draw(screen,self.MAP)
        #展示设施
        self.MAP.display_ornamentation(screen,self.characters_data,self.sangvisFerris_data)
        #加载雪花
        self._display_weather(screen)
        #如果战斗有对话
        if self.dialogKey != None:
            #设定初始化
            if self.dialogData == None:
                self.dialogData = {
                    "dialogId": 0,
                    "charactersPaths": None,
                    "secondsAlreadyIdle":0,
                    "secondsToIdle":None
                }
            #对话系统总循环
            if self.dialogData["dialogId"] < len(self.dialog_during_battle[self.dialogKey]):
                currentDialog = self.dialog_during_battle[self.dialogKey][self.dialogData["dialogId"]]
                #如果操作是移动
                if "move" in currentDialog and currentDialog["move"] != None:
                    #为所有角色设置路径
                    if self.dialog_ifPathSet == False:
                        for key,pos in currentDialog["move"].items():
                            if key in self.characters_data:
                                routeTmp = self.MAP.findPath(self.characters_data[key],pos,self.characters_data,self.sangvisFerris_data)
                                if len(routeTmp)>0:
                                    self.characters_data[key].move_follow(routeTmp)
                                else:
                                    raise Exception('ZeroEngine-Error: Character {} cannot find a valid path!'.format(key))
                            elif key in self.sangvisFerris_data:
                                routeTmp = self.MAP.findPath(self.sangvisFerris_data[key],pos,self.sangvisFerris_data,self.characters_data)
                                if len(routeTmp)>0:
                                    self.sangvisFerris_data[key].move_follow(routeTmp)
                                else:
                                    raise Exception('ZeroEngine-Error: Character {} cannot find a valid path!'.format(key))
                            else:
                                raise Exception('ZeroEngine-Error: Cannot find character {}!'.format(key))
                        self.dialog_ifPathSet = True
                    #播放脚步声
                    self.footstep_sounds.play()
                    #是否所有角色都已经到达对应点
                    allGetToTargetPos = True
                    #是否需要重新渲染地图
                    reProcessMap = False
                    for key in currentDialog["move"]:
                        if key in self.characters_data:
                            if self.characters_data[key].is_idle() == False:
                                allGetToTargetPos = False
                            if self.characters_data[key].needUpdateMap():
                                reProcessMap = True
                        elif key in self.sangvisFerris_data and self.sangvisFerris_data[key].is_idle() == False:
                            allGetToTargetPos = False
                        else:
                            raise Exception('ZeroEngine-Error: Cannot find character {}!'.format(key))
                    if reProcessMap:
                        self.MAP.calculate_darkness(self.characters_data)
                    if allGetToTargetPos:
                        #脚步停止
                        self.footstep_sounds.stop()
                        self.dialogData["dialogId"] += 1
                        self.dialog_ifPathSet = False
                #改变方向
                elif "direction" in currentDialog and currentDialog["direction"] != None:
                    for key,value in currentDialog["direction"].items():
                        if key in self.characters_data:
                            self.characters_data[key].setFlip(value)
                        elif key in self.sangvisFerris_data:
                            self.sangvisFerris_data[key].setFlip(value)
                        else:
                            raise Exception('ZeroEngine-Error: Cannot find character {}!'.format(key))
                    self.dialogData["dialogId"] += 1
                #改变动作（一次性）
                elif "action" in currentDialog and currentDialog["action"] != None:
                    for key,action in currentDialog["action"].items():
                        if key in self.characters_data:
                            self.characters_data[key].set_action(action,False)
                        elif key in self.sangvisFerris_data:
                            self.sangvisFerris_data[key].set_action(action,False)
                    self.dialogData["dialogId"] += 1 
                #改变动作（长期）
                elif "actionLoop" in currentDialog and currentDialog["actionLoop"] != None:
                    for key,action in currentDialog["actionLoop"].items():
                        if key in self.characters_data:
                            self.characters_data[key].set_action(action)
                        elif key in self.sangvisFerris_data:
                            self.sangvisFerris_data[key].set_action(action)
                    self.dialogData["dialogId"] += 1
                #开始对话
                elif "dialoguebox_up" in currentDialog or "dialoguebox_down" in currentDialog:
                    #上方对话框
                    if currentDialog["dialoguebox_up"] != None:
                        #对话框的移动
                        if self.dialoguebox_up.x > self.window_x/2+self.dialoguebox_up.get_width()*0.4:
                            self.dialoguebox_up.x -= self.dialoguebox_up.get_width()*0.134
                        elif self.dialoguebox_up.updated == False:
                            currentTmp = currentDialog["dialoguebox_up"]
                            self.dialoguebox_up.update(currentTmp["content"],currentTmp["speaker"],currentTmp["speaker_icon"])
                            del currentTmp
                        #对话框图片
                        self.dialoguebox_up.display(screen,self.characterInfoBoardUI)
                    #下方对话框
                    if currentDialog["dialoguebox_down"] != None:
                        #对话框的移动
                        if self.dialoguebox_down.x < self.window_x/2-self.dialoguebox_down.get_width()*1.4:
                            self.dialoguebox_down.x += self.dialoguebox_down.get_width()*0.134
                        elif self.dialoguebox_down.updated == False:
                            currentTmp = currentDialog["dialoguebox_down"]
                            self.dialoguebox_down.update(currentTmp["content"],currentTmp["speaker"],currentTmp["speaker_icon"])
                            del currentTmp
                        #对话框图片
                        self.dialoguebox_down.display(screen,self.characterInfoBoardUI)
                #闲置一定时间（秒）
                elif "idle" in currentDialog and currentDialog["idle"] != None:
                    if self.dialogData["secondsToIdle"] == None:
                        self.dialogData["secondsToIdle"] = currentDialog["idle"]*display.fps
                    else:
                        if self.dialogData["secondsAlreadyIdle"] < self.dialogData["secondsToIdle"]:
                            self.dialogData["secondsAlreadyIdle"] += 1
                        else:
                            self.dialogData["dialogId"] += 1
                            self.dialogData["secondsAlreadyIdle"] = 0
                            self.dialogData["secondsToIdle"] = None
                #调整窗口位置
                elif "changePos" in currentDialog and currentDialog["changePos"] != None:
                    if self.screen_to_move_x == None and "x" in currentDialog["changePos"]:
                        self.screen_to_move_x = currentDialog["changePos"]["x"]
                    if self.screen_to_move_y == None and "y" in currentDialog["changePos"]:
                        self.screen_to_move_y = currentDialog["changePos"]["y"]
                    self._move_screen()
                    if self.screen_to_move_x == 0 and self.screen_to_move_y == 0 or self.screen_to_move_x == None and self.screen_to_move_y == None:
                        self.screen_to_move_x = None
                        self.screen_to_move_y = None
                        self.dialogData["dialogId"] += 1
                #玩家输入按键判定
                for event in self._get_event():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            pause_menu.display(screen)
                            self.__save_data()
                            if pause_menu.ifBackToMainMenu == True:
                                unloadBackgroundMusic()
                                self.isPlaying = False
                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 or event.type == pygame.JOYBUTTONDOWN and controller.joystick.get_button(0) == 1:
                        if "dialoguebox_up" in currentDialog or "dialoguebox_down" in currentDialog:
                            self.dialogData["dialogId"] += 1
                        if self.dialogData["dialogId"] < len(self.dialog_during_battle[self.dialogKey]):
                            currentDialog = self.dialog_during_battle[self.dialogKey][self.dialogData["dialogId"]]
                            lastDialog = self.dialog_during_battle[self.dialogKey][self.dialogData["dialogId"]-1] if self.dialogData["dialogId"] > 0 else {}
                            if "dialoguebox_up" in currentDialog:
                                #检测上方对话框
                                if currentDialog["dialoguebox_up"] == None or "dialoguebox_up" not in lastDialog or lastDialog["dialoguebox_up"] == None or currentDialog["dialoguebox_up"]["speaker"] != lastDialog["dialoguebox_up"]["speaker"]:
                                    self.dialoguebox_up.reset()
                                elif currentDialog["dialoguebox_up"]["content"] != lastDialog["dialoguebox_up"]["content"]:
                                    self.dialoguebox_up.updated = False
                            else:
                                self.dialoguebox_up.reset()
                            if "dialoguebox_down" in currentDialog:
                                #检测下方对话框    
                                if currentDialog["dialoguebox_down"] == None or "dialoguebox_down" not in lastDialog or lastDialog["dialoguebox_down"] == None or currentDialog["dialoguebox_down"]["speaker"] != lastDialog["dialoguebox_down"]["speaker"]:
                                    self.dialoguebox_down.reset()
                                elif currentDialog["dialoguebox_down"]["content"] != lastDialog["dialoguebox_down"]["content"]:
                                    self.dialoguebox_down.updated = False
                            else:
                                self.dialoguebox_down.reset()
                        else:
                            self.dialoguebox_up.reset()
                            self.dialoguebox_down.reset()
                        break
            else:
                self.dialogData = None
                self.dialogKey = None
                self.battleMode = True
        #如果战斗前无·对话
        elif self.dialogKey == None:
            #角色UI
            for every_chara in self.characters_data:
                self.characters_data[every_chara].drawUI(screen,self.original_UI_img,self.MAP)
            for enemies in self.sangvisFerris_data:
                if self.MAP.inLightArea(self.sangvisFerris_data[enemies]):
                    self.sangvisFerris_data[enemies].drawUI(screen,self.original_UI_img,self.MAP)
            if self.txt_alpha == 0:
                self.battleMode = True
    #战斗模块
    def __play_battle(self,screen):
        right_click = False
        show_pause_menu = False
        #获取鼠标坐标
        mouse_x,mouse_y = controller.get_pos()
        #攻击范围
        attacking_range = None
        skill_range = None
        friendsCanSave = []
        thingsCanReact = []
        for event in self._get_event():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and self.characterGetClick == None:
                    show_pause_menu = True
                if event.key == pygame.K_ESCAPE and self.isWaiting == True:
                    self.NotDrawRangeBlocks = True
                    self.characterGetClick = None
                    self.action_choice = None
                    attacking_range = None
                    skill_range = None
                    self.areaDrawColorBlock = {"green":[],"red":[],"yellow":[],"blue":[],"orange":[]}
                self._check_key_down(event)
                if event.key == pygame.K_m:
                    display.quit()
            elif event.type == pygame.KEYUP:
                self._check_key_up(event)
            #鼠标点击
            elif event.type == pygame.MOUSEBUTTONDOWN:
                #右键
                if event.button == 1 or event.type == pygame.JOYBUTTONDOWN and controller.joystick.get_button(0) == 1:
                    right_click = True
                #上下滚轮-放大和缩小地图
                elif event.button == 4 and self.zoomIntoBe < 400:
                    self.zoomIntoBe += 20
                elif event.button == 5 and self.zoomIntoBe > 200:
                    self.zoomIntoBe -= 20
        #其他移动的检查
        self._check_right_click_move(mouse_x,mouse_y)
        self._check_jostick_events()

        #根据self.zoomIntoBe调整self.zoomIn大小
        if self.zoomIntoBe != self.zoomIn:
            if self.zoomIntoBe < self.zoomIn:
                self.zoomIn -= 5
            elif self.zoomIntoBe > self.zoomIn:
                self.zoomIn += 5
            self.MAP.changePerBlockSize(self.window_x/self.MAP.column*self.zoomIn/100,self.window_y/self.MAP.row*self.zoomIn/100,self.window_x,self.window_y)
            #根据perBlockWidth和perBlockHeight重新加载对应尺寸的UI
            for key in self.UI_img:
                self.UI_img[key] = resizeImg(self.original_UI_img[key], (self.MAP.perBlockWidth*0.8, None))
            self.selectMenuUI.allButton = None
        else:
            self.zoomIn = self.zoomIntoBe
        #画出地图
        self._display_map(screen)
        #画出用彩色方块表示的范围
        for area in self.areaDrawColorBlock:
            for position in self.areaDrawColorBlock[area]:
                xTemp,yTemp = self.MAP.calPosInMap(position[0],position[1])
                drawImg(self.UI_img[area],(xTemp+self.MAP.perBlockWidth*0.1,yTemp),screen)

        #玩家回合
        if self.whose_round == "player":
            if right_click == True:
                block_get_click = self.MAP.calBlockInMap(mouse_x,mouse_y)
                #如果点击了回合结束的按钮
                if ifHover(self.end_round_button) and self.isWaiting == True:
                    self.whose_round = "playerToSangvisFerris"
                    self.characterGetClick = None
                    self.NotDrawRangeBlocks = True
                    attacking_range = None
                    skill_range = None
                    self.areaDrawColorBlock = {"green":[],"red":[],"yellow":[],"blue":[],"orange":[]}
                #是否在显示移动范围后点击了且点击区域在移动范围内
                elif len(self.the_route) != 0 and block_get_click != None and (block_get_click["x"], block_get_click["y"]) in self.the_route and self.NotDrawRangeBlocks==False:
                    self.isWaiting = False
                    self.NotDrawRangeBlocks = True
                    self.characters_data[self.characterGetClick].reduce_action_point(len(self.the_route)*2)
                    self.characters_data[self.characterGetClick].move_follow(self.the_route)
                    self.areaDrawColorBlock = {"green":[],"red":[],"yellow":[],"blue":[],"orange":[]}
                elif self.NotDrawRangeBlocks == "SelectMenu" and self.buttonGetHover == "attack":
                    if self.characters_data[self.characterGetClick].current_bullets > 0 and self.characters_data[self.characterGetClick].have_enough_action_point(5):
                        self.action_choice = "attack"
                        self.NotDrawRangeBlocks = False
                    elif self.characters_data[self.characterGetClick].current_bullets <= 0:
                        self.warnings_to_display.add("magazine_is_empty")
                    elif not self.characters_data[self.characterGetClick].have_enough_action_point(5):
                        self.warnings_to_display.add("no_enough_ap_to_attack")
                elif self.NotDrawRangeBlocks == "SelectMenu" and self.buttonGetHover == "move":
                    if self.characters_data[self.characterGetClick].have_enough_action_point(2):
                        self.action_choice = "move"
                        self.NotDrawRangeBlocks = False
                    else:
                        self.warnings_to_display.add("no_enough_ap_to_move")
                elif self.NotDrawRangeBlocks == "SelectMenu" and self.buttonGetHover == "skill":
                    if self.characters_data[self.characterGetClick].have_enough_action_point(8):
                        self.action_choice = "skill"
                        self.NotDrawRangeBlocks = False
                    else:
                        self.warnings_to_display.add("no_enough_ap_to_use_skill")
                elif self.NotDrawRangeBlocks == "SelectMenu" and self.buttonGetHover == "reload":
                    if self.characters_data[self.characterGetClick].have_enough_action_point(5) and self.characters_data[self.characterGetClick].bullets_carried > 0:
                        self.action_choice = "reload"
                        self.NotDrawRangeBlocks = False
                    elif self.characters_data[self.characterGetClick].bullets_carried <= 0:
                        self.warnings_to_display.add("no_bullets_left")
                    elif not self.characters_data[self.characterGetClick].have_enough_action_point(5):
                        self.warnings_to_display.add("no_enough_ap_to_reload")
                elif self.NotDrawRangeBlocks == "SelectMenu" and self.buttonGetHover == "rescue":
                    if self.characters_data[self.characterGetClick].have_enough_action_point(8):
                        self.action_choice = "rescue"
                        self.NotDrawRangeBlocks = False
                    else:
                        self.warnings_to_display.add("no_enough_ap_to_rescue")
                elif self.NotDrawRangeBlocks == "SelectMenu" and self.buttonGetHover == "interact":
                    if self.characters_data[self.characterGetClick].have_enough_action_point(2):
                        self.action_choice = "interact"
                        self.NotDrawRangeBlocks = False
                    else:
                        self.warnings_to_display.add("no_enough_ap_to_interact")
                #攻击判定
                elif self.action_choice == "attack" and self.NotDrawRangeBlocks == False and self.characterGetClick != None and len(self.enemiesGetAttack)>0:
                    self.characters_data[self.characterGetClick].reduce_action_point(5)
                    self.characters_data[self.characterGetClick].noticed()
                    self.characters_data[self.characterGetClick].set_action("attack",False)
                    self.isWaiting = False
                    self.NotDrawRangeBlocks = True
                    attacking_range = None
                    self.areaDrawColorBlock = {"green":[],"red":[],"yellow":[],"blue":[],"orange":[]}
                elif self.action_choice == "skill" and self.NotDrawRangeBlocks == False and self.characterGetClick != None and self.skill_target != None:
                    if self.skill_target in self.characters_data:
                        self.characters_data[self.characterGetClick].setFlipBasedPos(self.characters_data[self.skill_target])
                        
                    elif self.skill_target in self.sangvisFerris_data:
                        self.characters_data[self.characterGetClick].noticed()
                        self.characters_data[self.characterGetClick].setFlipBasedPos(self.sangvisFerris_data[self.skill_target])
                    self.characters_data[self.characterGetClick].reduce_action_point(8)
                    self.characters_data[self.characterGetClick].playSound("skill")
                    self.characters_data[self.characterGetClick].set_action("skill",False)
                    self.isWaiting = False
                    self.NotDrawRangeBlocks = True
                    skill_range = None
                    self.areaDrawColorBlock = {"green":[],"red":[],"yellow":[],"blue":[],"orange":[]}
                elif self.action_choice == "rescue" and self.NotDrawRangeBlocks == False and self.characterGetClick != None and self.friendGetHelp != None:
                    self.characters_data[self.characterGetClick].reduce_action_point(8)
                    self.characters_data[self.characterGetClick].noticed()
                    self.characters_data[self.friendGetHelp].heal(1)
                    self.characterGetClick = None
                    self.action_choice = None
                    self.isWaiting = True
                    self.NotDrawRangeBlocks = True
                    attacking_range = None
                    self.areaDrawColorBlock = {"green":[],"red":[],"yellow":[],"blue":[],"orange":[]}
                elif self.action_choice == "interact" and self.NotDrawRangeBlocks == False and self.characterGetClick != None and self.ornamentationGetClick != None:
                    self.characters_data[self.characterGetClick].reduce_action_point(2)
                    self.MAP.ornamentationData[self.ornamentationGetClick].triggered = not self.MAP.ornamentationData[self.ornamentationGetClick].triggered
                    self.MAP.calculate_darkness(self.characters_data)
                    self.characterGetClick = None
                    self.action_choice = None
                    self.isWaiting = True
                    self.NotDrawRangeBlocks = True
                    attacking_range = None
                    self.areaDrawColorBlock = {"green":[],"red":[],"yellow":[],"blue":[],"orange":[]}
                #判断是否有被点击的角色
                elif block_get_click != None:
                    for key in self.characters_data:
                        if self.characters_data[key].on_pos(block_get_click) and self.isWaiting == True and self.characters_data[key].dying == False and self.NotDrawRangeBlocks != False:
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
                            for i in range(len(self.MAP.ornamentationData)):
                                if self.MAP.ornamentationData[i].type == "campfire" and self.characters_data[key].near(self.MAP.ornamentationData[i]):
                                    thingsCanReact.append(i)
                            self.NotDrawRangeBlocks = "SelectMenu"
                            break
            #选择菜单的判定，显示功能在角色动画之后
            if self.NotDrawRangeBlocks == "SelectMenu":
                #移动画面以使得被点击的角色可以被更好的操作
                tempX,tempY = self.MAP.calPosInMap(self.characters_data[self.characterGetClick].x,self.characters_data[self.characterGetClick].y)
                if self.screen_to_move_x == None:
                    if tempX < self.window_x*0.2 and self.MAP.getPos_x()<=0:
                        self.screen_to_move_x = self.window_x*0.2-tempX
                    elif tempX > self.window_x*0.8 and self.MAP.getPos_x()>=self.MAP.column*self.MAP.perBlockWidth*-1:
                        self.screen_to_move_x = self.window_x*0.8-tempX
                if self.screen_to_move_y == None:
                    if tempY < self.window_y*0.2 and self.MAP.getPos_y()<=0:
                        self.screen_to_move_y = self.window_y*0.2-tempY
                    elif tempY > self.window_y*0.8 and self.MAP.getPos_y()>=self.MAP.row*self.MAP.perBlockHeight*-1:
                        self.screen_to_move_y = self.window_y*0.8-tempY
            #显示攻击/移动/技能范围
            if self.NotDrawRangeBlocks == False and self.characterGetClick != None:
                block_get_click = self.MAP.calBlockInMap(mouse_x,mouse_y)
                #显示移动范围
                if self.action_choice == "move":
                    self.areaDrawColorBlock["green"] = []
                    if block_get_click != None:
                        #根据行动值计算最远可以移动的距离
                        max_blocks_can_move = int(self.characters_data[self.characterGetClick].get_action_point()/2)
                        if 0<abs(block_get_click["x"]-self.characters_data[self.characterGetClick].x)+abs(block_get_click["y"]-self.characters_data[self.characterGetClick].y)<=max_blocks_can_move:
                            self.the_route = self.MAP.findPath(self.characters_data[self.characterGetClick],block_get_click,self.characters_data,self.sangvisFerris_data,max_blocks_can_move)
                            if len(self.the_route)>0:
                                #显示路径
                                self.areaDrawColorBlock["green"] = self.the_route
                                xTemp,yTemp = self.MAP.calPosInMap(self.the_route[-1][0],self.the_route[-1][1])
                                screen.blit(self.FONT.render(str(len(self.the_route)*2),get_fontMode(),(255,255,255)),(xTemp+self.FONTSIZE*2,yTemp+self.FONTSIZE))
                                self.characters_data[self.characterGetClick].draw_custom("move",(xTemp,yTemp),screen,self.MAP)
                #显示攻击范围        
                elif self.action_choice == "attack":
                    if attacking_range == None:
                        attacking_range = self.characters_data[self.characterGetClick].getAttackRange(self.MAP)
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
                                                if self.MAP.ifBlockCanPassThrough({"x":x,"y":y}):
                                                    the_attacking_range_area.append([x,y])
                                        else:
                                            for x in range(block_get_click["x"]-self.characters_data[self.characterGetClick].attack_range+(y-block_get_click["y"])+1,block_get_click["x"]+self.characters_data[self.characterGetClick].attack_range-(y-block_get_click["y"])):
                                                if self.MAP.ifBlockCanPassThrough({"x":x,"y":y}):
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
                        self.action_choice = None
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
                                        if self.MAP.row>y>=0 and self.MAP.column>x>=0:
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
                                        elif self.MAP.row>y>=0 and self.MAP.column>x>=0:
                                            if "far" in self.characters_data[self.characterGetClick].skill_effective_range and self.characters_data[self.characterGetClick].skill_effective_range["far"] != None and self.characters_data[self.characterGetClick].skill_effective_range["far"][0] <= abs(x-self.characters_data[self.characterGetClick].x)+abs(y-self.characters_data[self.characterGetClick].y) <= self.characters_data[self.characterGetClick].skill_effective_range["far"][1]:
                                                skill_range["far"].append([x,y])
                                            elif "middle" in self.characters_data[self.characterGetClick].skill_effective_range and self.characters_data[self.characterGetClick].skill_effective_range["middle"] != None and self.characters_data[self.characterGetClick].skill_effective_range["middle"][0] <= abs(x-self.characters_data[self.characterGetClick].x)+abs(y-self.characters_data[self.characterGetClick].y) <= self.characters_data[self.characterGetClick].skill_effective_range["middle"][1]:
                                                skill_range["middle"].append([x,y])
                                            elif "near" in self.characters_data[self.characterGetClick].skill_effective_range and self.characters_data[self.characterGetClick].skill_effective_range["near"] != None and self.characters_data[self.characterGetClick].skill_effective_range["near"][0] <= abs(x-self.characters_data[self.characterGetClick].x)+abs(y-self.characters_data[self.characterGetClick].y) <= self.characters_data[self.characterGetClick].skill_effective_range["near"][1]:
                                                skill_range["near"].append([x,y])
                        self.areaDrawColorBlock["green"] = skill_range["near"]
                        self.areaDrawColorBlock["blue"] = skill_range["middle"]
                        self.areaDrawColorBlock["yellow"] = skill_range["far"]
                        block_get_click = self.MAP.calBlockInMap(mouse_x,mouse_y)
                        if block_get_click != None:
                            the_skill_cover_area = []
                            for area in skill_range:
                                if [block_get_click["x"],block_get_click["y"]] in skill_range[area]:
                                    for y in range(block_get_click["y"]-self.characters_data[self.characterGetClick].skill_cover_range,block_get_click["y"]+self.characters_data[self.characterGetClick].skill_cover_range):
                                        if y < block_get_click["y"]:
                                            for x in range(block_get_click["x"]-self.characters_data[self.characterGetClick].skill_cover_range-(y-block_get_click["y"])+1,block_get_click["x"]+self.characters_data[self.characterGetClick].skill_cover_range+(y-block_get_click["y"])):
                                                if self.MAP.row>y>=0 and self.MAP.column>x>=0 and self.MAP.ifBlockCanPassThrough({"x":x,"y":y}):
                                                    the_skill_cover_area.append([x,y])
                                        else:
                                            for x in range(block_get_click["x"]-self.characters_data[self.characterGetClick].skill_cover_range+(y-block_get_click["y"])+1,block_get_click["x"]+self.characters_data[self.characterGetClick].skill_cover_range-(y-block_get_click["y"])):
                                                if self.MAP.row>y>=0 and self.MAP.column>x>=0 and self.MAP.ifBlockCanPassThrough({"x":x,"y":y}):
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
                        #如果角色有换弹动画，则播放角色的换弹动画
                        if self.characters_data[self.characterGetClick].get_imgId("reload") != None:
                            self.characters_data[self.characterGetClick].set_action("reload",False)
                        #扣去对应的行动值
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
                        self.characterGetClick = None
                        self.action_choice = None
                        self.NotDrawRangeBlocks = True
                    #无需换弹
                    else:
                        self.warnings_to_display.add("magazine_is_full")
                        self.NotDrawRangeBlocks = "SelectMenu"
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
                        if block_get_click != None and block_get_click["x"] == self.MAP.ornamentationData[ornamentationId].x and block_get_click["y"] == self.MAP.ornamentationData[ornamentationId].y:
                            self.areaDrawColorBlock["orange"] = [(block_get_click["x"],block_get_click["y"])]
                            self.ornamentationGetClick = ornamentationId
                        else:
                            self.areaDrawColorBlock["green"].append((self.MAP.ornamentationData[ornamentationId].x,self.MAP.ornamentationData[ornamentationId].y))

            #当有角色被点击时
            if self.characterGetClick != None and self.isWaiting == False:
                #被点击的角色动画
                self.NotDrawRangeBlocks=True
                if self.action_choice == "move":
                    if not self.characters_data[self.characterGetClick].is_idle():
                        #播放脚步声
                        self.footstep_sounds.play()
                        #是否需要更新
                        if self.characters_data[self.characterGetClick].needUpdateMap():
                            for key in self.sangvisFerris_data:
                                if self.sangvisFerris_data[key].isInAttackRange(self.characters_data[self.characterGetClick],self.MAP):
                                    self.characters_data[self.characterGetClick].noticed()
                                    break
                            self.MAP.calculate_darkness(self.characters_data)
                    else:
                        self.footstep_sounds.stop()
                        #检测是不是站在补给上
                        for i in range(len(self.MAP.ornamentationData)-1,-1,-1):
                            if self.MAP.ornamentationData[i].type == "chest" and self.MAP.ornamentationData[i].get_pos() == self.characters_data[self.characterGetClick].get_pos():
                                self.original_UI_img["supplyBoard"].items = []
                                for key2,value2 in self.MAP.ornamentationData[i].items.items():
                                    if key2 == "bullet":
                                        self.characters_data[self.characterGetClick].bullets_carried += value2
                                        self.original_UI_img["supplyBoard"].items.append(self.FONT.render(self.battleModeUiTxt["getBullets"]+": "+str(value2),get_fontMode(),(255,255,255)))
                                    elif key2 == "hp":
                                        self.characters_data[self.characterGetClick].current_hp += value2
                                        self.original_UI_img["supplyBoard"].items.append(self.FONT.render(self.battleModeUiTxt["getHealth"]+": "+str(value2),get_fontMode(),(255,255,255)))
                                if len(self.original_UI_img["supplyBoard"].items)>0:
                                    self.original_UI_img["supplyBoard"].yTogo = 10
                                del self.MAP.ornamentationData[i]
                                break
                        keyTemp = str(self.characters_data[self.characterGetClick].x)+"-"+str(self.characters_data[self.characterGetClick].y) 
                        #检测是否角色有set的动画
                        self.isWaiting = True
                        self.characterGetClick = None
                        self.action_choice = None
                        if "move" in self.dialogInfo and keyTemp in self.dialogInfo["move"]:
                            self.dialogKey = self.dialogInfo["move"][keyTemp]
                            self.battleMode = False
                elif self.action_choice == "attack":
                    #根据敌我坐标判断是否需要反转角色
                    if self.characters_data[self.characterGetClick].get_imgId("attack") == 0:
                        block_get_click = self.MAP.calBlockInMap(mouse_x,mouse_y)
                        if block_get_click != None:
                            self.characters_data[self.characterGetClick].setFlipBasedPos(block_get_click)
                        self.characters_data[self.characterGetClick].playSound("attack")
                    #播放射击音效
                    elif self.characters_data[self.characterGetClick].get_imgId("attack") == 3:
                        self.attackingSounds.play(self.characters_data[self.characterGetClick].kind)
                    if self.characters_data[self.characterGetClick].get_imgId("attack") == self.characters_data[self.characterGetClick].get_imgNum("attack")-2:
                        for each_enemy in self.enemiesGetAttack:
                            if self.enemiesGetAttack[each_enemy] == "near" and random.randint(1,100) <= 95 or self.enemiesGetAttack[each_enemy] == "middle" and random.randint(1,100) <= 80 or self.enemiesGetAttack[each_enemy] == "far" and random.randint(1,100) <= 65:
                                the_damage = self.sangvisFerris_data[each_enemy].attackBy(self.characters_data[self.characterGetClick])
                                self.damage_do_to_characters[each_enemy] = self.FONT.render("-"+str(the_damage),get_fontMode(),findColorRGBA("red"))
                            else:
                                self.damage_do_to_characters[each_enemy] = self.FONT.render("Miss",get_fontMode(),findColorRGBA("red"))
                    elif self.characters_data[self.characterGetClick].get_imgId("attack") == self.characters_data[self.characterGetClick].get_imgNum("attack")-1:
                        self.characters_data[self.characterGetClick].current_bullets -= 1
                        self.isWaiting = True
                        self.characterGetClick = None
                        self.action_choice = None
                elif self.action_choice == "skill":
                    if self.characters_data[self.characterGetClick].get_imgId("skill") == self.characters_data[self.characterGetClick].get_imgNum("skill")-2:
                        self.damage_do_to_characters = skill(self.characterGetClick,None,None,self.sangvisFerris_data,self.characters_data,"react",self.skill_target,self.damage_do_to_characters)
                    elif self.characters_data[self.characterGetClick].get_imgId("skill") == self.characters_data[self.characterGetClick].get_imgNum("skill")-1:
                        self.MAP.calculate_darkness(self.characters_data)
                        self.isWaiting =True
                        self.characterGetClick = None
                        self.action_choice = None

        #敌方回合
        if self.whose_round == "sangvisFerris":
            self.enemy_in_control = self.sangvisFerris_name_list[self.enemies_in_control_id]
            if self.enemy_action == None:
                self.enemy_action = AI(self.enemy_in_control,self.MAP,self.characters_data,self.sangvisFerris_data,self.the_characters_detected_last_round)
                if self.enemy_action["action"] == "move" or self.enemy_action["action"] == "move&attack":
                    self.sangvisFerris_data[self.enemy_in_control].move_follow(self.enemy_action["route"])
                elif self.enemy_action["action"] == "attack":
                    self.sangvisFerris_data[self.enemy_in_control].set_action("attack")
                    self.sangvisFerris_data[self.enemy_in_control].setFlipBasedPos(self.characters_data[self.enemy_action["target"]])
                print(self.enemy_in_control+" choses "+self.enemy_action["action"])
            #根据选择调整动画
            if self.enemy_action["action"] == "move" or  self.enemy_action["action"] == "move&attack":
                if self.sangvisFerris_data[self.enemy_in_control].is_idle():
                    self.footstep_sounds.play()
                else:
                    self.footstep_sounds.stop()
                    if self.enemy_action["action"] == "move&attack":
                        self.enemy_action["action"] = "attack"
                        self.sangvisFerris_data[self.enemy_in_control].set_action("attack")
                        self.sangvisFerris_data[self.enemy_in_control].setFlipBasedPos(self.characters_data[self.enemy_action["target"]])
                    else:
                        self.enemy_action["action"] = "stay"
            elif self.enemy_action["action"] == "attack":
                if self.sangvisFerris_data[self.enemy_in_control].get_imgId("attack") == 3:
                    self.attackingSounds.play(self.sangvisFerris_data[self.enemy_in_control].kind)
                elif self.sangvisFerris_data[self.enemy_in_control].get_imgId("attack") == self.sangvisFerris_data[self.enemy_in_control].get_imgNum("attack")-1:
                    temp_value = random.randint(0,100)
                    if self.enemy_action["target_area"] == "near" and temp_value <= 95 or self.enemy_action["target_area"] == "middle" and temp_value <= 80 or self.enemy_action["target_area"] == "far" and temp_value <= 65:
                        the_damage = self.characters_data[self.enemy_action["target"]].attackBy(self.sangvisFerris_data[self.enemy_in_control],self.resultInfo)
                        self.MAP.calculate_darkness(self.characters_data)
                        self.damage_do_to_characters[self.enemy_action["target"]] = self.FONT.render("-"+str(the_damage),get_fontMode(),findColorRGBA("red"))
                    else:
                        self.damage_do_to_characters[self.enemy_action["target"]] = self.FONT.render("Miss",get_fontMode(),findColorRGBA("red"))
                    self.enemy_action["action"] = "stay"
            #最终的idle状态
            elif self.enemy_action["action"] == "stay":
                self.sangvisFerris_data[self.enemy_in_control].set_action()
                self.enemies_in_control_id +=1
                if self.enemies_in_control_id >= len(self.sangvisFerris_name_list):
                    self.whose_round = "sangvisFerrisToPlayer"
                    self.resultInfo["total_rounds"] += 1
                self.enemy_action = None
                self.enemy_in_control = None
            else:
                print("warning: not choice")

        """↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓角色动画展示区↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓"""
        rightClickCharacterAlphaDeduct = True
        for key,value in dicMerge(self.characters_data,self.sangvisFerris_data).items():
            #如果天亮的双方都可以看见/天黑，但是是友方角色/天黑，但是是敌方角色在可观测的范围内 -- 则画出角色
            if value.faction == "character" or value.faction == "sangvisFerri" and self.MAP.inLightArea(value):
                if self.NotDrawRangeBlocks == True and pygame.mouse.get_pressed()[2]:
                    block_get_click = self.MAP.calBlockInMap(mouse_x,mouse_y)
                    if block_get_click != None and block_get_click["x"] == value.x and block_get_click["y"]  == value.y:
                        rightClickCharacterAlphaDeduct = False
                        if self.rightClickCharacterAlpha == None:
                            self.rightClickCharacterAlpha = 0
                        if self.rightClickCharacterAlpha < 255:
                            self.rightClickCharacterAlpha += 17
                            self.UI_img["yellow"].set_alpha(self.rightClickCharacterAlpha)
                            self.UI_img["blue"].set_alpha(self.rightClickCharacterAlpha)
                            self.UI_img["green"].set_alpha(self.rightClickCharacterAlpha)
                        rangeCanAttack =  value.getAttackRange(self.MAP)
                        self.areaDrawColorBlock["yellow"] = rangeCanAttack["far"]
                        self.areaDrawColorBlock["blue"] =  rangeCanAttack["middle"]
                        self.areaDrawColorBlock["green"] = rangeCanAttack["near"]
                value.draw(screen,self.MAP)
            #是否有在播放死亡角色的动画（而不是倒地状态）
            if value.current_hp<=0 and key not in self.the_dead_one:
                if value.kind == "HOC" or value.faction == "sangvisFerri":
                    self.the_dead_one[key] = value.faction
            #伤害/治理数值显示
            if key in self.damage_do_to_characters:
                the_alpha_to_check = self.damage_do_to_characters[key].get_alpha()
                if the_alpha_to_check > 0:
                    xTemp,yTemp = self.MAP.calPosInMap(value.x,value.y)
                    xTemp+=self.MAP.perBlockWidth*0.05
                    yTemp-=self.MAP.perBlockWidth*0.05
                    displayInCenter(self.damage_do_to_characters[key],self.UI_img["green"],xTemp,yTemp,screen)
                    self.damage_do_to_characters[key].set_alpha(the_alpha_to_check-5)
                else:
                    del self.damage_do_to_characters[key]
        #移除死亡的角色
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
                            self.MAP.calculate_darkness(self.characters_data)
            for key in the_dead_one_remove:
                del self.the_dead_one[key]
        """↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑角色动画展示区↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑"""
        #调整范围方块的透明度
        if rightClickCharacterAlphaDeduct == True and self.rightClickCharacterAlpha != None:
            if self.rightClickCharacterAlpha>0:
                self.rightClickCharacterAlpha-=17
                self.UI_img["yellow"].set_alpha(self.rightClickCharacterAlpha)
                self.UI_img["blue"].set_alpha(self.rightClickCharacterAlpha)
                self.UI_img["green"].set_alpha(self.rightClickCharacterAlpha)
            elif self.rightClickCharacterAlpha == 0:
                self.areaDrawColorBlock["yellow"] = []
                self.areaDrawColorBlock["blue"] = []
                self.areaDrawColorBlock["green"] = []
                self.UI_img["yellow"].set_alpha(255)
                self.UI_img["blue"].set_alpha(255)
                self.UI_img["green"].set_alpha(255)
                self.rightClickCharacterAlpha = None
        #展示设施
        self.MAP.display_ornamentation(screen,self.characters_data,self.sangvisFerris_data)
        #展示所有角色Ui
        for every_chara in self.characters_data:
            self.characters_data[every_chara].drawUI(screen,self.original_UI_img,self.MAP)
        for enemies in self.sangvisFerris_data:
            if self.MAP.isPosInLightArea(int(self.sangvisFerris_data[enemies].x),int(self.sangvisFerris_data[enemies].y)):
                self.sangvisFerris_data[enemies].drawUI(screen,self.original_UI_img,self.MAP)

        #显示选择菜单
        if self.NotDrawRangeBlocks == "SelectMenu":
            #左下角的角色信息
            self.characterInfoBoardUI.display(screen,self.characters_data[self.characterGetClick],self.original_UI_img)
            #----选择菜单----
            self.buttonGetHover = self.selectMenuUI.display(screen,round(self.MAP.perBlockWidth/10),self.MAP.getBlockExactLocation(self.characters_data[self.characterGetClick].x,self.characters_data[self.characterGetClick].y),self.characters_data[self.characterGetClick].kind,friendsCanSave,thingsCanReact)
        #加载雪花
        self._display_weather(screen)
        
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
        if len(self.sangvisFerris_data) == 0 and self.whose_round != "result_win":
            self.characterGetClick = None
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
            screen.blit(self.end_round_txt,(self.end_round_button.x+self.end_round_button.width-self.end_round_txt.get_width()-self.FONTSIZE,self.end_round_button.y+(self.end_round_button.height-self.FONTSIZE)/2.3))

        #显示警告
        self.warnings_to_display.display(screen)

        #加载并播放音乐
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.load("Assets/music/"+self.bg_music)
            pygame.mixer.music.play()
            pygame.mixer.music.set_volume(get_setting("Sound","background_music")/100.0)

        #结束动画--胜利
        if self.whose_round == "result_win":
            if self.ResultBoardUI == None:
                self.resultInfo["total_time"] = time.localtime(time.time()-self.resultInfo["total_time"])
                self.ResultBoardUI = ResultBoard(self.resultInfo,self.window_x,self.window_y)
            for event in self._get_event():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.battleMode = False
                        self.isPlaying = False
            self.ResultBoardUI.display(screen)
        #结束动画--失败
        elif self.whose_round == "result_fail":
            pass
        #展示暂停菜单
        if show_pause_menu == True:
            pause_menu.display(screen)
            self.__save_data()
            if pause_menu.ifBackToMainMenu == True:
                unloadBackgroundMusic()
                self.isPlaying = False
