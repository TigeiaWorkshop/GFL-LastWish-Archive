import random

class characterDataManager:
    def __init__(self, name, min_damage,max_damage,max_hp,current_hp,x,y,attack_range,move_range,detect,gif_dic,current_bullets,maximum_bullets):
        self.name = name
        self.min_damage = min_damage
        self.max_damage = max_damage
        self.max_hp = max_hp
        self.current_hp = current_hp
        self.x = x
        self.y = y
        self.attack_range = attack_range
        self.move_range = move_range
        self.undetected = detect
        self.gif = gif_dic
        self.current_bullets = current_bullets
        self.maximum_bullets = maximum_bullets
        
    def decreaseHp(self,min_damage,max_damage):
        damage = random.randint(min_damage,max_damage)
        self.current_hp-=damage

    def heal(self,hpHealed):
        self.current_hp+=hpHealed

class sangvisFerriDataManager:
    def __init__(self, name, min_damage,max_damage,max_hp,current_hp,x,y,attack_range,move_range,gif_dic,current_bullets,maximum_bullets,patrol_path):
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
        self.current_bullets = current_bullets
        self.maximum_bullets = maximum_bullets
        self.patrol_path = patrol_path
        
    def decreaseHp(self,min_damage,max_damage):
        damage = random.randint(min_damage,max_damage)
        self.current_hp-=damage

    def heal(self,hpHealed):
        self.current_hp+=hpHealed