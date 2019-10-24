#image purchased from unity store and internet
import pygame
import time
from pygame.locals import *
from sys import exit
import os
import glob
import yaml
import random
from hpManager import *
pygame.init()

#加载设置
with open("setting.yaml", "r", encoding='utf-8') as f:
    setting = yaml.load(f.read(),Loader=yaml.FullLoader)
    window_x = setting['Screen_size_x']
    window_y =  setting['Screen_size_y']
    lang_file = setting['Language']

# 创建窗口
screen = pygame.display.set_mode([window_x, window_y])
pygame.display.set_caption("Girls frontline-Last Wish") #窗口标题

#加载背景图片
all_env_file_list = glob.glob(r'img\environment\*.png')
env_img_list={}
for i in range(len(all_env_file_list)):
    img_name = all_env_file_list[i].replace("img","").replace("environment","").replace(".png","").replace("\\","").replace("/","")
    env_img_list[img_name] = pygame.image.load(os.path.join(all_env_file_list[i])).convert_alpha()

#读取并初始化章节信息
with open("data/main_chapter/chapter1.yaml", "r", encoding='utf-8') as f:
    chapter_info = yaml.load(f.read(),Loader=yaml.FullLoader)
    block_y = len(chapter_info["map"])
    block_x = len(chapter_info["map"][0])
    characters = chapter_info["character"]
    sangvisFerris = chapter_info["sangvisFerri"]
    map = chapter_info["map"]
block_x_length = window_x/block_x
block_y_length = window_y/block_y

#动图制作模块：接受一个友方角色名和动作，返回对应角色动作list和
def character_creater(character_name,action,kind="character"):
    global block_x_length
    global block_y_length
    character_gif=[]
    files_amount = 0
    for file in os.listdir("img/"+kind+"/"+character_name+"/"+action):
        files_amount+=1
    for i in range(files_amount):
        path = "img/"+kind+"/"+character_name+"/"+action+"/"+character_name+"_"+action+"_"+str(i)+".png"
        character_gif.append(pygame.transform.scale(pygame.image.load(os.path.join(path)), (int(block_x_length*2), int(block_y_length*2))))
    return [character_gif,files_amount]

#动图字典制作模块：接受一个友方角色名，返回对应的动图字典：
def character_gif_dic(character_name,kind="character"):
    if kind == "character":
        gif_dic = {
            "attack":[character_creater(character_name,"attack"),0],
            "die":[character_creater(character_name,"die"),0],
            "move":[character_creater(character_name,"move"),0],
            "victory":[character_creater(character_name,"victory"),0],
            "victoryloop":[character_creater(character_name,"victoryloop"),0],
            "wait":[character_creater(character_name,"wait"),0],
        }
    else:
        gif_dic = {
        "attack":[character_creater(character_name,"attack",kind),0],
        "die":[character_creater(character_name,"die",kind),0],
        "move":[character_creater(character_name,"move",kind),0],
        "wait":[character_creater(character_name,"wait",kind),0],
        }
    return gif_dic

#加载友方角色
characters_dic={}
for character in characters:
    characters_dic[character] = character_gif_dic(character)
#加载敌方角色
sangvisFerris_dic={}
for sangvisFerri in sangvisFerris:
    sangvisFerris_dic[sangvisFerri] = character_gif_dic(sangvisFerri,"sangvisFerri")

#加载动作：接受一个带有[动作]的gif字典，完成对应的指令
def action_displayer(gif_dic,action,x,y,isContinue=True):
    global isWaiting
    global round
    img_of_char = gif_dic[action][0][0][gif_dic[action][1]]
    screen.blit(img_of_char,(x*green.get_width()-green.get_width()/2,y*green.get_height()-green.get_height()/2))
    gif_dic[action][1]+=1
    if gif_dic[action][1] == 5 and action == "attack":
        pass
        #bullets_list.append(Bullet(characters_data.x+img_of_char.get_width()-20,characters_data.y+img_of_char.get_height()/2-5,300))
    if isContinue==True:
        if gif_dic[action][1] == gif_dic[action][0][1]:
            gif_dic[action][1] = 0
    if isContinue=="die":
        if gif_dic[action][1] == gif_dic[action][0][1]:
            gif_dic[action][1] -= 1
    else:
        if gif_dic[action][1] == gif_dic[action][0][1]:
            gif_dic[action][1] = 0
            isWaiting = True
            round = 'sangvisFerri'
            direction_to_move = -1
            how_many_moved = 0
            sangvisFerris_data["ripper"].decreaseHp(random.randint(characters_data.min_damage,characters_data.max_damage))


#生存随机方块名
map_img_list = []
for i in range(len(map)):
    map_img_per_line = []
    for a in range(len(map[i])):
        if map[i][a] == 0:
            img_name = "mountainSnow"+str(random.randint(0,7))
        elif map[i][a] == 1:
            img_name = "plainsColdSnowCovered"+str(random.randint(0,3))
        elif map[i][a] == 2:
            img_name = "forestPineSnowCovered"+str(random.randint(0,4))
        elif map[i][a] == 3:
            img_name = "ocean"+str(random.randint(0,4))
        map_img_per_line.append(img_name)
    map_img_list.append(map_img_per_line)

#初始化角色信息
#hpManager(self, 最小攻击力, 最大攻击力, 血量上限 , 当前血量, x轴位置，y轴位置，攻击范围，移动范围)
characters_data = characterDataManager("sv-98",150,200,500,500,3,8,8,3)
sangvisFerris_data = {}
for enemy in sangvisFerris:
    sangvisFerris_data[enemy] = characterDataManager(enemy,50,100,500,500,5,4,5,3)

#加载子弹图片
bullet_img = pygame.transform.scale(pygame.image.load(os.path.join("img/others/bullet.png")), (int(block_x_length/6), int(block_y_length/12)))
bullets_list = []

#绿色方块/方块标准
green = pygame.transform.scale(pygame.image.load(os.path.join("img/others/green.png")), (int(block_x_length), int(block_y_length)))
green.set_alpha(100)
red = pygame.transform.scale(pygame.image.load(os.path.join("img/others/red.png")), (int(block_x_length), int(block_y_length)))
red.set_alpha(100)
new_block_type = 0
per_block_width = green.get_width()
per_block_height = green.get_height()
green_hide = True
action = "wait"
isWaiting = True
round="player"

#加载选择菜单：
select_menu = pygame.transform.scale(pygame.image.load(os.path.join("img/others/select_menu.png")), (int(block_x_length)*3, int(block_y_length)*3))
select_menu.set_alpha(200)
select_menu_show = False

# 游戏主循环
while True:
    #加载地图
    for i in range(len(map_img_list)):
        for a in range(len(map_img_list[i])):
            img_display = pygame.transform.scale(env_img_list[map_img_list[i][a]], (int(block_x_length), int(block_y_length*1.5)))
            screen.blit(img_display,(a*block_x_length,i*block_y_length-block_x_length/2))
    if green_hide ==False:
        for x in range(characters_data.x-characters_data.attack_range,characters_data.x+characters_data.attack_range+1):
            attack_range_difference = characters_data.attack_range - characters_data.move_range
            if x < block_x:
                if x < characters_data.x-characters_data.move_range-1:
                    screen.blit(red,(x*green.get_width(),characters_data.y*green.get_height()+7))
                elif characters_data.x-characters_data.move_range-1<x<characters_data.x+characters_data.move_range+1:
                    if map[characters_data.y][x] == 0 or map[characters_data.y][x] == 3:
                        screen.blit(red,(x*green.get_width(),characters_data.y*green.get_height()+7))
                    else:
                        screen.blit(green,(x*green.get_width(),characters_data.y*green.get_height()+7))
                else:
                    screen.blit(red,(x*green.get_width(),characters_data.y*green.get_height()+7))
        for y in range(characters_data.y-characters_data.attack_range,characters_data.y+characters_data.attack_range+1):
            attack_range_difference = characters_data.attack_range - characters_data.move_range
            if y < block_y:
                if y < characters_data.y-characters_data.move_range-1:
                    screen.blit(red,(characters_data.x*green.get_width(),y*green.get_height()+7))
                elif characters_data.y-characters_data.move_range-1<y<characters_data.y+characters_data.move_range+1:
                    if map[y][characters_data.x] == 0 or map[y][characters_data.x] == 3:
                        screen.blit(red,(characters_data.x*green.get_width(),y*green.get_height()+7))
                    else:
                        screen.blit(green,(characters_data.x*green.get_width(),y*green.get_height()+7))
                else:
                    screen.blit(red,(characters_data.x*green.get_width(),y*green.get_height()+7))
    if round == "player":
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    exit()
            elif event.type == MOUSEBUTTONDOWN:
                mouse_x,mouse_y=pygame.mouse.get_pos()
                block_get_click_x = int(mouse_x/green.get_width())
                block_get_click_y = int(mouse_y/green.get_height())
                if green_hide == False:
                    if characters_data.x-characters_data.move_range-1<block_get_click_x<characters_data.x+characters_data.move_range+1 and characters_data.y == block_get_click_y:
                        if map[characters_data.y][block_get_click_x] == 1 or map[characters_data.y][block_get_click_x] ==2:
                            temp_x = characters_data.x
                            temp_max = block_get_click_x
                            isWaiting = "LEFTANDRIGHT"
                    elif characters_data.y-characters_data.move_range-1<block_get_click_y<characters_data.y+characters_data.move_range+1 and characters_data.x == block_get_click_x:
                        if map[block_get_click_y][characters_data.x] ==1 or map[block_get_click_y][characters_data.x] ==2:
                            temp_y = characters_data.y
                            temp_max = block_get_click_y
                            isWaiting = "TOPANDBOTTOM"
                    if characters_data.x-characters_data.attack_range-1<block_get_click_x<characters_data.x+characters_data.attack_range+1 and characters_data.y == block_get_click_y:
                        if block_get_click_x == sangvisFerris_data["ripper"].x and  block_get_click_y == sangvisFerris_data["ripper"].y:
                            isWaiting = "ATTACKING"
                    elif characters_data.y-characters_data.attack_range-1<block_get_click_y<characters_data.y+characters_data.attack_range+1 and characters_data.x == block_get_click_x:
                        if block_get_click_x == sangvisFerris_data["ripper"].x and  block_get_click_y == sangvisFerris_data["ripper"].y:
                            isWaiting = "ATTACKING"
                if block_get_click_x == characters_data.x and block_get_click_y == characters_data.y:
                    if green_hide == True:
                        action = "move"
                        green_hide = False
                    else:
                        green_hide = True
                        isWaiting = True
                        action = "wait"

        #角色动画
        if isWaiting == True:
            action_displayer(characters_dic[characters_data.name],action,characters_data.x,characters_data.y)
        elif isWaiting == "LEFTANDRIGHT":
            if temp_x < temp_max:
                temp_x+=0.1
                action_displayer(characters_dic[characters_data.name],action,temp_x,characters_data.y)
                if temp_x >= temp_max:
                    isWaiting = True
                    characters_data.x = block_get_click_x
                    round = 'sangvisFerri'
                    direction_to_move = -1
                    how_many_moved = 0
            elif temp_x > temp_max:
                temp_x-=0.1
                action_displayer(characters_dic[characters_data.name],action,temp_x,characters_data.y)
                if temp_x <= temp_max:
                    isWaiting = True
                    characters_data.x = block_get_click_x
                    round = 'sangvisFerri'
                    direction_to_move = -1
                    how_many_moved = 0
        elif isWaiting == "TOPANDBOTTOM":
            if temp_y < temp_max:
                temp_y+=0.1
                action_displayer(characters_dic[characters_data.name],action,characters_data.x,temp_y,)
                if temp_y >= temp_max:
                    isWaiting = True
                    characters_data.y = block_get_click_y
                    round = 'sangvisFerri'
                    direction_to_move = -1
                    how_many_moved = 0
            elif temp_y > temp_max:
                temp_y-=0.1
                action_displayer(characters_dic[characters_data.name],action,characters_data.x,temp_y,)
                if temp_y <= temp_max:
                    isWaiting = True
                    characters_data.y = block_get_click_y
                    round = 'sangvisFerri'
                    direction_to_move = -1
                    how_many_moved = 0
        elif isWaiting == "ATTACKING":
                action_displayer(characters_dic[characters_data.name],"attack",characters_data.x,characters_data.y,False)
        if sangvisFerris_data["ripper"].current_hp>0:
            action_displayer(sangvisFerris_dic["ripper"],"wait",sangvisFerris_data["ripper"].x,sangvisFerris_data["ripper"].y)
        elif sangvisFerris_data["ripper"].current_hp<=0:
            action_displayer(sangvisFerris_dic["ripper"],"die",sangvisFerris_data["ripper"].x,sangvisFerris_data["ripper"].y,"die")

        #子弹
        for per_bullet in bullets_list:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_1]:
                new_block_type = 0
            screen.blit(bullet_img, (per_bullet.x,per_bullet.y))
            per_bullet.x += 100
            if per_bullet.x > window_x:
                bullets_list.remove(per_bullet)

    if round == "sangvisFerri":
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    exit()
        green_hide = True
        action_displayer(characters_dic[characters_data.name],"wait",characters_data.x,characters_data.y,)
        if direction_to_move == -1:
            direction_to_move = random.randint(0,3) #0左1上2右3下
        if direction_to_move == 0:
            how_many_to_move = sangvisFerris_data["ripper"].x-sangvisFerris_data["ripper"].move_range
            if how_many_to_move<0:
                how_many_to_move=0
            action_displayer(sangvisFerris_dic["ripper"],"move",sangvisFerris_data["ripper"].x-how_many_moved,sangvisFerris_data["ripper"].y)
        elif direction_to_move == 2:
            how_many_to_move = sangvisFerris_data["ripper"].x+sangvisFerris_data["ripper"].move_range
            if how_many_to_move>block_x:
                how_many_to_move=block_x
            action_displayer(sangvisFerris_dic["ripper"],"move",sangvisFerris_data["ripper"].x+how_many_moved,sangvisFerris_data["ripper"].y)
        elif direction_to_move == 1:
            how_many_to_move = sangvisFerris_data["ripper"].y-sangvisFerris_data["ripper"].move_range
            if how_many_to_move<0:
                how_many_to_move=0
            action_displayer(sangvisFerris_dic["ripper"],"move",sangvisFerris_data["ripper"].x,sangvisFerris_data["ripper"].y-how_many_moved)
        elif direction_to_move == 3:
            how_many_to_move = sangvisFerris_data["ripper"].y+sangvisFerris_data["ripper"].move_range
            if how_many_to_move>block_y:
                how_many_to_move=block_y
            action_displayer(sangvisFerris_dic["ripper"],"move",sangvisFerris_data["ripper"].x,sangvisFerris_data["ripper"].y+how_many_moved)
        if how_many_moved > how_many_to_move:
            if direction_to_move == 0:
                sangvisFerris_data["ripper"].x-=sangvisFerris_data["ripper"].move_range
            elif direction_to_move == 2:
                sangvisFerris_data["ripper"].x+=sangvisFerris_data["ripper"].move_range
            elif direction_to_move == 1:
                sangvisFerris_data["ripper"].y-=sangvisFerris_data["ripper"].move_range
            elif direction_to_move == 3:
                sangvisFerris_data["ripper"].y+=sangvisFerris_data["ripper"].move_range
            round = "player"
        else:
            how_many_moved+=0.1

    while pygame.mixer.music.get_busy() != 1:
        pygame.mixer.music.load('music/Snowflake.mp3')
        pygame.mixer.music.play(loops=9999, start=0.0)

    time.sleep(0.025)
    pygame.display.update()
