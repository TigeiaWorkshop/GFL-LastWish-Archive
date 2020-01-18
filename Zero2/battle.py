import glob
import math
import time
from sys import exit

import pygame
import yaml
from pygame.locals import *

from Zero2.basic import *
from Zero2.characterDataManager import *
from Zero2.map import *


def battle(chapter_name,window_x,window_y,screen,lang):
    #卸载音乐
    pygame.mixer.music.unload()

    #加载动作：接受角色名，动作，方位，完成对应的指令
    def action_displayer(chara_name,action,x,y,isContinue=True,ifFlip=False):
        if chara_name in sangvisFerris_name_list:
            hidden = sangvisFerris_data[chara_name].undetected
            gif_dic = sangvisFerris_data[chara_name].gif
            if sangvisFerris_data[chara_name].current_hp < 0:
                sangvisFerris_data[chara_name].current_hp = 0
            current_hp_to_display = fontRender(str(sangvisFerris_data[chara_name].current_hp)+"/"+str(sangvisFerris_data[chara_name].max_hp),"black",10)
            percent_of_hp = sangvisFerris_data[chara_name].current_hp/sangvisFerris_data[chara_name].max_hp
            current_bullets_situation = fontRender(str(sangvisFerris_data[chara_name].current_bullets)+"/"+str(sangvisFerris_data[chara_name].maximum_bullets),"black",10)
        elif chara_name in characters_name_list:
            hidden = characters_data[chara_name].undetected
            gif_dic = characters_data[chara_name].gif
            if characters_data[chara_name].current_hp<0:
                characters_data[chara_name].current_hp = 0
            current_hp_to_display = fontRender(str(characters_data[chara_name].current_hp)+"/"+str(characters_data[chara_name].max_hp),"black",10)
            percent_of_hp = characters_data[chara_name].current_hp/characters_data[chara_name].max_hp
            current_bullets_situation = fontRender(str(characters_data[chara_name].current_bullets)+"/"+str(characters_data[chara_name].maximum_bullets),"black",10)

        if percent_of_hp<0:
            percent_of_hp=0

        img_of_char = gif_dic[action][0][0][gif_dic[action][1]]
        if hidden == True:
            img_of_char.set_alpha(130)
        else:
            img_of_char.set_alpha(300)
        if ifFlip == True:
            printf(pygame.transform.flip(img_of_char,True,False),(x*green.get_width()-green.get_width()/2,y*green.get_height()-green.get_height()/2),screen,local_x,local_y)
        else:
            printf(img_of_char,(x*green.get_width()-green.get_width()/2,y*green.get_height()-green.get_height()/2),screen,local_x,local_y)
        if percent_of_hp>0:
            printf(hp_empty,(x*green.get_width(),y*green.get_height()*0.98),screen,local_x,local_y)
            printf(pygame.transform.scale(hp_red,(int(block_x_length*percent_of_hp),int(block_y_length/5))),(x*green.get_width(),y*green.get_height()*0.98),screen,local_x,local_y)
            printf(current_hp_to_display,(x*green.get_width(),y*green.get_height()*0.98),screen,local_x,local_y)
            printf(current_bullets_situation,(x*green.get_width()+current_hp_to_display.get_width()-current_bullets_situation.get_width(),y*green.get_height()*0.98-current_bullets_situation.get_height()),screen,local_x,local_y)
        gif_dic[action][1]+=1
        #射击动作
        if gif_dic[action][1] == 5 and action == "attack":
            pass
            #bullets_list.append(Bullet(characters_data.x+img_of_char.get_width()-20,characters_data.y+img_of_char.get_height()/2-5,300))
        if isContinue==True:
            if gif_dic[action][1] == gif_dic[action][0][1]:
                gif_dic[action][1] = 0
        elif isContinue==False:
            if gif_dic[action][1] == gif_dic[action][0][1]:
                return("Done")

    #加载背景图片
    all_env_file_list = glob.glob(r'Assets/img/environment/*.png')
    env_img_list={}
    for i in range(len(all_env_file_list)):
        img_name = all_env_file_list[i].replace("Assets","").replace("img","").replace("environment","").replace(".png","").replace("\\","").replace("/","")
        env_img_list[img_name] = loadImg(all_env_file_list[i]).convert_alpha()

    my_font =pygame.font.SysFont('simsunnsimsun',25)
    #读取并初始化章节信息
    with open("Data/main_chapter/"+chapter_name+"_map.yaml", "r", encoding='utf-8') as f:
        chapter_info = yaml.load(f.read(),Loader=yaml.FullLoader)
        chapter_title = chapter_info["title"]
        block_y = len(chapter_info["map"])
        block_x = len(chapter_info["map"][0])
        characters = chapter_info["character"]
        sangvisFerris = chapter_info["sangvisFerri"]
        theMap = chapter_info["map"]
        bg_music = chapter_info["background_music"]

    #地图方块图片随机化
    with open("Data/blocks.yaml", "r", encoding='utf-8') as f:
        reader = yaml.load(f.read(),Loader=yaml.FullLoader)
        blocks_setting = reader["blocks"]
    map_img_list = randomBlock(theMap,blocks_setting)
    #一个方块的长
    block_x_length = window_x/block_x*2
    #一个方块的高
    block_y_length = window_y/block_y*2

    #章节标题显示
    the_black = loadImg("Assets/img/UI/black.png",window_x,window_y)
    title_number_display = fontRender("Chapter-1","white")
    title_main_display = fontRender(chapter_title,"white")

    for i in range(0,600,1):
        printf(the_black,(0,0),screen)
        title_number_display.set_alpha(i)
        title_main_display.set_alpha(i)
        printf(title_number_display,((window_x-title_number_display.get_width())/2,400),screen)
        printf(title_main_display,((window_x-title_main_display.get_width())/2,500),screen)
        pygame.display.update()
    
    #加载雪花
    all_snow_img = glob.glob(r'Assets/img/environment/snow/*.png')
    snow_list = []
    for snowflake in all_snow_img:
        snow_list.append(loadImg(snowflake))

    snow_width = int(window_x/200)
    all_snow_img_len = len(snow_list)-1
    all_snow_on_screen = []

    class theImg:
        def __init__(self,x,y,img):
            self.x = x
            self.y = y 
            self.img = img

    for i in range(100):
        the_snow_add_y = random.randint(1,window_y)
        the_snow_add_x = random.randint(1,window_x*1.5)
        the_snow_add_img = pygame.transform.scale(snow_list[random.randint(0,all_snow_img_len)], (snow_width,snow_width))
        all_snow_on_screen.append(theImg(the_snow_add_x,the_snow_add_y,the_snow_add_img))
    
    #初始化角色信息
    #hpManager(名字, 最小攻击力, 最大攻击力, 血量上限 , 当前血量, x轴位置，y轴位置，攻击范围，移动范围,gif字典)
    characters_name_list = []
    characters_data = {}
    for jiaose in characters:
        characters_data[jiaose] = characterDataManager(jiaose,characters[jiaose]["min_damage"],characters[jiaose]["max_damage"],characters[jiaose]["max_hp"],characters[jiaose]["current_hp"],characters[jiaose]["x"],characters[jiaose]["y"],characters[jiaose]["attack_range"],characters[jiaose]["move_range"],characters[jiaose]["undetected"],character_gif_dic(jiaose,block_x_length,block_y_length),characters[jiaose]["current_bullets"],characters[jiaose]["maximum_bullets"])
        characters_name_list.append(jiaose)

    sangvisFerris_name_list = []
    sangvisFerris_data = {}
    for enemy in sangvisFerris:
        sangvisFerris_data[enemy] = characterDataManager(enemy,sangvisFerris[enemy]["min_damage"],sangvisFerris[enemy]["max_damage"],sangvisFerris[enemy]["max_hp"],sangvisFerris[enemy]["current_hp"],sangvisFerris[enemy]["x"],sangvisFerris[enemy]["y"],sangvisFerris[enemy]["attack_range"],sangvisFerris[enemy]["move_range"],sangvisFerris[enemy]["undetected"],character_gif_dic(enemy,block_x_length,block_y_length,"sangvisFerri"),sangvisFerris[enemy]["current_bullets"],sangvisFerris[enemy]["maximum_bullets"])
        sangvisFerris_name_list.append(enemy)

    #加载UI
    #加载按钮的文字
    with open("Lang/"+lang+".yaml", "r", encoding='utf-8') as f:
        chapter_info = yaml.load(f.read(),Loader=yaml.FullLoader)
        selectMenuButtons_dic = chapter_info["select_menu"]
    selectMenuFont = pygame.font.SysFont('simsunnsimsun',int(block_x_length/2))
    attack_button_txt = selectMenuFont.render(selectMenuButtons_dic["attack"], True, (105,105,105))
    move_button_txt = selectMenuFont.render(selectMenuButtons_dic["move"], True, (105,105,105))
    skill_button_txt = selectMenuFont.render(selectMenuButtons_dic["skill"], True, (105,105,105))
    reload_button_txt = selectMenuFont.render(selectMenuButtons_dic["reload"], True, (105,105,105))
    #加载选择菜单的图片
    select_menu_button = loadImg("Assets/img/UI/menu.png", block_x_length*2, block_x_length/1.3)
    #加载结束回合的图片
    end_round_button = loadImg("Assets/img/UI/endRound.png", block_x_length*2*28/15, block_x_length*2)
    #加载子弹图片
    bullet_img = loadImg("Assets/img/UI/bullet.png", block_x_length/6, block_y_length/12)
    bullets_list = []
    #加载血条
    hp_empty = loadImg("Assets/img/UI/hp_empty.png", block_x_length, block_y_length/5)
    hp_red = loadImg("Assets/img/UI/hp_red.png", block_x_length, block_y_length/5)
    #绿色方块/方块标准
    green = loadImg("Assets/img/UI/green.png", block_x_length, block_y_length).convert_alpha()
    green.set_alpha(100)
    red = loadImg("Assets/img/UI/red.png", block_x_length, block_y_length).convert_alpha()
    red.set_alpha(100)
    black = loadImg("Assets/img/UI/black.png", block_x_length, block_y_length).convert_alpha()
    black.set_alpha(100)
    new_block_type = 0
    per_block_width = green.get_width()
    per_block_height = green.get_height()
    
    #章节标题淡出
    for t in range(250,200,-1):
        for i in range(len(map_img_list)):
            for a in range(len(map_img_list[i])):
                img_display = pygame.transform.scale(env_img_list[map_img_list[i][a]], (int(block_x_length), int(block_y_length*1.5)))
                img_display.set_alpha(250-t)
                printf(img_display,(a*block_x_length,(i+1)*block_y_length-int(block_y_length*1.5)),screen)
        title_number_display.set_alpha(i)
        title_main_display.set_alpha(i)
        printf(title_number_display,((window_x-title_number_display.get_width())/2,400),screen)
        printf(title_main_display,((window_x-title_main_display.get_width())/2,500),screen)
        pygame.display.update()
    
    #部分设定初始化
    the_character_get_click = ""
    enemies_get_attack = ""
    enemies_in_control = ""
    action_choice =""
    green_hide = True
    battle=True
    how_many_to_move = 0
    how_many_moved = 0
    isWaiting = True
    the_dead_one = ""
    whose_round = "player"
    local_x = 0
    local_y = 0
    
    #行动点数
    action_points = len(characters_name_list)*7
    
    #计算光亮区域
    def calculate_darkness():
        light_area = []
        for each_chara in characters_data:
            for y in range(characters_data[each_chara].y-characters_data[each_chara].attack_range,characters_data[each_chara].y+characters_data[each_chara].attack_range):
                if y < characters_data[each_chara].y:
                    for x in range(characters_data[each_chara].x-characters_data[each_chara].attack_range-(y-characters_data[each_chara].y)+1,characters_data[each_chara].x+characters_data[each_chara].attack_range+(y-characters_data[each_chara].y)):
                        if (x,y) not in light_area:
                            light_area.append((x,y))
                else:
                    for x in range(characters_data[each_chara].x-characters_data[each_chara].attack_range+(y-characters_data[each_chara].y)+1,characters_data[each_chara].x+characters_data[each_chara].attack_range-(y-characters_data[each_chara].y)):
                        if (x,y) not in light_area:
                            light_area.append((x,y))
        return light_area
    
    light_area = calculate_darkness()

    # 游戏主循环
    while battle==True:
        #加载地图
        for i in range(len(map_img_list)):
            for a in range(len(map_img_list[i])):
                img_display = pygame.transform.scale(env_img_list[map_img_list[i][a]], (int(block_x_length), int(block_y_length*1.5)))
                printf(img_display,(a*block_x_length,(i+1)*block_y_length-block_y_length*1.5),screen,local_x,local_y)
        
        #加载阴环境
        for y in range(len(map_img_list)):
            for x in range(len(map_img_list[i])):
                if (x,y) not in light_area:
                    printf(black,(x*block_x_length,y*block_y_length),screen,local_x,local_y,)
        
        #加载结束回合的按钮
        printf(end_round_button,(window_x-select_menu_button.get_width()*1.5,window_y-300),screen)
        
        #加载玩家回合
        if whose_round == "player":
            #玩家输入按键判定
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        exit()
                    elif event.key == K_s:
                        local_y += 10
                    elif event.key == K_w:
                        local_y -= 10
                    elif event.key == K_a:
                        local_x -= 10
                    elif event.key == K_d:
                        local_x += 10
                elif event.type == MOUSEBUTTONDOWN:
                    if isGetClick(select_menu_button,(window_x-select_menu_button.get_width()*1.5,window_y-300))==True:
                        whose_round = "playerToSangvisFerris"
                        break
                    #获取角色坐标
                    mouse_x,mouse_y=pygame.mouse.get_pos()
                    block_get_click_x = int(mouse_x/green.get_width())
                    block_get_click_y = int(mouse_y/green.get_height())
                    for key in characters_data:
                        if characters_data[key].x == block_get_click_x and characters_data[key].y == block_get_click_y:
                            if key != the_character_get_click:
                                the_character_get_click = key
                                green_hide = "SelectMenu"
                                break
                            else:
                                green_hide = True
                                the_character_get_click = ""
            #显示选择菜单
            if green_hide == "SelectMenu":
                displayInCenter(attack_button_txt,select_menu_button,characters_data[the_character_get_click].x*green.get_width()-select_menu_button.get_width()-block_x_length*0.5,characters_data[the_character_get_click].y*green.get_height(),screen)
                displayInCenter(move_button_txt,select_menu_button,characters_data[the_character_get_click].x*green.get_width()+select_menu_button.get_width()-block_x_length*0.5,characters_data[the_character_get_click].y*green.get_height(),screen)
                displayInCenter(skill_button_txt,select_menu_button,characters_data[the_character_get_click].x*green.get_width()-block_x_length*0.5,characters_data[the_character_get_click].y*green.get_height()-select_menu_button.get_height()-block_x_length*0.5,screen)
                displayInCenter(reload_button_txt,select_menu_button,characters_data[the_character_get_click].x*green.get_width()-block_x_length*0.5,characters_data[the_character_get_click].y*green.get_height()+select_menu_button.get_height()+block_x_length*0.5,screen)
                if pygame.mouse.get_pressed()[0]:
                    if isGetClick(select_menu_button,(characters_data[the_character_get_click].x*green.get_width()-select_menu_button.get_width()-block_x_length*0.5,characters_data[the_character_get_click].y*green.get_height())):
                        if characters_data[the_character_get_click].current_bullets > 0:
                            action_choice = "attack"
                            block_get_click_x = -100
                            block_get_click_y = -100
                            green_hide = False
                    elif isGetClick(select_menu_button,(characters_data[the_character_get_click].x*green.get_width()+select_menu_button.get_width()-block_x_length*0.5,characters_data[the_character_get_click].y*green.get_height())):
                        action_choice = "move"
                        block_get_click_x = -100
                        block_get_click_y = -100
                        green_hide = False
                    elif isGetClick(select_menu_button,(characters_data[the_character_get_click].x*green.get_width()-block_x_length*0.5,characters_data[the_character_get_click].y*green.get_height()-select_menu_button.get_height()-block_x_length*0.5)):
                        action_choice = "skill"
                        block_get_click_x = -100
                        block_get_click_y = -100
                        green_hide = False
                    elif isGetClick(select_menu_button,(characters_data[the_character_get_click].x*green.get_width()-block_x_length*0.5,characters_data[the_character_get_click].y*green.get_height()+select_menu_button.get_height()+block_x_length*0.5)):
                        action_choice = "reload"
                        block_get_click_x = -100
                        block_get_click_y = -100
                        green_hide = False
            #显示攻击或移动范围
            if green_hide == False:
                #显示移动范围
                if action_choice == "move":
                    the_moving_range=[]
                    for x in range(characters_data[the_character_get_click].x+1,characters_data[the_character_get_click].x+characters_data[the_character_get_click].move_range+1):
                        if blocks_setting[theMap[characters_data[the_character_get_click].y][x]][1] == True:
                            printf(green,(x*green.get_width(),characters_data[the_character_get_click].y*green.get_height()),screen)
                        else:
                            the_moving_range.append(x-1)
                            for x_red in range(x,characters_data[the_character_get_click].x+characters_data[the_character_get_click].move_range+1):
                                printf(red,(x_red*green.get_width(),characters_data[the_character_get_click].y*green.get_height()),screen)
                            break
                        if(x == characters_data[the_character_get_click].x+characters_data[the_character_get_click].move_range):
                            the_moving_range.append(x)
                            
                    for x in range(characters_data[the_character_get_click].x-1,characters_data[the_character_get_click].x-characters_data[the_character_get_click].move_range-1,-1):
                        if blocks_setting[theMap[characters_data[the_character_get_click].y][x]][1] == True:
                            printf(green,(x*green.get_width(),characters_data[the_character_get_click].y*green.get_height()),screen)
                        else:
                            the_moving_range.append(x+1)
                            for x_red in range(x,characters_data[the_character_get_click].x-characters_data[the_character_get_click].move_range-1,-1):
                                printf(red,(x_red*green.get_width(),characters_data[the_character_get_click].y*green.get_height()),screen)
                            break
                        if(x == characters_data[the_character_get_click].x-characters_data[the_character_get_click].move_range):
                            the_moving_range.append(x)
                    for y in range(characters_data[the_character_get_click].y+1,characters_data[the_character_get_click].y+characters_data[the_character_get_click].move_range+1):
                        if blocks_setting[theMap[y][characters_data[the_character_get_click].x]][1] == True:
                            printf(green,(characters_data[the_character_get_click].x*green.get_width(),y*green.get_height()),screen)
                        else:
                            the_moving_range.append(y-1)
                            for y_red in range(y,characters_data[the_character_get_click].y+characters_data[the_character_get_click].move_range+1):
                                printf(red,(characters_data[the_character_get_click].x*green.get_width(),y_red*green.get_height()),screen)
                            break
                        if(y == characters_data[the_character_get_click].y+characters_data[the_character_get_click].move_range):
                            the_moving_range.append(y)
                    for y in range(characters_data[the_character_get_click].y-1,characters_data[the_character_get_click].y-characters_data[the_character_get_click].move_range-1,-1):
                        if blocks_setting[theMap[y][characters_data[the_character_get_click].x]][1] == True:
                            printf(green,(characters_data[the_character_get_click].x*green.get_width(),y*green.get_height()),screen)
                        else:
                            the_moving_range.append(y+1)
                            for y_red in range(y,characters_data[the_character_get_click].y-characters_data[the_character_get_click].move_range-1,-1):
                                printf(red,(characters_data[the_character_get_click].x*green.get_width(),y_red*green.get_height()),screen)
                            break
                        if(y == characters_data[the_character_get_click].y-characters_data[the_character_get_click].move_range):
                            the_moving_range.append(y)
                    if the_moving_range[0]>=block_get_click_x>=the_moving_range[1] and characters_data[the_character_get_click].y == block_get_click_y:
                        temp_x = characters_data[the_character_get_click].x
                        temp_max = block_get_click_x
                        isWaiting = "LEFTANDRIGHT"
                        green_hide = True
                        action_points -= abs(block_get_click_x-characters_data[the_character_get_click].x)
                    elif the_moving_range[2]>=block_get_click_y>=the_moving_range[3] and characters_data[the_character_get_click].x == block_get_click_x:
                        temp_y = characters_data[the_character_get_click].y
                        temp_max = block_get_click_y
                        isWaiting = "TOPANDBOTTOM"
                        green_hide = True
                        action_points -= abs(block_get_click_y-characters_data[the_character_get_click].y)
                    
                #显示攻击范围        
                elif action_choice == "attack" or action_choice == "skill":
                    attacking_range = []
                    for y in range(characters_data[the_character_get_click].y-characters_data[the_character_get_click].attack_range,characters_data[the_character_get_click].y+characters_data[the_character_get_click].attack_range):
                        if y < characters_data[the_character_get_click].y:
                            for x in range(characters_data[the_character_get_click].x-characters_data[the_character_get_click].attack_range-(y-characters_data[the_character_get_click].y)+1,characters_data[the_character_get_click].x+characters_data[the_character_get_click].attack_range+(y-characters_data[the_character_get_click].y)):
                                if blocks_setting[theMap[y][x]][1] == True:
                                    printf(green,(x*green.get_width(),y*green.get_height()),screen)
                                    attacking_range.append([x,y])
                                else:
                                    printf(red,(x*green.get_width(),y*green.get_height()),screen)
                        else:
                            for x in range(characters_data[the_character_get_click].x-characters_data[the_character_get_click].attack_range+(y-characters_data[the_character_get_click].y)+1,characters_data[the_character_get_click].x+characters_data[the_character_get_click].attack_range-(y-characters_data[the_character_get_click].y)):
                                if x == characters_data[the_character_get_click].x and y == characters_data[the_character_get_click].y:
                                    pass
                                else:
                                    if blocks_setting[theMap[y][x]][1] == True:
                                        printf(green,(x*green.get_width(),y*green.get_height()),screen)
                                        attacking_range.append([x,y])
                                    else:
                                        printf(red,(x*green.get_width(),y*green.get_height()),screen)
                    if [block_get_click_x,block_get_click_y] in attacking_range:
                        for enemies in sangvisFerris_data:
                            if block_get_click_x == sangvisFerris_data[enemies].x and  block_get_click_y == sangvisFerris_data[enemies].y:
                                isWaiting = "ATTACKING"
                                enemies_get_attack = enemies
                                green_hide = True
                                break
                elif action_choice == "reload":
                    if characters_data[the_character_get_click].maximum_bullets-characters_data[the_character_get_click].current_bullets > 0:
                        #向上取整
                        action_points -= math.ceil((characters_data[the_character_get_click].maximum_bullets-characters_data[the_character_get_click].current_bullets)/2)
                        characters_data[the_character_get_click].current_bullets = characters_data[the_character_get_click].maximum_bullets
                    else:
                        #无需换弹
                        pass
            
            #当有角色被点击时
            if the_character_get_click != "":
                #被点击的角色动画
                if isWaiting == "LEFTANDRIGHT":
                    green_hide=True
                    if temp_x < temp_max:
                        temp_x+=0.1
                        action_displayer(the_character_get_click,"move",temp_x,characters_data[the_character_get_click].y)
                        if temp_x >= temp_max:
                            characters_data[the_character_get_click].x = temp_max
                            #endOfPlayerRound()
                            light_area = calculate_darkness()
                            isWaiting =True
                            the_character_get_click = ""
                    elif temp_x > temp_max:
                        temp_x-=0.1
                        action_displayer(characters_data[the_character_get_click].name,"move",temp_x,characters_data[the_character_get_click].y,True,True)
                        if temp_x <= temp_max:
                            characters_data[the_character_get_click].x = temp_max
                            #endOfPlayerRound()
                            light_area = calculate_darkness()
                            isWaiting =True
                            the_character_get_click = ""
                elif isWaiting == "TOPANDBOTTOM":
                    green_hide=True
                    if temp_y < temp_max:
                        temp_y+=0.1
                        action_displayer(characters_data[the_character_get_click].name,"move",characters_data[the_character_get_click].x,temp_y)
                        if temp_y >= temp_max:
                            characters_data[the_character_get_click].y = temp_max
                            #endOfPlayerRound()
                            light_area = calculate_darkness()
                            isWaiting =True
                            the_character_get_click = ""
                    elif temp_y > temp_max:
                        temp_y-=0.1
                        action_displayer(characters_data[the_character_get_click].name,"move",characters_data[the_character_get_click].x,temp_y)
                        if temp_y <= temp_max:
                            characters_data[the_character_get_click].y = temp_max
                            #endOfPlayerRound()
                            light_area = calculate_darkness()
                            isWaiting =True
                            the_character_get_click = ""
                elif isWaiting == "ATTACKING":
                    green_hide=True
                    if action_choice == "attack":
                        action_displayer(characters_data[the_character_get_click].name,"attack",characters_data[the_character_get_click].x,characters_data[the_character_get_click].y,False)
                        if characters_data[the_character_get_click].gif["attack"][1] == characters_data[the_character_get_click].gif["attack"][0][1]-2:
                            sangvisFerris_data[enemies_get_attack].decreaseHp(characters_data[the_character_get_click].min_damage,characters_data[the_character_get_click].max_damage)
                        
                        the_characters_attacking = characters_data[the_character_get_click].gif
                        if the_characters_attacking["attack"][1] == the_characters_attacking["attack"][0][1]-1:
                            the_characters_attacking["attack"][1] = 0
                            characters_data[the_character_get_click].current_bullets -= 1
                            isWaiting =True
                            the_character_get_click = ""
                    if action_choice == "skill":
                        action_displayer(characters_data[the_character_get_click].name,"skill",characters_data[the_character_get_click].x,characters_data[the_character_get_click].y,False)
                        if characters_data[the_character_get_click].gif["skill"][1] == characters_data[the_character_get_click].gif["skill"][0][1]-2:
                            sangvisFerris_data[enemies_get_attack].decreaseHp(characters_data[the_character_get_click].min_damage,characters_data[the_character_get_click].max_damage)
                        
                        the_characters_attacking = characters_data[the_character_get_click].gif
                        if the_characters_attacking["skill"][1] == the_characters_attacking["skill"][0][1]-1:
                            the_characters_attacking["skill"][1] = 0
                            isWaiting =True
                            the_character_get_click = ""
                elif isWaiting == True:
                    action_displayer(characters_data[the_character_get_click].name,"wait",characters_data[the_character_get_click].x,characters_data[the_character_get_click].y)
            
            #子弹
            for per_bullet in bullets_list:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_1]:
                    new_block_type = 0
                printf(bullet_img, (per_bullet.x,per_bullet.y))
                per_bullet.x += 100
                if per_bullet.x > window_x:
                    bullets_list.remove(per_bullet)

        #↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓中间检测区↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓#
        if whose_round == "playerToSangvisFerris" or whose_round == "sangvisFerrisToPlayer":
            for enemies in sangvisFerris_data:
                action_displayer(enemies,"wait",sangvisFerris_data[enemies].x,sangvisFerris_data[enemies].y)
            for every_chara in characters:
                action_displayer(characters_data[every_chara].name,"wait",characters_data[every_chara].x,characters_data[every_chara].y)
            if whose_round == "playerToSangvisFerris":
                whose_round = "sangvisFerris"
            elif whose_round == "sangvisFerrisToPlayer":
                whose_round = "player"
        """
        #检测所有敌人是否都已经被消灭
        for i in range(len(sangvisFerris_name_list)):
            if sangvisFerris_data[sangvisFerris_name_list[i]].current_hp>0:
                break
            if i == len(sangvisFerris_name_list)-1:
                battle = False
        if battle == False:
            exit()
            break
        """
        #↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑中间检测区↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑#
        #敌方回合
        if whose_round == "sangvisFerris":
        
            if sangvisFerris_data[object_to_play[round]].current_hp<=0:
                round += 1
                #if round != len(object_to_play):
                    #resetEnemyMovingData()
            else:
                green_hide = True
                for every_chara in characters:
                    action_displayer(characters_data[every_chara].name,"wait",characters_data[every_chara].x,characters_data[every_chara].y)
                
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
                    #if round != len(object_to_play): 
                        #resetEnemyMovingData()
                elif how_many_moved < how_many_to_move:
                    how_many_moved+=0.1
        """
        while pygame.mixer.music.get_busy() != 1:
            pygame.mixer.music.load("Assets/music/"+bg_music)
            pygame.mixer.music.play(loops=9999, start=0.0)
        """
        #↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓角色动画展示区↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓#
        # 我方角色动画
        for every_chara in characters:
            if every_chara != the_character_get_click:
                if theMap[characters_data[every_chara].y][characters_data[every_chara].x] == 2:
                    characters_data[every_chara].undetected = True
                else:
                    characters_data[every_chara].undetected = False
                action_displayer(characters_data[every_chara].name,"wait",characters_data[every_chara].x,characters_data[every_chara].y)
        #敌方动画
        for enemies in sangvisFerris_data:
            if enemies != enemies_in_control:
                if sangvisFerris_data[enemies].current_hp>0:
                    if (sangvisFerris_data[enemies].x,sangvisFerris_data[enemies].y) in light_area:
                        if green_hide == True and pygame.mouse.get_pressed()[2]:
                            mouse_x,mouse_y=pygame.mouse.get_pos()
                            block_get_click_x2 = int(mouse_x/green.get_width())
                            block_get_click_y2 = int(mouse_y/green.get_height())
                            if block_get_click_x2 == sangvisFerris_data[enemies].x and block_get_click_y2 == sangvisFerris_data[enemies].y:
                                for y in range(sangvisFerris_data[enemies].y-sangvisFerris_data[enemies].attack_range,sangvisFerris_data[enemies].y+sangvisFerris_data[enemies].attack_range):
                                    if y < sangvisFerris_data[enemies].y:
                                        for x in range(sangvisFerris_data[enemies].x-sangvisFerris_data[enemies].attack_range-(y-sangvisFerris_data[enemies].y)+1,sangvisFerris_data[enemies].x+sangvisFerris_data[enemies].attack_range+(y-sangvisFerris_data[enemies].y)):
                                            if blocks_setting[theMap[y][x]][1] == True:
                                                printf(green,(x*green.get_width(),y*green.get_height()))
                                            else:
                                                printf(red,(x*green.get_width(),y*green.get_height()))
                                    else:
                                        for x in range(sangvisFerris_data[enemies].x-sangvisFerris_data[enemies].attack_range+(y-sangvisFerris_data[enemies].y)+1,sangvisFerris_data[enemies].x+sangvisFerris_data[enemies].attack_range-(y-sangvisFerris_data[enemies].y)):
                                            if x == sangvisFerris_data[enemies].x and y == sangvisFerris_data[enemies].y:
                                                pass
                                            else:
                                                if blocks_setting[theMap[y][x]][1] == True:
                                                    printf(green,(x*green.get_width(),y*green.get_height()))
                                                else:
                                                    printf(red,(x*green.get_width(),y*green.get_height()))
                        action_displayer(enemies,"wait",sangvisFerris_data[enemies].x,sangvisFerris_data[enemies].y)
                elif sangvisFerris_data[enemies].current_hp<=0:
                    action_displayer(enemies,"die",sangvisFerris_data[enemies].x,sangvisFerris_data[enemies].y,False)
                    the_dead_one = enemies
        if the_dead_one != "":
            the_characters_attacking = sangvisFerris_data[the_dead_one].gif
            if the_characters_attacking["die"][1] == the_characters_attacking["die"][0][1]-1:
                sangvisFerris_data.pop(the_dead_one)
            the_dead_one=""
        #↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑角色动画展示区↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑#

        #加载雪花
        for i in range(len(all_snow_on_screen)):
            printf(all_snow_on_screen[i].img,(all_snow_on_screen[i].x,all_snow_on_screen[i].y),screen)
            all_snow_on_screen[i].x -= 10
            all_snow_on_screen[i].y += 20
            if all_snow_on_screen[i].x < 0 or all_snow_on_screen[i].y > 1080:
                all_snow_on_screen[i].y = 0
                all_snow_on_screen[i].x = random.randint(1,window_x*1.5)
        
        points_left_txt = fontRender("剩余行动值："+str(action_points), "white")

        printf(points_left_txt,(0,0),screen)

        #画面更新
        pygame.display.update()
