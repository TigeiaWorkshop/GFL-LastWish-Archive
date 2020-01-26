import random
import yaml

#随机地图方块
def randomBlock(theMap,blocks_setting):
    map_img_list = []
    for i in range(len(theMap)):
        map_img_per_line = []
        for a in range(len(theMap[i])):
            img_name = blocks_setting[theMap[i][a]][0]+str(random.randint(0,blocks_setting[theMap[i][a]][2]))
            map_img_per_line.append(img_name)
        map_img_list.append(map_img_per_line)
    return map_img_list

#计算光亮区域
def calculate_darkness(characters_data):
    light_area = []
    for each_chara in characters_data:
        for y in range(int(characters_data[each_chara].y-characters_data[each_chara].attack_range),int(characters_data[each_chara].y+characters_data[each_chara].attack_range)):
            if y < characters_data[each_chara].y:
                for x in range(int(characters_data[each_chara].x-characters_data[each_chara].attack_range-(y-characters_data[each_chara].y)+1),int(characters_data[each_chara].x+characters_data[each_chara].attack_range+(y-characters_data[each_chara].y))):
                    if (x,y) not in light_area:
                        light_area.append((x,y))
            else:
                for x in range(int(characters_data[each_chara].x-characters_data[each_chara].attack_range+(y-characters_data[each_chara].y)+1),int(characters_data[each_chara].x+characters_data[each_chara].attack_range-(y-characters_data[each_chara].y))):
                    if (x,y) not in light_area:
                        light_area.append((x,y))
    return light_area


def create_map_with_path(x_start,y_start,map_in,blocks_setting):
    map_out = []
    for y in range(len(map_in)):
        map_out_line = []
        for x in range(len(map_in[y])):
            if blocks_setting[map_in[y][x]][1] == True:
                if y <= y_start and x <= x_start:
                    map_out_line.append(x_start+y_start-x-y)
                elif y <= y_start and x >= x_start:
                    map_out_line.append(x+y_start-x_start-y)
                elif y >= y_start and x <= x_start:
                    map_out_line.append(x_start+y-x-y_start)
                elif y >= y_start and x >= x_start:
                    map_out_line.append(x+y-x_start-y_start)     
            else:
                map_out_line.append(-1)
        map_out.append(map_out_line)
    return map_out

def findPath(x_start,y_start,x_togo,y_togo,theMapWithRoute,route_move=[],direction_not_work=[],main=True):
    the_point_value = theMapWithRoute[y_togo][x_togo]
    if the_point_value == -1:
        temp_points = []
        if theMapWithRoute[y_togo+1][x_togo] != -1 and [x_togo,y_togo+1] not in direction_not_work:
            temp_points.append(theMapWithRoute[y_togo+1][x_togo])
        if theMapWithRoute[y_togo-1][x_togo] != -1 and [x_togo,y_togo-1] not in direction_not_work:
            temp_points.append(theMapWithRoute[y_togo-1][x_togo])
        if theMapWithRoute[y_togo][x_togo-1] != -1 and [x_togo-1,y_togo] not in direction_not_work:
            temp_points.append(theMapWithRoute[y_togo][x_togo-1])
        if theMapWithRoute[y_togo][x_togo+1] != -1 and [x_togo+1,y_togo] not in direction_not_work:
            temp_points.append(theMapWithRoute[y_togo][x_togo+1])
        if temp_points == []:
            return []
        else:
            the_point_value = min(temp_points)
            if the_point_value == theMapWithRoute[y_togo+1][x_togo]:
                y_togo+=1
            elif the_point_value == theMapWithRoute[y_togo-1][x_togo]:
                y_togo-=1
            elif the_point_value == theMapWithRoute[y_togo][x_togo+1]:
                x_togo+=1
            elif the_point_value == theMapWithRoute[y_togo][x_togo-1]:
                x_togo-=1
    if route_move==[]:
        route_move = [[x_togo,y_togo]]
    while the_point_value > 0:
        if y_start <= y_togo and theMapWithRoute[y_togo-1][x_togo] == the_point_value-1 and route_move+[[x_togo,y_togo-1]] not in direction_not_work:
            y_togo-=1
            route_move.append([x_togo,y_togo])
        elif y_start >= y_togo and theMapWithRoute[y_togo+1][x_togo] == the_point_value-1 and route_move+[[x_togo,y_togo+1]] not in direction_not_work:
            y_togo+=1
            route_move.append([x_togo,y_togo])
        elif x_start <= x_togo and theMapWithRoute[y_togo][x_togo-1] == the_point_value-1 and route_move+[[x_togo-1,y_togo]] not in direction_not_work:
            x_togo-=1
            route_move.append([x_togo,y_togo])
        elif x_start >= x_togo and theMapWithRoute[y_togo][x_togo+1] == the_point_value-1 and route_move+[[x_togo+1,y_togo]] not in direction_not_work:
            x_togo+=1
            route_move.append([x_togo,y_togo])
        else:
            direction_not_work.append(route_move)
            if len(route_move) > 1:
                route_move.pop()
                x_togo = route_move[-1][0]
                y_togo = route_move[-1][1]
            other_paths=[]
            if route_move+[[x_togo,y_togo-1]] not in direction_not_work and theMapWithRoute[y_togo-1][x_togo] != -1:
                temp_route = findPath(x_start,y_start,x_togo,y_togo-1,theMapWithRoute,route_move,direction_not_work,False)
                if temp_route != []:
                    other_paths.append(temp_route)
            if route_move+[[x_togo,y_togo+1]] not in direction_not_work and theMapWithRoute[y_togo+1][x_togo] != -1:
                temp_route = findPath(x_start,y_start,x_togo,y_togo+1,theMapWithRoute,route_move,direction_not_work,False)
                if temp_route != []:
                    other_paths.append(temp_route)
            if route_move+[[x_togo-1,y_togo]] not in direction_not_work and theMapWithRoute[y_togo][x_togo-1] != -1:
                temp_route = findPath(x_start,y_start,x_togo-1,y_togo,theMapWithRoute,route_move,direction_not_work,False)
                if temp_route != []:
                    other_paths.append(temp_route)
            if route_move+[[x_togo+1,y_togo]] not in direction_not_work and theMapWithRoute[y_togo][x_togo-1] != -1:
                temp_route = findPath(x_start,y_start,x_togo+1,y_togo,theMapWithRoute,route_move,direction_not_work,False)
                if temp_route != []:
                    other_paths.append(temp_route)
            if other_paths == []:
                return []
            else:
                min_len_route = other_paths[0]
                if len(other_paths)==1:
                    if main == False:
                        return min_len_route
                    else:
                        route_move = min_len_route
                else:
                    for i in range(1,len(other_paths)):
                        if len(other_paths[i])< len(min_len_route):
                            min_len_route = other_paths[i]
                    if main == False:
                        return min_len_route
                    else:
                        route_move = min_len_route
        the_point_value-=1
    route_move.append([x_start,y_start])
    return route_move
