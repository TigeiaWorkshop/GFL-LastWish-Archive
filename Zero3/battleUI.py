# cython: language_level=3
from Zero3.basic import *

#显示回合切换的UI
class RoundSwitch:
    def __init__(self,window_x,window_y,battleUiTxt):
        self.lineRedDown = loadImg("Assets/image/UI/lineRed.png",window_x,window_y/50)
        self.lineRedUp = pygame.transform.rotate(self.lineRedDown, 180)
        self.lineGreenDown = loadImg("Assets/image/UI/lineGreen.png",window_x,window_y/50)
        self.lineGreenUp = pygame.transform.rotate(self.lineGreenDown, 180)
        self.baseImg = loadImg("Assets/image/UI/roundSwitchBase.png",window_x,window_y/5)
        self.baseImg.set_alpha(0)
        self.x = -window_x
        self.y = int((window_y - self.baseImg.get_height())/2)
        self.y2 = self.y+self.baseImg.get_height()-self.lineRedDown.get_height()
        self.baseAlphaUp = True
        self.TxtAlphaUp = True
        self.idleTime = 60
        self.now_total_rounds_text = battleUiTxt["numRound"]
        self.now_total_rounds_surface = None
        self.your_round_txt_surface = fontRender(battleUiTxt["yourRound"], "white",window_x/36)
        self.your_round_txt_surface.set_alpha(0)
        self.enemy_round_txt_surface = fontRender(battleUiTxt["enemyRound"], "white",window_x/36)
        self.enemy_round_txt_surface.set_alpha(0)
    def display(self,screen,whose_round,total_rounds):
        #如果“第N回合”的文字surface还没有初始化，则初始化该文字
        if self.now_total_rounds_surface == None:
            self.now_total_rounds_surface = fontRender(self.now_total_rounds_text.replace("NaN",str(total_rounds)), "white",screen.get_width()/38)
            self.now_total_rounds_surface.set_alpha(0)
        #如果UI底的alpha值在渐入阶段
        if self.baseAlphaUp == True:
            alphaTemp = self.baseImg.get_alpha()
            #如果值还未到255（即完全显露），则继续增加，反之如果x到0了再进入淡出阶段
            if alphaTemp > 250 and self.x >= 0:
                self.baseAlphaUp = False
            elif alphaTemp <= 250 :
                self.baseImg.set_alpha(alphaTemp+5)
        #如果UI底的alpha值在淡出阶段
        elif self.baseAlphaUp == False:
            #如果文字不在淡出阶段
            if self.TxtAlphaUp == True:
                alphaTemp = self.now_total_rounds_surface.get_alpha()
                #“第N回合”的文字先渐入
                if alphaTemp < 250:
                    self.now_total_rounds_surface.set_alpha(alphaTemp+10)
                else:
                    #然后“谁的回合”的文字渐入
                    if whose_round == "playerToSangvisFerris":
                        alphaTemp = self.enemy_round_txt_surface.get_alpha()
                        if alphaTemp < 250:
                            self.enemy_round_txt_surface.set_alpha(alphaTemp+10)
                        else:
                            self.TxtAlphaUp = False
                    if whose_round == "sangvisFerrisToPlayer":
                        alphaTemp = self.your_round_txt_surface.get_alpha()
                        if alphaTemp < 250:
                            self.your_round_txt_surface.set_alpha(alphaTemp+10)
                        else:
                            self.TxtAlphaUp = False
            #如果2个文字都渐入完了，会进入idle时间
            elif self.idleTime > 0:
                self.idleTime -= 1
            #如果idle时间结束，则所有UI开始淡出
            else:
                alphaTemp = self.baseImg.get_alpha()
                if alphaTemp > 0:
                    alphaTemp -= 10
                    self.baseImg.set_alpha(alphaTemp)
                    self.now_total_rounds_surface.set_alpha(alphaTemp)
                    if whose_round == "playerToSangvisFerris":
                        self.lineRedUp.set_alpha(alphaTemp)
                        self.lineRedDown.set_alpha(alphaTemp)
                        self.enemy_round_txt_surface.set_alpha(alphaTemp)
                    elif whose_round == "sangvisFerrisToPlayer":
                        self.lineGreenUp.set_alpha(alphaTemp)
                        self.lineGreenDown.set_alpha(alphaTemp)
                        self.your_round_txt_surface.set_alpha(alphaTemp)
                else:
                    if whose_round == "playerToSangvisFerris":
                        self.lineRedUp.set_alpha(255)
                        self.lineRedDown.set_alpha(255)
                    elif whose_round == "sangvisFerrisToPlayer":
                        self.lineGreenUp.set_alpha(255)
                        self.lineGreenDown.set_alpha(255)
                    #淡出完成，重置部分参数，UI播放结束
                    self.x = -screen.get_width()
                    self.baseAlphaUp = True
                    self.TxtAlphaUp = True
                    self.idleTime = 60
                    self.now_total_rounds_surface = None
                    return True
        #横条移动
        if self.x < 0:
            self.x += screen.get_width()/35
        #展示UI
        drawImg(self.baseImg,(0,self.y),screen)
        drawImg(self.now_total_rounds_surface,(screen.get_width()/2-self.now_total_rounds_surface.get_width(),self.y+screen.get_width()/36),screen)
        if whose_round == "playerToSangvisFerris":
            drawImg(self.lineRedUp,(abs(self.x),self.y),screen)
            drawImg(self.lineRedDown,(self.x,self.y2),screen)
            drawImg(self.enemy_round_txt_surface,(screen.get_width()/2,self.y+screen.get_width()/18),screen)
        elif whose_round == "sangvisFerrisToPlayer":
            drawImg(self.lineGreenUp,(abs(self.x),self.y),screen)
            drawImg(self.lineGreenDown,(self.x,self.y2),screen)
            drawImg(self.your_round_txt_surface,(screen.get_width()/2,self.y+screen.get_width()/18),screen)
        #如果UI展示还未完成，返回False
        return False

#警告系统
class WarningSystem:
    def __init__(self,warningsTxt):
        self.all_warnings = []
        self.warnings = warningsTxt
    def add(self,the_warning,fontSize=30):
        if len(self.all_warnings)>=5:
            self.all_warnings.pop()
        self.all_warnings.insert(0,fontRender(self.warnings[the_warning],"red",fontSize,True))
    def display(self,screen):
        for i in range(len(self.all_warnings)):
            try:
                img_alpha = self.all_warnings[i].get_alpha()
            except BaseException:
                break
            if img_alpha > 0:
                screen.blit(self.all_warnings[i],((screen.get_width()-self.all_warnings[i].get_width())/2,(screen.get_height()-self.all_warnings[i].get_height())/2+i*self.all_warnings[i].get_height()*1.2))
                self.all_warnings[i].set_alpha(img_alpha-5)
            else:
                del self.all_warnings[i]
    def empty(self):
        self.all_warnings = []

#角色行动选项菜单
class SelectMenu:
    def __init__(self,selectMenuTxtDic):
        self.selectButtonImg = loadImg("Assets/image/UI/menu.png")
        #攻击
        self.attackAP = 5
        self.attackTxt = selectMenuTxtDic["attack"]
        self.attackAPTxt = str(self.attackAP)+" AP"
        #移动
        self.moveAP = 2
        self.moveTxt = selectMenuTxtDic["move"]
        self.moveAPTxt = str(self.moveAP)+"N AP"
        #换弹
        self.reloadAP = 5
        self.reloadTxt = selectMenuTxtDic["reload"]
        self.reloadAPTxt = str(self.reloadAP)+" AP"
        #技能
        self.skillAP = 8
        self.skillTxt = selectMenuTxtDic["skill"]
        self.skillAPTxt = str(self.skillAP)+" AP"
        #救助
        self.rescueAP = 8
        self.rescueTxt = selectMenuTxtDic["rescue"]
        self.rescueAPTxt = str(self.rescueAP)+" AP"
    def display(self,screen,fontSize,location,kind,friendsCanSave,controller):
        selectButtonBase =  resizeImg(self.selectButtonImg, (round(fontSize*5), round(fontSize*2.5)))
        selectButtonBaseWidth = selectButtonBase.get_width()
        buttonGetHover = None
        sizeBig = int(fontSize)
        sizeSmall = int(fontSize*0.75)
        #攻击按钮 - 左
        txt_temp = fontRender(self.attackTxt,"black",sizeBig)
        txt_temp2 = fontRender(self.attackAPTxt,"black",sizeSmall)
        txt_tempX = location["xStart"]-selectButtonBaseWidth*0.6
        txt_tempY = location["yStart"]
        if controller.ifHover(selectButtonBase,(txt_tempX,txt_tempY)):
            buttonGetHover = "attack"
        screen.blit(selectButtonBase,(txt_tempX,txt_tempY))
        screen.blit(txt_temp,((selectButtonBaseWidth-txt_temp.get_width())/2+txt_tempX,txt_temp.get_height()*0.4+txt_tempY))
        screen.blit(txt_temp2,((selectButtonBaseWidth-txt_temp2.get_width())/2+txt_tempX,txt_temp.get_height()*1.5+txt_tempY))
        #移动按钮 - 右
        txt_temp = fontRender(self.moveTxt,"black",sizeBig)
        txt_temp2 = fontRender(self.moveAPTxt,"black",sizeSmall)
        txt_tempX = location["xEnd"]-selectButtonBaseWidth*0.4
        #txt_tempY 与攻击按钮一致
        if controller.ifHover(selectButtonBase,(txt_tempX,txt_tempY)):
            buttonGetHover = "move"
        screen.blit(selectButtonBase,(txt_tempX,txt_tempY))
        screen.blit(txt_temp,((selectButtonBaseWidth-txt_temp.get_width())/2+txt_tempX,txt_temp.get_height()*0.4+txt_tempY))
        screen.blit(txt_temp2,((selectButtonBaseWidth-txt_temp2.get_width())/2+txt_tempX,txt_temp.get_height()*1.5+txt_tempY))
        #换弹按钮 - 下
        txt_temp = fontRender(self.reloadTxt,"black",sizeBig)
        txt_temp2 = fontRender(self.reloadAPTxt,"black",sizeSmall)
        txt_tempX = location["xStart"]+selectButtonBaseWidth*0.5
        txt_tempY = location["yEnd"]-selectButtonBaseWidth*0.25
        if controller.ifHover(selectButtonBase,(txt_tempX,txt_tempY)):
            buttonGetHover = "reload"
        screen.blit(selectButtonBase,(txt_tempX,txt_tempY))
        screen.blit(txt_temp,((selectButtonBaseWidth-txt_temp.get_width())/2+txt_tempX,txt_temp.get_height()*0.4+txt_tempY))
        screen.blit(txt_temp2,((selectButtonBaseWidth-txt_temp2.get_width())/2+txt_tempX,txt_temp.get_height()*1.5+txt_tempY))
        #技能按钮 - 上
        if kind != "HOC":
            txt_temp = fontRender(self.skillTxt,"black",sizeBig)
            txt_temp2 = fontRender(self.skillAPTxt,"black",sizeSmall)
            #txt_tempX与换弹按钮一致
            txt_tempY = location["yStart"]-selectButtonBaseWidth*0.7
            if controller.ifHover(selectButtonBase,(txt_tempX,txt_tempY)):
                buttonGetHover = "skill"
            screen.blit(selectButtonBase,(txt_tempX,txt_tempY))
            screen.blit(txt_temp,((selectButtonBaseWidth-txt_temp.get_width())/2+txt_tempX,txt_temp.get_height()*0.4+txt_tempY))
            screen.blit(txt_temp2,((selectButtonBaseWidth-txt_temp2.get_width())/2+txt_tempX,txt_temp.get_height()*1.5+txt_tempY))
        #救助队友
        if len(friendsCanSave)>0:
            txt_temp = fontRender(self.rescueTxt,"black",sizeBig)
            txt_temp2 = fontRender(self.rescueAPTxt,"black",sizeSmall)
            txt_tempX = location["xStart"]-selectButtonBaseWidth*0.6
            txt_tempY = location["yStart"]-selectButtonBaseWidth*0.7
            if controller.ifHover(selectButtonBase,(txt_tempX,txt_tempY)):
                buttonGetHover = "rescue"
            screen.blit(selectButtonBase,(txt_tempX,txt_tempY))
            screen.blit(txt_temp,((selectButtonBaseWidth-txt_temp.get_width())/2+txt_tempX,txt_temp.get_height()*0.4+txt_tempY))
            screen.blit(txt_temp2,((selectButtonBaseWidth-txt_temp2.get_width())/2+txt_tempX,txt_temp.get_height()*1.5+txt_tempY))
        return buttonGetHover

#角色信息版
class CharacterInfoBoard:
    def __init__(self,window_x,window_y,text_size=20):
        self.boardImg = loadImage("Assets/image/UI/score.png",(0,window_y-window_y/6),window_x/5,window_y/6)
        self.characterIconImages = {}
        all_icon_file_list = glob.glob(r'Assets/image/npc_icon/*.png')
        for i in range(len(all_icon_file_list)):
            img_name = all_icon_file_list[i].replace("Assets","").replace("image","").replace("npc_icon","").replace(".png","").replace("\\","").replace("/","")
            self.characterIconImages[img_name] = loadImg(all_icon_file_list[i],window_y*0.08,window_y*0.08)
        del all_icon_file_list
        self.text_size = text_size
    def display(self,screen,theCharacterData,original_UI_img):
        self.boardImg.draw(screen)
        padding = (self.boardImg.height-self.characterIconImages[theCharacterData.type].get_height())/2
        #画出角色图标
        screen.blit(self.characterIconImages[theCharacterData.type],(self.boardImg.x+padding,self.boardImg.y+padding))
        #加载所需的文字
        tcgc_hp1 = fontRender("HP: ","white",screen.get_width()/96)
        tcgc_hp2 = fontRender(str(theCharacterData.current_hp)+"/"+str(theCharacterData.max_hp),"black",screen.get_width()/96)
        tcgc_action_point1 = fontRender("AP: ","white",screen.get_width()/96)
        tcgc_action_point2 = fontRender(str(theCharacterData.current_action_point)+"/"+str(theCharacterData.max_action_point),"black",screen.get_width()/96)
        tcgc_bullets_situation1 = fontRender("BP: ","white",screen.get_width()/96)
        tcgc_bullets_situation2 = fontRender(str(theCharacterData.current_bullets)+"/"+str(theCharacterData.bullets_carried),"black",screen.get_width()/96)
        #先画出hp,ap和bp的文字
        temp_posX = self.characterIconImages[theCharacterData.type].get_width()*2+self.boardImg.x
        temp_posY = padding+self.boardImg.y
        screen.blit(tcgc_hp1,(temp_posX,temp_posY))
        screen.blit(tcgc_action_point1,(temp_posX,temp_posY+self.text_size*1.5))
        screen.blit(tcgc_bullets_situation1,(temp_posX,temp_posY+self.text_size*3))
        #画出底部空白的血条格
        hp_empty = resizeImg(original_UI_img["hp_empty"],(int(self.boardImg.width/3),int(self.text_size)))
        temp_posX = self.characterIconImages[theCharacterData.type].get_width()*2.4+self.boardImg.x
        temp_posY = padding+self.boardImg.y
        screen.blit(hp_empty,(temp_posX,temp_posY))
        screen.blit(hp_empty,(temp_posX,temp_posY+self.text_size*1.5))
        screen.blit(hp_empty,(temp_posX,temp_posY+self.text_size*3))
        #画出三个信息条
        screen.blit(resizeImg(original_UI_img["hp_green"],(int(hp_empty.get_width()*theCharacterData.current_hp/theCharacterData.max_hp),int(self.text_size))),(temp_posX ,temp_posY))
        screen.blit(resizeImg(original_UI_img["action_point_blue"],(int(hp_empty.get_width()*theCharacterData.current_action_point/theCharacterData.max_action_point),int(self.text_size))),(temp_posX ,temp_posY+self.text_size*1.5))
        screen.blit(resizeImg(original_UI_img["bullets_number_brown"],(int(hp_empty.get_width()*theCharacterData.current_bullets/theCharacterData.magazine_capacity),int(self.text_size))),(temp_posX ,temp_posY+self.text_size*3))
        displayInCenter(tcgc_hp2,hp_empty,temp_posX ,temp_posY,screen)
        displayInCenter(tcgc_action_point2,hp_empty,temp_posX ,temp_posY+self.text_size*1.5,screen)
        displayInCenter(tcgc_bullets_situation2,hp_empty,temp_posX ,temp_posY+self.text_size*3,screen)

#计分板
class ResultBoard:
    def __init__(self,resultTxt,finalResult,window_x,window_y):
        self.boardImg = loadImg("Assets/image/UI/score.png",window_x/6,window_x/3)
        self.x = int(window_x/9.6)
        self.y = int(window_x/9.6)
        self.txt_x = int(window_x/7.68)
        self.total_kills = fontRender(resultTxt["total_kills"]+": "+str(finalResult["total_kills"]),"white",window_x/96)
        self.total_time = fontRender(resultTxt["total_time"]+": "+str(time.strftime('%M:%S',finalResult["total_time"])),"white",window_x/96)
        self.total_rounds_txt = fontRender(resultTxt["total_rounds"]+": "+str(finalResult["total_rounds"]),"white",window_x/96)
        self.characters_down = fontRender(resultTxt["characters_down"]+": "+str(finalResult["times_characters_down"]),"white",window_x/96)
        self.player_rate = fontRender(resultTxt["rank"]+": "+"A","white",window_x/96)
        self.pressKeyContinue = fontRender(resultTxt["pressKeyContinue"],"white",window_x/96)
    def display(self,screen):
        screen.blit(self.boardImg,(self.x,self.y))
        screen.blit(self.total_kills,(self.txt_x ,300))
        screen.blit(self.total_time,(self.txt_x ,350))
        screen.blit(self.total_rounds_txt ,(self.txt_x ,400))
        screen.blit(self.characters_down,(self.txt_x ,450))
        screen.blit(self.player_rate,(self.txt_x ,500))
        screen.blit(self.pressKeyContinue,(self.txt_x ,700))

#章节标题(在加载时显示)
class LoadingTitle:
    def __init__(self,window_x,window_y,numChapter_txt,chapter_name,chapterTitle_txt,chapterDesc_txt):
        self.black_bg = loadImage("Assets/image/UI/black.png",(0,0),window_x,window_y)
        title_chapterNum = fontRender(numChapter_txt.replace("NaN",chapter_name.replace("chapter","")),"white",window_x/38)
        self.title_chapterNum = ImageSurface(title_chapterNum,(window_x-title_chapterNum.get_width())/2,window_y*0.37)
        title_chapterName = fontRender(chapterTitle_txt,"white",window_x/38)
        self.title_chapterName = ImageSurface(title_chapterName,(window_x-title_chapterName.get_width())/2,window_y*0.46)
        title_description = fontRender(chapterDesc_txt,"white",window_x/76)
        self.title_description = ImageSurface(title_description,(window_x-title_description.get_width())/2,window_y*0.6)
    def display(self,screen,alpha=255):
        self.title_chapterNum.set_alpha(alpha)
        self.title_chapterName.set_alpha(alpha)
        self.title_description.set_alpha(alpha)
        self.black_bg.draw(screen)
        self.title_chapterNum.draw(screen)
        self.title_chapterName.draw(screen)
        self.title_description.draw(screen)