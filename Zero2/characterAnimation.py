import os
import pygame
#动图制作模块：接受一个友方角色名和动作,当前的方块标准长和高，返回对应角色动作list和
def character_creator(character_name,action,block_x_length,block_y_length,kind="character"):
    character_gif=[]
    files_amount = 0
    if os.path.exists("../Assets/img/"+kind+"/"+character_name+"/"+action):
        for file in os.listdir("../Assets/img/"+kind+"/"+character_name+"/"+action):
            files_amount+=1
        for i in range(files_amount):
            path = "../Assets/img/"+kind+"/"+character_name+"/"+action+"/"+character_name+"_"+action+"_"+str(i)+".png"
            character_gif.append(pygame.image.load(os.path.join(path)).convert_alpha())
        return [[character_gif,files_amount],0]
    elif os.path.exists("Assets/img/"+kind+"/"+character_name+"/"+action):
        for file in os.listdir("Assets/img/"+kind+"/"+character_name+"/"+action):
            files_amount+=1
        for i in range(files_amount):
            path = "Assets/img/"+kind+"/"+character_name+"/"+action+"/"+character_name+"_"+action+"_"+str(i)+".png"
            character_gif.append(pygame.image.load(os.path.join(path)).convert_alpha())
        return [[character_gif,files_amount],0]
    else:
        return None

#动图字典制作模块：接受一个友方角色名，返回对应的动图字典：
def character_gif_dic(character_name,block_x_length,block_y_length,kind="character"):
    gif_dic = {
        "attack":character_creator(character_name,"attack",block_x_length,block_y_length,kind),
        "attack2":character_creator(character_name,"attack2",block_x_length,block_y_length,kind),
        "die":character_creator(character_name,"die",block_x_length,block_y_length,kind),
        "move":character_creator(character_name,"move",block_x_length,block_y_length,kind),
        "reload":character_creator(character_name,"reload",block_x_length,block_y_length,kind),
        "set":character_creator(character_name,"set",block_x_length,block_y_length,kind),
        "skill":character_creator(character_name,"skill",block_x_length,block_y_length,kind),
        "victory":character_creator(character_name,"victory",block_x_length,block_y_length,kind),
        "victoryloop":character_creator(character_name,"victoryloop",block_x_length,block_y_length,kind),
        "wait":character_creator(character_name,"wait",block_x_length,block_y_length,kind),
        "wait2":character_creator(character_name,"wait2",block_x_length,block_y_length,kind),
    }
    return gif_dic