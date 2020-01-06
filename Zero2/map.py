import random
#随机地图方块

def randomBlock(map):
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
    return map_img_list