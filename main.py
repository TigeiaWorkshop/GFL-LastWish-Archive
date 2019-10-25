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

#加载主菜单文字
with open("lang/"+lang_file+".yaml", "r", encoding='utf-8') as f:
    lang_cn = yaml.load(f.read(),Loader=yaml.FullLoader)
    my_font =pygame.font.SysFont('simsunnsimsun',60)
    text_title =  lang_cn['main_menu']['text_title']
    text_continue = my_font.render(lang_cn['main_menu']['text_continue'], True, (105,105,105))
    text_chooseChapter = my_font.render(lang_cn['main_menu']['text_chooseChapter'], True, (255, 255, 255))
    text_setting = my_font.render(lang_cn['main_menu']['text_setting'], True, (105,105,105))
    text_dlc = my_font.render(lang_cn['main_menu']['text_dlc'], True, (105,105,105))
    text_wrokshop = my_font.render(lang_cn['main_menu']['text_wrokshop'], True, (105,105,105))
    text_exit = my_font.render(lang_cn['main_menu']['text_exit'], True, (255, 255, 255))
    c1 = my_font.render(lang_cn['chapter']['c1'], True, (255, 255, 255))
    c2 = my_font.render(lang_cn['chapter']['c2'], True, (105,105,105))
    c3 = my_font.render(lang_cn['chapter']['c3'], True, (105,105,105))
    c4 = my_font.render(lang_cn['chapter']['c4'], True, (105,105,105))
    c5 = my_font.render(lang_cn['chapter']['c5'], True, (105,105,105))
    c6 = my_font.render(lang_cn['chapter']['c6'], True, (105,105,105))
    c7 = my_font.render(lang_cn['chapter']['c7'], True, (105,105,105))
    c8 = my_font.render(lang_cn['chapter']['c8'], True, (105,105,105))
    back_button = my_font.render(lang_cn['chapter']['back'], True, (255, 255, 255))

# 创建窗口
screen = pygame.display.set_mode([window_x, window_y])
pygame.display.set_caption(text_title) #窗口标题

#加载主菜单背景
background_img_id = 0
background_img_list=[]
loading_img = pygame.image.load(os.path.join("img/loading_img/img1.png"))
while True:
    for event in pygame.event.get():
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            exit()
        if event.type == KEYDOWN and event.key == K_s:
            pygame.display.toggle_fullscreen()
    path = "img/main_menu/background_img"+str(background_img_id)+".jpg"
    background_img_list.append(pygame.image.load(os.path.join(path)).convert_alpha())
    percent_of_img_loaded = '{:.0f}%'.format(background_img_id/374*100)
    background_img_id+=1
    if background_img_id == 375:
        break
    screen.blit(loading_img, (0,0))
    screen.blit(my_font.render(str(percent_of_img_loaded), True, (255, 255, 255)), (10,10))
    pygame.display.update()

#加载地图背景图片
all_env_file_list = glob.glob(r'img\environment\*.png')
env_img_list={}
for i in range(len(all_env_file_list)):
    img_name = all_env_file_list[i].replace("img","").replace("environment","").replace(".png","").replace("\\","").replace("/","")
    env_img_list[img_name] = pygame.image.load(os.path.join(all_env_file_list[i])).convert_alpha()

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

background_img_id = 0
menu_type = 0
txt_location = int(window_x*2/3)
main_menu = True
# 游戏主循环
while True:
    while main_menu == True:
        for event in pygame.event.get():
            if event.type == KEYDOWN and event.key == K_s:
                pygame.display.toggle_fullscreen()
            elif event.type == MOUSEBUTTONDOWN:
                mouse_x,mouse_y=pygame.mouse.get_pos()
                if txt_location<mouse_x<txt_location+text_exit.get_width() and 750<mouse_y<750+text_exit.get_height():
                    exit()
                elif txt_location<mouse_x<txt_location+text_chooseChapter.get_width() and 350<mouse_y<350+text_chooseChapter.get_height():
                    if menu_type == 0:
                        menu_type = 1
                elif txt_location<mouse_x<txt_location+back_button.get_width() and window_y-150<mouse_y<window_y-150+back_button.get_height():
                    if menu_type == 1:
                        menu_type = 0
                elif txt_location<mouse_x<txt_location+c1.get_width() and (window_y-200)/9<mouse_y<(window_y-200)/9+c1.get_height():
                    if menu_type == 1:
                        main_menu = False

        screen.blit(background_img_list[background_img_id], (0,0))
        #角色动作
        if menu_type == 0:
            screen.blit(text_continue, (txt_location,250))
            screen.blit(text_chooseChapter, (txt_location,350))
            screen.blit(text_setting, (txt_location,450))
            screen.blit(text_dlc, (txt_location,550))
            screen.blit(text_wrokshop, (txt_location,650))
            screen.blit(text_exit, (txt_location,750))
        elif menu_type == 1:
            screen.blit(c1, (txt_location,(window_y-200)/9*1))
            screen.blit(c2, (txt_location,(window_y-200)/9*2))
            screen.blit(c3, (txt_location,(window_y-200)/9*3))
            screen.blit(c4, (txt_location,(window_y-200)/9*4))
            screen.blit(c5, (txt_location,(window_y-200)/9*5))
            screen.blit(c6, (txt_location,(window_y-200)/9*6))
            screen.blit(c7, (txt_location,(window_y-200)/9*7))
            screen.blit(c8, (txt_location,(window_y-200)/9*8))
            screen.blit(back_button, (txt_location,window_y-150))

        background_img_id += 1
        if background_img_id == 374:
            background_img_id = 0
        time.sleep(0.04)
        while pygame.mixer.music.get_busy() != 1:
            pygame.mixer.music.load('music/White_Front.mp3')
            pygame.mixer.music.play(loops=9999, start=0.0)
        pygame.display.update()
    pygame.mixer.music.stop()
    pygame.mixer.music.unload()

    my_font =pygame.font.SysFont('simsunnsimsun',25)
    #读取并初始化章节信息
    with open("data/main_chapter/chapter1.yaml", "r", encoding='utf-8') as f:
        chapter_info = yaml.load(f.read(),Loader=yaml.FullLoader)
        block_y = len(chapter_info["map"])
        block_x = len(chapter_info["map"][0])
        characters = chapter_info["character"]
        sangvisFerris = chapter_info["sangvisFerri"]
        map = chapter_info["map"]
        dialog1 = chapter_info["dialog"]
        dialog2 = chapter_info["dialog2"]
    block_x_length = window_x/block_x
    block_y_length = window_y/block_y

    #加载友方角色动画
    characters_dic={}
    for character in characters:
        characters_dic[character] = character_gif_dic(character)
    #加载敌方角色动画
    sangvisFerris_dic={}
    for sangvisFerri in sangvisFerris:
        sangvisFerris_dic[sangvisFerri] = character_gif_dic(sangvisFerri,"sangvisFerri")
    #初始化角色信息
    #hpManager(self, 最小攻击力, 最大攻击力, 血量上限 , 当前血量, x轴位置，y轴位置，攻击范围，移动范围)
    characters_data = {}
    i = 0
    for jiaose in characters:
        characters_data[jiaose] = characterDataManager(jiaose,150,200,300,300,3+i,4+i,4,2)
        i+=1
    sangvisFerris_data = {}
    for enemy in sangvisFerris:
        sangvisFerris_data[enemy] = characterDataManager(enemy,50,100,500,500,5,4,5,3)

    #生成随机方块名
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
    the_character_get_click = "sv-98"

    #故事前
    helianthus = pygame.image.load(os.path.join("img/npc/helianthus.png"))
    kryuger = pygame.image.load(os.path.join("img/npc/kryuger.png"))
    sv98_big_img = pygame.image.load(os.path.join("img/npc/sv98.png"))
    duel = pygame.transform.scale(pygame.image.load(os.path.join("img/others/duel.jpg")),(window_x,window_y))
    snowfield = pygame.transform.scale(pygame.image.load(os.path.join("img/others/snowfield.jpg")),(window_x,window_y))
    dialoguebox = pygame.transform.scale(pygame.image.load(os.path.join("img/others/dialoguebox.png")),(window_x-200,300))
    display_num = 0
    dialog1_display = True
    while len(dialog1)!=0 and dialog1_display == True:
        while pygame.mixer.music.get_busy() != 1:
            pygame.mixer.music.load('music/Machines_Are_Talking.mp3')
            pygame.mixer.music.play(loops=9999, start=0.0)
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    exit()
            elif event.type == MOUSEBUTTONDOWN:
                display_num += 1
                if display_num >= len(dialog1):
                    display_num -= 1
                    dialog1_display = False
        if len(dialog1[display_num])==3:
            display_name = my_font.render(dialog1[display_num][0], True, (255,255,255))
            display_content = my_font.render(dialog1[display_num][-1], True, (255,255,255))
            #背景
            screen.blit(duel,(0,0))
            #角色
            screen.blit(helianthus,(-100,100))
            screen.blit(kryuger,(window_x-1000,100))
        if len(dialog1[display_num])==2:
            display_name = my_font.render(dialog1[display_num][0], True, (255,255,255))
            display_content = my_font.render(dialog1[display_num][1], True, (255,255,255))
            #背景
            screen.blit(snowfield,(0,0))
            #角色
            big_img_x = (window_x - sv98_big_img.get_width())/2
            screen.blit(sv98_big_img,(big_img_x,100))
        #对话框内容
        screen.blit(dialoguebox,(100,window_y-dialoguebox.get_height()-50))
        screen.blit(display_name,(500,window_y-dialoguebox.get_height()))
        screen.blit(display_content,(440,window_y-dialoguebox.get_height()+70))
        pygame.display.update()
    # 游戏主循环
    pygame.mixer.music.stop()
    battle=True
    while battle==True:
        while pygame.mixer.music.get_busy() != 1:
            pygame.mixer.music.load('music/Snowflake.mp3')
            pygame.mixer.music.play(loops=9999, start=0.0)
        #加载地图
        for i in range(len(map_img_list)):
            for a in range(len(map_img_list[i])):
                img_display = pygame.transform.scale(env_img_list[map_img_list[i][a]], (int(block_x_length), int(block_y_length*1.5)))
                screen.blit(img_display,(a*block_x_length,i*block_y_length-block_x_length/2))
        if green_hide ==False:
            for x in range(characters_data[the_character_get_click].x-characters_data[the_character_get_click].attack_range,characters_data[the_character_get_click].x+characters_data[the_character_get_click].attack_range+1):
                attack_range_difference = characters_data[the_character_get_click].attack_range - characters_data[the_character_get_click].move_range
                if x < block_x:
                    if x < characters_data[the_character_get_click].x-characters_data[the_character_get_click].move_range-1:
                        screen.blit(red,(x*green.get_width(),characters_data[the_character_get_click].y*green.get_height()+7))
                    elif characters_data[the_character_get_click].x-characters_data[the_character_get_click].move_range-1<x<characters_data[the_character_get_click].x+characters_data[the_character_get_click].move_range+1:
                        if map[characters_data[the_character_get_click].y][x] == 0 or map[characters_data[the_character_get_click].y][x] == 3:
                            screen.blit(red,(x*green.get_width(),characters_data[the_character_get_click].y*green.get_height()+7))
                        else:
                            screen.blit(green,(x*green.get_width(),characters_data[the_character_get_click].y*green.get_height()+7))
                    else:
                        screen.blit(red,(x*green.get_width(),characters_data[the_character_get_click].y*green.get_height()+7))
            for y in range(characters_data[the_character_get_click].y-characters_data[the_character_get_click].attack_range,characters_data[the_character_get_click].y+characters_data[the_character_get_click].attack_range+1):
                #attack_range_difference = characters_data.attack_range - characters_data.move_range
                if y < block_y:
                    if y < characters_data[the_character_get_click].y-characters_data[the_character_get_click].move_range-1:
                        screen.blit(red,(characters_data[the_character_get_click].x*green.get_width(),y*green.get_height()+7))
                    elif characters_data[the_character_get_click].y-characters_data[the_character_get_click].move_range-1<y<characters_data[the_character_get_click].y+characters_data[the_character_get_click].move_range+1:
                        if map[y][characters_data[the_character_get_click].x] == 0 or map[y][characters_data[the_character_get_click].x] == 3:
                            screen.blit(red,(characters_data[the_character_get_click].x*green.get_width(),y*green.get_height()+7))
                        else:
                            screen.blit(green,(characters_data[the_character_get_click].x*green.get_width(),y*green.get_height()+7))
                    else:
                        screen.blit(red,(characters_data[the_character_get_click].x*green.get_width(),y*green.get_height()+7))
        if round == "player":
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        exit()
                    if event.key == K_t:
                        exit()
                elif event.type == MOUSEBUTTONDOWN:
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
                            if block_get_click_x == sangvisFerris_data["ripper"].x and  block_get_click_y == sangvisFerris_data["ripper"].y:
                                isWaiting = "ATTACKING"
                        elif characters_data[the_character_get_click].y-characters_data[the_character_get_click].attack_range-1<block_get_click_y<characters_data[the_character_get_click].y+characters_data[the_character_get_click].attack_range+1 and characters_data[the_character_get_click].x == block_get_click_x:
                            if block_get_click_x == sangvisFerris_data["ripper"].x and  block_get_click_y == sangvisFerris_data["ripper"].y:
                                isWaiting = "ATTACKING"
                    if block_get_click_x == characters_data[the_character_get_click].x and block_get_click_y == characters_data[the_character_get_click].y:
                        if green_hide == True:
                            action = "move"
                            green_hide = False
                        else:
                            green_hide = True
                            isWaiting = True
                            action = "wait"
                    if characters_data[the_character_get_click].x ==30 and characters_data[the_character_get_click].y ==14:
                        battle=False

            #角色动画
            if isWaiting == True:
                for every_chara in characters:
                    if every_chara != the_character_get_click:
                        action_displayer(characters_dic[characters_data[every_chara].name],"wait",characters_data[every_chara].x,characters_data[every_chara].y,)
                    else:
                        action_displayer(characters_dic[every_chara],action,characters_data[every_chara].x,characters_data[every_chara].y)
            elif isWaiting == "LEFTANDRIGHT":
                if temp_x < temp_max:
                    temp_x+=0.1
                    action_displayer(characters_dic[the_character_get_click],action,temp_x,characters_data[the_character_get_click].y)
                    for every_chara in characters:
                        if every_chara != the_character_get_click:
                            action_displayer(characters_dic[characters_data[every_chara].name],"wait",characters_data[every_chara].x,characters_data[every_chara].y,)
                    if temp_x >= temp_max:
                        isWaiting = True
                        characters_data[the_character_get_click].x = block_get_click_x
                        direction_to_move = -1
                        round = 'sangvisFerri'
                elif temp_x > temp_max:
                    temp_x-=0.1
                    action_displayer(characters_dic[characters_data[the_character_get_click].name],action,temp_x,characters_data[the_character_get_click].y)
                    for every_chara in characters:
                        if every_chara != the_character_get_click:
                            action_displayer(characters_dic[characters_data[every_chara].name],"wait",characters_data[every_chara].x,characters_data[every_chara].y,)
                    if temp_x <= temp_max:
                        isWaiting = True
                        characters_data[the_character_get_click].x = block_get_click_x
                        direction_to_move = -1
                        round = 'sangvisFerri'
            elif isWaiting == "TOPANDBOTTOM":
                if temp_y < temp_max:
                    temp_y+=0.1
                    action_displayer(characters_dic[characters_data[the_character_get_click].name],action,characters_data[the_character_get_click].x,temp_y,)
                    for every_chara in characters:
                        if every_chara != the_character_get_click:
                            action_displayer(characters_dic[characters_data[every_chara].name],"wait",characters_data[every_chara].x,characters_data[every_chara].y,)
                    if temp_y >= temp_max:
                        isWaiting = True
                        characters_data[the_character_get_click].y = block_get_click_y
                        direction_to_move = -1
                        round = 'sangvisFerri'
                elif temp_y > temp_max:
                    temp_y-=0.1
                    action_displayer(characters_dic[characters_data[the_character_get_click].name],action,characters_data[the_character_get_click].x,temp_y,)
                    for every_chara in characters:
                        if every_chara != the_character_get_click:
                            action_displayer(characters_dic[characters_data[every_chara].name],"wait",characters_data[every_chara].x,characters_data[every_chara].y,)
                    if temp_y <= temp_max:
                        isWaiting = True
                        characters_data[the_character_get_click].y = block_get_click_y
                        direction_to_move = -1
                        round = 'sangvisFerri'
            elif isWaiting == "ATTACKING":
                for every_chara in characters:
                    if every_chara != the_character_get_click:
                        action_displayer(characters_dic[characters_data[every_chara].name],"wait",characters_data[every_chara].x,characters_data[every_chara].y,)
                    else:
                        action_displayer(characters_dic[characters_data[every_chara].name],"attack",characters_data[every_chara].x,characters_data[every_chara].y,False)
                if characters_dic[characters_data[the_character_get_click].name]["attack"][1] == characters_dic[characters_data[the_character_get_click].name]["attack"][0][1]:
                    sangvisFerris_data["ripper"].decreaseHp(random.randint(characters_data[the_character_get_click].min_damage,characters_data[the_character_get_click].max_damage))
                    isWaiting = True
                    direction_to_move = -1
                    round = 'sangvisFerri'
                    characters_dic[characters_data[the_character_get_click].name]["attack"][1] = 0
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
            if sangvisFerris_data["ripper"].current_hp>0:
                for event in pygame.event.get():
                    if event.type == KEYDOWN:
                        if event.key == K_ESCAPE:
                            exit()
                green_hide = True
                for every_chara in characters:
                    action_displayer(characters_dic[characters_data[every_chara].name],"wait",characters_data[every_chara].x,characters_data[every_chara].y,)
                if direction_to_move == -1:
                    direction_to_move = random.randint(0,3) #0左1上2右3下
                    how_many_moved = 0
                    if direction_to_move == 0:
                        how_many_to_move = sangvisFerris_data["ripper"].x-sangvisFerris_data["ripper"].move_range
                    elif direction_to_move == 2:
                        how_many_to_move = sangvisFerris_data["ripper"].x+sangvisFerris_data["ripper"].move_range
                    elif direction_to_move == 1:
                        how_many_to_move = sangvisFerris_data["ripper"].y-sangvisFerris_data["ripper"].move_range
                    elif direction_to_move == 3:
                        how_many_to_move = sangvisFerris_data["ripper"].y+sangvisFerris_data["ripper"].move_range
                if direction_to_move == 0:
                    action_displayer(sangvisFerris_dic["ripper"],"move",sangvisFerris_data["ripper"].x-how_many_moved,sangvisFerris_data["ripper"].y)
                elif direction_to_move == 2:
                    action_displayer(sangvisFerris_dic["ripper"],"move",sangvisFerris_data["ripper"].x+how_many_moved,sangvisFerris_data["ripper"].y)
                elif direction_to_move == 1:
                    action_displayer(sangvisFerris_dic["ripper"],"move",sangvisFerris_data["ripper"].x,sangvisFerris_data["ripper"].y-how_many_moved)
                elif direction_to_move == 3:
                    action_displayer(sangvisFerris_dic["ripper"],"move",sangvisFerris_data["ripper"].x,sangvisFerris_data["ripper"].y+how_many_moved)
                if how_many_moved > sangvisFerris_data["ripper"].move_range:
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
                    if direction_to_move == 0:
                        if map[sangvisFerris_data["ripper"].y][int(sangvisFerris_data["ripper"].x-how_many_moved-1)]==0 or map[sangvisFerris_data["ripper"].y][int(sangvisFerris_data["ripper"].x-how_many_moved-1)]==3:
                            sangvisFerris_data["ripper"].x-=int(how_many_moved)
                            round = "player"
                    elif direction_to_move == 2:
                        if map[sangvisFerris_data["ripper"].y][int(sangvisFerris_data["ripper"].x+how_many_moved-1)]==0 or map[sangvisFerris_data["ripper"].y][int(sangvisFerris_data["ripper"].x+how_many_moved+1)]==3:
                            sangvisFerris_data["ripper"].x+=int(how_many_moved)
                            round = "player"
                    elif direction_to_move == 1:
                        if map[int(sangvisFerris_data["ripper"].y-how_many_moved-1)][sangvisFerris_data["ripper"].x]==0 or map[int(sangvisFerris_data["ripper"].y-how_many_moved-1)][sangvisFerris_data["ripper"].x]==3:
                            sangvisFerris_data["ripper"].y-=int(how_many_moved)
                            round = "player"
                    elif direction_to_move == 3:
                        if map[int(sangvisFerris_data["ripper"].y+how_many_moved-1)][sangvisFerris_data["ripper"].x]==0 or map[int(sangvisFerris_data["ripper"].y+how_many_moved-1)][sangvisFerris_data["ripper"].x]==3:
                            sangvisFerris_data["ripper"].y+=int(how_many_moved)
                            round = "player"
                    how_many_moved+=0.1
            else:
                round = "player"
        #胜利条件
        time.sleep(0.025)
        pygame.display.update()
    pygame.mixer.music.stop()
    #故事后
    kalina_img_list = []
    for i in range(7):
        kalina_img_list.append(pygame.image.load(os.path.join("img/npc/kalina/kalina_"+str(i)+".png")))
    researchJPG = pygame.transform.scale(pygame.image.load(os.path.join("img/others/research.jpg")),(window_x,window_y))
    display_num = 0
    dialog2_display = True
    while len(dialog2)!=0 and dialog2_display == True:
        while pygame.mixer.music.get_busy() != 1:
            pygame.mixer.music.load('music/Machines_Are_Talking.mp3')
            pygame.mixer.music.play(loops=9999, start=0.0)
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    exit()
            elif event.type == MOUSEBUTTONDOWN:
                display_num += 1
                if display_num >= len(dialog2):
                    dialog2_display = False
                    display_num -= 1
                    main_menu = True
        display_name = my_font.render(dialog2[display_num][0], True, (255,255,255))
        display_content = my_font.render(dialog2[display_num][-1], True, (255,255,255))
        screen.blit(researchJPG,(0,0))
        big_img_x = (window_x - kalina_img_list[2].get_width())/2
        screen.blit(kalina_img_list[display_num+1],(big_img_x,100))
        screen.blit(dialoguebox,(100,window_y-dialoguebox.get_height()-50))
        screen.blit(display_name,(500,window_y-dialoguebox.get_height()))
        screen.blit(display_content,(440,window_y-dialoguebox.get_height()+70))
        pygame.display.update()
    pygame.mixer.music.stop()
