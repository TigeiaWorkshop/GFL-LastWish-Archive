# cython: language_level=3
from Zero2.basic import *
from Zero2.map import *

def AI(aiInControl,theMap,characters_data,sangvisFerris_data,the_characters_detected_last_round):
    character_with_min_hp = None
    characters_can_be_detect = []
    #检测是否有可以立马攻击的敌人
    for character in characters_data:
        if characters_data[character].undetected == True and characters_data[character].current_hp>0:
            #如果现在还没有可以直接攻击的角色或者当前历遍到角色的血量比最小值要高
            if character_with_min_hp == None or characters_data[character].current_hp <= characters_data[character_with_min_hp[0]].current_hp:
                temp_distance = abs(characters_data[character].x-sangvisFerris_data[aiInControl].x)+abs(characters_data[character].y-sangvisFerris_data[aiInControl].y)
                if "far" in sangvisFerris_data[aiInControl].effective_range and sangvisFerris_data[aiInControl].effective_range["far"][0] <= temp_distance <= sangvisFerris_data[aiInControl].effective_range["far"][1]:
                    character_with_min_hp = [character,"far"]
                elif "middle" in sangvisFerris_data[aiInControl].effective_range and sangvisFerris_data[aiInControl].effective_range["middle"][0] <= temp_distance <= sangvisFerris_data[aiInControl].effective_range["middle"][1]:
                    character_with_min_hp = [character,"middle"]
                elif "near" in sangvisFerris_data[aiInControl].effective_range and sangvisFerris_data[aiInControl].effective_range["near"][0] <= temp_distance <= sangvisFerris_data[aiInControl].effective_range["near"][1]:
                    if character_with_min_hp == None or characters_data[character].current_hp <= characters_data[character_with_min_hp[0]].current_hp:
                        character_with_min_hp = [character,"near"]
            if len(characters_can_be_detect) == 0:
                characters_can_be_detect = [character]
            else:
                for i in range(len(characters_can_be_detect)):
                    if characters_data[character].current_hp < characters_data[characters_can_be_detect[i]].current_hp:
                        characters_can_be_detect.insert(i,character)
    if character_with_min_hp != None:
        #[行动, 需要攻击的目标, 所在范围]
        return {"action": "attack",
        "target": character_with_min_hp[0],
        "target_area": character_with_min_hp[1]
        }
    elif sangvisFerris_data[aiInControl].kind == "HOC":
        return {"action": "stay"}
    else:
        #先检测是否有可以移动后攻击的敌人
        ap_need_to_attack = 5
        max_moving_routes_for_attacking = int((sangvisFerris_data[aiInControl].max_action_point - ap_need_to_attack)/2)
        #建立地图
        map2d=Array2D(len(theMap.mapData[0]),len(theMap.mapData))
        #历遍地图，设置障碍方块
        for y in range(len(theMap.mapData)):
            for x in range(len(theMap.mapData[y])):
                if theMap.mapData[y][x].canPassThrough == False:
                    map2d[x][y]=1
        #历遍设施，设置障碍方块
        for key1 in theMap.facilityData:
            for key2,value2 in theMap.facilityData[key1].items():
                map2d[value2["x"]][value2["y"]]=1
        #历遍所有角色，将角色的坐标点设置为障碍方块
        for character in characters_data:
            map2d[characters_data[character].x][characters_data[character].y] = 1
        for character in sangvisFerris_data:
            if character != aiInControl:
                map2d[sangvisFerris_data[character].x][sangvisFerris_data[character].y] = 1
        characters_can_be_attacked = {}
        #再次历遍所有characters_data以获取所有当前角色可以在移动后攻击到的敌对阵营角色
        for character in characters_data:
            if characters_data[character].undetected == True and characters_data[character].current_hp>0:
                map2d[characters_data[character].x][characters_data[character].y] = 0
                aStar=AStar(map2d,Point(sangvisFerris_data[aiInControl].x,sangvisFerris_data[aiInControl].y),Point(characters_data[character].x,characters_data[character].y))
                pathList=aStar.start()
                #检测当前角色移动后足以攻击到这个敌对阵营的角色
                temp_x = sangvisFerris_data[aiInControl].x
                temp_y = sangvisFerris_data[aiInControl].y
                the_route = []
                for i in range(max_moving_routes_for_attacking):
                    if Point(temp_x+1,temp_y) in pathList and [temp_x+1,temp_y] not in the_route:
                        temp_x+=1
                    elif Point(temp_x-1,temp_y) in pathList and [temp_x-1,temp_y] not in the_route:
                        temp_x-=1
                    elif Point(temp_x,temp_y+1) in pathList and [temp_x,temp_y+1] not in the_route:
                        temp_y+=1
                    elif Point(temp_x,temp_y-1) in pathList and [temp_x,temp_y-1] not in the_route:
                        temp_y-=1
                    else:
                        break
                    the_route.append([temp_x,temp_y])
                if [characters_data[character].x,characters_data[character].y] in the_route:
                    the_route.remove([characters_data[character].x,characters_data[character].y])
                if abs(characters_data[character].x-temp_x)+abs(characters_data[character].y-temp_y)<sangvisFerris_data[aiInControl].max_effective_range+1:
                    characters_can_be_attacked[character] = the_route
                map2d[characters_data[character].x][characters_data[character].y] = 1
        #如果存在可以在移动后攻击到的敌人
        if len(characters_can_be_attacked) >= 1:
            character_with_min_hp = None
            for key in characters_can_be_attacked:
                if character_with_min_hp == None or characters_data[key].current_hp < characters_data[character_with_min_hp[0]].current_hp:
                    character_with_min_hp = [key,characters_can_be_attacked[key]]
            temp_distance = abs(characters_data[character_with_min_hp[0]].x-character_with_min_hp[1][-1][0])+abs(characters_data[character_with_min_hp[0]].y-character_with_min_hp[1][-1][1])
            if "far" in sangvisFerris_data[aiInControl].effective_range and sangvisFerris_data[aiInControl].effective_range["far"][0] <= temp_distance <= sangvisFerris_data[aiInControl].effective_range["far"][1]:
                temp_area = "far"
            elif "middle" in sangvisFerris_data[aiInControl].effective_range and sangvisFerris_data[aiInControl].effective_range["middle"][0] <= temp_distance <= sangvisFerris_data[aiInControl].effective_range["middle"][1]:
                temp_area = "middle"
            elif "near" in sangvisFerris_data[aiInControl].effective_range and sangvisFerris_data[aiInControl].effective_range["near"][0] <= temp_distance <= sangvisFerris_data[aiInControl].effective_range["near"][1]:
                temp_area = "near"
            else:
                print('A character named '+aiInControl+' is causing trouble while attacking '+character_with_min_hp[0]+'. Then route is:')
                print(character_with_min_hp[1])
                print("temp_distance:",temp_distance)
                print('sangvisFerris_data[aiInControl].max_effective_range:',sangvisFerris_data[aiInControl].max_effective_range)
                raise Exception("Please double check this character's effective_range.")
            #[行动，已经整理好的路线，需要攻击的目标，所在范围]
            return {
                "action":"move&attack",
                "route":character_with_min_hp[1],
                "target":character_with_min_hp[0],
                "target_area": temp_area
            }
        #如果不存在可以在移动后攻击到的敌人
        elif len(characters_can_be_attacked) == 0:
            #如果这一回合没有敌人暴露
            if len(characters_can_be_detect) == 0:
                #如果上一个回合没有敌人暴露
                if len(the_characters_detected_last_round) == 0:
                    #如果敌人没有巡逻路线
                    if sangvisFerris_data[aiInControl].patrol_path == []:
                        return {"action": "stay"}
                    #如果敌人有巡逻路线
                    else:
                        temp_x = sangvisFerris_data[aiInControl].x
                        temp_y = sangvisFerris_data[aiInControl].y
                        #创建AStar对象
                        aStar=AStar(map2d,Point(temp_x,temp_y),Point(sangvisFerris_data[aiInControl].patrol_path[0][0],sangvisFerris_data[aiInControl].patrol_path[0][1]))
                        #开始寻路
                        pathList=aStar.start()
                        #遍历路径点,讲指定数量的点放到路径列表中
                        the_route = []
                        for i in range(sangvisFerris_data[aiInControl].max_action_point):
                            if Point(temp_x+1,temp_y) in pathList and [temp_x+1,temp_y] not in the_route:
                                temp_x+=1
                            elif Point(temp_x-1,temp_y) in pathList and [temp_x-1,temp_y] not in the_route:
                                temp_x-=1
                            elif Point(temp_x,temp_y+1) in pathList and [temp_x,temp_y+1] not in the_route:
                                temp_y+=1
                            elif Point(temp_x,temp_y-1) in pathList and [temp_x,temp_y-1] not in the_route:
                                temp_y-=1
                            else:
                                break
                            the_route.append([temp_x,temp_y])
                        if the_route[-1][0] == sangvisFerris_data[aiInControl].patrol_path[0][0] and the_route[-1][1] == sangvisFerris_data[aiInControl].patrol_path[0][1] and len(sangvisFerris_data[aiInControl].patrol_path) > 1:
                            sangvisFerris_data[aiInControl].patrol_path.append(sangvisFerris_data[aiInControl].patrol_path[0])
                            sangvisFerris_data[aiInControl].patrol_path.pop(0)
                        return {"action": "move","route":the_route}
                #如果上一个回合有敌人暴露
                else:
                    that_character = None
                    for each_chara in the_characters_detected_last_round:
                        if that_character== None:
                            that_character = each_chara
                        else:
                            if sangvisFerris_data[that_character].current_hp < sangvisFerris_data[that_character].current_hp:
                                that_character = that_character
                    temp_x = sangvisFerris_data[aiInControl].x
                    temp_y = sangvisFerris_data[aiInControl].y
                    #创建AStar对象
                    aStar=AStar(map2d,Point(temp_x,temp_y),Point(the_characters_detected_last_round[that_character][0],the_characters_detected_last_round[that_character][1]))
                    #开始寻路
                    pathList=aStar.start()
                    #遍历路径点,讲指定数量的点放到路径列表中
                    if pathList != None:
                        the_route = []
                        for i in range(sangvisFerris_data[aiInControl].max_action_point):
                            if Point(temp_x+1,temp_y) in pathList and [temp_x+1,temp_y] not in the_route:
                                temp_x+=1
                            elif Point(temp_x-1,temp_y) in pathList and [temp_x-1,temp_y] not in the_route:
                                temp_x-=1
                            elif Point(temp_x,temp_y+1) in pathList and [temp_x,temp_y+1] not in the_route:
                                temp_y+=1
                            elif Point(temp_x,temp_y-1) in pathList and [temp_x,temp_y-1] not in the_route:
                                temp_y-=1
                            else:
                                break
                            the_route.append([temp_x,temp_y])
                        return {"action": "move","route":the_route}
                    else:
                        return {"action": "stay"}
                    
            #如果这一回合有敌人暴露
            else:
                map2d[characters_data[characters_can_be_detect[0]].x][characters_data[characters_can_be_detect[0]].y] = 0
                #创建AStar对象
                temp_x = sangvisFerris_data[aiInControl].x
                temp_y = sangvisFerris_data[aiInControl].y
                aStar=AStar(map2d,Point(temp_x,temp_y),Point(characters_data[characters_can_be_detect[0]].x,characters_data[characters_can_be_detect[0]].y))
                pathList=aStar.start()
                #遍历路径点,讲指定数量的点放到路径列表中
                if pathList != None:
                    the_route = []
                    for i in range(sangvisFerris_data[aiInControl].max_action_point):
                        if Point(temp_x+1,temp_y) in pathList and [temp_x+1,temp_y] not in the_route:
                            temp_x+=1
                        elif Point(temp_x-1,temp_y) in pathList and [temp_x-1,temp_y] not in the_route:
                            temp_x-=1
                        elif Point(temp_x,temp_y+1) in pathList and [temp_x,temp_y+1] not in the_route:
                            temp_y+=1
                        elif Point(temp_x,temp_y-1) in pathList and [temp_x,temp_y-1] not in the_route:
                            temp_y-=1
                        else:
                            break
                        the_route.append([temp_x,temp_y])
                    if the_route[-1][0] == characters_data[characters_can_be_detect[0]].x and the_route[-1][1] == characters_data[characters_can_be_detect[0]].y:
                        the_route.pop()
                    return {"action": "move","route":the_route}
                else:
                    return {"action": "stay"}