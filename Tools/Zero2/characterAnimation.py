import os
import pygame
#动图制作模块：接受一个友方角色名和动作,当前的方块标准长和高，返回对应角色动作list和
def character_creator(character_name,action,block_x_length,block_y_length,kind="character"):
    character_gif=[]
    files_amount = 0
    for file in os.listdir("../Assets/img/"+kind+"/"+character_name+"/"+action):
        files_amount+=1
    for i in range(files_amount):
        path = "../Assets/img/"+kind+"/"+character_name+"/"+action+"/"+character_name+"_"+action+"_"+str(i)+".png"
        character_gif.append(pygame.image.load(os.path.join(path)).convert_alpha())
    return [character_gif,files_amount]

#动图字典制作模块：接受一个友方角色名，返回对应的动图字典：
def character_gif_dic(character_name,block_x_length,block_y_length,kind="character"):
    if kind == "character":
        gif_dic = {
            "attack":[character_creator(character_name,"attack",block_x_length,block_y_length),0],
            "die":[character_creator(character_name,"die",block_x_length,block_y_length),0],
            "move":[character_creator(character_name,"move",block_x_length,block_y_length),0],
            "skill":[character_creator(character_name,"skill",block_x_length,block_y_length),0],
            #"victory":[character_creator(character_name,"victory",block_x_length,block_y_length),0],
            #"victoryloop":[character_creator(character_name,"victoryloop",block_x_length,block_y_length),0],
            "wait":[character_creator(character_name,"wait",block_x_length,block_y_length),0],
        }
    else:
        gif_dic = {
        "attack":[character_creator(character_name,"attack",block_x_length,block_y_length,kind),0],
        "die":[character_creator(character_name,"die",block_x_length,block_y_length,kind),0],
        "move":[character_creator(character_name,"move",block_x_length,block_y_length,kind),0],
        "wait":[character_creator(character_name,"wait",block_x_length,block_y_length,kind),0],
        }
    return gif_dic

