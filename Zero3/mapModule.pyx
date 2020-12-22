# cython: language_level=3

#方块类
class BlockObject:
    def __init__(self,name,canPassThrough):
        self.name = name
        self.canPassThrough = canPassThrough
    def update(self,name,canPassThrough):
        self.name = name
        self.canPassThrough = canPassThrough

#管理场景装饰物的类
class OrnamentationObject:
    def  __init__(self,x,y,itemType,image):
        self.x = x
        self.y = y
        self.type = itemType
        self.image = image
        self.alpha = None
    def __lt__(self,other):
        return self.y+self.x < other.y+other.x
    def get_pos(self):
        return self.x,self.y

#点
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __eq__(self, other):
        if self.x == other.x and self.y == other.y:
            return True
        return False

#描述AStar算法中的节点数据
class Node:
    def __init__(self, point, endPoint, g=0):
        self.point = point  # 自己的坐标
        self.father = None  # 父节点
        self.g = g  # g值，g值在用到的时候会重新算
        self.h = (abs(endPoint.x - point.x) + abs(endPoint.y - point.y)) * 10  # 计算h值