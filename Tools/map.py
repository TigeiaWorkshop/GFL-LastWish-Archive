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