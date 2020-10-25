# cython: language_level=3
import numpy
import pygame
import os
from Zero3.basic import addDarkness, dicMerge, loadImg, loadYaml, randomInt, resizeImg

_MAP_ENV_IMAGE = None

#地图场景模块
class EnvImagesManagement:
    def __init__(self,theMap,ornamentationData,bgImgName,theWidth,darkMode,darkness=150):
        self.__ENV_IMAGE_DICT_ORIGINAL = {}
        self.__ENV_IMAGE_DICT_ORIGINAL_DARK = None
        self.__ENV_IMAGE_DICT = {}
        self.__ENV_IMAGE_DICT_DARK = None
        self.__ORNAMENTATION_IMAGE_DICT = {}
        self.__ORNAMENTATION_IMAGE_DICT_DARK = None
        #self.__BACKGROUND_IMAGE = pygame.image.load(os.path.join("Assets/image/dialog_background/",bgImgName)).convert() if bgImgName != None else None
        self.__BACKGROUND_IMAGE = pygame.image.load(os.path.join("Assets/image/dialog_background/",bgImgName)).convert_alpha() if bgImgName != None else None
        self.__MAP_SURFACE = None
        all_images_needed = []
        for i in range(len(theMap)):
            for a in range(len(theMap[i])):
                if theMap[i][a].name not in all_images_needed:
                    all_images_needed.append(theMap[i][a].name)
        #加载背景图片
        for i in range(len(all_images_needed)):
            try:
                self.__ENV_IMAGE_DICT_ORIGINAL[all_images_needed[i]] = loadImg("Assets/image/environment/block/"+all_images_needed[i]+".png")
                self.__ENV_IMAGE_DICT[all_images_needed[i]] = loadImg("Assets/image/environment/block/"+all_images_needed[i]+".png",theWidth,None)
            except BaseException:
                raise Exception('ZeroEngine-Error: An map-block called '+all_images_needed[i]+' cannot find its image in the folder.')
        #加载场地设施的图片
        for ornamentation in ornamentationData:
            #--篝火--
            if ornamentation.type == "campfire":
                if "campfire" not in self.__ORNAMENTATION_IMAGE_DICT:
                    self.__ORNAMENTATION_IMAGE_DICT["campfire"] = []
                    for i in range(1,12):
                        self.__ORNAMENTATION_IMAGE_DICT["campfire"].append(loadImg("Assets/image/environment/campfire/{}.png".format(i)))
            elif ornamentation.type not in self.__ORNAMENTATION_IMAGE_DICT:
                self.__ORNAMENTATION_IMAGE_DICT[ornamentation.type] = {}
                self.__ORNAMENTATION_IMAGE_DICT[ornamentation.type][ornamentation.image] = loadImg("Assets/image/environment/decoration/"+ornamentation.image+".png")
            elif ornamentation.image not in self.__ORNAMENTATION_IMAGE_DICT[ornamentation.type]:
                self.__ORNAMENTATION_IMAGE_DICT[ornamentation.type][ornamentation.image] = loadImg("Assets/image/environment/decoration/"+ornamentation.image+".png")
        #如果是夜战模式
        if darkMode==True:
            self.__ENV_IMAGE_DICT_ORIGINAL_DARK = {}
            for img,value in self.__ENV_IMAGE_DICT_ORIGINAL.items():
                self.__ENV_IMAGE_DICT_ORIGINAL_DARK[img] = addDarkness(value,darkness)
            self.__ENV_IMAGE_DICT_DARK = {}
            for img,value in self.__ENV_IMAGE_DICT.items():
                self.__ENV_IMAGE_DICT_DARK[img] = addDarkness(value,darkness)
            self.__ORNAMENTATION_IMAGE_DICT_DARK = {}
            for key,value in self.__ORNAMENTATION_IMAGE_DICT.items():
                if key != "campfire":
                    self.__ORNAMENTATION_IMAGE_DICT_DARK[key] = {}
                    for key2,value2 in value.items():
                        self.__ORNAMENTATION_IMAGE_DICT_DARK[key][key2] = addDarkness(value2,darkness)
                elif "campfire" not in self.__ORNAMENTATION_IMAGE_DICT_DARK:
                    self.__ORNAMENTATION_IMAGE_DICT_DARK["campfire"] = {}
                    self.__ORNAMENTATION_IMAGE_DICT_DARK["campfire"]["campfire"] = (addDarkness(self.__ORNAMENTATION_IMAGE_DICT["campfire"][-1],darkness))
    def resize(self,newWidth):
        for key in self.__ENV_IMAGE_DICT:
            self.__ENV_IMAGE_DICT[key] = resizeImg(self.__ENV_IMAGE_DICT_ORIGINAL[key],(newWidth, None))
        if self.__ENV_IMAGE_DICT_ORIGINAL_DARK != None:
            for key in self.__ENV_IMAGE_DICT_DARK:
                self.__ENV_IMAGE_DICT_DARK[key] = resizeImg(self.__ENV_IMAGE_DICT_ORIGINAL_DARK[key],(newWidth,None))
    def get_env_image(self,key,darkMode,darkness=150):
        try:
            if darkMode == True:
                return self.__ENV_IMAGE_DICT_DARK[key]
            else:
                return self.__ENV_IMAGE_DICT[key]
        except BaseException:
            print('ZeroEngine-Warning: Cannot find block image "{}", we will try to load it for you right now, but please by aware.'.format(key))
            imgTmp = loadImg("Assets/image/environment/block/"+key+".png")
            self.__ENV_IMAGE_DICT_ORIGINAL[key] = imgTmp
            self.__ENV_IMAGE_DICT[key] = resizeImg(imgTmp,(self.perBlockWidth,None))
            if self.__ENV_IMAGE_DICT_ORIGINAL_DARK != None:
                imgTmp = addDarkness(imgTmp,150)
                self.__ENV_IMAGE_DICT_ORIGINAL_DARK[key] = imgTmp
                self.__ENV_IMAGE_DICT_DARK[key] = resizeImg(imgTmp,(self.perBlockWidth,None))
    def get_ornamentation_image(self,ornamentationType,key,darkMode,darkness=150):
        try:
            if darkMode == True:
                return self.__ORNAMENTATION_IMAGE_DICT_DARK[ornamentationType][key]
            else:
                return self.__ORNAMENTATION_IMAGE_DICT[ornamentationType][key]
        #如果图片没找到
        except BaseException:
            print('ZeroEngine-Warning: Cannot find ornamentation image "{0}" in type "{1}", we will try to load it for you right now, but please by aware.'.format(key,ornamentationType))
            imgTmp = loadImg("Assets/image/environment/decoration/"+key+".png")
            self.__ORNAMENTATION_IMAGE_DICT[ornamentationType][key] = imgTmp
            if self.__ORNAMENTATION_IMAGE_DICT_DARK != None:
                self.__ORNAMENTATION_IMAGE_DICT_DARK[ornamentationType][key] = addDarkness(imgTmp,darkness)
    def get_ornamentation_num(self,ornamentationType):
        return len(self.__ORNAMENTATION_IMAGE_DICT[ornamentationType])
    def get_new_background_image(self,width,height):
        if self.__BACKGROUND_IMAGE != None:
            self.__MAP_SURFACE = pygame.transform.scale(self.__BACKGROUND_IMAGE,(width,height))
        else:
            self.__MAP_SURFACE = pygame.surface.Surface((width,height)).convert()
        return self.__MAP_SURFACE
    def get_background_image(self):
        return self.__MAP_SURFACE

#地图模块
class MapObject:
    def  __init__(self,mapDataDic,perBlockWidth,local_x=0,local_y=0):
        #加载地图设置
        blocks_setting = loadYaml("Data/blocks.yaml")["blocks"]
        self.darkMode = mapDataDic["darkMode"]
        self.perBlockWidth = perBlockWidth
        mapData = mapDataDic["map"]
        self.row = len(mapData)
        self.column = len(mapData[0])
        #初始化地图数据
        self.mapData = mapData
        self.backgroundImageName = mapDataDic["backgroundImage"]
        for y in range(len(mapData)):
            for x in range(len(mapData[y])):
                self.mapData[y][x] = BlockObject(mapData[y][x],blocks_setting[mapData[y][x]]["canPassThrough"])
        self.ornamentationData = []
        for ornamentationType,itemsThatType in mapDataDic["ornamentation"].items():
            for itemKey,itemData in itemsThatType.items():
                if ornamentationType == "campfire":
                    self.ornamentationData.append(OrnamentationObject(itemData["x"],itemData["y"],ornamentationType,ornamentationType))
                    self.ornamentationData[-1].imgId = randomInt(0,9)
                    self.ornamentationData[-1].range = itemData["range"]
                    self.ornamentationData[-1].alpha = 255
                    self.ornamentationData[-1].triggered = True
                elif ornamentationType == "chest":
                    self.ornamentationData.append(OrnamentationObject(itemData["x"],itemData["y"],ornamentationType,ornamentationType))
                    self.ornamentationData[-1].items = itemData["items"]
                else:
                    self.ornamentationData.append(OrnamentationObject(itemData["x"],itemData["y"],ornamentationType,itemData["image"]))
        self.ornamentationData.sort()
        self.lightArea = []
        self.surface_width = int(perBlockWidth*0.9*((len(mapData)+len(mapData[0])+1)/2))
        self.surface_height = int(perBlockWidth*0.45*((len(mapData)+len(mapData[0])+1)/2)+perBlockWidth)
        self.__local_x = local_x
        self.__local_y = local_y
        self.ifProcessMap = True
        self.load_env_img()
    def load_env_img(self):
        global _MAP_ENV_IMAGE
        _MAP_ENV_IMAGE = EnvImagesManagement(self.mapData,self.ornamentationData,self.backgroundImageName,self.perBlockWidth,self.darkMode)
    #控制地图放大缩小
    def changePerBlockSize(self,newPerBlockWidth,window_x,window_y):
        self.perBlockWidth = newPerBlockWidth
        _MAP_ENV_IMAGE.resize(self.perBlockWidth)
        self.surface_width = int(newPerBlockWidth*0.9*((len(self.mapData)+len(self.mapData[0])+1)/2))
        self.surface_height = int(newPerBlockWidth*0.45*((len(self.mapData)+len(self.mapData[0])+1)/2)+newPerBlockWidth)
        if self.surface_width < window_x:
            self.surface_width = window_x
        if self.surface_height < window_y:
            self.surface_height = window_y
        self.process_map(window_x,window_y)
    #获取local坐标
    def getPos(self):
        return self.__local_x,self.__local_y
    def getPos_x(self):
        return self.__local_x
    def getPos_y(self):
        return self.__local_y
    #设置local坐标
    def setPos(self,x,y):
        self.setPos_x(x)
        self.setPos_y(y)
    def setPos_x(self,value):
        tempValue = round(value)
        if self.__local_x != tempValue:
            self.__local_x = tempValue
            self.ifProcessMap = True
    def setPos_y(self,value):
        tempValue = round(value)
        if self.__local_y != tempValue:
            self.__local_y = tempValue
            self.ifProcessMap = True
    #增加local坐标
    def addPos_x(self,value):
        tempValue = int(value)
        if tempValue !=0:
            self.__local_x += tempValue
            self.ifProcessMap = True
    def addPos_y(self,value):
        tempValue = int(value)
        if tempValue !=0:
            self.__local_y += tempValue
            self.ifProcessMap = True
    #把地图画到屏幕上
    def display_map(self,screen,screen_to_move_x=0,screen_to_move_y=0):
        #检测屏幕是不是移到了不移到的地方
        if self.__local_x < screen.get_width()-self.surface_width:
            self.__local_x = screen.get_width()-self.surface_width
            screen_to_move_x = 0
        elif self.__local_x > 0:
            self.__local_x = 0
            screen_to_move_x = 0
        if self.__local_y < screen.get_height()-self.surface_height:
            self.__local_y = screen.get_height()-self.surface_height
            screen_to_move_y = 0
        elif self.__local_y > 0:
            self.__local_y = 0
            screen_to_move_y = 0
        if self.ifProcessMap == True:
            self.ifProcessMap = False
            self.process_map(screen.get_width(),screen.get_height())
        screen.blit(_MAP_ENV_IMAGE.get_background_image(),(0,0))
        return (screen_to_move_x,screen_to_move_y)
    #画上设施
    def display_ornamentation(self,screen,characters_data,sangvisFerris_data):
        charatcersPos = None
        for item in self.ornamentationData:
            imgToBlit = None
            xTemp,yTemp = self.calPosInMap(item.x,item.y)
            if -self.perBlockWidth<=xTemp<screen.get_width() and -self.perBlockWidth<=yTemp<screen.get_height():
                if self.darkMode == True and item.get_pos() not in self.lightArea:
                    keyWordTemp = True
                else:
                    keyWordTemp = False
                #画上篝火
                if item.type == "campfire":
                    #查看篝火的状态是否正在变化，并调整对应的alpha值
                    if item.triggered == True and item.alpha < 255:
                        item.alpha += 15
                    elif item.triggered == False and item.alpha > 0:
                        item.alpha -= 15
                    #根据alpha值生成对应的图片
                    if item.alpha >= 255:
                        imgToBlit = pygame.transform.scale(_MAP_ENV_IMAGE.get_ornamentation_image("campfire",int(item.imgId),False), (round(self.perBlockWidth/2),round(self.perBlockWidth/2)))
                        if item.imgId >= _MAP_ENV_IMAGE.get_ornamentation_num("campfire")-2:
                            item.imgId = 0
                        else:
                            item.imgId += 0.1
                    elif item.alpha <= 0:
                        if keyWordTemp == False:
                            imgToBlit = pygame.transform.scale(_MAP_ENV_IMAGE.get_ornamentation_image("campfire",-1,False), (round(self.perBlockWidth/2),round(self.perBlockWidth/2)))
                        else:
                            imgToBlit = pygame.transform.scale(_MAP_ENV_IMAGE.get_ornamentation_image("campfire","campfire",True), (round(self.perBlockWidth/2),round(self.perBlockWidth/2)))
                    else:
                        imgToBlit = pygame.transform.scale(_MAP_ENV_IMAGE.get_ornamentation_image("campfire",-1,False), (round(self.perBlockWidth/2),round(self.perBlockWidth/2)))
                        screen.blit(imgToBlit,(xTemp+round(self.perBlockWidth/4),yTemp-round(self.perBlockWidth/8)))
                        imgToBlit = pygame.transform.scale(_MAP_ENV_IMAGE.get_ornamentation_image("campfire",int(item.imgId),False), (round(self.perBlockWidth/2),round(self.perBlockWidth/2)))
                        imgToBlit.set_alpha(item.alpha)
                        if item.imgId >= _MAP_ENV_IMAGE.get_ornamentation_num("campfire")-2:
                            item.imgId = 0
                        else:
                            item.imgId += 0.1
                # 画上树
                elif item.type == "tree":
                    imgToBlit = pygame.transform.scale(_MAP_ENV_IMAGE.get_ornamentation_image("tree",item.image,keyWordTemp),(round(self.perBlockWidth*0.75),round(self.perBlockWidth*0.75)))
                    xTemp -= self.perBlockWidth*0.125
                    yTemp -= self.perBlockWidth*0.25
                    #如果的确有树需要被画出
                    if charatcersPos == None:
                        charatcersPos = []
                        for name,dataDic in dicMerge(characters_data,sangvisFerris_data).items():
                            charatcersPos.append((int(dataDic.x),int(dataDic.y)))
                            charatcersPos.append((int(dataDic.x)+1,int(dataDic.y)+1))
                    if item.get_pos() in charatcersPos:
                        if self.darkMode == False or item.get_pos() in self.lightArea:
                            imgToBlit.set_alpha(100)
                elif item.type == "decoration" or item.type == "obstacle" or item.type == "chest":
                    imgToBlit = pygame.transform.scale(_MAP_ENV_IMAGE.get_ornamentation_image(item.type,item.image,keyWordTemp),(round(self.perBlockWidth/2),round(self.perBlockWidth/2)))
                if imgToBlit != None:
                    screen.blit(imgToBlit,(xTemp+round(self.perBlockWidth/4),yTemp-round(self.perBlockWidth/8)))
    #寻路功能
    def findPath(self,startPosition,endPosition,characters_data,sangvisFerris_data,routeLen=None,ignoreCharacter=[]):
        startX = startPosition[0]
        startY = startPosition[1]
        endX = endPosition[0]
        endY = endPosition[1]
        #建立地图
        map2d=numpy.zeros((self.column,self.row), dtype=numpy.int8)
        #历遍地图，设置障碍方块
        """
        for y in range(theMap.row):
            for x in range(theMap.column):
                if theMap.mapData[y][x].canPassThrough == False:
                    map2d[x][y]=1
        """
        #历遍设施，设置障碍方块
        for item in self.ornamentationData:
            if item.type == "obstacle" or item.type == "campfire":
                map2d[item.x][item.y]=1
        # 历遍所有角色，将角色的坐标点设置为障碍方块
        for key,value in characters_data.items():
            if key not in ignoreCharacter:
                map2d[value.x][value.y] = 1
        for key,value in sangvisFerris_data.items():
            if key not in ignoreCharacter and value.current_hp>0:
                map2d[value.x][value.y] = 1
        if map2d[endX][endY] != 0:
            return []
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
        mapSurface = _MAP_ENV_IMAGE.get_new_background_image(window_x,window_y)
        #画出地图
        for y in range(len(self.mapData)):
            anyBlockPrint = False
            for x in range(len(self.mapData[y])):
                xTemp,yTemp = self.calPosInMap(x,y)
                if -self.perBlockWidth<=xTemp<window_x and -self.perBlockWidth<=yTemp<window_y:
                    anyBlockPrint = True
                    if self.darkMode == True and (x,y) not in self.lightArea:
                        mapSurface.blit(_MAP_ENV_IMAGE.get_env_image(self.mapData[y][x].name,True),(xTemp,yTemp))
                    else:
                        mapSurface.blit(_MAP_ENV_IMAGE.get_env_image(self.mapData[y][x].name,False),(xTemp,yTemp))
                elif xTemp>=window_x or yTemp>=window_y:
                    break
            if anyBlockPrint == False and yTemp>=window_y:
                break
    #计算在地图中的方块
    def calBlockInMap(self,block,mouse_x,mouse_y):
        guess_x = int(((mouse_x-self.__local_x-self.row*self.perBlockWidth*0.43)/0.43+(mouse_y-self.__local_y-self.perBlockWidth*0.4)/0.22)/2/self.perBlockWidth)
        guess_y = int((mouse_y-self.__local_y-self.perBlockWidth*0.4)/self.perBlockWidth/0.22) - guess_x
        block_get_click = None
        lenUnitH = block.get_height()/4
        lenUnitW = block.get_width()/4
        for y in range(guess_y-1,guess_y+4):
            for x in range(guess_x-1,guess_x+4):
                xTemp,yTemp = self.calPosInMap(x,y)
                xTemp+=self.perBlockWidth*0.05
                if xTemp+lenUnitW<mouse_x<xTemp+lenUnitW*3 and yTemp<mouse_y<yTemp+lenUnitH*4:
                    block_get_click = {"x":x,"y":y}
                    break
        return block_get_click
    #计算方块被画出的位置
    def getBlockExactLocation(self,x,y):
        xStart,yStart = self.calPosInMap(x,y)
        return {
        "xStart": xStart,
        "xEnd": xStart + self.perBlockWidth,
        "yStart": yStart,
        "yEnd": yStart + self.perBlockWidth*0.5
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
        for item in self.ornamentationData:
            if item.type == "campfire" and item.triggered == True:
                for y in range(int(item.y-item.range),int(item.y+item.range)):
                    if y < item.y:
                        for x in range(int(item.x-item.range-(y-item.y)+1),int(item.x+item.range+(y-item.y))):
                            if (x,y) not in self.lightArea:
                                self.lightArea.append((x,y))
                    else:
                        for x in range(int(item.x-item.range+(y-item.y)+1),int(item.x+item.range-(y-item.y))):
                            if (x,y) not in self.lightArea:
                                self.lightArea.append((x,y))
        self.ifProcessMap = True
    #计算在地图中的位置
    def calPosInMap(self,x,y):
        return round((x-y)*self.perBlockWidth*0.43+self.__local_x+self.row*self.perBlockWidth*0.43,1),round((y+x)*self.perBlockWidth*0.22+self.__local_y+self.perBlockWidth*0.4,1)

#方块类
class BlockObject:
    def  __init__(self,name,canPassThrough):
        self.name = name
        self.canPassThrough = canPassThrough

#管理场景装饰物的类
class OrnamentationObject:
    def  __init__(self,x,y,type,image):
        self.x = x
        self.y = y
        self.type = type
        self.image = image
        self.alpha = None
    def __lt__(self,other):
        return self.y+self.x < other.y+other.x
    def get_pos(self):
        return self.x,self.y

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
        mapRow,mapCol = self.map2d.shape
        if minF.point.x + offsetX < 0 or minF.point.x + offsetX > mapCol - 1 or minF.point.y + offsetY < 0 or minF.point.y + offsetY > mapRow - 1:
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
        mapRow,mapCol = self.map2d.shape
        if self.endPoint.y < 0 or self.endPoint.y >= mapRow or self.endPoint.x < 0 or self.endPoint.x >= mapCol or self.map2d[self.endPoint.x][self.endPoint.y] != self.passTag:
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
