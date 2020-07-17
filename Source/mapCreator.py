# cython: language_level=3
from Zero3.basic import *
from Zero3.characterDataManager import *
from Zero3.map import *

def mapCreator(chapterName,screen,setting):
    #控制器输入组件
    InputController = GameController(screen)
    #屏幕尺寸
    window_x = screen.get_width()
    window_y = screen.get_height()
    #窗口标题
    pygame.display.set_caption("Girls frontline-Last Wish: MapCreator") 
    #卸载音乐
    pygame.mixer.music.unload()

    #加载地图设置
    with open("Data/blocks.yaml", "r", encoding='utf-8') as f:
        loadData = yaml.load(f.read(),Loader=yaml.FullLoader)
        blocks_setting = loadData["blocks"]
    with open("Data/decorations.yaml", "r", encoding='utf-8') as f:
        loadData = yaml.load(f.read(),Loader=yaml.FullLoader)
        decorations_setting = loadData["decorations"]

    #读取地图
    with open("Data/main_chapter/"+chapterName+"_map.yaml", "r", encoding='utf-8') as f:
        loadData = yaml.load(f.read(),Loader=yaml.FullLoader)
        #初始化角色信息
        characters_data = {}
        for each_character in loadData["character"]:
            characters_data[each_character] = CharacterDataManager(window_y,loadData["character"][each_character],"dev")
        sangvisFerris_data = {}
        for each_character in loadData["sangvisFerri"]:
            sangvisFerris_data[each_character] = SangvisFerriDataManager(loadData["sangvisFerri"][each_character],"dev")
        #初始化地图
        theMap = loadData["map"]
        if theMap == None or len(theMap) == 0:
            SnowEnvImg = ["TileSnow01","TileSnow01ToStone01","TileSnow01ToStone02","TileSnow02","TileSnow02ToStone01","TileSnow02ToStone02"]
            block_y = 50
            block_x = 50
            default_map = []
            for i in range(block_y):
                map_per_line = []
                for a in range(block_x):
                    map_per_line.append(SnowEnvImg[random.randint(0,5)])
                default_map.append(map_per_line)
            with open("Data/main_chapter/"+chapterName+"_map.yaml", "w", encoding='utf-8') as f:
                loadData["map"] = default_map
                yaml.dump(loadData, f)
        else:
            block_y = len(loadData["map"])
            block_x = len(loadData["map"][0])
    
    perBlockHeight = int(window_y/block_y*0.9)
    #加载地图
    theMap = MapObject(loadData,int(window_x/10))
    theMap.process_map(window_x,window_y)

    #加载背景图片
    all_env_file_list = glob.glob(r'Assets/image/environment/block/*.png')
    env_img_list={}
    for i in range(len(all_env_file_list)):
        img_name = all_env_file_list[i].replace(".","").replace("Assets","").replace("block","").replace("image","").replace("environment","").replace("png","").replace("\\","").replace("/","")
        env_img_list[img_name] = loadImg(all_env_file_list[i],int(theMap.perBlockWidth/3))

    #加载所有的角色的图片文件
    all_characters_list  = glob.glob(r'Assets/image/character/*')
    all_characters_img_list={}
    for i in range(len(all_characters_list)):
        img_name = all_characters_list[i].replace(".","").replace("Assets","").replace("image","").replace("character","").replace("\\","").replace("/","")
        all_characters_img_list[img_name] = loadImg(all_characters_list[i]+"/wait/"+img_name+"_wait_0.png",theMap.perBlockWidth)

    all_sangvisFerris_list  = glob.glob(r'Assets/image/sangvisFerri/*')
    all_sangvisFerris_img_list={}
    for i in range(len(all_sangvisFerris_list)):
        img_name = all_sangvisFerris_list[i].replace(".","").replace("Assets","").replace("image","").replace("sangvisFerri","").replace("\\","").replace("/","")
        all_sangvisFerris_img_list[img_name] = loadImg(all_sangvisFerris_list[i]+"/wait/"+img_name+"_wait_0.png",theMap.perBlockWidth)
    
    #加载所有的装饰品
    all_decorations  = glob.glob(r'Assets/image/environment/decoration/*')
    all_decorations_img_list = {}
    for i in range(len(all_decorations)):
        img_name = all_decorations[i].replace(".png","").replace(".","").replace("Assets","").replace("image","").replace("environment","").replace("decoration","").replace("\\","").replace("/","")
        all_decorations_img_list[img_name] = loadImg(all_decorations[i],theMap.perBlockWidth/5)
    
    del all_characters_list,all_sangvisFerris_list,all_decorations,all_env_file_list

    #绿色方块/方块标准
    green = loadImg("Assets/image/UI/green.png",int(theMap.perBlockWidth*0.8))
    green.set_alpha(150)
    red = loadImg("Assets/image/UI/red.png",int(theMap.perBlockWidth*0.8))
    red.set_alpha(150)
    deleteMode = False
    object_to_put_down = None
    #加载容器图片
    UIContainer = loadImage("Assets/image/UI/container.png",(-2,window_y*0.8),int(window_x*0.8), int(window_y*0.2))
    UIContainerRight = loadImage("Assets/image/UI/container.png",(window_x*0.825,0),int(window_x*0.175), int(window_y*1.025))
    #按钮
    UIButton = {
        "save": loadImage("Assets/image/UI/menu.png",(theMap.perBlockWidth*0.2,window_y*0.01),int(theMap.perBlockWidth*0.7)),
        "back": loadImage("Assets/image/UI/menu.png",(theMap.perBlockWidth*1,window_y*0.01),int(theMap.perBlockWidth*0.7)),
        "delete": loadImage("Assets/image/UI/menu.png",(theMap.perBlockWidth*1.8,window_y*0.01),int(theMap.perBlockWidth*0.7)),
        "reload": loadImage("Assets/image/UI/menu.png",(theMap.perBlockWidth*2.6,window_y*0.01),int(theMap.perBlockWidth*0.7)),
    }
    UIButtonTxt = {}

    #加载按钮的文字
    with open("Lang/"+setting["Language"]+".yaml", "r", encoding='utf-8') as f:
        loadData = yaml.load(f.read(),Loader=yaml.FullLoader)
        for txt in UIButton:
            UIButtonTxt[txt] = fontRender(loadData["mapCreator"][txt],"black",window_x/80)
            
    #数据控制器
    data_to_edit = None

    UI_local_x = 0
    UI_local_y = 0
    screen_to_move_x=None
    screen_to_move_y=None
    mouse_move_temp_x = -1
    mouse_move_temp_y = -1
    pressKeyToMove={"up":False,"down":False,"left":False,"right":False}

    #读取地图
    with open("Data/main_chapter/"+chapterName+"_map.yaml", "r", encoding='utf-8') as f:
        originalData = yaml.load(f.read(),Loader=yaml.FullLoader)

    isBuilding = True
    # 游戏主循环
    while isBuilding == True:
        mouse_x,mouse_y=InputController.get_pos()
        block_get_click = theMap.calBlockInMap(green,mouse_x,mouse_y)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    object_to_put_down = None
                    data_to_edit = None
                    deleteMode = False
                if event.key == pygame.K_w:
                    pressKeyToMove["up"]=True
                if event.key == pygame.K_s:
                    pressKeyToMove["down"]=True
                if event.key == pygame.K_a:
                    pressKeyToMove["left"]=True
                if event.key == pygame.K_d:
                    pressKeyToMove["right"]=True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    pressKeyToMove["up"]=False
                if event.key == pygame.K_s:
                    pressKeyToMove["down"]=False
                if event.key == pygame.K_a:
                    pressKeyToMove["left"]=False
                if event.key == pygame.K_d:
                    pressKeyToMove["right"]=False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if InputController.ifHover(UIContainerRight):
                    #上下滚轮-放大和缩小地图
                    if event.button == 4 and UI_local_y<0:
                        UI_local_y += window_y*0.1
                    elif event.button == 5:
                        UI_local_y -= window_y*0.1
                elif InputController.ifHover(UIContainer):
                    #上下滚轮-放大和缩小地图
                    if event.button == 4 and UI_local_x<0:
                        UI_local_x += window_x*0.05
                    elif event.button == 5:
                        UI_local_x -= window_x*0.05
                elif deleteMode == True and block_get_click != None:
                    any_dec_replace_name = None
                    any_dec_replace_type = None
                    for key,value in theMap.facilityData.items():
                        for key2,value2 in value.items():
                            if value2["x"] == block_get_click["x"] and value2["y"] == block_get_click["y"]:
                                any_dec_replace_name = key2
                                any_dec_replace_type = key
                                break
                    #如果发现有冲突的装饰物
                    if any_dec_replace_name != None:
                        originalData["facility"][any_dec_replace_type].pop(any_dec_replace_name)
                        theMap.facilityData[any_dec_replace_type].pop(any_dec_replace_name)
                    else:
                        any_chara_replace = None
                        for key,value in dicMerge(characters_data,sangvisFerris_data).items():
                            if value.x == block_get_click["x"] and value.y == block_get_click["y"]:
                                any_chara_replace = key
                                break
                        if any_chara_replace != None:
                            if any_chara_replace in characters_data:
                                characters_data.pop(any_chara_replace)
                                originalData["character"].pop(any_chara_replace)
                            elif any_chara_replace in sangvisFerris_data:
                                sangvisFerris_data.pop(any_chara_replace)
                                originalData["sangvisFerri"].pop(any_chara_replace)
                elif InputController.ifHover(UIButton["save"]) and object_to_put_down == None and deleteMode == False:
                    with open("Data/main_chapter/"+chapterName+"_map.yaml", "w", encoding='utf-8') as f:
                        yaml.dump(originalData, f)
                elif InputController.ifHover(UIButton["back"]) and object_to_put_down == None and deleteMode == False:
                    isBuilding = False
                    break
                elif InputController.ifHover(UIButton["delete"]) and object_to_put_down == None and deleteMode == False:
                    object_to_put_down = None
                    data_to_edit = None
                    deleteMode = True
                elif InputController.ifHover(UIButton["reload"]) and object_to_put_down == None and deleteMode == False:
                    tempLocal_x = theMap.local_x
                    tempLocal_y = theMap.local_y
                    #读取地图
                    with open("Data/main_chapter/"+chapterName+"_map.yaml", "r", encoding='utf-8') as f:
                        loadData = yaml.load(f.read(),Loader=yaml.FullLoader)
                        #初始化角色信息
                        characters_data = {}
                        for each_character in loadData["character"]:
                            characters_data[each_character] = CharacterDataManager(window_y,loadData["character"][each_character],"dev")
                        sangvisFerris_data = {}
                        for each_character in loadData["sangvisFerri"]:
                            sangvisFerris_data[each_character] = SangvisFerriDataManager(loadData["sangvisFerri"][each_character],"dev")
                    #加载地图
                    theMap = MapObject(loadData,int(window_x/10))
                    theMap.process_map(window_x,window_y)
                    theMap.local_x = tempLocal_x
                    theMap.local_y = tempLocal_y
                    #读取地图
                    with open("Data/main_chapter/"+chapterName+"_map.yaml", "r", encoding='utf-8') as f:
                        originalData = yaml.load(f.read(),Loader=yaml.FullLoader)
                else:
                    if pygame.mouse.get_pressed()[0] and block_get_click != None:
                        if object_to_put_down != None:
                            if object_to_put_down["type"] == "block":
                                originalData["map"][block_get_click["y"]][block_get_click["x"]] = object_to_put_down["id"]
                                theMap.mapData[block_get_click["y"]][block_get_click["x"]] = Block(object_to_put_down["id"],False)
                                theMap.process_map(window_x,window_y)
                            elif object_to_put_down["type"] == "decoration":
                                #查看当前位置是否有物品
                                any_dec_replace_name = None
                                any_dec_replace_type = None
                                for key,value in theMap.facilityData.items():
                                    for key2,value2 in value.items():
                                        if value2["x"] == block_get_click["x"] and value2["y"] == block_get_click["y"]:
                                            any_dec_replace_name = key2
                                            any_dec_replace_type = key
                                            break
                                #如果发现有冲突的装饰物
                                if any_dec_replace_name != None:
                                    originalData["facility"][any_dec_replace_type].pop(any_dec_replace_name)
                                    theMap.facilityData[any_dec_replace_type].pop(any_dec_replace_name)
                                decorationType = decorations_setting[object_to_put_down["id"]]
                                if decorationType not in originalData["facility"]:
                                    originalData["facility"][decorationType] = {}
                                    theMap.facilityData[decorationType] = {}
                                the_id = 0
                                while object_to_put_down["id"]+"_"+str(the_id) in originalData["facility"][decorationType]:
                                    the_id+=1
                                nameTemp = object_to_put_down["id"]+"_"+str(the_id)
                                originalData["facility"][decorationType][nameTemp] = {"image": object_to_put_down["id"],"x": block_get_click["x"],"y": block_get_click["y"]}
                                theMap.facilityData[decorationType][nameTemp] = {"image": object_to_put_down["id"],"x": block_get_click["x"],"y": block_get_click["y"]}
                            elif object_to_put_down["type"] == "character" or object_to_put_down["type"] == "sangvisFerri":
                                any_chara_replace = None
                                for key,value in dicMerge(characters_data,sangvisFerris_data).items():
                                    if value.x == block_get_click["x"] and value.y == block_get_click["y"]:
                                        any_chara_replace = key
                                        break
                                if any_chara_replace != None:
                                    if any_chara_replace in characters_data:
                                        characters_data.pop(any_chara_replace)
                                        originalData["character"].pop(any_chara_replace)
                                    elif any_chara_replace in sangvisFerris_data:
                                        sangvisFerris_data.pop(any_chara_replace)
                                        originalData["sangvisFerri"].pop(any_chara_replace)
                                the_id = 0
                                if object_to_put_down["type"] == "character":
                                    while object_to_put_down["id"]+"_"+str(the_id) in characters_data:
                                        the_id+=1
                                    nameTemp = object_to_put_down["id"]+"_"+str(the_id)
                                    originalData["character"][nameTemp] = {
                                        "action_point": 1,
                                        "attack_range": 1,
                                        "bullets_carried": 1,
                                        "current_bullets": 1,
                                        "current_hp": 1,
                                        "effective_range": {"far":[3,3],"middle":[2,2],"near":[1,1]},
                                        "kind": "HG",
                                        "magazine_capacity": 1,
                                        "max_damage": 1,
                                        "max_hp": 1,
                                        "min_damage": 1,
                                        "skill_cover_range": 1,
                                        "skill_effective_range":{"near":[1,1]},
                                        "type": object_to_put_down["id"],
                                        "detection": None,
                                        "x": block_get_click["x"],
                                        "y": block_get_click["y"],
                                    }
                                    characters_data[nameTemp] = CharacterDataManager(window_y,originalData["character"][nameTemp],"dev")
                                elif object_to_put_down["type"] == "sangvisFerri":
                                    while object_to_put_down["id"]+"_"+str(the_id) in sangvisFerris_data:
                                        the_id+=1
                                    nameTemp = object_to_put_down["id"]+"_"+str(the_id)
                                    originalData["sangvisFerri"][nameTemp] = {
                                        "action_point": 1,
                                        "attack_range": 1,
                                        "current_bullets": 1,
                                        "current_hp": 1,
                                        "effective_range": {"far":[3,3],"middle":[2,2],"near":[1,1]},
                                        "kind": "HG",
                                        "magazine_capacity": 1,
                                        "max_damage": 1,
                                        "max_hp": 1,
                                        "min_damage": 1,
                                        "patrol_path": [],
                                        "type": object_to_put_down["id"],
                                        "x": block_get_click["x"],
                                        "y": block_get_click["y"],
                                    }
                                    sangvisFerris_data[nameTemp] = SangvisFerriDataManager(originalData["sangvisFerri"][nameTemp],"dev")
        #移动屏幕
        if pygame.mouse.get_pressed()[2]:
            if mouse_move_temp_x == -1 and mouse_move_temp_y == -1:
                mouse_move_temp_x = mouse_x
                mouse_move_temp_y = mouse_y
            else:
                if mouse_move_temp_x != mouse_x or mouse_move_temp_y != mouse_y:
                    if mouse_move_temp_x > mouse_x:
                        theMap.local_x += mouse_move_temp_x-mouse_x
                    elif mouse_move_temp_x < mouse_x:
                        theMap.local_x -= mouse_x-mouse_move_temp_x
                    if mouse_move_temp_y > mouse_y:
                        theMap.local_y += mouse_move_temp_y-mouse_y
                    elif mouse_move_temp_y < mouse_y:
                        theMap.local_y -= mouse_y-mouse_move_temp_y
                    mouse_move_temp_x = mouse_x
                    mouse_move_temp_y = mouse_y
        else:
            mouse_move_temp_x = -1
            mouse_move_temp_y = -1
                        

        #根据按键情况设定要移动的数值
        if pressKeyToMove["up"] == True:
            if screen_to_move_y == None:
                screen_to_move_y = perBlockHeight/2
            else:
                screen_to_move_y += perBlockHeight/2
        if pressKeyToMove["down"] == True:
            if screen_to_move_y == None:
                screen_to_move_y = -perBlockHeight/2
            else:
                screen_to_move_y -= perBlockHeight/2
        if pressKeyToMove["left"] == True:
            if screen_to_move_x == None:
                screen_to_move_x = theMap.perBlockWidth/2
            else:
                screen_to_move_x += theMap.perBlockWidth/2
        if pressKeyToMove["right"] == True:
            if screen_to_move_x == None:
                screen_to_move_x = -theMap.perBlockWidth/2
            else:
                screen_to_move_x -= theMap.perBlockWidth/2
        
        #如果需要移动屏幕
        if screen_to_move_x != None and screen_to_move_x != 0:
            temp_value = theMap.local_x + screen_to_move_x*0.2
            if window_x-theMap.mapSurface.get_width()<=temp_value<=0:
                theMap.local_x = temp_value
                screen_to_move_x*=0.8
                if int(screen_to_move_x) == 0:
                    screen_to_move_x = 0
            else:
                screen_to_move_x = 0
        if screen_to_move_y != None and screen_to_move_y !=0:
            temp_value = theMap.local_y + screen_to_move_y*0.2
            if window_y-theMap.mapSurface.get_height()<=temp_value<=0:
                theMap.local_y = temp_value
                screen_to_move_y*=0.8
                if int(screen_to_move_y) == 0:
                    screen_to_move_y = 0
            else:
                screen_to_move_y = 0

        #加载地图
        screen_to_move_x,screen_to_move_y = theMap.display_map(screen,screen_to_move_x,screen_to_move_y)
        theMap.display_facility_ahead(screen)

        if block_get_click != None and InputController.ifHover(UIContainerRight)==False and InputController.ifHover(UIContainer)==False:
            if deleteMode == True:
                xTemp,yTemp = theMap.calPosInMap(block_get_click["x"],block_get_click["y"])
                drawImg(red,(xTemp+theMap.perBlockWidth*0.1,yTemp),screen)
            elif object_to_put_down != None:
                xTemp,yTemp = theMap.calPosInMap(block_get_click["x"],block_get_click["y"])
                drawImg(green,(xTemp+theMap.perBlockWidth*0.1,yTemp),screen)

        #角色动画
        for every_chara in characters_data:
            characters_data[every_chara].draw("wait",screen,theMap)
            if object_to_put_down == None and pygame.mouse.get_pressed()[0] and characters_data[every_chara].x == int(mouse_x/green.get_width()) and characters_data[every_chara].y == int(mouse_y/green.get_height()):
                data_to_edit = characters_data[every_chara]
        for enemies in sangvisFerris_data:
            sangvisFerris_data[enemies].draw("wait",screen,theMap)
            if object_to_put_down == None and pygame.mouse.get_pressed()[0] and sangvisFerris_data[enemies].x == int(mouse_x/green.get_width()) and sangvisFerris_data[enemies].y == int(mouse_y/green.get_height()):
                data_to_edit = sangvisFerris_data[enemies]
        
        #展示设施
        theMap.display_facility(screen,characters_data,sangvisFerris_data)

        #画出UI
        UIContainer.draw(screen)
        UIContainerRight.draw(screen)
        for Image in UIButton:
            if InputController.ifHover(UIButton[Image]) and object_to_put_down == None and deleteMode == False:
                UIButton[Image].set_alpha(255)
                UIButtonTxt[Image].set_alpha(255)
            else:
                UIButton[Image].set_alpha(100)
                UIButtonTxt[Image].set_alpha(100)
            UIButton[Image].draw(screen)
            posTempX = UIButton[Image].x+(UIButton[Image].width - UIButtonTxt[Image].get_width())/2
            posTempY = UIButton[Image].y+(UIButton[Image].height - UIButtonTxt[Image].get_height())/2
            drawImg(UIButtonTxt[Image],(posTempX,posTempY),screen)
            
        #显示所有可放置的友方角色
        i=0
        for every_chara in all_characters_img_list:
            tempX = theMap.perBlockWidth*i*0.6+UI_local_x
            if 0 <= tempX <= UIContainer.width*0.9:
                tempY = window_y*0.75
                drawImg(all_characters_img_list[every_chara],(tempX,tempY),screen)
                if pygame.mouse.get_pressed()[0] and InputController.ifHover(all_characters_img_list[every_chara],(tempX,tempY)):
                    object_to_put_down = {"type":"character","id":every_chara}
            elif tempX > UIContainer.width*0.9:
                break
            i+=1
        i=0
        #显示所有可放置的敌方角色
        for enemies in all_sangvisFerris_img_list:
            tempX = theMap.perBlockWidth*i*0.6+UI_local_x
            if 0 <= tempX <= UIContainer.width*0.9:
                tempY = window_y*0.83
                drawImg(all_sangvisFerris_img_list[enemies],(tempX,tempY),screen)
                if pygame.mouse.get_pressed()[0] and InputController.ifHover(all_sangvisFerris_img_list[enemies],(tempX,tempY)):
                    object_to_put_down = {"type":"sangvisFerri","id":enemies}
            elif tempX > UIContainer.width*0.9:
                break
            i+=1
        
        #显示所有可放置的环境方块
        i=0
        for img_name in env_img_list:
            posY = perBlockHeight*3*int(i/4)+UI_local_y
            if window_y*0.05<posY<window_y*0.9:
                posX = window_x*0.84+theMap.perBlockWidth/2.7*(i%4)
                drawImg(env_img_list[img_name],(posX,posY),screen)
                if pygame.mouse.get_pressed()[0] and InputController.ifHover(env_img_list[img_name],(posX,posY)):
                    object_to_put_down = {"type":"block","id":img_name}
            i+=1
        for img_name in all_decorations_img_list:
            posY = perBlockHeight*3*int(i/4)+UI_local_y
            if window_y*0.05<posY<window_y*0.9:
                posX = window_x*0.84+theMap.perBlockWidth/2.7*(i%4)
                drawImg(all_decorations_img_list[img_name],(posX,posY),screen)
                if pygame.mouse.get_pressed()[0] and InputController.ifHover(all_decorations_img_list[img_name],(posX,posY)):
                    object_to_put_down = {"type":"decoration","id":img_name}
            i+=1
        
        #跟随鼠标显示即将被放下的物品
        if object_to_put_down != None:
            if object_to_put_down["type"] == "block":
                drawImg(env_img_list[object_to_put_down["id"]],(mouse_x,mouse_y),screen)
            elif object_to_put_down["type"] == "decoration":
                drawImg(all_decorations_img_list[object_to_put_down["id"]],(mouse_x,mouse_y),screen)
            elif object_to_put_down["type"] == "character":
                drawImg(all_characters_img_list[object_to_put_down["id"]],(mouse_x-theMap.perBlockWidth/2,mouse_y-theMap.perBlockWidth/2.1),screen)
            elif object_to_put_down["type"] == "sangvisFerri":
                drawImg(all_sangvisFerris_img_list[object_to_put_down["id"]],(mouse_x-theMap.perBlockWidth/2,mouse_y-theMap.perBlockWidth/2.1),screen)
        
        #显示即将被编辑的数据
        object_edit_id = 0
        if data_to_edit != None:
            drawImg(fontRender("action points: "+str(data_to_edit.max_action_point),"black",15),(window_x*0.91,window_y*0.8),screen)
            drawImg(fontRender("attack range: "+str(data_to_edit.attack_range),"black",15),(window_x*0.91,window_y*0.8+20),screen)
            drawImg(fontRender("current bullets: "+str(data_to_edit.current_bullets),"black",15),(window_x*0.91,window_y*0.8+20*2),screen)
            drawImg(fontRender("magazine capacity: "+str(data_to_edit.magazine_capacity),"black",15),(window_x*0.91,window_y*0.8+20*3),screen)
            drawImg(fontRender("max hp: "+str(data_to_edit.max_hp),"black",15),(window_x*0.91,window_y*0.8+20*4),screen)
            drawImg(fontRender("effective range: "+str(data_to_edit.effective_range),"black",15),(window_x*0.91,window_y*0.8+20*5),screen)
            drawImg(fontRender("max damage: "+str(data_to_edit.max_damage),"black",15),(window_x*0.91,window_y*0.8+20*6),screen)
            drawImg(fontRender("min damage: "+str(data_to_edit.min_damage),"black",15),(window_x*0.91,window_y*0.8+20*7),screen)
            drawImg(fontRender("x: "+str(data_to_edit.x),"black",15),(window_x*0.91,window_y*0.8+20*8),screen)
            drawImg(fontRender("y: "+str(data_to_edit.y),"black",15),(window_x*0.91,window_y*0.8+20*9),screen)

        InputController.display(screen)
        pygame.display.flip()
