# cython: language_level=3
from Zero3.basic import *

#视觉小说系统模块
class DialogSystem:
    def __init__(self,chapter_name,screen,setting,part):
        #控制器输入组件
        self.InputController = GameController(screen)
        #获取屏幕的尺寸
        self.window_x,self.window_y = screen.get_size()
        #读取章节信息
        with open("Data/main_chapter/{0}_dialogs_{1}.yaml".format(chapter_name,setting['Language']), "r", encoding='utf-8') as f:
            self.dialog_content = yaml.load(f.read(),Loader=yaml.FullLoader)[part]
            if len(self.dialog_content)==0:
                raise Exception('Warning: The dialog has no content!')
        #选项栏
        self.optionBox = pygame.image.load(os.path.join("Assets/image/UI/option.png")).convert_alpha()
        #UI按钮
        self.ButtonsMananger = DialogButtons()
        #黑色帘幕
        black_bg_temp = pygame.Surface((self.window_x,self.window_y),flags=pygame.SRCALPHA).convert_alpha()
        pygame.draw.rect(black_bg_temp,(0,0,0),(0,0,self.window_x,self.window_y))
        self.black_bg = ImageSurface(black_bg_temp,0,0,self.window_x,self.window_y)
        #加载对话框系统
        self.dialogTxtSystem = DialogContent(self.window_x*0.015)
        #设定初始化
        self.dialogId = "head"
        #如果dialog_content没有头
        if self.dialogId not in self.dialog_content:
            raise Exception('Warning: The dialog must have a head!')
        else:
            self.dialogTxtSystem.updateContent(self.dialog_content[self.dialogId]["content"],self.dialog_content[self.dialogId]["narrator"])
        #玩家在对话时做出的选择
        self.dialog_options = {}
        #加载npc立绘系统并初始化
        self.npc_img_dic = NpcImageSystem()
        self.npc_img_dic.process(None,self.dialog_content[self.dialogId]["characters_img"])
        #加载对话的背景图片
        self.backgroundContent = DialogBackground(setting["Sound"]["background_music"])
        self.backgroundContent.update(self.dialog_content[self.dialogId]["background_img"],None)
        self.showHistory = False
        self.historySurface = None
    def display(self,screen):
        #背景
        self.backgroundContent.display(screen)
        self.npc_img_dic.display(screen)
        #按钮
        buttonEvent = self.ButtonsMananger.display(screen,self.InputController)
        #显示对话框和对应文字
        dialogPlayResult = self.dialogTxtSystem.display(screen)
        if dialogPlayResult == True:
            if self.dialog_content[self.dialogId]["next_dialog_id"] != None and self.dialog_content[self.dialogId]["next_dialog_id"][0] == "option":
                #显示选项
                optionBox_y_base = (self.window_y*3/4-(len(self.dialog_content[self.dialogId]["next_dialog_id"])-1)*2*self.window_x*0.03)/4
                for i in range(1,len(self.dialog_content[self.dialogId]["next_dialog_id"])):
                    option_txt = self.dialogTxtSystem.fontRender(self.dialog_content[self.dialogId]["next_dialog_id"][i][0],(255, 255, 255))
                    optionBox_scaled = pygame.transform.scale(self.optionBox,(int(option_txt.get_width()+self.window_x*0.05),int(self.window_x*0.05)))
                    optionBox_x = (self.window_x-optionBox_scaled.get_width())/2
                    optionBox_y = i*2*self.window_x*0.03+optionBox_y_base
                    displayWithInCenter(option_txt,optionBox_scaled,optionBox_x,optionBox_y,screen)
                    if pygame.mouse.get_pressed()[0] and self.InputController.ifHover(optionBox_scaled,(optionBox_x,optionBox_y)):
                        #下一个dialog的Id
                        theNextDialogId = self.dialog_content[self.dialogId]["next_dialog_id"][i][1]
                        #更新背景
                        self.backgroundContent.update(self.dialog_content[theNextDialogId]["background_img"],self.dialog_content[theNextDialogId]["background_music"])
                        #保存选取的选项
                        self.dialog_options[len(self.dialog_options)] = i
                        #重设立绘系统
                        self.npc_img_dic.process(self.dialog_content[self.dialogId]["characters_img"],self.dialog_content[theNextDialogId]["characters_img"])
                        #切换dialogId
                        self.dialogId = theNextDialogId
                        self.dialogTxtSystem.updateContent(self.dialog_content[self.dialogId]["content"],self.dialog_content[self.dialogId]["narrator"])
                        break
        #按键判定
        leftClick = False
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.JOYBUTTONDOWN:
                if pygame.mouse.get_pressed()[0] or self.InputController.joystick.get_button(0) == 1:
                    if buttonEvent == "hide" and self.showHistory != True:
                        self.dialogTxtSystem.hideSwitch()
                    #如果接来下没有文档了或者玩家按到了跳过按钮
                    elif buttonEvent == "skip" and self.showHistory != True:
                        #淡出
                        self.fadeOut(screen)
                        return True
                    elif buttonEvent == "auto" and self.showHistory != True:
                        self.ButtonsMananger.autoModeSwitch()
                        self.dialogTxtSystem.autoMode = self.ButtonsMananger.autoMode
                    elif buttonEvent == "history" and self.showHistory != True:
                        self.showHistory = True
                    #如果所有行都没有播出，则播出所有行
                    elif dialogPlayResult == False:
                        self.dialogTxtSystem.playAll()
                    else:
                        leftClick = True
                #返回上一个对话场景（在被允许的情况下）
                elif pygame.mouse.get_pressed()[2] or self.InputController.joystick.get_button(1) == 1:
                    theNextDialogId = self.dialog_content[self.dialogId]["last_dialog_id"]
                    if theNextDialogId != None:
                        #更新背景
                        self.backgroundContent.update(self.dialog_content[theNextDialogId]["background_img"],self.dialog_content[theNextDialogId]["background_music"])
                        #重设立绘系统
                        self.npc_img_dic.process(self.dialog_content[self.dialogId]["characters_img"],self.dialog_content[theNextDialogId]["characters_img"])
                        #切换dialogId
                        self.dialogId = theNextDialogId
                        self.dialogTxtSystem.updateContent(self.dialog_content[self.dialogId]["content"],self.dialog_content[self.dialogId]["narrator"],True)
        if self.showHistory == True:
            if self.historySurface == None:
                self.historySurface = pygame.Surface((self.window_x,self.window_y),flags=pygame.SRCALPHA).convert_alpha()
                pygame.draw.rect(self.historySurface,(0,0,0),(0,0,self.window_x,self.window_y))
                self.historySurface.set_alpha(150)
                dialogIdTemp = "head"
                local_y = 0
                while dialogIdTemp != None:
                    if self.dialog_content[dialogIdTemp]["narrator"] == None:
                        narratorTemp = self.dialogTxtSystem.fontRender("旁白: ",(255, 255, 255))
                    else:
                        narratorTemp = self.dialogTxtSystem.fontRender(self.dialog_content[dialogIdTemp]["narrator"]+": ",(255, 255, 255))
                    self.historySurface.blit(narratorTemp,(self.window_x*0.15-narratorTemp.get_width(),self.window_y*0.1+local_y))
                    for i in range(len(self.dialog_content[dialogIdTemp]["content"])):
                        self.historySurface.blit(self.dialogTxtSystem.fontRender(self.dialog_content[dialogIdTemp]["content"][i],(255, 255, 255)),(self.window_x*0.15,self.window_y*0.1+local_y))
                        local_y+=self.dialogTxtSystem.FONTSIZE*1.5
                    if self.dialog_content[dialogIdTemp]["next_dialog_id"][0] == "default":
                        dialogIdTemp = self.dialog_content[dialogIdTemp]["next_dialog_id"][1]
                    else:
                        dialogIdTemp = None
            screen.blit(self.historySurface,(0,0))
        elif self.dialogTxtSystem.forceUpdate() or leftClick:
            if self.dialog_content[self.dialogId]["next_dialog_id"] == None:
                self.fadeOut(screen)
                return True
            elif self.dialog_content[self.dialogId]["next_dialog_id"][0] == "default":
                theNextDialogId = self.dialog_content[self.dialogId]["next_dialog_id"][1]
                #更新背景
                self.backgroundContent.update(self.dialog_content[theNextDialogId]["background_img"],self.dialog_content[theNextDialogId]["background_music"])
                #重设立绘系统
                self.npc_img_dic.process(self.dialog_content[self.dialogId]["characters_img"],self.dialog_content[theNextDialogId]["characters_img"])
                #切换dialogId
                self.dialogId = theNextDialogId
                self.dialogTxtSystem.updateContent(self.dialog_content[self.dialogId]["content"],self.dialog_content[self.dialogId]["narrator"])
            #如果是切换场景
            elif self.dialog_content[self.dialogId]["next_dialog_id"][0] == "changeScene":
                self.fadeOut(screen)
                time.sleep(2)
                self.dialogId = self.dialog_content[self.dialogId]["next_dialog_id"][1]
                self.dialogTxtSystem.resetDialogueboxData()
                self.dialogTxtSystem.updateContent(self.dialog_content[self.dialogId]["content"],self.dialog_content[self.dialogId]["narrator"])
                self.backgroundContent.update(self.dialog_content[self.dialogId]["background_img"],None)
                self.fadeIn(screen)
                #更新背景（音乐）
                self.ready()
        self.InputController.display(screen)
        return False
    def ready(self):
        self.backgroundContent.update(self.dialog_content[self.dialogId]["background_img"],self.dialog_content[self.dialogId]["background_music"])
    #淡出
    def fadeOut(self,screen):
        pygame.mixer.music.fadeout(1000)
        for i in range(0,255,5):
            self.black_bg.set_alpha(i)
            self.black_bg.draw(screen)
            pygame.display.flip()
    #淡入
    def fadeIn(self,screen):
        for i in range(255,0,-5):
            self.backgroundContent.display(screen)
            self.black_bg.set_alpha(i)
            self.black_bg.draw(screen)
            pygame.display.flip()
        #重设black_bg的alpha值以便下一次使用
        self.black_bg.set_alpha(255)

#npc立绘系统
class NpcImageSystem:
    def __init__(self):
        self.imgDic = {}
        self.npcLastRound = []
        self.npcLastRoundImgAlpha = 255
        self.npcThisRound = []
        self.npcThisRoundImgAlpha = 0
        self.npcBothRound = []
        self.communication = pygame.image.load(os.path.join("Assets/image/UI/communication.png")).convert_alpha()
    def displayTheNpc(self,name,x,y,alpha,screen):
        if alpha <= 0:
            return False
        nameTemp = name.replace("&communication","").replace("&dark","")
        img_width = int(screen.get_width()/2)
        #加载npc的基础立绘
        if nameTemp not in self.imgDic:
            self.imgDic[nameTemp] = {"normal":pygame.transform.scale(pygame.image.load(os.path.join("Assets/image/npc/"+nameTemp+".png")).convert_alpha(),(img_width,img_width))}
            #生成深色图片
            self.imgDic[nameTemp]["dark"] = self.imgDic[nameTemp]["normal"].copy()
            self.imgDic[nameTemp]["dark"].fill((50, 50, 50), special_flags=pygame.BLEND_RGB_SUB) 
        if "&communication" in name:
            if "communication" not in self.imgDic[nameTemp]:
                #生成通讯图片
                self.imgDic[nameTemp]["communication"] = pygame.Surface((int(img_width/1.9), int(img_width/1.8)), flags=pygame.SRCALPHA)
                self.imgDic[nameTemp]["communication"].blit(self.imgDic[nameTemp]["normal"],(-int(img_width/4),0))
                self.imgDic[nameTemp]["communication"].blit(pygame.transform.scale(self.communication,(int(img_width/1.9), int(img_width/1.7))),(0,0))
                #生成深色的通讯图片
                self.imgDic[nameTemp]["communication_dark"] = self.imgDic[nameTemp]["communication"].copy()
                dark = pygame.Surface((int(img_width/1.9), int(img_width/1.8)), flags=pygame.SRCALPHA).convert_alpha()
                dark.fill((50,50,50))
                self.imgDic[nameTemp]["communication_dark"].blit(dark, (0, 0), special_flags=pygame.BLEND_RGB_SUB)
            x+=int(img_width/4)
            if "&dark" in name:
                img = self.imgDic[nameTemp]["communication_dark"]
            else:
                img = self.imgDic[nameTemp]["communication"]
        elif "&dark" in name:
            img = self.imgDic[nameTemp]["dark"]
        else:
            img = self.imgDic[nameTemp]["normal"]
        if img.get_alpha() != alpha:
            img.set_alpha(alpha)
        screen.blit(img,(x,y))
    def display(self,screen):
        window_x = screen.get_width()
        window_y = screen.get_height()
        if self.npcLastRoundImgAlpha != 0 and len(self.npcLastRound)>0:
            #调整alpha值
            self.npcLastRoundImgAlpha -= 15
            #画上上一幕的立绘
            if len(self.npcLastRound)==2:
                if self.npcLastRound[0] not in self.npcBothRound:
                    self.displayTheNpc(self.npcLastRound[0],0,window_y-window_x/2,self.npcLastRoundImgAlpha,screen)
                if self.npcLastRound[1] not in self.npcBothRound:
                    self.displayTheNpc(self.npcLastRound[1],window_x/2,window_y-window_x/2,self.npcLastRoundImgAlpha,screen)
            elif len(self.npcLastRound)==1 and self.npcLastRound[0] not in self.npcBothRound:
                self.displayTheNpc(self.npcLastRound[0],window_x/4,window_y-window_x/2,self.npcLastRoundImgAlpha,screen)
        #加载对话人物立绘
        if len(self.npcThisRound)>0:
            #调整alpha值
            if self.npcThisRoundImgAlpha < 255:
                self.npcThisRoundImgAlpha += 25
            #画上当前幕的立绘
            if len(self.npcThisRound)==2:
                if self.npcThisRound[0] not in self.npcBothRound:
                    self.displayTheNpc(self.npcThisRound[0],0,window_y-window_x/2,self.npcThisRoundImgAlpha,screen)
                else:
                    self.displayTheNpc(self.npcThisRound[0],0,window_y-window_x/2,255,screen)
                if self.npcThisRound[1] not in self.npcBothRound:
                    self.displayTheNpc(self.npcThisRound[1],window_x/2,window_y-window_x/2,self.npcThisRoundImgAlpha,screen)
                else:
                    self.displayTheNpc(self.npcThisRound[1],window_x/2,window_y-window_x/2,255,screen)
            elif len(self.npcThisRound)==1:
                if self.npcThisRound[0] not in self.npcBothRound:
                    self.displayTheNpc(self.npcThisRound[0],window_x/4,window_y-window_x/2,self.npcThisRoundImgAlpha,screen)
                else:
                    self.displayTheNpc(self.npcThisRound[0],window_x/4,window_y-window_x/2,255,screen)
    def process(self,lastRoundCharacterNameList,thisRoundCharacterNameList):
        if lastRoundCharacterNameList == None:
            self.npcLastRound = []
        else:
            self.npcLastRound = lastRoundCharacterNameList
        if thisRoundCharacterNameList == None:
            self.npcThisRound = []
        else:
            self.npcThisRound = thisRoundCharacterNameList
        self.npcLastRoundImgAlpha = 255
        self.npcThisRoundImgAlpha = 5
        self.npcBothRound = []
        for name in self.npcThisRound:
            if name in self.npcLastRound:
                self.npcBothRound.append(name)

#对话框和对话框内容
class DialogContent:
    def __init__(self,fontSize):
        self.content = ""
        self.textIndex = None
        self.displayedLine = None
        self.textPlayingSound = pygame.mixer.Sound("Assets/sound/ui/dialog_words_playing.ogg")
        with open("Save/setting.yaml", "r", encoding='utf-8') as f:
            DATA = yaml.load(f.read(),Loader=yaml.FullLoader)
            self.FONT = DATA["Font"]
            self.MODE = DATA["Antialias"]
            self.READINGSPEED = DATA["ReadingSpeed"]
        self.FONTSIZE = int(fontSize)
        self.FONT = pygame.font.SysFont(self.FONT,self.FONTSIZE)
        self.dialoguebox = pygame.image.load(os.path.join("Assets/image/UI/dialoguebox.png")).convert_alpha()
        self.dialoguebox_y = None
        self.dialoguebox_height = 0
        self.dialoguebox_max_height = None
        self.narrator = None
        #鼠标图标
        self.mouseImg_none = pygame.image.load(os.path.join("Assets/image/UI/mouse_none.png")).convert_alpha()
        self.mouseImg_click = pygame.image.load(os.path.join("Assets/image/UI/mouse.png")).convert_alpha()
        self.mouse_gif_id = 0
        self.ifHide = False
        self.readTime = 0
        self.totalLetters = 0
        self.autoMode = False
    def hideSwitch(self):
        if self.ifHide == False:
            self.ifHide = True
        else:
            self.ifHide = False
    def updateContent(self,txt,narrator,forceNotResizeDialoguebox=False):
        self.content = txt
        self.totalLetters = 0
        self.readTime = 0
        for i in range(len(self.content)):
            self.totalLetters += len(self.content[i])
        if self.narrator != narrator:
            if forceNotResizeDialoguebox == False:
                self.resetDialogueboxData()
            else:
                pass
            self.narrator = narrator
        self.textIndex = 0
        self.displayedLine = 0
        if pygame.mixer.get_busy() == True:
            self.textPlayingSound.stop()
    def resetDialogueboxData(self):
        self.dialoguebox_height = 0
        self.dialoguebox_y = None
    def setSoundVolume(self,num):
        self.textPlayingSound.set_volume(num/100.0)
    def playAll(self):
        self.displayedLine = len(self.content)-1
        self.textIndex = len(self.content[self.displayedLine])-1
    def fontRender(self,txt,color):
        return self.FONT.render(txt,self.MODE,color)
    def display(self,screen):
        if self.ifHide == False:
            #如果对话框图片的最高高度没有被设置，则根据屏幕大小设置一个
            if self.dialoguebox_max_height == None:
                self.dialoguebox_max_height = screen.get_height()/4
            #如果当前对话框图片的y坐标不存在（一般出现在对话系统例行初始化后），则根据屏幕大小设置一个
            if self.dialoguebox_y == None:
                self.dialoguebox_y = screen.get_height()*0.65+self.dialoguebox_max_height/2
            #画出对话框图片
            screen.blit(pygame.transform.scale(self.dialoguebox,(int(screen.get_width()*0.74),int(self.dialoguebox_height))),(screen.get_width()*0.13,self.dialoguebox_y))
            #如果对话框图片还在放大阶段
            if self.dialoguebox_height < self.dialoguebox_max_height:
                self.dialoguebox_height += self.dialoguebox_max_height/12
                self.dialoguebox_y -= self.dialoguebox_max_height/24
            #如果已经放大好了
            else:
                x = int(screen.get_width()*0.2)
                y = int(screen.get_height()*0.74)
                #写上当前讲话人的名字
                if self.narrator != None:
                    screen.blit(self.FONT.render(self.narrator,self.MODE,(255, 255, 255)),(x,self.dialoguebox_y+self.FONTSIZE))
                #鼠标gif的ID
                if self.mouse_gif_id<100:
                    self.mouse_gif_id += 0.25
                else:
                    self.mouse_gif_id = 0
                #根据ID画出鼠标gif
                if int(self.mouse_gif_id/10)%2==0:
                    screen.blit(pygame.transform.scale(self.mouseImg_none,(self.FONTSIZE,self.FONTSIZE)),(screen.get_width()*0.82,screen.get_height()*0.83))
                else:
                    screen.blit(pygame.transform.scale(self.mouseImg_click,(self.FONTSIZE,self.FONTSIZE)),(screen.get_width()*0.82,screen.get_height()*0.83))
                #对话框已播放的内容
                for i in range(self.displayedLine):
                    screen.blit(self.FONT.render(self.content[i],self.MODE,(255, 255, 255)),(x,y+self.FONTSIZE*1.5*i))
                #对话框正在播放的内容
                screen.blit(self.FONT.render(self.content[self.displayedLine][:self.textIndex],self.MODE,(255, 255, 255)),(x,y+self.FONTSIZE*1.5*self.displayedLine))
                #如果当前行的字符还没有完全播出
                if self.textIndex < len(self.content[self.displayedLine]):
                    if pygame.mixer.get_busy() == False:
                        self.textPlayingSound.play()
                    self.textIndex +=1
                #当前行的所有字都播出后，播出下一行
                elif self.displayedLine < len(self.content)-1:
                    if pygame.mixer.get_busy() == False:
                        self.textPlayingSound.play()
                    self.textIndex = 1
                    self.displayedLine += 1
                #当所有行都播出后
                else:
                    if pygame.mixer.get_busy() == True:
                        self.textPlayingSound.stop()
                    if self.autoMode == True and self.readTime < self.totalLetters:
                        self.readTime += self.READINGSPEED
                    return True
        return False
    def forceUpdate(self):
        if self.autoMode == True and self.readTime >= self.totalLetters:
            return True
        else:
            return False

#背景音乐和图片管理
class DialogBackground:
    def __init__(self,backgroundMusicVolume):
        self.backgroundImgName = None
        self.backgroundImgSurface = None
        self.nullSurface = pygame.image.load(os.path.join("Assets/image/UI/black.png")).convert_alpha()
        self.backgroundMusicName = None
        self.setBgmVolume(backgroundMusicVolume)
    def setBgmVolume(self,backgroundMusicVolume):
        self.backgroundMusicVolume = backgroundMusicVolume/100.0
        pygame.mixer.music.set_volume(self.backgroundMusicVolume)
    def update(self,backgroundImgName,backgroundMusicName):
        #如果需要更新背景图片
        if self.backgroundImgName != backgroundImgName:
            self.backgroundImgName = backgroundImgName
            if self.backgroundImgName != None:
                if os.path.exists("Assets/image/dialog_background/{}.png".format(self.backgroundImgName)):
                    self.backgroundImgSurface = pygame.image.load(os.path.join("Assets/image/dialog_background/{}.png".format(self.backgroundImgName))).convert_alpha()
                elif os.path.exists("Assets/image/dialog_background/{}.jpg".format(self.backgroundImgName)):
                    self.backgroundImgSurface = pygame.image.load(os.path.join("Assets/image/dialog_background/{}.jpg".format(self.backgroundImgName))).convert_alpha()
                elif os.path.exists("Assets/movie/"+self.backgroundImgName):
                    self.backgroundImgSurface = VideoObject("Assets/movie/"+self.backgroundImgName,True)
                else:
                    raise Exception('Warning: Cannot find background image or video file.')
            else:
                self.backgroundImgSurface = None
        #如果需要更新背景音乐
        if self.backgroundMusicName != backgroundMusicName:
            self.backgroundMusicName = backgroundMusicName
            if self.backgroundMusicName != None:
                if os.path.exists("Assets/music/{}.mp3".format(self.backgroundMusicName)):
                    pygame.mixer.music.load("Assets/music/{}.mp3".format(self.backgroundMusicName))
                elif os.path.exists("Assets/music/{}.ogg".format(self.backgroundMusicName)):
                    pygame.mixer.music.load("Assets/music/{}.ogg".format(self.backgroundMusicName))
                else:
                    raise Exception('Warning: Cannot find background music file.')
                pygame.mixer.music.play(loops=9999, start=0.0)
            else:
                pygame.mixer.music.unload()
    def display(self,screen):
        if self.backgroundImgName != None:
            if isinstance(self.backgroundImgSurface,VideoObject):
                self.backgroundImgSurface.display(screen)
            else:
                screen.blit(pygame.transform.scale(self.backgroundImgSurface,screen.get_size()),(0,0))
        else:
            screen.blit(pygame.transform.scale(self.nullSurface,screen.get_size()),(0,0))

#对话系统按钮UI模块
class DialogButtons:
    def __init__(self):
        with open("Save/setting.yaml", "r", encoding='utf-8') as f:
            setting = yaml.load(f.read(),Loader=yaml.FullLoader)
            window_x = int(setting['Screen_size_x'])
            window_y = int(setting['Screen_size_y'])
            self.FONTSIZE = int(window_x*0.0175)
            self.FONT = pygame.font.SysFont(setting["Font"],self.FONTSIZE)
            self.FONTMODE = setting["Antialias"]
        with open("Lang/"+setting['Language']+".yaml", "r", encoding='utf-8') as f:
            dialog_txt = yaml.load(f.read(),Loader=yaml.FullLoader)["Dialog"]
            #生成跳过按钮
            tempButtonIcon = pygame.transform.scale(pygame.image.load(os.path.join("Assets/image/UI/dialog_skip.png")).convert_alpha(),(self.FONTSIZE,self.FONTSIZE))
            tempButtonTxt = self.FONT.render(dialog_txt["skip"],self.FONTMODE,(255, 255, 255))
            temp_w = tempButtonTxt.get_width()+self.FONTSIZE*1.5
            self.skipButton = pygame.Surface((temp_w, self.FONTSIZE),flags=pygame.SRCALPHA).convert_alpha()
            self.skipButtonHovered = pygame.Surface((temp_w, self.FONTSIZE),flags=pygame.SRCALPHA).convert_alpha()
            self.skipButtonHovered.blit(tempButtonIcon,(tempButtonTxt.get_width()+self.FONTSIZE*0.5,0))
            self.skipButtonHovered.blit(tempButtonTxt,(0,0))
            tempButtonTxt = self.FONT.render(dialog_txt["skip"],self.FONTMODE,(105, 105, 105))
            tempButtonIcon.fill((100,100,100), special_flags=pygame.BLEND_RGB_SUB)
            self.skipButton.blit(tempButtonIcon,(tempButtonTxt.get_width()+self.FONTSIZE*0.5,0))
            self.skipButton.blit(tempButtonTxt,(0,0))
            self.skipButton = ImageSurface(self.skipButton,window_x*0.9,window_y*0.05)
            self.skipButtonHovered = ImageSurface(self.skipButtonHovered,window_x*0.9,window_y*0.05)
            #生成自动播放按钮
            self.autoIconHovered = pygame.transform.scale(pygame.image.load(os.path.join("Assets/image/UI/dialog_auto.png")).convert_alpha(),(self.FONTSIZE,self.FONTSIZE))
            self.autoIcon = self.autoIconHovered.copy()
            self.autoIcon.fill((100,100,100), special_flags=pygame.BLEND_RGB_SUB)
            self.autoIconDegree = 0
            self.autoIconDegreeChange = (2**0.5-1)*self.FONTSIZE/45
            self.autoMode = False
            tempButtonTxt = self.FONT.render(dialog_txt["auto"],self.FONTMODE,(105, 105, 105))
            temp_w = tempButtonTxt.get_width()+self.FONTSIZE*1.5
            self.autoButton = pygame.Surface((temp_w, self.FONTSIZE),flags=pygame.SRCALPHA).convert_alpha()
            self.autoButtonHovered = pygame.Surface((temp_w, self.FONTSIZE),flags=pygame.SRCALPHA).convert_alpha()
            self.autoButton.blit(tempButtonTxt,(0,0))
            self.autoButtonHovered.blit(self.FONT.render(dialog_txt["auto"],self.FONTMODE,(255, 255, 255)),(0,0))
            self.autoButton = ImageSurface(self.autoButton,window_x*0.8,window_y*0.05)
            self.autoButton.description = int(self.autoButton.x+self.autoButton.img.get_width()-self.FONTSIZE)
            self.autoButtonHovered = ImageSurface(self.autoButtonHovered,window_x*0.8,window_y*0.05)
            self.autoButtonHovered.description = int(self.autoButtonHovered.x+self.autoButtonHovered.img.get_width()-self.FONTSIZE)
            #隐藏按钮
            hideUI_img = pygame.transform.scale(pygame.image.load(os.path.join("Assets/image/UI/dialog_hide.png")).convert_alpha(),(self.FONTSIZE,self.FONTSIZE))
            hideUI_imgTemp = hideUI_img.copy()
            hideUI_imgTemp.fill((100,100,100), special_flags=pygame.BLEND_RGB_SUB)
            self.hideButton = Button(hideUI_imgTemp,window_x*0.05,window_y*0.05)
            self.hideButton.setHoverImg(hideUI_img)
            #历史回溯按钮
            history_img = pygame.transform.scale(pygame.image.load(os.path.join("Assets/image/UI/dialog_history.png")).convert_alpha(),(self.FONTSIZE,self.FONTSIZE))
            history_imgTemp = history_img.copy()
            history_imgTemp.fill((100,100,100), special_flags=pygame.BLEND_RGB_SUB)
            self.historyButton = Button(history_imgTemp,window_x*0.1,window_y*0.05)
            self.historyButton.setHoverImg(history_img)
    def display(self,screen,theGameController):
        self.hideButton.display(screen)
        self.historyButton.display(screen)
        action = ""
        if theGameController.ifHover(self.skipButton):
            self.skipButtonHovered.draw(screen)
            action = "skip"
        else:
            self.skipButton.draw(screen)
        if theGameController.ifHover(self.autoButton):
            self.autoButtonHovered.draw(screen)
            if self.autoMode == True:
                rotatedIcon = pygame.transform.rotate(self.autoIconHovered,self.autoIconDegree)
                screen.blit(rotatedIcon,(self.autoButtonHovered.description+self.autoIconHovered.get_width()/2-rotatedIcon.get_width()/2,self.autoButtonHovered.y+self.autoIconHovered.get_height()/2-rotatedIcon.get_height()/2))
                if self.autoIconDegree < 180:
                    self.autoIconDegree+=1
                else:
                    self.autoIconDegree=0
            else:
                screen.blit(self.autoIconHovered,(self.autoButtonHovered.description,self.autoButtonHovered.y))
            action = "auto"
        else:
            if self.autoMode == True:
                self.autoButtonHovered.draw(screen)
                rotatedIcon = pygame.transform.rotate(self.autoIconHovered,self.autoIconDegree)
                screen.blit(rotatedIcon,(self.autoButtonHovered.description+self.autoIconHovered.get_width()/2-rotatedIcon.get_width()/2,self.autoButtonHovered.y+self.autoIconHovered.get_height()/2-rotatedIcon.get_height()/2))
                if self.autoIconDegree < 180:
                    self.autoIconDegree+=1
                else:
                    self.autoIconDegree=0
            else:
                self.autoButton.draw(screen)
                screen.blit(self.autoIcon,(self.autoButton.description,self.autoButton.y))
        if theGameController.ifHover(self.hideButton):
            action = "hide"
        elif theGameController.ifHover(self.historyButton):
            action = "history"
        return action
    def autoModeSwitch(self):
        if self.autoMode == False:
            self.autoMode = True
        else:
            self.autoMode = False
            self.autoIconDegree = 0