import random
import yaml
#import math

#随机地图方块
def randomBlock(theMap,blocks_setting):
    map_img_list = []
    for i in range(len(theMap)):
        map_img_per_line = []
        for a in range(len(theMap[i])):
            if blocks_setting[theMap[i][a]]["imgNum"] > 1:
                img_name = blocks_setting[theMap[i][a]]["name"]+str(random.randint(0,blocks_setting[theMap[i][a]]["imgNum"]-1))
            else:
                img_name = blocks_setting[theMap[i][a]]["name"]
            map_img_per_line.append(img_name)
        map_img_list.append(map_img_per_line)
    return map_img_list

#计算光亮区域
def calculate_darkness(characters_data,campfire_data):
    light_area = []
    for each_chara in characters_data:
        the_character_effective_range = 2
        if characters_data[each_chara].current_hp > 0 :
            if characters_data[each_chara].effective_range["far"] != None:
                the_character_effective_range = characters_data[each_chara].effective_range["far"][1]+1
            elif characters_data[each_chara].effective_range["middle"] != None:
                the_character_effective_range = characters_data[each_chara].effective_range["middle"][1]+1
            elif characters_data[each_chara].effective_range["near"] != None:
                the_character_effective_range = characters_data[each_chara].effective_range["near"][1]+1
        for y in range(int(characters_data[each_chara].y-the_character_effective_range),int(characters_data[each_chara].y+the_character_effective_range)):
            if y < characters_data[each_chara].y:
                for x in range(int(characters_data[each_chara].x-the_character_effective_range-(y-characters_data[each_chara].y)+1),int(characters_data[each_chara].x+the_character_effective_range+(y-characters_data[each_chara].y))):
                    if (x,y) not in light_area:
                        light_area.append((x,y))
            else:
                for x in range(int(characters_data[each_chara].x-the_character_effective_range+(y-characters_data[each_chara].y)+1),int(characters_data[each_chara].x+the_character_effective_range-(y-characters_data[each_chara].y))):
                    if (x,y) not in light_area:
                        light_area.append((x,y))
    if campfire_data != None:
        for the_campfire in campfire_data:
            for y in range(int(campfire_data[the_campfire]["y"]-campfire_data[the_campfire]["range"]),int(campfire_data[the_campfire]["y"]+campfire_data[the_campfire]["range"])):
                if y < campfire_data[the_campfire]["y"]:
                    for x in range(int(campfire_data[the_campfire]["x"]-campfire_data[the_campfire]["range"]-(y-campfire_data[the_campfire]["y"])+1),int(campfire_data[the_campfire]["x"]+campfire_data[the_campfire]["range"]+(y-campfire_data[the_campfire]["y"]))):
                        if (x,y) not in light_area:
                            light_area.append((x,y))
                else:
                    for x in range(int(campfire_data[the_campfire]["x"]-campfire_data[the_campfire]["range"]+(y-campfire_data[the_campfire]["y"])+1),int(campfire_data[the_campfire]["x"]+campfire_data[the_campfire]["range"]-(y-campfire_data[the_campfire]["y"]))):
                        if (x,y) not in light_area:
                            light_area.append((x,y))
    return light_area

def calculate_darkness_before_battle(characters_data,campfire_data):
    light_area = []
    for each_chara in characters_data:
        the_character_effective_range = 2
        if characters_data[each_chara].current_hp > 0 :
            if characters_data[each_chara].effective_range["far"] != None:
                the_character_effective_range = characters_data[each_chara].effective_range["far"][1]+1
            elif characters_data[each_chara].effective_range["middle"] != None:
                the_character_effective_range = characters_data[each_chara].effective_range["middle"][1]+1
            elif characters_data[each_chara].effective_range["near"] != None:
                the_character_effective_range = characters_data[each_chara].effective_range["near"][1]+1
        for y in range(int(characters_data[each_chara].start_position[1]-the_character_effective_range),int(characters_data[each_chara].start_position[1]+the_character_effective_range)):
            if y < characters_data[each_chara].start_position[1]:
                for x in range(int(characters_data[each_chara].start_position[0]-the_character_effective_range-(y-characters_data[each_chara].start_position[1])+1),int(characters_data[each_chara].start_position[0]+the_character_effective_range+(y-characters_data[each_chara].start_position[1]))):
                    if (x,y) not in light_area:
                        light_area.append((x,y))
            else:
                for x in range(int(characters_data[each_chara].start_position[0]-the_character_effective_range+(y-characters_data[each_chara].start_position[1])+1),int(characters_data[each_chara].start_position[0]+the_character_effective_range-(y-characters_data[each_chara].start_position[1]))):
                    if (x,y) not in light_area:
                        light_area.append((x,y))
    if campfire_data != None:
        for the_campfire in campfire_data:
            campfire_data[the_campfire]
            for y in range(int(campfire_data[the_campfire]["y"]-campfire_data[the_campfire]["range"]),int(campfire_data[the_campfire]["y"]+campfire_data[the_campfire]["range"])):
                if y < campfire_data[the_campfire]["y"]:
                    for x in range(int(campfire_data[the_campfire]["x"]-campfire_data[the_campfire]["range"]-(y-campfire_data[the_campfire]["y"])+1),int(campfire_data[the_campfire]["x"]+campfire_data[the_campfire]["range"]+(y-campfire_data[the_campfire]["y"]))):
                        if (x,y) not in light_area:
                            light_area.append((x,y))
                else:
                    for x in range(int(campfire_data[the_campfire]["x"]-campfire_data[the_campfire]["range"]+(y-campfire_data[the_campfire]["y"])+1),int(campfire_data[the_campfire]["x"]+campfire_data[the_campfire]["range"]-(y-campfire_data[the_campfire]["y"]))):
                        if (x,y) not in light_area:
                            light_area.append((x,y))
    return light_area

class Array2D:
    """
        说明：
            1.构造方法需要两个参数，即二维数组的宽和高
            2.成员变量w和h是二维数组的宽和高
            3.使用：‘对象[x][y]’可以直接取到相应的值
            4.数组的默认值都是0
    """
    def __init__(self,w,h):
        self.w=w
        self.h=h
        self.data=[]
        self.data=[[0 for y in range(h)] for x in range(w)]

    def showArray2D(self):
        for y in range(self.h):
            for x in range(self.w):
                print(self.data[x][y],end=' ')
            print("")

    def __getitem__(self, item):
        return self.data[item]

class Point:
    """
    表示一个点
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if self.x == other.x and self.y == other.y:
            return True
        return False

    def __str__(self):
        return "x:" + str(self.x) + ",y:" + str(self.y)

class AStar:
    class Node:  # 描述AStar算法中的节点数据
        def __init__(self, point, endPoint, g=0):
            self.point = point  # 自己的坐标
            self.father = None  # 父节点
            self.g = g  # g值，g值在用到的时候会重新算
            self.h = (abs(endPoint.x - point.x) + abs(endPoint.y - point.y)) * 10  # 计算h值
    def __init__(self, map2d, startPoint, endPoint, passTag=0):
        """
        构造AStar算法的启动条件
        :param map2d: Array2D类型的寻路数组
        :param startPoint: Point或二元组类型的寻路起点
        :param endPoint: Point或二元组类型的寻路终点
        :param passTag: int类型的可行走标记（若地图数据!=passTag即为障碍）
        """
        # 开启表
        self.openList = []
        # 关闭表
        self.closeList = []
        # 寻路地图
        self.map2d = map2d
        # 起点终点
        if isinstance(startPoint, Point) and isinstance(endPoint, Point):
            self.startPoint = startPoint
            self.endPoint = endPoint
        else:
            self.startPoint = Point(*startPoint)
            self.endPoint = Point(*endPoint)

        # 可行走标记
        self.passTag = passTag

    def getMinNode(self):
        """
        获得openlist中F值最小的节点
        :return: Node
        """
        currentNode = self.openList[0]
        for node in self.openList:
            if node.g + node.h < currentNode.g + currentNode.h:
                currentNode = node
        return currentNode

    def pointInCloseList(self, point):
        for node in self.closeList:
            if node.point == point:
                return True
        return False

    def pointInOpenList(self, point):
        for node in self.openList:
            if node.point == point:
                return node
        return None

    def endPointInCloseList(self):
        for node in self.openList:
            if node.point == self.endPoint:
                return node
        return None

    def searchNear(self, minF, offsetX, offsetY):
        """
        搜索节点周围的点
        :param minF:F值最小的节点
        :param offsetX:坐标偏移量
        :param offsetY:
        :return:
        """
        # 越界检测
        if minF.point.x + offsetX < 0 or minF.point.x + offsetX > self.map2d.w - 1 or minF.point.y + offsetY < 0 or minF.point.y + offsetY > self.map2d.h - 1:
            return
        # 如果是障碍，就忽略
        if self.map2d[minF.point.x + offsetX][minF.point.y + offsetY] != self.passTag:
            return
        # 如果在关闭表中，就忽略
        currentPoint = Point(minF.point.x + offsetX, minF.point.y + offsetY)
        if self.pointInCloseList(currentPoint):
            return
        # 设置单位花费
        if offsetX == 0 or offsetY == 0:
            step = 10
        else:
            step = 14
        # 如果不再openList中，就把它加入openlist
        currentNode = self.pointInOpenList(currentPoint)
        if not currentNode:
            currentNode = AStar.Node(currentPoint, self.endPoint, g=minF.g + step)
            currentNode.father = minF
            self.openList.append(currentNode)
            return
        # 如果在openList中，判断minF到当前点的G是否更小
        if minF.g + step < currentNode.g:  # 如果更小，就重新计算g值，并且改变father
            currentNode.g = minF.g + step
            currentNode.father = minF
    def start(self):
        """
        开始寻路
        :return: None或Point列表（路径）
        """
        # 判断寻路终点是否是障碍
        if self.map2d[self.endPoint.x][self.endPoint.y] != self.passTag:
            return None
        # 1.将起点放入开启列表
        startNode = AStar.Node(self.startPoint, self.endPoint)
        self.openList.append(startNode)
        # 2.主循环逻辑
        while True:
            # 找到F值最小的点
            minF = self.getMinNode()
            # 把这个点加入closeList中，并且在openList中删除它
            self.closeList.append(minF)
            self.openList.remove(minF)
            # 判断这个节点的上下左右节点
            self.searchNear(minF, 0, -1)
            self.searchNear(minF, 0, 1)
            self.searchNear(minF, -1, 0)
            self.searchNear(minF, 1, 0)
            # 判断是否终止
            point = self.endPointInCloseList()
            if point:  # 如果终点在关闭表中，就返回结果
                # print("关闭表中")
                cPoint = point
                pathList = []
                while True:
                    if cPoint.father:
                        pathList.append(cPoint.point)
                        cPoint = cPoint.father
                    else:
                        # print(pathList)
                        # print(list(reversed(pathList)))
                        # print(pathList.reverse())
                        return list(reversed(pathList))
            if len(self.openList) == 0:
                return None
