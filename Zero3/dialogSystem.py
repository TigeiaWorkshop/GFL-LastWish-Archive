# cython: language_level=3
from Zero3.basic import *

#视觉小说系统模块
class DialogSystem:
    def __init__(self,dialogType,chapterName,lang,part):
        #读取章节信息
        with open("Data/{0}/{1}_dialogs_{2}.yaml".format(dialogType,chapterName,lang),"r",encoding='utf-8') as f:
            self.dialogData = yaml.load(f.read(),Loader=yaml.FullLoader)
        if "default_lang" in self.dialogData and self.dialogData["default_lang"] != None:
            with open("Data/{0}/{1}_dialogs_{2}.yaml".format(dialogType,chapterName,self.dialogData["default_lang"]),"r",encoding='utf-8') as f:
                self.dialog_content = yaml.load(f.read(),Loader=yaml.FullLoader)[part]
            for key,currentDialog in self.dialogData[part].items():
                for key2,dataNeedReplace in currentDialog.items():
                    self.dialog_content[key][key2] = dataNeedReplace
        else:
            self.dialog_content = self.dialogData[part]
            if len(self.dialog_content)==0:
                raise Exception('ZeroEngine-Error: The dialog has no content!')
        #加载对话的背景图片
        self.backgroundContent = DialogBackground()
        #获取屏幕的尺寸
        self.window_x,self.window_y = display.get_size()
        #选项栏
        self.optionBox = pygame.image.load(os.path.join("Assets/image/UI/option.png")).convert_alpha()
        #UI按钮
        self.ButtonsMananger = DialogButtons()
        #黑色帘幕
        self.black_bg = get_SingleColorSurface("black")
        #加载对话框系统
        self.dialogTxtSystem = DialogContent(self.window_x*0.015)
        #设定初始化
        self.dialogId = "head"
        #如果dialog_content没有头
        if self.dialogId not in self.dialog_content:
            raise Exception('ZeroEngine-Error: The dialog must have a head!')
        else:
            self.dialogTxtSystem.update(self.dialog_content[self.dialogId]["content"],self.dialog_content[self.dialogId]["narrator"])
        #更新背景音乐
        self.backgroundContent.update(self.dialog_content[self.dialogId]["background_img"],None)
        #玩家在对话时做出的选择
        self.dialog_options = {}
        #加载npc立绘系统并初始化
        self.npc_img_dic = NpcImageSystem()
        self.npc_img_dic.process(None,self.dialog_content[self.dialogId]["characters_img"])
        self.showHistory = False
        self.historySurface = None
        self.historySurface_local_y = 0
        #展示历史界面-返回按钮
        buttonTemp = pygame.transform.scale(pygame.image.load(os.path.join("Assets/image/UI/back.png")).convert_alpha(),(int(self.window_x*0.03),int(self.window_y*0.04)))
        self.history_back = Button(addDarkness(buttonTemp,100),self.window_x*0.04,self.window_y*0.04)
        self.history_back.setHoverImg(buttonTemp)
        self.__events = None
    def __update_event(self):
        self.__events = pygame.event.get()
    def get_event(self):
        return self.__events
    def __update_scene(self,theNextDialogId):
        #更新背景
        self.backgroundContent.update(self.dialog_content[theNextDialogId]["background_img"],self.dialog_content[theNextDialogId]["background_music"])
        #重设立绘系统
        self.npc_img_dic.process(self.dialog_content[self.dialogId]["characters_img"],self.dialog_content[theNextDialogId]["characters_img"])
        #切换dialogId
        self.dialogId = theNextDialogId
        self.dialogTxtSystem.update(self.dialog_content[self.dialogId]["content"],self.dialog_content[self.dialogId]["narrator"])
    def display(self,screen):
        #背景
        self.backgroundContent.display(screen)
        self.npc_img_dic.display(screen)
        #按钮
        buttonEvent = self.ButtonsMananger.display(screen,self.dialogTxtSystem.ifHide)
        #显示对话框和对应文字
        dialogPlayResult = self.dialogTxtSystem.display(screen)
        #更新event
        self.__update_event()
        #按键判定
        leftClick = False
        for event in self.__events:
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.JOYBUTTONDOWN:
                if pygame.mouse.get_pressed()[0] or controller.joystick.get_button(0) == 1:
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
                    elif ifHover(self.history_back) and self.showHistory == True:
                        self.showHistory = False
                        self.historySurface = None
                    #如果所有行都没有播出，则播出所有行
                    elif dialogPlayResult == False:
                        self.dialogTxtSystem.playAll()
                    else:
                        leftClick = True
                elif event.button == 4 and self.historySurface_local_y<0:
                    self.historySurface = None
                    self.historySurface_local_y += self.window_y*0.1
                elif event.button == 5:
                    self.historySurface = None
                    self.historySurface_local_y -= self.window_y*0.1
                #返回上一个对话场景（在被允许的情况下）
                elif pygame.mouse.get_pressed()[2] or controller.joystick.get_button(1) == 1:
                    if self.dialog_content[self.dialogId]["last_dialog_id"] != None:
                        self.__update_scene(self.dialog_content[self.dialogId]["last_dialog_id"])
                        dialogPlayResult = False
                    else:
                        pass
        #显示选项
        if dialogPlayResult == True and self.dialog_content[self.dialogId]["next_dialog_id"] != None and self.dialog_content[self.dialogId]["next_dialog_id"]["type"] == "option":
            optionBox_y_base = (self.window_y*3/4-(len(self.dialog_content[self.dialogId]["next_dialog_id"]["target"]))*2*self.window_x*0.03)/4
            for i in range(len(self.dialog_content[self.dialogId]["next_dialog_id"]["target"])):
                option_txt = self.dialogTxtSystem.fontRender(self.dialog_content[self.dialogId]["next_dialog_id"]["target"][i]["txt"],(255, 255, 255))
                optionBox_scaled = pygame.transform.scale(self.optionBox,(int(option_txt.get_width()+self.window_x*0.05),int(self.window_x*0.05)))
                optionBox_x = (self.window_x-optionBox_scaled.get_width())/2
                optionBox_y = (i+1)*2*self.window_x*0.03+optionBox_y_base
                displayWithInCenter(option_txt,optionBox_scaled,optionBox_x,optionBox_y,screen)
                if ifHover(optionBox_scaled,(optionBox_x,optionBox_y)) and leftClick == True and self.showHistory == False:
                    #保存选取的选项
                    nextDialogId = self.dialog_content[self.dialogId]["next_dialog_id"]["target"][i]["id"]
                    self.dialog_options[self.dialogId] = {"id":i,"target":nextDialogId}
                    #更新场景
                    self.__update_scene(nextDialogId)
                    del nextDialogId
                    leftClick = False
                    break
        #展示历史
        if self.showHistory == True:
            if self.historySurface == None:
                self.historySurface = pygame.Surface((self.window_x,self.window_y),flags=pygame.SRCALPHA).convert_alpha()
                pygame.draw.rect(self.historySurface,(0,0,0),(0,0,self.window_x,self.window_y))
                self.historySurface.set_alpha(150)
                dialogIdTemp = "head"
                local_y = self.historySurface_local_y
                while dialogIdTemp != None:
                    if self.dialog_content[dialogIdTemp]["narrator"] != None:
                        narratorTemp = self.dialogTxtSystem.fontRender(self.dialog_content[dialogIdTemp]["narrator"]+': ["',(255, 255, 255))
                        self.historySurface.blit(narratorTemp,(self.window_x*0.15-narratorTemp.get_width(),self.window_y*0.1+local_y))
                    for i in range(len(self.dialog_content[dialogIdTemp]["content"])):
                        txt = self.dialog_content[dialogIdTemp]["content"][i]
                        txt += '"]' if i == len(self.dialog_content[dialogIdTemp]["content"])-1 and self.dialog_content[dialogIdTemp]["narrator"] != None else ""
                        self.historySurface.blit(self.dialogTxtSystem.fontRender(txt,(255, 255, 255)),(self.window_x*0.15,self.window_y*0.1+local_y))
                        local_y+=self.dialogTxtSystem.FONTSIZE*1.5
                    if dialogIdTemp != self.dialogId:
                        if self.dialog_content[dialogIdTemp]["next_dialog_id"]["type"] == "default" or self.dialog_content[dialogIdTemp]["next_dialog_id"]["type"] == "changeScene":
                            dialogIdTemp = self.dialog_content[dialogIdTemp]["next_dialog_id"]["target"]
                        elif self.dialog_content[dialogIdTemp]["next_dialog_id"]["type"] == "option":
                            narratorTemp = self.dialogTxtSystem.fontRender(self.ButtonsMananger.choiceTxt+" - ",(0,191,255))
                            self.historySurface.blit(narratorTemp,(self.window_x*0.15-narratorTemp.get_width(),self.window_y*0.1+local_y))
                            self.historySurface.blit(self.dialogTxtSystem.fontRender(str(self.dialog_options[dialogIdTemp]["target"]),(0,191,255)),(self.window_x*0.15,self.window_y*0.1+local_y))
                            local_y+=self.dialogTxtSystem.FONTSIZE*1.5
                            dialogIdTemp = self.dialog_options[dialogIdTemp]["target"]
                        else:
                            dialogIdTemp = None
                    else:
                        dialogIdTemp = None
            screen.blit(self.historySurface,(0,0))
            self.history_back.display(screen)
            ifHover(self.history_back)
        elif self.dialogTxtSystem.forceUpdate() or leftClick:
            if self.dialog_content[self.dialogId]["next_dialog_id"] == None or self.dialog_content[self.dialogId]["next_dialog_id"]["target"] == None:
                self.fadeOut(screen)
                return True
            elif self.dialog_content[self.dialogId]["next_dialog_id"]["type"] == "default":
                self.__update_scene(self.dialog_content[self.dialogId]["next_dialog_id"]["target"])
            #如果是切换场景
            elif self.dialog_content[self.dialogId]["next_dialog_id"]["type"] == "changeScene":
                self.fadeOut(screen)
                pygame.time.wait(2000)
                #重设立绘系统
                theNextDialogId = self.dialog_content[self.dialogId]["next_dialog_id"]["target"]
                self.npc_img_dic.process(self.dialog_content[self.dialogId]["characters_img"],self.dialog_content[theNextDialogId]["characters_img"])
                self.dialogId = theNextDialogId
                self.dialogTxtSystem.resetDialogueboxData()
                self.dialogTxtSystem.update(self.dialog_content[self.dialogId]["content"],self.dialog_content[self.dialogId]["narrator"])
                self.backgroundContent.update(self.dialog_content[self.dialogId]["background_img"],None)
                self.fadeIn(screen)
                #更新背景（音乐）
                self.ready()
        controller.display(screen)
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

class DialogSystemDev:
    def __init__(self,dialogType,chapterName,lang):
        self.deafult_dialog_format = {
            "background_img": None,
            "background_music": None,
            "characters_img": [],
            "content": [],
            "last_dialog_id": None,
            "narrator": None,
            "next_dialog_id": {"type":"default","target":1}
        }
        self.dialogType = dialogType
        self.chapterName = chapterName
        self.lang = lang
        self.__loadDialogData()
        #获取屏幕的尺寸
        self.window_x,self.window_y = display.get_size()
        #黑色帘幕
        black_bg_temp = pygame.Surface((self.window_x,self.window_y),flags=pygame.SRCALPHA).convert_alpha()
        pygame.draw.rect(black_bg_temp,(0,0,0),(0,0,self.window_x,self.window_y))
        self.black_bg = ImageSurface(black_bg_temp,0,0,self.window_x,self.window_y)
        #选项栏
        self.optionBox = pygame.image.load(os.path.join("Assets/image/UI/option.png")).convert_alpha()
        #设定初始化
        self.dialogId = "head"
        self.part = "dialog_before_battle"
        widthTmp = int(self.window_x*0.2)
        self.UIContainerRight = loadDynamicImage("Assets/image/UI/container.png",(self.window_x*0.8+widthTmp,0),(self.window_x*0.8,0),(widthTmp/10,0),widthTmp,self.window_y)
        self.UIContainerRightButton = loadImage("Assets/image/UI/container_button.png",(-self.window_x*0.03,self.window_y*0.4),int(self.window_x*0.04),int(self.window_y*0.2))
        self.UIContainerRight.rotate(90)
        self.UIContainerRightButton.rotate(90)
        CONFIG = get_lang("DialogCreator")
        self.buttonsUI = {
            "add": ButtonWithDes("Assets/image/UI/add.png",50,50,50,50,CONFIG["add"]),
            "back": ButtonWithDes("Assets/image/UI/back.png",150,50,50,50,CONFIG["back"]),
            "delete": ButtonWithDes("Assets/image/UI/delete.png",250,50,50,50,CONFIG["delete"]),
            "previous": ButtonWithDes("Assets/image/UI/previous.png",350,50,50,50,CONFIG["previous"]),
            "next": ButtonWithDes("Assets/image/UI/dialog_skip.png",450,50,50,50,CONFIG["next"]),
            "reload": ButtonWithDes("Assets/image/UI/reload.png",550,50,50,50,CONFIG["reload"]),
            "save": ButtonWithDes("Assets/image/UI/save.png",650,50,50,50,CONFIG["save"])
        } 
        #加载背景图片
        self.all_background_image = {}
        for imgPath in glob.glob("Assets/image/dialog_background/*"):
            self.all_background_image[os.path.basename(imgPath)] = loadImg(imgPath)
        self.background_image_local_y = self.window_y*0.1
        self.FONT = createFont(self.window_x*0.0175)
    #保存数据
    def __save(self):
        with open("Data/{0}/{1}_dialogs_{2}.yaml".format(self.dialogType,self.chapterName,self.lang), "w", encoding='utf-8') as f:
            yaml.dump(self.dialog_content, f, allow_unicode=True)
    #读取章节信息
    def __loadDialogData(self):
        with open("Data/{0}/{1}_dialogs_{2}.yaml".format(self.dialogType,self.chapterName,self.lang), "r", encoding='utf-8') as f:
            self.dialog_content = yaml.load(f.read(),Loader=yaml.FullLoader)
        #初始化文件的数据
        if "dialog_before_battle" not in self.dialog_content:
            self.dialog_content["dialog_before_battle"] = {}
        if "head" not in self.dialog_content["dialog_before_battle"]:
            self.dialog_content["dialog_before_battle"]["head"] = self.deafult_dialog_format
        if "dialog_after_battle" not in self.dialog_content:
            self.dialog_content["dialog_after_battle"] = {}
        if "head" not in self.dialog_content["dialog_after_battle"]:
            self.dialog_content["dialog_after_battle"]["head"] = self.deafult_dialog_format
    def display(self,screen):
        if self.dialog_content[self.part][self.dialogId]["background_img"] == None:
            self.black_bg.draw(screen)
        else:
            screen.blit(pygame.transform.scale(self.all_background_image[self.dialog_content[self.part][self.dialogId]["background_img"]],(self.window_x,self.window_y)),(0,0))
        self.UIContainerRightButton.draw(screen,self.UIContainerRight.x)
        self.UIContainerRight.draw(screen)
        buttonHovered = None
        for button in self.buttonsUI:
            if ifHover(self.buttonsUI[button]):
                buttonHovered = button
            self.buttonsUI[button].display(screen)
        if buttonHovered != None:
            self.buttonsUI[buttonHovered].displayDes(screen)
        leftClick = False
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.JOYBUTTONDOWN:
                if pygame.mouse.get_pressed()[0] or controller.joystick.get_button(0) == 1:
                    if ifHover(self.UIContainerRightButton,None,self.UIContainerRight.x):
                        self.UIContainerRight.switch()
                        self.UIContainerRightButton.flip(True,False)
                    #退出
                    elif buttonHovered == "back":
                        return True
                    elif buttonHovered == "previous":
                        lastId = self.dialog_content[self.part][self.dialogId]["last_dialog_id"]
                        if lastId != None:
                            self.dialogId = lastId
                        else:
                            print("no last_dialog_id")
                    elif buttonHovered == "next":
                        if self.dialog_content[self.part][self.dialogId]["next_dialog_id"]["type"] == "default" or self.dialog_content[self.part][self.dialogId]["next_dialog_id"]["type"] == "changeScene":
                            self.dialogId = self.dialog_content[self.part][self.dialogId]["next_dialog_id"]["target"]
                        elif self.dialog_content[self.part][self.dialogId]["next_dialog_id"]["type"] == "option":
                            optionBox_y_base = (self.window_y*3/4-(len(self.dialog_content[self.part][self.dialogId]["next_dialog_id"]["target"]))*2*self.window_x*0.03)/4
                            for i in range(len(self.dialog_content[self.part][self.dialogId]["next_dialog_id"]["target"])):
                                option_txt = self.FONT.render(self.dialog_content[self.part][self.dialogId]["next_dialog_id"]["target"][i]["txt"],get_fontMode(),(255, 255, 255))
                                optionBox_scaled = pygame.transform.scale(self.optionBox,(int(option_txt.get_width()+self.window_x*0.05),int(self.window_x*0.05)))
                                optionBox_x = (self.window_x-optionBox_scaled.get_width())/2
                                optionBox_y = (i+1)*2*self.window_x*0.03+optionBox_y_base
                                displayWithInCenter(option_txt,optionBox_scaled,optionBox_x,optionBox_y,screen)
                            loop=True
                            while loop:
                                leftClick = False
                                for event in pygame.event.get():
                                    if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.JOYBUTTONDOWN:
                                        leftClick = True
                                        break
                                for i in range(len(self.dialog_content[self.part][self.dialogId]["next_dialog_id"]["target"])):
                                    option_txt = self.FONT.render(self.dialog_content[self.part][self.dialogId]["next_dialog_id"]["target"][i]["txt"],get_fontMode(),(255, 255, 255))
                                    optionBox_scaled = pygame.transform.scale(self.optionBox,(int(option_txt.get_width()+self.window_x*0.05),int(self.window_x*0.05)))
                                    optionBox_x = (self.window_x-optionBox_scaled.get_width())/2
                                    optionBox_y = (i+1)*2*self.window_x*0.03+optionBox_y_base
                                    if ifHover(optionBox_scaled,(optionBox_x,optionBox_y)) and leftClick == True:
                                        self.dialogId = self.dialog_content[self.part][self.dialogId]["next_dialog_id"]["target"][i]["id"]
                                        loop = False
                                        break
                                display.flip()
                    elif buttonHovered == "save":
                        self.__save()
                    elif buttonHovered == "reload":
                        self.__loadDialogData()
                    else:
                        leftClick = True
        if self.UIContainerRight.x<self.window_x:
            i = 0
            for img in self.all_background_image:
                imgTmp = resizeImg(self.all_background_image[img],(self.UIContainerRight.width*0.8,None))
                pos = (self.UIContainerRight.x+self.UIContainerRight.width*0.1,self.background_image_local_y+imgTmp.get_height()*1.5*i)
                screen.blit(imgTmp,pos)
                i+=1
                if leftClick == True and ifHover(imgTmp,pos):
                    self.dialog_content[self.part][self.dialogId]["background_img"] = img
        return False

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
            self.imgDic[nameTemp] = {"normal":pygame.transform.scale(pygame.image.load(os.path.join("Assets/image/npc",nameTemp)).convert_alpha(),(img_width,img_width))}
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
class DialogContent(DialogInterface):
    def __init__(self,fontSize):
        DialogInterface.__init__(self,pygame.image.load(os.path.join("Assets/image/UI/dialoguebox.png")).convert_alpha(),fontSize)
        self.textPlayingSound = pygame.mixer.Sound("Assets/sound/ui/dialog_words_playing.ogg")
        self.READINGSPEED = get_setting("ReadingSpeed")
        self.dialoguebox_y = None
        self.dialoguebox_height = 0
        self.dialoguebox_max_height = None
        #鼠标图标
        self.mouseImg_none = pygame.image.load(os.path.join("Assets/image/UI/mouse_none.png")).convert_alpha()
        self.mouseImg_click = pygame.image.load(os.path.join("Assets/image/UI/mouse.png")).convert_alpha()
        self.mouse_gif_id = 0
        self.ifHide = False
        self.readTime = 0
        self.totalLetters = 0
        self.autoMode = False
    def hideSwitch(self):
        self.ifHide = not self.ifHide
    def update(self,txt,narrator,forceNotResizeDialoguebox=False):
        self.totalLetters = 0
        self.readTime = 0
        for i in range(len(self.content)):
            self.totalLetters += len(self.content[i])
        if self.narrator != narrator and forceNotResizeDialoguebox == False:
            self.resetDialogueboxData()
        super().update(txt,narrator)
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
        return self.FONT.render(txt,get_fontMode(),color)
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
                y = int(screen.get_height()*0.73)
                #写上当前讲话人的名字
                if self.narrator != None:
                    screen.blit(self.FONT.render(self.narrator,get_fontMode(),(255, 255, 255)),(x,self.dialoguebox_y+self.FONTSIZE))
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
                    screen.blit(self.FONT.render(self.content[i],get_fontMode(),(255, 255, 255)),(x,y+self.FONTSIZE*1.5*i))
                #对话框正在播放的内容
                screen.blit(self.FONT.render(self.content[self.displayedLine][:self.textIndex],get_fontMode(),(255, 255, 255)),(x,y+self.FONTSIZE*1.5*self.displayedLine))
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
    def __init__(self):
        self.backgroundImgName = None
        self.backgroundImgSurface = None
        self.nullSurface = get_SingleColorSurface("black")
        self.backgroundMusicName = None
        backgroundMusicVolume = get_setting("Sound")
        self.setBgmVolume(backgroundMusicVolume["background_music"])
    def setBgmVolume(self,backgroundMusicVolume):
        self.backgroundMusicVolume = backgroundMusicVolume/100.0
        pygame.mixer.music.set_volume(self.backgroundMusicVolume)
    def update(self,backgroundImgName,backgroundMusicName):
        #如果需要更新背景图片
        if self.backgroundImgName != backgroundImgName:
            self.backgroundImgName = backgroundImgName
            if self.backgroundImgName != None:
                #尝试背景加载图片
                if os.path.exists("Assets/image/dialog_background/{}".format(self.backgroundImgName)):
                    self.backgroundImgSurface = pygame.image.load(os.path.join("Assets/image/dialog_background",self.backgroundImgName)).convert_alpha()
                #如果在背景图片的文件夹里找不到对应的图片，则查看是否是视频文件
                elif os.path.exists("Assets/movie/"+self.backgroundImgName):
                    try:
                        from Zero3.movie import VideoObject
                        self.backgroundImgSurface = VideoObject("Assets/movie/"+self.backgroundImgName,True)
                    except BaseException:
                        raise Exception('ZeroEngine-Error: Cannot run movie module')
                else:
                    raise Exception('ZeroEngine-Error: Cannot find background image or video file.')
            else:
                self.backgroundImgSurface = None
        #如果需要更新背景音乐
        if self.backgroundMusicName != backgroundMusicName:
            self.backgroundMusicName = backgroundMusicName
            if self.backgroundMusicName != None:
                if os.path.exists("Assets/music/{}".format(self.backgroundMusicName)):
                    pygame.mixer.music.load("Assets/music/{}".format(self.backgroundMusicName))
                else:
                    raise Exception('ZeroEngine-Error: Cannot find background music file.')
                pygame.mixer.music.play(loops=9999, start=0.0)
            else:
                pygame.mixer.music.unload()
    def display(self,screen):
        if self.backgroundImgName != None:
            if isinstance(self.backgroundImgSurface,pygame.Surface):
                screen.blit(pygame.transform.scale(self.backgroundImgSurface,screen.get_size()),(0,0))
            else:
                try:
                    self.backgroundImgSurface.display(screen)
                except BaseException:
                    raise Exception('ZeroEngine-Error: "backgroundImgName" in DialogBackground is causing issue')
        else:
            self.nullSurface.draw(screen)

#对话系统按钮UI模块
class DialogButtons:
    def __init__(self):
        #从设置中读取信息
        window_x,window_y = display.get_size()
        self.FONTSIZE = int(window_x*0.0175)
        self.FONT = createFont(self.FONTSIZE)
        #从语言文件中读取按钮文字
        dialog_txt = get_lang("Dialog")
        #生成跳过按钮
        tempButtonIcon = pygame.transform.scale(pygame.image.load(os.path.join("Assets/image/UI/dialog_skip.png")).convert_alpha(),(self.FONTSIZE,self.FONTSIZE))
        tempButtonTxt = self.FONT.render(dialog_txt["skip"],get_fontMode(),(255, 255, 255))
        temp_w = tempButtonTxt.get_width()+self.FONTSIZE*1.5
        self.choiceTxt = dialog_txt["choice"]
        self.skipButton = pygame.Surface((temp_w,tempButtonTxt.get_height()),flags=pygame.SRCALPHA).convert_alpha()
        self.skipButtonHovered = pygame.Surface((temp_w,tempButtonTxt.get_height()),flags=pygame.SRCALPHA).convert_alpha()
        self.icon_y = (tempButtonTxt.get_height()-tempButtonIcon.get_height())/2
        self.skipButtonHovered.blit(tempButtonIcon,(tempButtonTxt.get_width()+self.FONTSIZE*0.5,self.icon_y))
        self.skipButtonHovered.blit(tempButtonTxt,(0,0))
        tempButtonTxt = self.FONT.render(dialog_txt["skip"],get_fontMode(),(105, 105, 105))
        tempButtonIcon.fill((100,100,100), special_flags=pygame.BLEND_RGB_SUB)
        self.skipButton.blit(tempButtonIcon,(tempButtonTxt.get_width()+self.FONTSIZE*0.5,self.icon_y))
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
        tempButtonTxt = self.FONT.render(dialog_txt["auto"],get_fontMode(),(105, 105, 105))
        temp_w = tempButtonTxt.get_width()+self.FONTSIZE*1.5
        self.autoButton = pygame.Surface((temp_w,tempButtonTxt.get_height()),flags=pygame.SRCALPHA).convert_alpha()
        self.autoButtonHovered = pygame.Surface((temp_w,tempButtonTxt.get_height()),flags=pygame.SRCALPHA).convert_alpha()
        self.autoButton.blit(tempButtonTxt,(0,0))
        self.autoButtonHovered.blit(self.FONT.render(dialog_txt["auto"],get_fontMode(),(255, 255, 255)),(0,0))
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
        showUI_img = pygame.transform.scale(pygame.image.load(os.path.join("Assets/image/UI/dialog_show.png")).convert_alpha(),(self.FONTSIZE,self.FONTSIZE))
        showUI_imgTemp = showUI_img.copy()
        showUI_imgTemp.fill((100,100,100), special_flags=pygame.BLEND_RGB_SUB)
        self.showButton = Button(showUI_imgTemp,window_x*0.05,window_y*0.05)
        self.showButton.setHoverImg(showUI_img)
        #历史回溯按钮
        history_img = pygame.transform.scale(pygame.image.load(os.path.join("Assets/image/UI/dialog_history.png")).convert_alpha(),(self.FONTSIZE,self.FONTSIZE))
        history_imgTemp = history_img.copy()
        history_imgTemp.fill((100,100,100), special_flags=pygame.BLEND_RGB_SUB)
        self.historyButton = Button(history_imgTemp,window_x*0.1,window_y*0.05)
        self.historyButton.setHoverImg(history_img)
    def display(self,screen,ifHide):
        if ifHide == True:
            self.showButton.display(screen)
            return "hide" if ifHover(self.showButton) else ""
        elif ifHide == False:
            self.hideButton.display(screen)
            self.historyButton.display(screen)
            action = ""
            if ifHover(self.skipButton):
                self.skipButtonHovered.draw(screen)
                action = "skip"
            else:
                self.skipButton.draw(screen)
            if ifHover(self.autoButton):
                self.autoButtonHovered.draw(screen)
                if self.autoMode == True:
                    rotatedIcon = pygame.transform.rotate(self.autoIconHovered,self.autoIconDegree)
                    screen.blit(rotatedIcon,(self.autoButtonHovered.description+self.autoIconHovered.get_width()/2-rotatedIcon.get_width()/2,self.autoButtonHovered.y+self.icon_y+self.autoIconHovered.get_height()/2-rotatedIcon.get_height()/2))
                    if self.autoIconDegree < 180:
                        self.autoIconDegree+=1
                    else:
                        self.autoIconDegree=0
                else:
                    screen.blit(self.autoIconHovered,(self.autoButtonHovered.description,self.autoButtonHovered.y+self.icon_y))
                action = "auto"
            else:
                if self.autoMode == True:
                    self.autoButtonHovered.draw(screen)
                    rotatedIcon = pygame.transform.rotate(self.autoIconHovered,self.autoIconDegree)
                    screen.blit(rotatedIcon,(self.autoButtonHovered.description+self.autoIconHovered.get_width()/2-rotatedIcon.get_width()/2,self.autoButtonHovered.y+self.icon_y+self.autoIconHovered.get_height()/2-rotatedIcon.get_height()/2))
                    if self.autoIconDegree < 180:
                        self.autoIconDegree+=1
                    else:
                        self.autoIconDegree=0
                else:
                    self.autoButton.draw(screen)
                    screen.blit(self.autoIcon,(self.autoButton.description,self.autoButton.y+self.icon_y))
            if ifHover(self.hideButton):
                action = "hide"
            elif ifHover(self.historyButton):
                action = "history"
            return action
    def autoModeSwitch(self):
        if self.autoMode == False:
            self.autoMode = True
        else:
            self.autoMode = False
            self.autoIconDegree = 0