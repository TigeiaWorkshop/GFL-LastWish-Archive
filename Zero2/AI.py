from Zero2.basic import *

def AI(aiInControl,the_map_data,characters_data,sangvisFerris_data,the_characters_detected_last_round):
    attacking_range = []
    for y in range(sangvisFerris_data[aiInControl].y-sangvisFerris_data[aiInControl].attack_range,sangvisFerris_data[aiInControl].y+sangvisFerris_data[aiInControl].attack_range):
        if y < sangvisFerris_data[aiInControl].y:
            for x in range(sangvisFerris_data[aiInControl].x-sangvisFerris_data[aiInControl].attack_range-(y-sangvisFerris_data[aiInControl].y)+1,sangvisFerris_data[aiInControl].x+sangvisFerris_data[aiInControl].attack_range+(y-sangvisFerris_data[aiInControl].y)):
                if blocks_setting[theMap[y][x]][1] == True:
                    attacking_range.append([x,y])
        else:
            for x in range(sangvisFerris_data[aiInControl].x-sangvisFerris_data[aiInControl].attack_range+(y-sangvisFerris_data[aiInControl].y)+1,sangvisFerris_data[aiInControl].x+sangvisFerris_data[aiInControl].attack_range-(y-sangvisFerris_data[aiInControl].y)):
                if x == sangvisFerris_data[aiInControl].x and y == sangvisFerris_data[aiInControl].y:
                    pass
                else:
                    if blocks_setting[theMap[y][x]][1] == True:
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
                        break
                    if i == len(characters_can_be_attacked)-1:
                        characters_can_be_attacked.append(character)
        #检测是否有可以立马攻击的敌人
        elif characters_data[character].undetected == False:
            if len(characters_can_be_detect) == 0:
                characters_can_be_detect = [character]
            else:
                for i in range(len(characters_can_be_detect)):
                    if characters_data[character].current_hp < characters_data[characters_can_be_detect[i]].current_hp:
                        characters_can_be_detect.insert(i,character)
                        break
                    if i == len(characters_can_be_detect)-1:
                        characters_can_be_detect.append(character)

    if len(characters_can_be_attacked) > 0:
        return ["attack",characters_can_be_attacked[0]]
    else:
        if len(characters_can_be_detect) == 0:
            #上一个回合没有敌人暴露
            if len(the_characters_detected_last_round) == 0:
                if sangvisFerris_data[aiInControl].patrol_path == []:
                    return ["stay"]
                else:
                    map2d=Array2D(len(theMap[0]),len(theMap))
                    for y in range(len(theMap)):
                        for x in range(len(theMap[y])):
                            if blocks_setting[theMap[y][x]][1] == False:
                                map2d[x][y]=1
                            else:
                                temp_dic = dicMerge(characters_data,sangvisFerris_data)
                                for every_chara in temp_dic:
                                    if every_chara != the_character_get_click:
                                        map2d[temp_dic[every_chara].x][temp_dic[every_chara].y] = 1

                    #创建AStar对象,并设置起点和终点为
                    star_point_x = sangvisFerris_data[aiInControl].x
                    star_point_y = sangvisFerris_data[aiInControl].y
                    aStar=AStar(map2d,Point(star_point_x,star_point_y),Point(sangvisFerris_data[aiInControl].patrol_path[0][0],sangvisFerris_data[aiInControl].patrol_path[0][1]))
                    #开始寻路
                    pathList=aStar.start()
                    #遍历路径点,讲指定数量的点放到路径列表中
                    the_route = []
                    for i in range(sangvisFerris_data[aiInControl].move_range):
                        if Point(star_point_x+1,star_point_y) in pathList and [star_point_x+1,star_point_y] not in the_route:
                            star_point_x+=1
                        elif Point(star_point_x-1,star_point_y) in pathList and [star_point_x-1,star_point_y] not in the_route:
                            star_point_x-=1
                        elif Point(star_point_x,star_point_y+1) in pathList and [star_point_x,star_point_y+1] not in the_route:
                            star_point_y+=1
                        elif Point(star_point_x,star_point_y-1) in pathList and [star_point_x,star_point_y-1] not in the_route:
                            star_point_y-=1
                        the_route.append([star_point_x,star_point_y])
                    if the_route[-1][0] = sangvisFerris_data[aiInControl].patrol_path[0][0] and the_route[-1][1] = sangvisFerris_data[aiInControl].patrol_path[0][1] and len(sangvisFerris_data[aiInControl].patrol_path) >=2:
                        sangvisFerris_data[aiInControl].patrol_path.append(sangvisFerris_data[aiInControl].patrol_path[0])
                        sangvisFerris_data[aiInControl].patrol_path.pop(0)
            #上一个回合有敌人暴露
            else:
                pass
