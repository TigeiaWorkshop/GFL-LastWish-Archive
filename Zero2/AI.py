from Zero2.basic import *
from Zero2.map import *

def AI(aiInControl,theMap,characters_data,sangvisFerris_data,the_characters_detected_last_round,blocks_setting,facilities_data):
    attacking_range = []
    for y in range(sangvisFerris_data[aiInControl].y-sangvisFerris_data[aiInControl].attack_range,sangvisFerris_data[aiInControl].y+sangvisFerris_data[aiInControl].attack_range):
        if y < sangvisFerris_data[aiInControl].y:
            for x in range(sangvisFerris_data[aiInControl].x-sangvisFerris_data[aiInControl].attack_range-(y-sangvisFerris_data[aiInControl].y)+1,sangvisFerris_data[aiInControl].x+sangvisFerris_data[aiInControl].attack_range+(y-sangvisFerris_data[aiInControl].y)):
                if blocks_setting[theMap[y][x]]["canPassThrough"] == True:
                    attacking_range.append([x,y])
        else:
            for x in range(sangvisFerris_data[aiInControl].x-sangvisFerris_data[aiInControl].attack_range+(y-sangvisFerris_data[aiInControl].y)+1,sangvisFerris_data[aiInControl].x+sangvisFerris_data[aiInControl].attack_range-(y-sangvisFerris_data[aiInControl].y)):
                if x == sangvisFerris_data[aiInControl].x and y == sangvisFerris_data[aiInControl].y:
                    pass
                else:
                    if blocks_setting[theMap[y][x]]["canPassThrough"] == True:
                        attacking_range.append([x,y])
    characters_can_be_attacked = []
    characters_can_be_detect = []
    for character in characters_data:
        #检测是否有可以立马攻击的敌人
        if [characters_data[character].x,characters_data[character].y] in attacking_range and characters_data[character].undetected == False:
            if len(characters_can_be_attacked) == 0:
                characters_can_be_attacked = [character]
            else:
                for i in range(len(characters_can_be_attacked)):
                    if characters_data[character].current_hp < characters_data[characters_can_be_attacked[i]].current_hp:
                        characters_can_be_attacked.insert(i,character)
        #检测是否有可以立马攻击的敌人
        elif characters_data[character].undetected == False:
            if len(characters_can_be_detect) == 0:
                characters_can_be_detect = [character]
            else:
                for i in range(len(characters_can_be_detect)):
                    if characters_data[character].current_hp < characters_data[characters_can_be_detect[i]].current_hp:
                        characters_can_be_detect.insert(i,character)
                    
    if len(characters_can_be_attacked) > 0:
        return ["attack",characters_can_be_attacked[0]]
    else:
        #建立地图
        map2d=Array2D(len(theMap[0]),len(theMap))
        all_characters_data = dicMerge(characters_data,sangvisFerris_data)
        #历遍地图，设置障碍方块
        for y in range(len(theMap)):
            for x in range(len(theMap[y])):
                if blocks_setting[theMap[y][x]]["canPassThrough"] == False:
                    map2d[x][y]=1
        #历遍设施，设置障碍方块
        for key1 in facilities_data:
            for key2 in facilities_data[key1]:
                map2d[facilities_data[key1][key2]["x"]][facilities_data[key1][key2]["y"]]=1
        # 历遍所有角色，将角色的坐标点设置为障碍方块
        for every_chara in all_characters_data:
            if every_chara != aiInControl:
                map2d[all_characters_data[every_chara].x][all_characters_data[every_chara].y] = 1
        #设置起点和终点为
        star_point_x = sangvisFerris_data[aiInControl].x
        star_point_y = sangvisFerris_data[aiInControl].y

        #如果这一回合没有敌人暴露
        if len(characters_can_be_detect) == 0:
            #如果上一个回合没有敌人暴露
            if len(the_characters_detected_last_round) == 0:
                #如果敌人没有巡逻路线
                if sangvisFerris_data[aiInControl].patrol_path == []:
                    return ["stay"]
                #如果敌人有巡逻路线
                else:
                    #创建AStar对象
                    aStar=AStar(map2d,Point(star_point_x,star_point_y),Point(sangvisFerris_data[aiInControl].patrol_path[0][0],sangvisFerris_data[aiInControl].patrol_path[0][1]))
                    #开始寻路
                    pathList=aStar.start()
                    #遍历路径点,讲指定数量的点放到路径列表中
                    the_route = []
                    for i in range(sangvisFerris_data[aiInControl].max_action_point):
                        if Point(star_point_x+1,star_point_y) in pathList and [star_point_x+1,star_point_y] not in the_route:
                            star_point_x+=1
                        elif Point(star_point_x-1,star_point_y) in pathList and [star_point_x-1,star_point_y] not in the_route:
                            star_point_x-=1
                        elif Point(star_point_x,star_point_y+1) in pathList and [star_point_x,star_point_y+1] not in the_route:
                            star_point_y+=1
                        elif Point(star_point_x,star_point_y-1) in pathList and [star_point_x,star_point_y-1] not in the_route:
                            star_point_y-=1
                        else:
                            break
                        the_route.append([star_point_x,star_point_y])
                    if the_route[-1][0] == sangvisFerris_data[aiInControl].patrol_path[0][0] and the_route[-1][1] == sangvisFerris_data[aiInControl].patrol_path[0][1] and len(sangvisFerris_data[aiInControl].patrol_path) > 1:
                        sangvisFerris_data[aiInControl].patrol_path.append(sangvisFerris_data[aiInControl].patrol_path[0])
                        sangvisFerris_data[aiInControl].patrol_path.pop(0)
                    return ["move",the_route]
            #如果上一个回合有敌人暴露
            else:
                that_character = None
                for each_chara in the_characters_detected_last_round:
                    if that_character== None:
                        that_character = each_chara
                    else:
                        if sangvisFerris_data[that_character].current_hp < sangvisFerris_data[that_character].current_hp:
                            that_character = that_character
                #创建AStar对象
                aStar=AStar(map2d,Point(star_point_x,star_point_y),Point(the_characters_detected_last_round[that_character][0],the_characters_detected_last_round[that_character][1]))
                #开始寻路
                pathList=aStar.start()
                #遍历路径点,讲指定数量的点放到路径列表中
                if pathList != None:
                    the_route = []
                    for i in range(sangvisFerris_data[aiInControl].max_action_point):
                        if Point(star_point_x+1,star_point_y) in pathList and [star_point_x+1,star_point_y] not in the_route:
                            star_point_x+=1
                        elif Point(star_point_x-1,star_point_y) in pathList and [star_point_x-1,star_point_y] not in the_route:
                            star_point_x-=1
                        elif Point(star_point_x,star_point_y+1) in pathList and [star_point_x,star_point_y+1] not in the_route:
                            star_point_y+=1
                        elif Point(star_point_x,star_point_y-1) in pathList and [star_point_x,star_point_y-1] not in the_route:
                            star_point_y-=1
                        else:
                            break
                        the_route.append([star_point_x,star_point_y])
                    return ["move",the_route]
                else:
                    return ["stay"]
                
        #如果这一回合有敌人暴露
        else:
            map2d[characters_data[characters_can_be_detect[0]].x][characters_data[characters_can_be_detect[0]].y] = 0
            #创建AStar对象
            aStar=AStar(map2d,Point(star_point_x,star_point_y),Point(characters_data[characters_can_be_detect[0]].x,characters_data[characters_can_be_detect[0]].y))
            pathList=aStar.start()
            #遍历路径点,讲指定数量的点放到路径列表中
            if pathList != None:
                the_route = []
                for i in range(sangvisFerris_data[aiInControl].max_action_point):
                    if Point(star_point_x+1,star_point_y) in pathList and [star_point_x+1,star_point_y] not in the_route:
                        star_point_x+=1
                    elif Point(star_point_x-1,star_point_y) in pathList and [star_point_x-1,star_point_y] not in the_route:
                        star_point_x-=1
                    elif Point(star_point_x,star_point_y+1) in pathList and [star_point_x,star_point_y+1] not in the_route:
                        star_point_y+=1
                    elif Point(star_point_x,star_point_y-1) in pathList and [star_point_x,star_point_y-1] not in the_route:
                        star_point_y-=1
                    else:
                        break
                    the_route.append([star_point_x,star_point_y])
                if the_route[-1][0] == characters_data[characters_can_be_detect[0]].x and the_route[-1][1] == characters_data[characters_can_be_detect[0]].y:
                    the_route.pop()
                return ["move",the_route]
            else:
                return ["stay"]