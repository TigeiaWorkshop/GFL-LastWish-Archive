import os
import pygame
import random
#动图制作模块：接受一个友方角色名和动作,当前的方块标准长和高，返回对应角色动作list或者因为没图片而返回None
#810*810 possition:405/567
def character_creator(character_name,action,kind="character"):
    character_gif=[]
    files_amount = 0
    if os.path.exists("../Assets/image/"+kind+"/"+character_name+"/"+action):
        for file in os.listdir("../Assets/image/"+kind+"/"+character_name+"/"+action):
            files_amount+=1
        for i in range(files_amount):
            path = "../Assets/image/"+kind+"/"+character_name+"/"+action+"/"+character_name+"_"+action+"_"+str(i)+".png"
            character_gif.append(pygame.transform.scale(pygame.image.load(os.path.join(path)).convert_alpha(), (375, 375)))
        return [[character_gif,files_amount],0]
    elif os.path.exists("Assets/image/"+kind+"/"+character_name+"/"+action):
        for file in os.listdir("Assets/image/"+kind+"/"+character_name+"/"+action):
            files_amount+=1
        for i in range(files_amount):
            path = "Assets/image/"+kind+"/"+character_name+"/"+action+"/"+character_name+"_"+action+"_"+str(i)+".png"
            character_gif.append(pygame.transform.scale(pygame.image.load(os.path.join(path)).convert_alpha(), (375, 375)))
        return [[character_gif,files_amount],0]
    else:
        return None

#动图字典制作模块：接受一个友方角色名，返回对应的动图字典：
def character_gif_dic(character_name,kind="character"):
    gif_dic = {
        "attack":character_creator(character_name,"attack",kind),
        "attack2":character_creator(character_name,"attack2",kind),
        "move":character_creator(character_name,"move",kind),
        "reload":character_creator(character_name,"reload",kind),
        "repair":character_creator(character_name,"reload",kind),
        "set":character_creator(character_name,"set",kind),
        "skill":character_creator(character_name,"skill",kind),
        "victory":character_creator(character_name,"victory",kind),
        "victoryloop":character_creator(character_name,"victoryloop",kind),
        "wait":character_creator(character_name,"wait",kind),
        "wait2":character_creator(character_name,"wait2",kind),
    }
    if kind == "character" or "jupiter" in character_name.lower():
        gif_dic["die"] = character_creator(character_name,"die",kind)
    else:
        temp = random.randint(0,2)
        if temp == 0:
            gif_dic["die"] = character_creator(character_name,"die",kind)
        else:
            temp = str(temp+1)
            gif_dic["die"] = character_creator(character_name,"die"+temp,kind)
    return gif_dic