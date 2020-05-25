# cython: language_level=3
from Zero2.basic import *

class MapObject:
    def  __init__(self,mapDataDic,perBlockWidth):
        #加载地图设置
        with open("Data/blocks.yaml", "r", encoding='utf-8') as f:
            blocks_setting = yaml.load(f.read(),Loader=yaml.FullLoader)["blocks"]
        mapData = mapDataDic["map"]
        facilityData = mapDataDic["facility"]
        self.darkMode = mapDataDic["darkMode"]
        self.perBlockWidth = perBlockWidth
        self.row = len(mapData)
        self.column = len(mapData[0])
        self.env_img_list_original = load_env_images(mapData,None,None,self.darkMode)
        self.env_img_list = load_env_images(mapData,perBlockWidth,None,self.darkMode)
        self.mapData = initialBlockData(mapData,facilityData,blocks_setting)
        self.facilityImg = loadFacilityImg(facilityData,self.darkMode)
        self.facilityData = initialFacility(facilityData)
        self.lightArea = []
        self.surface_width = int(perBlockWidth*0.9*((len(mapData)+len(mapData[0])+1)/2))
        self.surface_height = int(perBlockWidth*0.45*((len(mapData)+len(mapData[0])+1)/2)+perBlockWidth)
        self.bgImg = loadImg("Assets/image/dialog_background/"+mapDataDic["backgroundImage"])
        self.mapSurface = pygame.surface.Surface((self.surface_width,self.surface_height)).convert()
        self.mapBlocks =  initalBlocks(mapData)
        for eachBlock in self.mapBlocks:
            eachBlock.redrawArea(self.env_img_list,perBlockWidth,self.darkMode)
    #控制地图放大缩小
    def changePerBlockSize(self,newPerBlockWidth,window_x,window_y):
        self.perBlockWidth = newPerBlockWidth
        for key in self.env_img_list["normal"]:
            self.env_img_list["normal"][key] = pygame.transform.scale(self.env_img_list_original["normal"][key], (self.perBlockWidth, round(self.perBlockWidth/self.env_img_list_original["normal"][key].get_width()*self.env_img_list_original["normal"][key].get_height())))
        if self.darkMode == True:
            for key in self.env_img_list["dark"]:
                self.env_img_list["dark"][key] = pygame.transform.scale(self.env_img_list_original["dark"][key], (self.perBlockWidth, round(self.perBlockWidth/self.env_img_list_original["dark"][key].get_width()*self.env_img_list_original["dark"][key].get_height())))
        self.surface_width = int(newPerBlockWidth*0.9*((len(self.mapData)+len(self.mapData[0])+1)/2))
        self.surface_height = int(newPerBlockWidth*0.45*((len(self.mapData)+len(self.mapData[0])+1)/2)+newPerBlockWidth)
        self.mapSurface = pygame.surface.Surface((self.surface_width,self.surface_height))
        self.process_map(window_x,window_y)
    #把地图画到屏幕上
    def display_map(self,screen,local_x=0,local_y=0):
        screen.blit(self.mapSurface,(local_x,local_y))
        self.drawChest(screen,local_x,local_y)
    #画上设施
    def display_facility(self,characters_data,screen,local_x=0,local_y=0):
        for key,value in self.facilityData.items():
            for key2,value2 in value.items():
                imgToBlit = None
                xTemp,yTemp = calPosInMap(self.row,self.perBlockWidth,value2["x"],value2["y"],local_x,local_y)
                if -self.perBlockWidth<=xTemp<screen.get_width() and -self.perBlockWidth<=yTemp<screen.get_height():
                    if self.darkMode == True and (value2["x"],value2["y"]) not in self.lightArea:
                        keyWordTemp = "dark"
                    else:
                        keyWordTemp = "normal"
                    #画上篝火
                    if key == "campfire":
                        imgToBlit = pygame.transform.scale(self.facilityImg["normal"]["campfire"][int(value2["imgId"])], (round(self.perBlockWidth/2),round(self.perBlockWidth/2)))
                        if value2["imgId"] >= len(self.facilityImg["normal"]["campfire"])-1:
                            value2["imgId"] = 0
                        else:
                            value2["imgId"] += 0.1
                    # 画上树
                    elif key == "tree":
                        imgToBlit = pygame.transform.scale(self.facilityImg[keyWordTemp][value2["image"]], (round(self.perBlockWidth*0.75),round(self.perBlockWidth*0.75)))
                        xTemp -= self.perBlockWidth*0.125
                        yTemp -= self.perBlockWidth*0.25
                        for theCharacter in characters_data:
                            if characters_data[theCharacter].x == value2["x"] and characters_data[theCharacter].y == value2["y"] or characters_data[theCharacter].x+1 == value2["x"] and characters_data[theCharacter].y+1 == value2["y"]:
                                imgToBlit.set_alpha(100)
                                break
                    elif key == "decoration" or key == "obstacle":
                        imgToBlit = pygame.transform.scale(self.facilityImg[keyWordTemp][value2["image"]], (round(self.perBlockWidth/2),round(self.perBlockWidth/2)))
                    if imgToBlit != None:
                        screen.blit(imgToBlit,(xTemp+round(self.perBlockWidth/4),yTemp-round(self.perBlockWidth/8)))
    #画上箱子
    def drawChest(self,screen,local_x,local_y):
        for key,value in self.facilityData["chest"].items():
            xTemp,yTemp = calPosInMap(self.row,self.perBlockWidth,value["x"],value["y"],local_x,local_y)
            if self.darkMode == True and (value["x"],value["y"]) not in self.lightArea:
                screen.blit(pygame.transform.scale(self.facilityImg["dark"]["chest"], (round(self.perBlockWidth/2),round(self.perBlockWidth/2))),(xTemp+round(self.perBlockWidth/4),yTemp-round(self.perBlockWidth/8)))
            else:
                screen.blit(pygame.transform.scale(self.facilityImg["normal"]["chest"], (round(self.perBlockWidth/2),round(self.perBlockWidth/2))),(xTemp+round(self.perBlockWidth/4),yTemp-round(self.perBlockWidth/8)))
    #寻路功能
    def findPath(self,startPosition,endPosition,characters_data,sangvisFerris_data,routeLen=None,ignoreCharacter=[]):
        startX = startPosition[0]
        startY = startPosition[1]
        endX = endPosition[0]
        endY = endPosition[1]
        #建立地图
        map2d=Array2D(self.column,self.row)
        #历遍地图，设置障碍方块
        """
        for y in range(theMap.row):
            for x in range(theMap.column):
                if theMap.mapData[y][x].canPassThrough == False:
                    map2d[x][y]=1
        """
        #历遍设施，设置障碍方块
        for key,value in self.facilityData.items():
            if key == "obstacle" or key == "campfire":
                for key2,value2 in value.items():
                    map2d[value2["x"]][value2["y"]]=1
        # 历遍所有角色，将角色的坐标点设置为障碍方块
        for key,value in dicMerge(characters_data,sangvisFerris_data).items():
            if key not in ignoreCharacter:
                map2d[value.x][value.y] = 1
        aStar=AStar(map2d,Point(startX,startY),Point(endX,endY))
        #开始寻路
        pathList=aStar.start()
        #遍历路径点,讲指定数量的点放到路径列表中
        the_route = []
        if pathList != None:
            if routeLen != None and len(pathList) < routeLen or routeLen == None:
                routeLen = len(pathList)
            for i in range(routeLen):
                if Point(startX+1,startY) in pathList and (startX+1,startY) not in the_route:
                    startX+=1
                elif Point(startX-1,startY) in pathList and (startX-1,startY) not in the_route:
                    startX-=1
                elif Point(startX,startY+1) in pathList and (startX,startY+1) not in the_route:
                    startY+=1
                elif Point(startX,startY-1) in pathList and (startX,startY-1) not in the_route:
                    startY-=1
                else:
                    #快速跳出
                    break
                the_route.append((startX,startY))
        return the_route
    #重新绘制地图
    def process_map(self,window_x,window_y):
        if self.surface_width < window_x:
            self.surface_width = window_x
        if self.surface_height < window_y:
            self.surface_height = window_y
        self.mapSurface = pygame.surface.Surface((self.surface_width,self.surface_height)).convert()
        if self.bgImg != None:
            self.mapSurface.blit(pygame.transform.scale(self.bgImg,(self.surface_width,self.surface_height)),(0,0))
        for y in range(len(self.mapData)):
            for x in range(len(self.mapData[y])):
                xTemp,yTemp = calPosInMap(self.row,self.perBlockWidth,x,y)
                #画上场景图片
                if self.darkMode == True and (x,y) not in self.lightArea:
                    self.mapSurface.blit(self.env_img_list["dark"][self.mapData[y][x].name],(xTemp,yTemp))
                else:
                    self.mapSurface.blit(self.env_img_list["normal"][self.mapData[y][x].name],(xTemp,yTemp))
    #计算在地图中的方块
    def calBlockInMap(self,block,mouse_x,mouse_y,local_x=0,local_y=0):
        guess_x = int(((mouse_x-local_x-self.row*self.perBlockWidth*0.43)/0.43+(mouse_y-local_y-self.perBlockWidth*0.4)/0.22)/2/self.perBlockWidth)
        guess_y = int((mouse_y-local_y-self.perBlockWidth*0.4)/self.perBlockWidth/0.22) - guess_x
        block_get_click = None
        lenUnitH = block.get_height()/4
        lenUnitW = block.get_width()/4
        for y in range(guess_y-1,guess_y+5):
            for x in range(guess_x-1,guess_x+5):
                xTemp,yTemp = calPosInMap(self.row,self.perBlockWidth,x,y,local_x,local_y)
                xTemp+=self.perBlockWidth*0.05
                if xTemp+lenUnitW<mouse_x<xTemp+lenUnitW*3 and yTemp<mouse_y<yTemp+lenUnitH*4:
                    block_get_click = {"x":x,"y":y}
                    break
        return block_get_click
    #计算方块被画出的位置
    def getBlockExactLocation(self,x,y,local_x,local_y):
        xStart,yStart = calPosInMap(self.row,self.perBlockWidth,x,y,local_x,local_y)
        return {
        "xStart": xStart,
        "xEnd": xStart + self.env_img_list["normal"][self.mapData[y][x].name].get_width(),
        "yStart": yStart,
        "yEnd": yStart + self.env_img_list["normal"][self.mapData[y][x].name].get_width()*0.5
        }
    #计算光亮区域
    def calculate_darkness(self,characters_data,window_x,window_y):
        self.lightArea = []
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
                        if (x,y) not in self.lightArea:
                            self.lightArea.append((x,y))
                else:
                    for x in range(int(characters_data[each_chara].x-the_character_effective_range+(y-characters_data[each_chara].y)+1),int(characters_data[each_chara].x+the_character_effective_range-(y-characters_data[each_chara].y))):
                        if (x,y) not in self.lightArea:
                            self.lightArea.append((x,y))
        if self.facilityData["campfire"] != None:
            for the_campfire in self.facilityData["campfire"]:
                for y in range(int(self.facilityData["campfire"][the_campfire]["y"]-self.facilityData["campfire"][the_campfire]["range"]),int(self.facilityData["campfire"][the_campfire]["y"]+self.facilityData["campfire"][the_campfire]["range"])):
                    if y < self.facilityData["campfire"][the_campfire]["y"]:
                        for x in range(int(self.facilityData["campfire"][the_campfire]["x"]-self.facilityData["campfire"][the_campfire]["range"]-(y-self.facilityData["campfire"][the_campfire]["y"])+1),int(self.facilityData["campfire"][the_campfire]["x"]+self.facilityData["campfire"][the_campfire]["range"]+(y-self.facilityData["campfire"][the_campfire]["y"]))):
                            if (x,y) not in self.lightArea:
                                self.lightArea.append((x,y))
                    else:
                        for x in range(int(self.facilityData["campfire"][the_campfire]["x"]-self.facilityData["campfire"][the_campfire]["range"]+(y-self.facilityData["campfire"][the_campfire]["y"])+1),int(self.facilityData["campfire"][the_campfire]["x"]+self.facilityData["campfire"][the_campfire]["range"]-(y-self.facilityData["campfire"][the_campfire]["y"]))):
                            if (x,y) not in self.lightArea:
                                self.lightArea.append((x,y))
        self.process_map(window_x,window_y)

#初始化地图数据
def initialBlockData(mapData,facilityData,blocks_setting):
    for y in range(len(mapData)):
        for x in range(len(mapData[y])):
            mapData[y][x] = Block(mapData[y][x],blocks_setting[mapData[y][x]]["canPassThrough"])
    return mapData

#计算在地图中的位置
def calPosInMap(row,perBlockWidth,x,y,local_x=0,local_y=0):
    return (x-y)*perBlockWidth*0.43+local_x+row*perBlockWidth*0.43,(y+x)*perBlockWidth*0.22+local_y+perBlockWidth*0.4

#初始化设施数据
def initialFacility(facilityData):
    for key in facilityData["campfire"]:
        facilityData["campfire"][key]["imgId"] = random.randint(0,9)
    return facilityData

#方块类
class Block:
    def  __init__(self,name,canPassThrough):
        self.name = name
        self.canPassThrough = canPassThrough

class BlockArea:
    def  __init__(self,areaData,x,y):
        self.areaData = areaData
        self.lightArea = []
        self.x = x
        self.y = y
        self.row = len(areaData)
        self.column = len(areaData[0])
        self.mapSurface = None
    def updateLightArea(self,lightArea,envImgList,perBlockWidth,darkMode):
        newLightArea = []
        for position in lightArea:
            if self.x<=position[0]<=self.column+self.x and self.y<=position[1]<=self.row+self.y:
                newLightArea.append(position)
        if self.lightArea != newLightArea:
            self.lightArea = newLightArea
            self.redrawArea(envImgList,perBlockWidth,darkMode)
    def redrawArea(self,envImgList,perBlockWidth,darkMode):
        surface_width = int(perBlockWidth*0.9*(self.row+self.column+1)/2)
        surface_height = int(perBlockWidth*0.45*((self.row+self.column+1)/2)+perBlockWidth)
        self.mapSurface = pygame.surface.Surface((surface_width,surface_height)).convert_alpha()
        for y in range(self.row):
            for x in range(self.column):
                xTemp,yTemp = calPosInMap(self.row,perBlockWidth,x,y)
                #画上场景图片
                if darkMode == True and (x,y) not in self.lightArea:
                    self.mapSurface.blit(envImgList["dark"][self.areaData[y][x].name],(xTemp,yTemp))
                else:
                    self.mapSurface.blit(envImgList["normal"][self.areaData[y][x].name],(xTemp,yTemp))

def initalBlocks(mapData):
    allBlockArea = []
    rowPerBlockArea = 6
    columnPerBlockArea = 6
    rowExtra = len(mapData)%rowPerBlockArea
    columnExtra = len(mapData[0])%columnPerBlockArea
    for y in range(int(len(mapData)/rowPerBlockArea)):
        for x in range(int(len(mapData[0])/columnPerBlockArea)):
            tempArea = mapData[y*rowPerBlockArea:(y+1)*rowPerBlockArea-1]
            for i in range(len(tempArea)):
                tempArea[i] = tempArea[i][x*columnPerBlockArea:(x+1)*columnPerBlockArea-1]
            allBlockArea.append(BlockArea(tempArea,x*columnPerBlockArea,y*rowPerBlockArea))
    return allBlockArea

#环境系统
class WeatherSystem:
    def  __init__(self,weather,window_x,window_y):
        self.name = 0
        self.img_list = loadAllImgInFile("Assets/image/environment/"+weather+"/*.png")
        self.ImgObject = []
        for i in range(50):
            imgId = random.randint(0,len(self.img_list)-1)
            img_size = random.randint(5,10)
            img_speed = random.randint(1,3)
            img_x = random.randint(1,window_x*1.5)
            img_y = random.randint(1,window_y)
            self.ImgObject.append(Snow(imgId,img_size,img_speed,img_x,img_y))
    def display(self,screen,perBlockWidth,perBlockHeight,local_x=0,local_y=0):
        speed_unit = perBlockWidth/5
        for i in range(len(self.ImgObject)):
            if 0<=self.ImgObject[i].x<=screen.get_width() and 0<=self.ImgObject[i].y+local_y<=screen.get_height():
                imgTemp = pygame.transform.scale(self.img_list[self.ImgObject[i].imgId], (round(perBlockWidth/self.ImgObject[i].size), round(perBlockWidth/self.ImgObject[i].size)))
                screen.blit(imgTemp,(self.ImgObject[i].x,self.ImgObject[i].y+local_y))
            self.ImgObject[i].x -= self.ImgObject[i].speed*speed_unit
            self.ImgObject[i].y += self.ImgObject[i].speed*speed_unit
            if self.ImgObject[i].x <= 0 or self.ImgObject[i].y+local_y >= screen.get_height():
                self.ImgObject[i].y = random.randint(-50,0)
                self.ImgObject[i].x = random.randint(0,screen.get_width()*2)

#雪花片
class Snow:
    def  __init__(self,imgId,size,speed,x,y):
        self.imgId = imgId
        self.size = size
        self.speed = speed
        self.x = x
        self.y = y

#加载场地设施的图片
def loadFacilityImg(facilityData,darkMode=False):
    Facility_images = {"normal":{}}
    #加载篝火的图片
    if "campfire" in facilityData and facilityData["campfire"] != None:
        Facility_images["normal"]["campfire"] = []
        for i in range(1,11):
            try:
                Facility_images["normal"]["campfire"].append(loadImg("Assets/image/environment/campfire/"+str(i)+".png"))
            except BaseException:
                Facility_images["normal"]["campfire"].append(loadImg("../Assets/image/environment/campfire/"+str(i)+".png"))
    #加载箱子的图片
    if "chest" in facilityData and facilityData["chest"] != None:
        Facility_images["normal"]["chest"] = loadImg("Assets/image/environment/decoration/chest.png")
    #加载树的图片
    if "tree" in facilityData and facilityData["tree"] != None:
        for item in facilityData["tree"]:
            imageName = facilityData["tree"][item]["image"]
            if imageName not in Facility_images["normal"]:
                Facility_images["normal"][imageName] = loadImg("Assets/image/environment/decoration/"+imageName+".png")
    #加载其他设施的图片
    if "decoration" in facilityData and facilityData["decoration"] != None:
        for key,value in facilityData["decoration"].items():
            if value["image"] not in Facility_images["normal"]:
                Facility_images["normal"][value["image"]] = loadImg("Assets/image/environment/decoration/"+value["image"]+".png")
    if darkMode == True:
        Facility_images["dark"] = {}
        for key,value in Facility_images["normal"].items():
            if key != "campfire":
                Facility_images["dark"][key] = addDarkness(value,150)
    return Facility_images

#读取需要的地图图片
def load_env_images(theMap,theWidth=None,theHeight=None,darkMode=False):
    all_images_needed = []
    for i in range(len(theMap)):
        for a in range(len(theMap[i])):
            if theMap[i][a] not in all_images_needed:
                all_images_needed.append(theMap[i][a])
    #加载背景图片
    env_img_list={"normal":{}}
    for i in range(len(all_images_needed)):
        try:
            env_img_list["normal"][all_images_needed[i]] = loadImg("Assets/image/environment/block/"+all_images_needed[i]+".png",theWidth,theHeight)
        except BaseException:
            env_img_list["normal"][all_images_needed[i]] = loadImg("../Assets/image/environment/block/"+all_images_needed[i]+".png",theWidth,theHeight)
            
    if darkMode==True:
        env_img_list["dark"] = {}
        for img,value in env_img_list["normal"].items():
            env_img_list["dark"][img] = addDarkness(value,150)
    return env_img_list

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
                print(self.data[x][y])
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
