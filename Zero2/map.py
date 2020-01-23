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