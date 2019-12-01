import pygame
import time
from pygame.locals import *
from sys import exit
import os
import glob
import yaml
from characterDataManager import *

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

my_font =pygame.font.SysFont('simsunnsimsun',25)
#读取并初始化章节信息
with open("data/main_chapter/chapter1_map.yaml", "r", encoding='utf-8') as f:
    chapter_info = yaml.load(f.read(),Loader=yaml.FullLoader)
    chapter_title = chapter_info["title"]
    block_y = len(chapter_info["map"])
    block_x = len(chapter_info["map"][0])
    characters = chapter_info["character"]
    sangvisFerris = chapter_info["sangvisFerri"]
    map = chapter_info["map"]
block_x_length = window_x/block_x
block_y_length = window_y/block_y

#动图制作模块：接受一个友方角色名和动作，返回对应角色动作list和
def character_creator(character_name,action,kind="character"):
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
            "attack":[character_creator(character_name,"attack"),0],
            "die":[character_creator(character_name,"die"),0],
            "move":[character_creator(character_name,"move"),0],
            "victory":[character_creator(character_name,"victory"),0],
            "victoryloop":[character_creator(character_name,"victoryloop"),0],
            "wait":[character_creator(character_name,"wait"),0],
        }
    else:
        gif_dic = {
        "attack":[character_creator(character_name,"attack",kind),0],
        "die":[character_creator(character_name,"die",kind),0],
        "move":[character_creator(character_name,"move",kind),0],
        "wait":[character_creator(character_name,"wait",kind),0],
        }
    return gif_dic

#初始化角色信息
#hpManager(名字, 最小攻击力, 最大攻击力, 血量上限 , 当前血量, x轴位置，y轴位置，攻击范围，移动范围,gif字典)
characters_name_list = []
characters_data = {}
for jiaose in characters:
    characters_data[jiaose] = characterDataManager(jiaose,characters[jiaose]["min_damage"],characters[jiaose]["max_damage"],characters[jiaose]["max_hp"],characters[jiaose]["current_hp"],characters[jiaose]["x"],characters[jiaose]["y"],characters[jiaose]["attack_range"],characters[jiaose]["move_range"],character_gif_dic(jiaose))
    characters_name_list.append(jiaose)

sangvisFerris_name_list = []
sangvisFerris_data = {}
for enemy in sangvisFerris:
    sangvisFerris_data[enemy] = characterDataManager(enemy,sangvisFerris[enemy]["min_damage"],sangvisFerris[enemy]["max_damage"],sangvisFerris[enemy]["max_hp"],sangvisFerris[enemy]["current_hp"],sangvisFerris[enemy]["x"],sangvisFerris[enemy]["y"],sangvisFerris[enemy]["attack_range"],sangvisFerris[enemy]["move_range"],character_gif_dic(enemy,"sangvisFerri"))
    sangvisFerris_name_list.append(enemy)

hp_font =pygame.font.SysFont('simsunnsimsun',10)

#加载动作：接受角色名，动作，方位，完成对应的指令
def action_displayer(name,action,x,y,isContinue=True):
    global isWaiting
    global round
    if name in sangvisFerris_name_list:
        gif_dic = sangvisFerris_data[name].gif
        if sangvisFerris_data[name].current_hp < 0:
            sangvisFerris_data[name].current_hp = 0
        current_hp_to_display = hp_font.render(str(sangvisFerris_data[name].current_hp)+"/"+str(sangvisFerris_data[name].max_hp), True, (0,0,0))
        percent_of_hp = sangvisFerris_data[name].current_hp/sangvisFerris_data[name].max_hp
    else:
        gif_dic = characters_data[name].gif
        if characters_data[name].current_hp<0:
            characters_data[name].current_hp = 0
        current_hp_to_display = hp_font.render(str(characters_data[name].current_hp)+"/"+str(characters_data[name].max_hp), True, (0,0,0))
        percent_of_hp = characters_data[name].current_hp/characters_data[name].max_hp
    if percent_of_hp<0:
        percent_of_hp=0

    img_of_char = gif_dic[action][0][0][gif_dic[action][1]]
    screen.blit(img_of_char,(x*green.get_width()-green.get_width()/2,y*green.get_height()-green.get_height()/2))
    if percent_of_hp>0:
        screen.blit(hp_empty,(x*green.get_width(),y*green.get_height()*0.98))
        screen.blit(pygame.transform.scale(hp_red,(int(block_x_length*percent_of_hp),int(block_y_length/5))),(x*green.get_width(),y*green.get_height()*0.98))
        screen.blit(current_hp_to_display,(x*green.get_width(),y*green.get_height()*0.98))
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

#生存随机方块名
map_img_list = randomBlock(map)

#玩家回合结束
def endOfPlayerRound():
    global round
    global isWaiting
    isWaiting = True
    round += 1
    if round == len(characters_name_list):
        resetEnemyMovingData()

#重置敌方移动数值
def resetEnemyMovingData():
    global direction_to_move
    global how_many_moved
    global how_many_to_move
    global object_to_play
    global round
    #direction_to_move 0左1上2右3下
    if sangvisFerris_data[object_to_play[round]].x > characters_data["sv-98"].x:
        if sangvisFerris_data[object_to_play[round]].y > characters_data["sv-98"].y:
            if sangvisFerris_data[object_to_play[round]].x-characters_data["sv-98"].x > sangvisFerris_data[object_to_play[round]].y-characters_data["sv-98"].y:
                direction_to_move=0
            else:
                direction_to_move=1
        else:
            direction_to_move=2
    else:
        direction_to_move=3
    how_many_moved = 0
    how_many_to_move = sangvisFerris_data[object_to_play[round]].move_range
    for i in range(1, how_many_to_move+1):
        if direction_to_move == 0:
            if map[sangvisFerris_data[object_to_play[round]].y][sangvisFerris_data[object_to_play[round]].x-i] == 0 or map[sangvisFerris_data[object_to_play[round]].y][sangvisFerris_data[object_to_play[round]].x-i] == 3:
                how_many_to_move = i-1
                break
        elif direction_to_move == 2:
            if map[sangvisFerris_data[object_to_play[round]].y][sangvisFerris_data[object_to_play[round]].x+i] == 0 or map[sangvisFerris_data[object_to_play[round]].y][sangvisFerris_data[object_to_play[round]].x+i] == 3:
                how_many_to_move = i-1
                break
        elif direction_to_move == 1:
            if map[sangvisFerris_data[object_to_play[round]].y-i][sangvisFerris_data[object_to_play[round]].x] == 0 or map[sangvisFerris_data[object_to_play[round]].y-i][sangvisFerris_data[object_to_play[round]].x] == 3:
                how_many_to_move = i-1
                break
        elif direction_to_move == 3:
            if map[sangvisFerris_data[object_to_play[round]].y+i][sangvisFerris_data[object_to_play[round]].x] == 0 or map[sangvisFerris_data[object_to_play[round]].y+i][sangvisFerris_data[object_to_play[round]].x] == 3:
                how_many_to_move = i-1
                break
    if how_many_to_move < 1:
        resetEnemyMovingData()

#加载子弹图片
bullet_img = pygame.transform.scale(pygame.image.load(os.path.join("img/others/bullet.png")), (int(block_x_length/6), int(block_y_length/12)))
bullets_list = []

#绿色方块/方块标准
hp_empty = pygame.transform.scale(pygame.image.load(os.path.join("img/others/hp_empty.png")), (int(block_x_length), int(block_y_length/5)))
hp_red = pygame.transform.scale(pygame.image.load(os.path.join("img/others/hp_red.png")), (int(block_x_length), int(block_y_length/5)))
green = pygame.transform.scale(pygame.image.load(os.path.join("img/others/green.png")), (int(block_x_length), int(block_y_length)))
green.set_alpha(100)
red = pygame.transform.scale(pygame.image.load(os.path.join("img/others/red.png")), (int(block_x_length), int(block_y_length)))
red.set_alpha(100)
the_black = pygame.transform.scale(pygame.image.load(os.path.join("img/others/black.png")),(window_x,window_y))
new_block_type = 0
per_block_width = green.get_width()
per_block_height = green.get_height()

#章节标题
title_number_display = pygame.font.SysFont('simsunnsimsun',50).render("Chapter1", True, (255,255,255))
title_main_display = pygame.font.SysFont('simsunnsimsun',50).render(chapter_title, True, (255,255,255))
for i in range(0,600,1):
    screen.blit(the_black,(0,0))
    title_number_display.set_alpha(i)
    title_main_display.set_alpha(i)
    screen.blit(title_number_display,((window_x-title_number_display.get_width())/2,400))
    screen.blit(title_main_display,((window_x-title_main_display.get_width())/2,500))
    pygame.display.update()
for i in range(600,0,-1):
    screen.blit(the_black,(0,0))
    title_number_display.set_alpha(i)
    title_main_display.set_alpha(i)
    screen.blit(title_number_display,((window_x-title_number_display.get_width())/2,400))
    screen.blit(title_main_display,((window_x-title_main_display.get_width())/2,500))
    pygame.display.update()

#部分设定初始化
enemies_get_attack = sangvisFerris_name_list[0]
green_hide = True
action = "wait"
isWaiting = True
action_point = len(characters_name_list)#行动值
object_to_play = characters_name_list + sangvisFerris_name_list #行动顺序
round = 0
the_character_get_click = characters_name_list[0]
battle=True
direction_to_move = 0
how_many_to_move = 0
how_many_moved = 0
# 游戏主循环
while battle==True:
    #加载地图
    for i in range(len(map_img_list)):
        for a in range(len(map_img_list[i])):
            img_display = pygame.transform.scale(env_img_list[map_img_list[i][a]], (int(block_x_length), int(block_y_length*1.5)))
            screen.blit(img_display,(a*block_x_length,i*block_y_length-block_y_length/2))
    if green_hide ==False:
        for x in range(characters_data[the_character_get_click].x-characters_data[the_character_get_click].attack_range,characters_data[the_character_get_click].x+characters_data[the_character_get_click].attack_range+1):
            attack_range_difference = characters_data[the_character_get_click].attack_range - characters_data[the_character_get_click].move_range
            if x < block_x:
                if x < characters_data[the_character_get_click].x-characters_data[the_character_get_click].move_range-1:
                    screen.blit(red,(x*green.get_width(),characters_data[the_character_get_click].y*green.get_height()))
                elif characters_data[the_character_get_click].x-characters_data[the_character_get_click].move_range-1<x<characters_data[the_character_get_click].x+characters_data[the_character_get_click].move_range+1:
                    if map[characters_data[the_character_get_click].y][x] == 0 or map[characters_data[the_character_get_click].y][x] == 3:
                        screen.blit(red,(x*green.get_width(),characters_data[the_character_get_click].y*green.get_height()))
                    else:
                        screen.blit(green,(x*green.get_width(),characters_data[the_character_get_click].y*green.get_height()))
                else:
                    screen.blit(red,(x*green.get_width(),characters_data[the_character_get_click].y*green.get_height()))
        for y in range(characters_data[the_character_get_click].y-characters_data[the_character_get_click].attack_range,characters_data[the_character_get_click].y+characters_data[the_character_get_click].attack_range+1):
            if y < block_y:
                if y < characters_data[the_character_get_click].y-characters_data[the_character_get_click].move_range-1:
                    screen.blit(red,(characters_data[the_character_get_click].x*green.get_width(),y*green.get_height()))
                elif characters_data[the_character_get_click].y-characters_data[the_character_get_click].move_range-1<y<characters_data[the_character_get_click].y+characters_data[the_character_get_click].move_range+1:
                    if map[y][characters_data[the_character_get_click].x] == 0 or map[y][characters_data[the_character_get_click].x] == 3:
                        screen.blit(red,(characters_data[the_character_get_click].x*green.get_width(),y*green.get_height()))
                    else:
                        screen.blit(green,(characters_data[the_character_get_click].x*green.get_width(),y*green.get_height()))
                else:
                    screen.blit(red,(characters_data[the_character_get_click].x*green.get_width(),y*green.get_height()))
    #玩家输入按键判定
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                exit()
            if event.key == K_t:
                exit()
        elif event.type == MOUSEBUTTONDOWN:
            if isWaiting == True:
                mouse_x,mouse_y=pygame.mouse.get_pos()
                block_get_click_x = int(mouse_x/green.get_width())
                block_get_click_y = int(mouse_y/green.get_height())
                for key in characters_data:
                    if characters_data[key].x == block_get_click_x and characters_data[key].y == block_get_click_y:
                        the_character_get_click = key
                if green_hide == False:
                    if characters_data[the_character_get_click].x-characters_data[the_character_get_click].move_range-1<block_get_click_x<characters_data[the_character_get_click].x+characters_data[the_character_get_click].move_range+1 and characters_data[the_character_get_click].y == block_get_click_y:
                        if map[characters_data[the_character_get_click].y][block_get_click_x] == 1 or map[characters_data[the_character_get_click].y][block_get_click_x] ==2:
                            temp_x = characters_data[the_character_get_click].x
                            temp_max = block_get_click_x
                            isWaiting = "LEFTANDRIGHT"
                    elif characters_data[the_character_get_click].y-characters_data[the_character_get_click].move_range-1<block_get_click_y<characters_data[the_character_get_click].y+characters_data[the_character_get_click].move_range+1 and characters_data[the_character_get_click].x == block_get_click_x:
                        if map[block_get_click_y][characters_data[the_character_get_click].x] ==1 or map[block_get_click_y][characters_data[the_character_get_click].x] ==2:
                            temp_y = characters_data[the_character_get_click].y
                            temp_max = block_get_click_y
                            isWaiting = "TOPANDBOTTOM"
                    if characters_data[the_character_get_click].x-characters_data[the_character_get_click].attack_range-1<block_get_click_x<characters_data[the_character_get_click].x+characters_data[the_character_get_click].attack_range+1 and characters_data[the_character_get_click].y == block_get_click_y:
                        for enemies in sangvisFerris_data:
                            if block_get_click_x == sangvisFerris_data[enemies].x and  block_get_click_y == sangvisFerris_data[enemies].y:
                                isWaiting = "ATTACKING"
                                enemies_get_attack = enemies
                    elif characters_data[the_character_get_click].y-characters_data[the_character_get_click].attack_range-1<block_get_click_y<characters_data[the_character_get_click].y+characters_data[the_character_get_click].attack_range+1 and characters_data[the_character_get_click].x == block_get_click_x:
                        for enemies in sangvisFerris_data:
                            if block_get_click_x == sangvisFerris_data[enemies].x and  block_get_click_y == sangvisFerris_data[enemies].y:
                                isWaiting = "ATTACKING"
                                enemies_get_attack = enemies
                if block_get_click_x == characters_data[the_character_get_click].x and block_get_click_y == characters_data[the_character_get_click].y:
                    if green_hide == True:
                        action = "move"
                        green_hide = False
                    else:
                        green_hide = True
                        isWaiting = True
                        action = "wait"

    if object_to_play[round] in characters_name_list:
        #角色动画
        if isWaiting == True:
            for every_chara in characters:
                action_displayer(characters_data[every_chara].name,"wait",characters_data[every_chara].x,characters_data[every_chara].y,)
        elif isWaiting == "LEFTANDRIGHT":
            if temp_x < temp_max:
                temp_x+=0.1
                action_displayer(the_character_get_click,action,temp_x,characters_data[the_character_get_click].y)
                for every_chara in characters:
                    if every_chara != the_character_get_click:
                        action_displayer(characters_data[every_chara].name,"wait",characters_data[every_chara].x,characters_data[every_chara].y,)
                if temp_x >= temp_max:
                    characters_data[the_character_get_click].x = block_get_click_x
                    endOfPlayerRound()
            elif temp_x > temp_max:
                temp_x-=0.1
                action_displayer(characters_data[the_character_get_click].name,action,temp_x,characters_data[the_character_get_click].y)
                for every_chara in characters:
                    if every_chara != the_character_get_click:
                        action_displayer(characters_data[every_chara].name,"wait",characters_data[every_chara].x,characters_data[every_chara].y,)
                if temp_x <= temp_max:
                    characters_data[the_character_get_click].x = block_get_click_x
                    endOfPlayerRound()
        elif isWaiting == "TOPANDBOTTOM":
            if temp_y < temp_max:
                temp_y+=0.1
                action_displayer(characters_data[the_character_get_click].name,action,characters_data[the_character_get_click].x,temp_y,)
                for every_chara in characters:
                    if every_chara != the_character_get_click:
                        action_displayer(characters_data[every_chara].name,"wait",characters_data[every_chara].x,characters_data[every_chara].y,)
                if temp_y >= temp_max:
                    characters_data[the_character_get_click].y = block_get_click_y
                    endOfPlayerRound()
            elif temp_y > temp_max:
                temp_y-=0.1
                action_displayer(characters_data[the_character_get_click].name,action,characters_data[the_character_get_click].x,temp_y,)
                for every_chara in characters:
                    if every_chara != the_character_get_click:
                        action_displayer(characters_data[every_chara].name,"wait",characters_data[every_chara].x,characters_data[every_chara].y,)
                if temp_y <= temp_max:
                    characters_data[the_character_get_click].y = block_get_click_y
                    endOfPlayerRound()
        elif isWaiting == "ATTACKING":
            for every_chara in characters:
                if every_chara != the_character_get_click:
                    action_displayer(characters_data[every_chara].name,"wait",characters_data[every_chara].x,characters_data[every_chara].y,)
                else:
                    action_displayer(characters_data[every_chara].name,"attack",characters_data[every_chara].x,characters_data[every_chara].y,False)
            if characters_data[the_character_get_click].gif["attack"][1] == characters_data[the_character_get_click].gif["attack"][0][1]:
                sangvisFerris_data[enemies_get_attack].decreaseHp(characters_data[the_character_get_click].min_damage,characters_data[the_character_get_click].max_damage)
                endOfPlayerRound()
                characters_data[the_character_get_click].gif["attack"][1] = 0
        for enemies in sangvisFerris_data:
            if sangvisFerris_data[enemies].current_hp>0:
                action_displayer(enemies,"wait",sangvisFerris_data[enemies].x,sangvisFerris_data[enemies].y)
            elif sangvisFerris_data[enemies].current_hp<=0:
                action_displayer(enemies,"die",sangvisFerris_data[enemies].x,sangvisFerris_data[enemies].y,"die")

        #子弹
        for per_bullet in bullets_list:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_1]:
                new_block_type = 0
            screen.blit(bullet_img, (per_bullet.x,per_bullet.y))
            per_bullet.x += 100
            if per_bullet.x > window_x:
                bullets_list.remove(per_bullet)

    #检测所有敌人是否都已经被消灭
    for i in range(len(sangvisFerris_name_list)):
        if sangvisFerris_data[sangvisFerris_name_list[i]].current_hp>0:
            break
        if i == len(sangvisFerris_name_list)-1:
            battle = False
    if battle == False:
        exit()
        break

    #敌方回合
    if object_to_play[round] in sangvisFerris_name_list:
        if sangvisFerris_data[object_to_play[round]].current_hp<=0:
            round += 1
            if round != len(object_to_play):
                resetEnemyMovingData()
        else:
            green_hide = True
            for every_chara in characters:
                action_displayer(characters_data[every_chara].name,"wait",characters_data[every_chara].x,characters_data[every_chara].y)
            for enemies in sangvisFerris_data:
                if enemies != object_to_play[round]:
                    if sangvisFerris_data[enemies].current_hp<=0:
                        action_displayer(enemies,"die",sangvisFerris_data[enemies].x,sangvisFerris_data[enemies].y,"die")
                    else:
                        action_displayer(enemies,"wait",sangvisFerris_data[enemies].x,sangvisFerris_data[enemies].y)


            if direction_to_move == 0:
                action_displayer(object_to_play[round],"move",sangvisFerris_data[object_to_play[round]].x-how_many_moved,sangvisFerris_data[object_to_play[round]].y)
            elif direction_to_move == 2:
                action_displayer(object_to_play[round],"move",sangvisFerris_data[object_to_play[round]].x+how_many_moved,sangvisFerris_data[object_to_play[round]].y)
            elif direction_to_move == 1:
                action_displayer(object_to_play[round],"move",sangvisFerris_data[object_to_play[round]].x,sangvisFerris_data[object_to_play[round]].y-how_many_moved)
            elif direction_to_move == 3:
                action_displayer(object_to_play[round],"move",sangvisFerris_data[object_to_play[round]].x,sangvisFerris_data[object_to_play[round]].y+how_many_moved)

            if how_many_moved >= how_many_to_move:
                if direction_to_move == 0:
                    sangvisFerris_data[object_to_play[round]].x-=how_many_to_move
                elif direction_to_move == 2:
                    sangvisFerris_data[object_to_play[round]].x+=how_many_to_move
                elif direction_to_move == 1:
                    sangvisFerris_data[object_to_play[round]].y-=how_many_to_move
                elif direction_to_move == 3:
                    sangvisFerris_data[object_to_play[round]].y+=how_many_to_move
                round += 1
                if round != len(object_to_play):
                    resetEnemyMovingData()
            elif how_many_moved < how_many_to_move:
                how_many_moved+=0.1

    if round == len(object_to_play):
        round = 0
    """
    while pygame.mixer.music.get_busy() != 1:
        pygame.mixer.music.load('music/Snowflake.mp3')
        pygame.mixer.music.play(loops=9999, start=0.0)
    """

    #画面更新
    time.sleep(0.025)
    pygame.display.update()
