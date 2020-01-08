import os
import pygame


#文字制作模块：接受文字，颜色，模式，返回制作完的文字
def fontRender(txt,color,mode=True):
    class the_text:
        def __init__(self, n, b):
            self.n = n
            self.b = b
    #文字设定
    normal_font = pygame.font.SysFont('simsunnsimsun',50)
    big_font = pygame.font.SysFont('simsunnsimsun',75)
    if color == "gray" or color == "grey" or color == "disable":
        text_out = the_text(normal_font.render(txt, mode, (105,105,105)),big_font.render(txt, mode, (105,105,105)))
    elif color == "white" or color == "enable":
        text_out = the_text(normal_font.render(txt, mode, (255, 255, 255)),big_font.render(txt, mode, (255, 255, 255)))
    else:
        text_out = the_text(normal_font.render(txt, mode, color),big_font.render(txt, mode, color))
    return text_out

#检测是否被点击
def isGetClick(the_object,the_object_position):
    mouse_x,mouse_y=pygame.mouse.get_pos()
    if the_object_position[0]<mouse_x<the_object_position[0]+the_object.get_width() and the_object_position[1]<mouse_y<the_object_position[1]+the_object.get_height():
        return True
    else:
        return False

#动图制作模块：接受一个友方角色名和动作,当前的方块标准长和高，返回对应角色动作list和
def character_creator(character_name,action,block_x_length,block_y_length,kind="character"):
    character_gif=[]
    files_amount = 0
    for file in os.listdir("Assets/img/"+kind+"/"+character_name+"/"+action):
        files_amount+=1
    for i in range(files_amount):
        path = "Assets/img/"+kind+"/"+character_name+"/"+action+"/"+character_name+"_"+action+"_"+str(i)+".png"
        character_gif.append(pygame.transform.scale(pygame.image.load(os.path.join(path)), (int(block_x_length*2), int(block_y_length*2))))
    return [character_gif,files_amount]

#动图字典制作模块：接受一个友方角色名，返回对应的动图字典：
def character_gif_dic(character_name,block_x_length,block_y_length,kind="character"):
    if kind == "character":
        gif_dic = {
            "attack":[character_creator(character_name,"attack",block_x_length,block_y_length),0],
            "die":[character_creator(character_name,"die",block_x_length,block_y_length),0],
            "move":[character_creator(character_name,"move",block_x_length,block_y_length),0],
            "victory":[character_creator(character_name,"victory",block_x_length,block_y_length),0],
            "victoryloop":[character_creator(character_name,"victoryloop",block_x_length,block_y_length),0],
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

#中心展示模块：接受两个item和item2的x和y，将item1展示在item2的中心位置：
def displayInCenter(item1,item2,x,y,screen):
    local_x = (item2.get_width()-item1.get_width())/2
    local_y = (item2.get_height()-item1.get_height())/2
    screen.blit(item2,(x,y))
    screen.blit(item1,(x+local_x,y+local_y))