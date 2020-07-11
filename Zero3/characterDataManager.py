# cython: language_level=3
from Zero3.basic import *

class Doll:
    def __init__(self,action_point,attack_range,current_bullets,current_hp,effective_range,kind,faction,magazine_capacity,max_damage,max_hp,min_damage,type,x,y,mode):
        self.current_action_point = action_point
        self.max_action_point = action_point
        self.attack_range = attack_range
        self.current_bullets = current_bullets
        self.current_hp = current_hp
        self.dying = False if current_hp > 0 else 3
        self.effective_range = effective_range
        self.max_effective_range = calculate_range(effective_range)
        self.kind = kind
        self.faction = faction
        self.gif_dic = character_gif_dic(type,faction,mode)
        self.magazine_capacity = magazine_capacity
        self.max_damage = max_damage
        self.max_hp = max_hp
        self.min_damage = min_damage
        self.type = type
        self.ifFlip = False
        self.x = x
        self.y = y
    def decreaseHp(self,damage,result_of_round=None):
        self.current_hp-=damage
        if self.current_hp<=0:
            self.current_hp = 0
        if self.faction == "character" and self.dying == False and self.current_hp == 0 and self.kind != "HOC":
            self.dying = 3
            self.ImageGetHurt.x = -self.ImageGetHurt.width
            self.ImageGetHurt.set_alpha(255)
            self.ImageGetHurt.yToGo = 255
            result_of_round["times_characters_down"] += 1
        return result_of_round
    def heal(self,hpHealed):
        self.current_hp+=hpHealed
        if self.faction == "character" and self.dying != False:
            self.dying = False
    def setFlip(self,theBool):
        if self.ifFlip != theBool:
            self.ifFlip = theBool
    def draw(self,action,screen,theMapClass,isContinue=True):
        #调整小人图片的尺寸
        img_of_char = pygame.transform.scale(self.gif_dic[action]["img"][self.gif_dic[action]["imgId"]], (round(theMapClass.perBlockWidth*1.6), round(theMapClass.perBlockWidth*1.6)))
        #反转图片
        if self.ifFlip == True:
            img_of_char = pygame.transform.flip(img_of_char,True,False)
        #把角色图片画到屏幕上
        xTemp,yTemp = theMapClass.calPosInMap(self.x,self.y)
        screen.blit(img_of_char,(xTemp-theMapClass.perBlockWidth*0.3,yTemp-theMapClass.perBlockWidth*0.85))
        #调整id，并返回对应的bool状态
        if self.gif_dic[action]["imgId"] < self.gif_dic[action]["imgNum"]-1:
            self.gif_dic[action]["imgId"] += 1
            return True
        else:
            if isContinue == True:
                self.gif_dic[action]["imgId"] = 0
                return True
            else:
                return False
    def drawUI(self,screen,original_UI_img,theMapClass):
        hp_img = None
        if self.dying == False:
            if original_UI_img != None:
                hp_img = original_UI_img["hp_green"]
            current_hp_to_display = fontRender(str(self.current_hp)+"/"+str(self.max_hp),"black",10)
            percent_of_hp = self.current_hp/self.max_hp
        else:
            if original_UI_img != None:
                hp_img = original_UI_img["hp_red"]
            current_hp_to_display = fontRender(str(self.dying)+"/3","black",10)
            percent_of_hp = self.dying/3
        #把角色图片画到屏幕上
        xTemp,yTemp = theMapClass.calPosInMap(self.x,self.y)
        xTemp += theMapClass.perBlockWidth*0.25
        yTemp -= theMapClass.perBlockWidth*0.2
        if self.faction == "character" and self.detection != None:
            eyeImgWidth = round(theMapClass.perBlockWidth/6*self.eyeImgSize)
            eyeImgHeight = round(theMapClass.perBlockWidth/10*self.eyeImgSize)
            numberX = (eyeImgWidth - theMapClass.perBlockWidth/6)/2
            numberY = (eyeImgHeight - theMapClass.perBlockWidth/10)/2
            if self.detection == True:
                screen.blit(resizeImg(original_UI_img["eye_red"], (eyeImgWidth,eyeImgHeight)),(xTemp+theMapClass.perBlockWidth*0.51-numberX,yTemp-numberY))
            elif self.detection == False:
                screen.blit(resizeImg(original_UI_img["eye_orange"], (eyeImgWidth,eyeImgHeight)),(xTemp+theMapClass.perBlockWidth*0.51-numberX,yTemp-numberY))
            if self.eyeImgSize > 1:
                self.eyeImgSize-=1
            if self.kind != "HOC" and self.ImageGetHurt.x != None:
                self.ImageGetHurt.draw(screen)
                if self.ImageGetHurt.x < self.ImageGetHurt.width/4:
                    self.ImageGetHurt.x += self.ImageGetHurt.width/25
                else:
                    if self.ImageGetHurt.yToGo > 0:
                        self.ImageGetHurt.yToGo -= 5
                    else:
                        alphaTemp = self.ImageGetHurt.get_alpha()
                        if alphaTemp > 0:
                            self.ImageGetHurt.set_alpha(alphaTemp-2)
                        else:
                            self.ImageGetHurt.x = None
        hpEmptyScale = pygame.transform.scale(original_UI_img["hp_empty"], (round(theMapClass.perBlockWidth/2), round(theMapClass.perBlockWidth/10)))
        screen.blit(hpEmptyScale,(xTemp,yTemp))
        screen.blit(pygame.transform.scale(hp_img,(round(theMapClass.perBlockWidth*percent_of_hp/2),round(theMapClass.perBlockWidth/10))),(xTemp,yTemp))
        displayInCenter(current_hp_to_display,hpEmptyScale,xTemp,yTemp,screen)
    #获取角色特定动作的图片播放ID
    def get_imgId(self,action):
        return self.gif_dic[action]["imgId"]
    #设定角色特定动作的图片播放ID
    def set_imgId(self,action,theId):
        self.gif_dic[action]["imgId"] = theId
    #重置角色特定动作的图片播放ID
    def reset_imgId(self,action):
        self.gif_dic[action]["imgId"] = 0
    #调整角色的隐蔽度
    def noticed(self,force=False):
        if force == False:
            if self.detection == None:
                self.eyeImgSize = 10
                self.detection = False
            elif self.detection == False:
                self.eyeImgSize = 10
                self.detection = True
        elif force == True:
            self.eyeImgSize = 10
            self.detection = True
    #获取角色的攻击范围
    def getAttackRange(self,theMap):
        attacking_range = {"near":[],"middle":[],"far":[]}
        for y in range(self.y-self.max_effective_range,self.y+self.max_effective_range+1):
            if y < self.y:
                for x in range(self.x-self.max_effective_range-(y-self.y),self.x+self.max_effective_range+(y-self.y)+1):
                    if len(theMap.mapData)>y>=0 and len(theMap.mapData[y])>x>=0:
                        if "far" in self.effective_range and self.effective_range["far"] != None and self.effective_range["far"][0] <= abs(x-self.x)+abs(y-self.y) <= self.effective_range["far"][1]:
                            attacking_range["far"].append((x,y))
                        elif "middle" in self.effective_range and self.effective_range["middle"] != None and self.effective_range["middle"][0] <= abs(x-self.x)+abs(y-self.y) <= self.effective_range["middle"][1]:
                            attacking_range["middle"].append((x,y))
                        elif "near" in self.effective_range and self.effective_range["near"] != None and self.effective_range["near"][0] <= abs(x-self.x)+abs(y-self.y) <= self.effective_range["near"][1]:
                            attacking_range["near"].append((x,y))
            else:
                for x in range(self.x-self.max_effective_range+(y-self.y),self.x+self.max_effective_range-(y-self.y)+1):
                    if x == self.x and y == self.y:
                        pass
                    elif len(theMap.mapData)>y>=0 and len(theMap.mapData[y])>x>=0:
                        if "far" in self.effective_range and self.effective_range["far"] != None and self.effective_range["far"][0] <= abs(x-self.x)+abs(y-self.y) <= self.effective_range["far"][1]:
                            attacking_range["far"].append((x,y))
                        elif "middle" in self.effective_range and self.effective_range["middle"] != None and self.effective_range["middle"][0] <= abs(x-self.x)+abs(y-self.y) <= self.effective_range["middle"][1]:
                            attacking_range["middle"].append((x,y))
                        elif "near" in self.effective_range and self.effective_range["near"] != None and self.effective_range["near"][0] <= abs(x-self.x)+abs(y-self.y) <= self.effective_range["near"][1]:
                            attacking_range["near"].append((x,y))
        return attacking_range

#格里芬角色类
class CharacterDataManager(Doll):
    def __init__(self,window_y,theCharacterDataDic,mode=None):
        Doll.__init__(self,theCharacterDataDic["action_point"],theCharacterDataDic["attack_range"],theCharacterDataDic["current_bullets"],theCharacterDataDic["current_hp"],theCharacterDataDic["effective_range"],theCharacterDataDic["kind"],"character",theCharacterDataDic["magazine_capacity"],theCharacterDataDic["max_damage"],theCharacterDataDic["max_hp"],theCharacterDataDic["min_damage"],theCharacterDataDic["type"],theCharacterDataDic["x"],theCharacterDataDic["y"],mode)
        self.bullets_carried = theCharacterDataDic["bullets_carried"]
        self.skill_effective_range = theCharacterDataDic["skill_effective_range"]
        self.max_skill_range = calculate_range(theCharacterDataDic["skill_effective_range"])
        self.skill_cover_range = theCharacterDataDic["skill_cover_range"]
        self.detection = theCharacterDataDic["detection"]
        self.eyeImgSize = 0
        if theCharacterDataDic["kind"] != "HOC":
            try:
                self.ImageGetHurt = loadImage("Assets/image/npc/"+theCharacterDataDic["type"]+"_hurt.png",(None,window_y/4),window_y/2,window_y/2)
            except BaseException:
                print('警告：角色 {} 没有对应的破衣动画'.format(theCharacterDataDic["type"]))
                if not os.path.exists("Assets/image/npc_icon/{}.png".format(theCharacterDataDic["type"])):
                    print("而且你也忘了加入对应的头像")

#铁血角色类
class SangvisFerriDataManager(Doll):
    def __init__(self,theSangvisFerrisDataDic,mode=None):
        Doll.__init__(self,theSangvisFerrisDataDic["action_point"],theSangvisFerrisDataDic["attack_range"],theSangvisFerrisDataDic["current_bullets"],theSangvisFerrisDataDic["current_hp"],theSangvisFerrisDataDic["effective_range"],theSangvisFerrisDataDic["kind"],"sangvisFerri",theSangvisFerrisDataDic["magazine_capacity"],theSangvisFerrisDataDic["max_damage"],theSangvisFerrisDataDic["max_hp"],theSangvisFerrisDataDic["min_damage"],theSangvisFerrisDataDic["type"],theSangvisFerrisDataDic["x"],theSangvisFerrisDataDic["y"],mode)
        self.patrol_path = theSangvisFerrisDataDic["patrol_path"]

#计算最远攻击距离
def calculate_range(effective_range_dic):
    if effective_range_dic != None:
        max_attack_range = 0
        if "far" in effective_range_dic and effective_range_dic["far"] != None and max_attack_range < effective_range_dic["far"][-1]:
            max_attack_range = effective_range_dic["far"][-1]
        if "middle" in effective_range_dic and effective_range_dic["middle"] != None and max_attack_range < effective_range_dic["middle"][-1]:
            max_attack_range = effective_range_dic["middle"][-1]
        if "near" in effective_range_dic and effective_range_dic["near"] != None and max_attack_range < effective_range_dic["near"][-1]:
            max_attack_range = effective_range_dic["near"][-1]
        return max_attack_range
    else:
        return None

#动图制作模块：接受一个友方角色名和动作,当前的方块标准长和高，返回对应角色动作list或者因为没图片而返回None
#810*810 possition:405/567
def character_creator(character_name,action,faction):
    if os.path.exists("Assets/image/"+faction+"/"+character_name+"/"+action):
        files_amount = len(glob.glob("Assets/image/"+faction+"/"+character_name+"/"+action+"/*.png"))
        path = "Assets/image/"+faction+"/"+character_name+"/"+action+"/"+character_name+"_"+action+"_NaN.png"
    else:
        return None
    character_gif=[]
    if files_amount > 0:
        for i in range(files_amount):
            character_gif.append(pygame.image.load(os.path.join(path.replace("NaN",str(i)))).convert_alpha())
        return {
            "img":character_gif,
            "imgId":0,
            "imgNum":files_amount
        }
    else:
        return None

#动图字典制作模块：接受一个友方角色名，返回对应的动图字典：
def character_gif_dic(character_name,faction,mode):
    if mode == None:
        gif_dic = {
            "attack":character_creator(character_name,"attack",faction),
            "attack2":character_creator(character_name,"attack2",faction),
            "move":character_creator(character_name,"move",faction),
            "reload":character_creator(character_name,"reload",faction),
            "repair":character_creator(character_name,"reload",faction),
            "set":character_creator(character_name,"set",faction),
            "skill":character_creator(character_name,"skill",faction),
            "victory":character_creator(character_name,"victory",faction),
            "victoryloop":character_creator(character_name,"victoryloop",faction),
            "wait":character_creator(character_name,"wait",faction),
            "wait2":character_creator(character_name,"wait2",faction),
        }
        if faction == "character":
            gif_dic["die"] = character_creator(character_name,"die",faction)
        else:
            temp_list = ["","2","3"]
            gif_dic["die"] = character_creator(character_name,"die"+temp_list[random.randint(0,2)],faction)
            if gif_dic["die"]==None:
                gif_dic["die"] = character_creator(character_name,"die",faction)
    elif mode == "dev":
        gif_dic = {"wait":character_creator(character_name,"wait",faction)}
    else:
        raise Exception('Error: Mode does not exist.')
    return gif_dic