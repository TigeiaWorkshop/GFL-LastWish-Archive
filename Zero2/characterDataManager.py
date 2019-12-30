import random

class characterDataManager:
    def __init__(self, name, min_damage,max_damage,max_hp,current_hp,x,y,attack_range,move_range,gif_dic):
        self.name = name
        self.min_damage = min_damage
        self.max_damage = max_damage
        self.max_hp = max_hp
        self.current_hp = current_hp
        self.x = x
        self.y = y
        self.attack_range = attack_range
        self.move_range = move_range
        self.gif = gif_dic

    def decreaseHp(self,min_damage,max_damage):
        damage = random.randint(min_damage,max_damage)
        self.current_hp-=damage

    def heal(self,hpHealed):
        self.current_hp+=hpHealed

class Bullet:
    def __init__(self, x, y,damage):
        self.x = x
        self.y = y
        self.damage = damage

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