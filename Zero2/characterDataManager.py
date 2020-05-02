# cython: language_level=3
import random
import os
import pygame
import glob
from Zero2.basic import fontRender,displayInCenter

class Doll:
    def __init__(self,action_point,attack_range,current_bullets,current_hp,effective_range,kind,faction,magazine_capacity,max_damage,max_hp,min_damage,type,x,y):
        self.current_action_point = action_point
        self.max_action_point = action_point
        self.attack_range = attack_range
        self.current_bullets = current_bullets
        self.current_hp = current_hp
        self.dying = False
        self.effective_range = effective_range
        self.max_effective_range = calculate_range(effective_range)
        self.kind = kind
        self.faction = faction
        self.gif_dic = character_gif_dic(type,faction)
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
            result_of_round["times_characters_down"] += 1
        return result_of_round
    def heal(self,hpHealed):
        self.current_hp+=hpHealed
        if self.faction == "character" and self.dying != False:
            self.dying == False
            self.gif_dic["die"]["imgId"] = 0
    def setFlip(self,theBool):
        if self.ifFlip != theBool:
            self.ifFlip = theBool
    def draw(self,action,screen,original_UI_img,perBlockWidth,perBlockHeight,local_x=0,local_y=0,isContinue=True):
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
        original_alpha = self.gif_dic[action]["img"][self.gif_dic[action]["imgId"]].get_alpha()
        img_of_char = pygame.transform.scale(self.gif_dic[action]["img"][self.gif_dic[action]["imgId"]], (round(perBlockWidth*2), round(perBlockWidth*2)))
        if self.faction == "character" and self.current_hp>0:
            if self.undetected == True:
                img_of_char.set_alpha(130)
            else:
                img_of_char.set_alpha(255)
        else:
            img_of_char.set_alpha(original_alpha)
        if self.ifFlip == True:
            img_of_char = pygame.transform.flip(img_of_char,True,False)
        #把角色图片画到屏幕上
        xTemp = (self.x-self.y)*perBlockWidth*0.43+local_x
        yTemp = (self.y+self.x)*perBlockWidth*0.2+local_y
        xTemp2 = xTemp + perBlockWidth*0.25
        yTemp2 = yTemp - perBlockWidth*0.2
        screen.blit(img_of_char,(xTemp-perBlockWidth*0.5,yTemp-perBlockWidth*1.15))
        if original_UI_img != None:
            hpEmptyScale = pygame.transform.scale(original_UI_img["hp_empty"], (round(perBlockWidth/2), round(perBlockHeight/10)))
            screen.blit(hpEmptyScale,(xTemp2,yTemp2))
            screen.blit(pygame.transform.scale(hp_img,(round(perBlockWidth*percent_of_hp/2),round(perBlockHeight/10))),(xTemp2,yTemp2))
            displayInCenter(current_hp_to_display,hpEmptyScale,xTemp2,yTemp2,screen)
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
    def set_imgId(self,action,theId):
        self.gif_dic[action]["imgId"] = theId
    def reset_imgId(self,action):
        self.gif_dic[action]["imgId"] = 0


class CharacterDataManager(Doll):
    def __init__(self,action_point,attack_range,current_bullets,current_hp,effective_range,kind,magazine_capacity,max_damage,max_hp,min_damage,type,x,y,bullets_carried,skill_effective_range,skill_cover_range,detect):
        Doll.__init__(self,action_point,attack_range,current_bullets,current_hp,effective_range,kind,"character",magazine_capacity,max_damage,max_hp,min_damage,type,x,y)
        self.bullets_carried = bullets_carried
        self.skill_effective_range = skill_effective_range
        self.max_skill_range = calculate_range(skill_effective_range)
        self.skill_cover_range = skill_cover_range
        self.undetected = detect

class SangvisFerriDataManager(Doll):
    def __init__(self,action_point,attack_range,current_bullets,current_hp,effective_range,kind,magazine_capacity,max_damage,max_hp,min_damage,type,x,y,patrol_path):
        Doll.__init__(self,action_point,attack_range,current_bullets,current_hp,effective_range,kind,"sangvisFerri",magazine_capacity,max_damage,max_hp,min_damage,type,x,y)
        self.patrol_path = patrol_path

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
def character_creator(character_name,action,faction="character"):
    if os.path.exists("Assets/image/"+faction+"/"+character_name+"/"+action):
        files_amount = len(glob.glob("Assets/image/"+faction+"/"+character_name+"/"+action+"/*.png"))
        path = "Assets/image/"+faction+"/"+character_name+"/"+action+"/"+character_name+"_"+action+"_NaN.png"
    elif os.path.exists("../Assets/image/"+faction+"/"+character_name+"/"+action):
        files_amount = len(glob.glob("../Assets/image/"+faction+"/"+character_name+"/"+action+"/*.png"))
        path = "../Assets/image/"+faction+"/"+character_name+"/"+action+"/"+character_name+"_"+action+"_NaN.png"
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
def character_gif_dic(character_name,faction="character",mode=None):
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