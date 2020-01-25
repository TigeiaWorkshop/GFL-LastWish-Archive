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

def findPath(x_start,y_start,x_togo,y_togo,theMap,blocks_setting):
    theMapWithRoute = create_map_with_path(x_start,y_start,theMap,blocks_setting)
    the_point_value = theMapWithRoute[y_togo][x_togo]
    route_move = [[x_togo,y_togo]]
    temp_x = x_togo
    temp_y = y_togo
    direction_not_work=[]
    for i in range (theMapWithRoute[y_togo][x_togo],0,-1):
        if y_start < temp_y and theMapWithRoute[temp_y-1][temp_x] == the_point_value-1 and "top" not in direction_not_work:
            temp_y-=1
            route_move.append([temp_x,temp_y])
            direction_not_work=[]
        else:
            if y_start > temp_y and theMapWithRoute[temp_y+1][temp_x] == the_point_value-1 and "bottom" not in direction_not_work:
                temp_y+=1
                route_move.append([temp_x,temp_y])
                direction_not_work=[]
            else:
                if x_start < temp_x and theMapWithRoute[temp_y][temp_x-1] == the_point_value-1 and "left" not in direction_not_work:
                    temp_x-=1
                    route_move.append([temp_x,temp_y])
                    direction_not_work=[]
                else:
                    if x_start > temp_x and theMapWithRoute[temp_y][temp_x+1] == the_point_value-1 and  "right" not in direction_not_work:
                        temp_x+=1
                        route_move.append([temp_x,temp_y])
                        direction_not_work=[]
                    else:
                        if temp_x == route_move[-1][0]:
                            if temp_y == route_move[-1][1]-1:
                                direction_not_work.append("top")
                            else:
                                direction_not_work.append("bottom")
                            temp_y = route_move[-1][1]
                        else:
                            if temp_x == route_move[-1][0]-1:
                                direction_not_work.append("left")
                            else:
                                direction_not_work.append("right")
                            temp_x = route_move[-1][0]
        the_point_value-=1
    route_move.append([temp_x,temp_y])
    return route_move