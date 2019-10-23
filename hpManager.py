class characterDataManager:
    def __init__(self, name, min_damage,max_damage,max_hp,current_hp,x,y,speed):
        self.name = name
        self.min_damage = min_damage
        self.max_damage = max_damage
        self.max_hp = max_hp
        self.current_hp = current_hp
        self.x = x
        self.y = x
        self.speed = speed

    def decreaseHp(self,damage):
        self.current_hp-=damage

    def heal(self,hpHealed):
        self.current_hp+=hpHealed

class Bullet:
    def __init__(self, x, y,damage):
        self.x = x
        self.y = y
        self.damage = damage
