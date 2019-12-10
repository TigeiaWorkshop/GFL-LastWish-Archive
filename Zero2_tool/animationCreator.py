import pygame
import os

#动图制作模块：接受一个友方角色名和动作,当前的方块标准长和高，返回对应角色动作list和
def character_creator(character_name,action,block_x_length,block_y_length,kind="character"):
    character_gif=[]
    files_amount = 0
    for file in os.listdir("img/"+kind+"/"+character_name+"/"+action):
        files_amount+=1
    for i in range(files_amount):
        path = "img/"+kind+"/"+character_name+"/"+action+"/"+character_name+"_"+action+"_"+str(i)+".png"
        character_gif.append(pygame.transform.scale(pygame.image.load(os.path.join(path)), (int(block_x_length*2), int(block_y_length*2))))
    return [character_gif,files_amount]

#动图字典制作模块：接受一个友方角色名，返回对应的动图字典：
def character_gif_dic(character_name,block_x_length,block_y_length,kind="character"):
    if kind == "character":
        gif_dic = {
            "attack":[character_creator(character_name,block_x_length,block_y_length,"attack"),0],
            "die":[character_creator(character_name,block_x_length,block_y_length,"die"),0],
            "move":[character_creator(character_name,block_x_length,block_y_length,"move"),0],
            "victory":[character_creator(character_name,block_x_length,block_y_length,"victory"),0],
            "victoryloop":[character_creator(character_name,block_x_length,block_y_length,"victoryloop"),0],
            "wait":[character_creator(character_name,block_x_length,block_y_length,"wait"),0],
        }
    else:
        gif_dic = {
        "attack":[character_creator(character_name,block_x_length,block_y_length,"attack",kind),0],
        "die":[character_creator(character_name,block_x_length,block_y_length,"die",kind),0],
        "move":[character_creator(character_name,block_x_length,block_y_length,"move",kind),0],
        "wait":[character_creator(character_name,block_x_length,block_y_length,"wait",kind),0],
        }
    return gif_dic
    