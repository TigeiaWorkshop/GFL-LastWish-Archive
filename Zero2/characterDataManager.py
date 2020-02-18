import random

class Doll:
    def __init__(self,action_point,attack_range,current_bullets,current_hp,effective_range,gif_dic,magazine_capacity,max_damage,max_hp,min_damage,x,y):
        self.current_action_point = action_point
        self.max_action_point = action_point
        self.attack_range = attack_range
        self.current_bullets = current_bullets
        self.current_hp = current_hp
        self.effective_range = effective_range
        self.gif_dic = gif_dic
        self.magazine_capacity = magazine_capacity
        self.max_damage = max_damage
        self.max_hp = max_hp
        self.min_damage = min_damage
        self.x = x
        self.y = y
    def decreaseHp(self,min_damage,max_damage):
        damage = random.randint(min_damage,max_damage)
        self.current_hp-=damage
    def heal(self,hpHealed):
        self.current_hp+=hpHealed

class characterDataManager(Doll):
    def __init__(self,action_point,attack_range,current_bullets,current_hp,effective_range,gif_dic,magazine_capacity,max_damage,max_hp,min_damage,x,y,bullets_carried,start_position,detect):
        Doll.__init__(self,action_point,attack_range,current_bullets,current_hp,effective_range,gif_dic,magazine_capacity,max_damage,max_hp,min_damage,x,y)
        self.bullets_carried = bullets_carried
        self.start_position = start_position
        self.undetected = detect
        self.dying = False

class sangvisFerriDataManager(Doll):
    def __init__(self,action_point,attack_range,current_bullets,current_hp,effective_range,gif_dic,magazine_capacity,max_damage,max_hp,min_damage,x,y,patrol_path):
        Doll.__init__(self,action_point,attack_range,current_bullets,current_hp,effective_range,gif_dic,magazine_capacity,max_damage,max_hp,min_damage,x,y)
        self.patrol_path = patrol_path
