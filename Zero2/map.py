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

def findPath(x_start,y_start,x_togo,y_togo,theMapWithRoute,route_move=[],direction_not_work=[]):
    if route_move == []:
        the_point_value = theMapWithRoute[y_togo][x_togo]
        if the_point_value == -1:
            the_point_value = min([theMapWithRoute[y_togo+1][x_togo],theMapWithRoute[y_togo-1][x_togo],theMapWithRoute[y_togo][x_togo+1],theMapWithRoute[y_togo][x_togo-1]])
            if the_point_value ==  theMapWithRoute[y_togo+1][x_togo]:
                y_togo+=1
            elif the_point_value == theMapWithRoute[y_togo-1][x_togo]:
                y_togo-=1
            elif the_point_value == theMapWithRoute[y_togo][x_togo+1]:
                x_togo+=1
            elif the_point_value == theMapWithRoute[y_togo][x_togo-1]:
                x_togo-=1
            else:
                print("warning from findpath system")
        route_move = [[x_togo,y_togo]]
    while the_point_value > 0:
        if y_start < y_togo and theMapWithRoute[y_togo-1][x_togo] == the_point_value-1 and route_move+[[y_togo-1,x_togo]] not in direction_not_work:
            y_togo-=1
            route_move.append([x_togo,y_togo])
        elif y_start > y_togo and theMapWithRoute[y_togo+1][x_togo] == the_point_value-1 and route_move+[[y_togo+1,x_togo]] not in direction_not_work:
            y_togo+=1
            route_move.append([x_togo,y_togo])
        elif x_start < x_togo and theMapWithRoute[y_togo][x_togo-1] == the_point_value-1 and route_move+[[y_togo,x_togo-1]] not in direction_not_work:
            x_togo-=1
            route_move.append([x_togo,y_togo])
        elif x_start > x_togo and theMapWithRoute[y_togo][x_togo+1] == the_point_value-1 and route_move+[[y_togo,x_togo+1]] not in direction_not_work:
            x_togo+=1
            route_move.append([x_togo,y_togo])
        else:
            direction_not_work.append(route_move)
            if len(route_move) > 1:
                route_move.pop()
                x_togo = route_move[-1][0]
                y_togo = route_move[-1][1]
        
        the_point_value-=1
    route_move.append([x_start,y_start])
    return route_move
