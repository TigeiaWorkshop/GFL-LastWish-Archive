import os
import pygame

#图片加载模块：接收图片路径,长,高,返回对应图片
def loadImg(path,length=None,height=None):
    if length == None and height== None:
        return pygame.image.load(os.path.join(path))
    else:
        if length == None:
            raise Exception('Length is required')
        elif height== None:
            raise Exception('Height is required')
        elif length >= 0 and height >= 0:
            return pygame.transform.scale(pygame.image.load(os.path.join(path)), (int(length), int(height)))
        elif length < 0 or height < 0:
            raise Exception('Both length and height must be positive')

#高级图片加载模块：接收图片路径,长,高,返回对应的图片class
def loadImage(path,length=None,height=None):
    class theImg:
        def __init__(self,x,y,img):
            self.x = x
            self.y = y
            self.img = img 
    return theImg(0,0,loadImg(path,length,height))

#文字加载模块：接收图片路径,长,高,返回对应的图片class
def loadImage(path,length=None,height=None):
    class theImg:
        def __init__(self,x,y,img):
            self.x = x
            self.y = y
            self.img = img 
    return theImg(0,0,loadImg(path,length,height))

#文字制作模块：接受文字，颜色，文字大小，文字样式，模式，返回制作完的文字
def fontRender(txt,color,size=50,font="simsunnsimsun",mode=True):
    normal_font = pygame.font.SysFont(font,int(size))
    if color == "gray" or color == "grey" or color == "disable":
        text_out = normal_font.render(txt, mode, (105,105,105))
    elif color == "white" or color == "enable":
        text_out = normal_font.render(txt, mode, (255, 255, 255))
    elif color == "black":
        text_out = normal_font.render(txt, mode, (0, 0, 0))
    else:
        text_out = normal_font.render(txt, mode, color)
    return text_out

#高级文字制作模块：接受文字，颜色，文字大小，文字样式，模式，返回制作完的文字Class，该Class具有一大一普通的字号
def fontRenderPro(txt,color,size=50,font="simsunnsimsun",mode=True):
    class the_text:
        def __init__(self, n, b):
            self.n = n
            self.b = b
    #文字设定
    normal_font = pygame.font.SysFont(font,int(size))
    big_font = pygame.font.SysFont(font,int(size*1.5))
    if color == "gray" or color == "grey" or color == "disable":
        text_out = the_text(normal_font.render(txt, mode, (105,105,105)),big_font.render(txt, mode, (105,105,105)))
    elif color == "white" or color == "enable":
        text_out = the_text(normal_font.render(txt, mode, (255, 255, 255)),big_font.render(txt, mode, (255, 255, 255)))
    else:
        text_out = the_text(normal_font.render(txt, mode, color),big_font.render(txt, mode, color))
    return text_out

#检测是否被点击
def isGetClick(the_object,the_object_position,local_x=0,local_y=0):
    mouse_x,mouse_y=pygame.mouse.get_pos()
    if the_object_position[0]+local_x<mouse_x<the_object_position[0]+the_object.get_width()+local_x and the_object_position[1]+local_y<mouse_y<the_object_position[1]+the_object.get_height()+local_y:
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
        character_gif.append(pygame.transform.scale(pygame.image.load(os.path.join(path)).convert_alpha(), (int(block_x_length*2), int(block_y_length*2))))
    return [character_gif,files_amount]

#动图字典制作模块：接受一个友方角色名，返回对应的动图字典：
def character_gif_dic(character_name,block_x_length,block_y_length,kind="character"):
    if kind == "character":
        gif_dic = {
            "attack":[character_creator(character_name,"attack",block_x_length,block_y_length),0],
            "die":[character_creator(character_name,"die",block_x_length,block_y_length),0],
            "move":[character_creator(character_name,"move",block_x_length,block_y_length),0],
            "skill":[character_creator(character_name,"skill",block_x_length,block_y_length),0],
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
def displayInCenter(item1,item2,x,y,screen,local_x=0,local_y=0):
    added_x = (item2.get_width()-item1.get_width())/2
    added_y = (item2.get_height()-item1.get_height())/2
    screen.blit(item2,(x+local_x,y+local_y))
    screen.blit(item1,(x+added_x+local_x,y+added_y+local_y))

#图片blit模块：接受图片，位置（列表格式），屏幕，如果不是UI层需要local_x和local_y
def printf(img,position,screen,local_x=0,local_y=0):
    screen.blit(img,(position[0]+local_x,position[1]+local_y))
