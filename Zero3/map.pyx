# cython: language_level=3
import numpy
import pygame
import os
from Zero3.basic import addDarkness, loadImg, randomInt, resizeImg, loadConfig

_MAP_ENV_IMAGE = None
#方块数据
_BLOCKS_DATABASE = loadConfig("Data/blocks.yaml","blocks")

#地图场景模块
class EnvImagesManagement:
    def __init__(self,theMap,ornamentationData,bgImgName,theWidth,darkMode,darkness=150):
        self.__ENV_IMAGE_DICT_ORIGINAL = {}
        self.__ENV_IMAGE_DICT_ORIGINAL_DARK = None
        self.__ENV_IMAGE_DICT = {}
        self.__ENV_IMAGE_DICT_DARK = None
        self.__ORNAMENTATION_IMAGE_DICT = {}
        self.__ORNAMENTATION_IMAGE_DICT_DARK = None
        self.__BACKGROUND_IMAGE = pygame.image.load(os.path.join("Assets/image/dialog_background/",bgImgName)).convert() if bgImgName != None else None
        self.__BACKGROUND_SURFACE = None
        self.__MAP_BUFFER_SURFACE = None
        cdef list all_images_needed = []
        for y in range(len(theMap)):
            for x in range(len(theMap[y])):
                if theMap[y][x].name not in all_images_needed:
                    all_images_needed.append(theMap[y][x].name)
        #加载背景图片
        for fileName in all_images_needed:
            try:
                self.__ENV_IMAGE_DICT_ORIGINAL[fileName] = loadImg("Assets/image/environment/block/"+fileName+".png")
                self.__ENV_IMAGE_DICT[fileName] = resizeImg(self.__ENV_IMAGE_DICT_ORIGINAL[fileName],(theWidth,None))
            except BaseException:
                raise Exception('ZeroEngine-Error: An map-block called '+fileName+' cannot find its image in the folder.')
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
        if darkMode:
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
    def get_env_image(self,key,darkMode):
        try:
            if darkMode:
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
            if darkMode:
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
    #获取当前装饰物种类的数量
    def get_ornamentation_num(self,ornamentationType):
        return len(self.__ORNAMENTATION_IMAGE_DICT[ornamentationType])
    def get_new_background_image(self,screen_size,map_size):
        if self.__BACKGROUND_IMAGE != None:
            self.__BACKGROUND_SURFACE = resizeImg(self.__BACKGROUND_IMAGE,screen_size)
        else:
            self.__BACKGROUND_SURFACE = pygame.Surface(screen_size).convert()
        self.__MAP_BUFFER_SURFACE = pygame.Surface(map_size,flags=pygame.SRCALPHA).convert_alpha()
        return self.__MAP_BUFFER_SURFACE
    def display_background_surface(self,screen,pos):
        screen.blit(self.__BACKGROUND_SURFACE,(0,0))
        screen.blit(self.__MAP_BUFFER_SURFACE,pos)

#地图模块
class MapObject:
    def  __init__(self,mapDataDic,int perBlockWidth,int perBlockHeight):
        #加载地图设置
        self.darkMode = mapDataDic["darkMode"]
        self.perBlockWidth = perBlockWidth
        self.perBlockHeight = perBlockHeight
        #初始化地图数据
        self.__MapData = mapDataDic["map"]
        self.backgroundImageName = mapDataDic["backgroundImage"]
        for y in range(len(self.__MapData)):
            for x in range(len(self.__MapData[y])):
                item = self.__MapData[y][x]
                self.__MapData[y][x] = BlockObject(item,_BLOCKS_DATABASE[item]["canPassThrough"])
        self.__MapData = numpy.asarray(self.__MapData)
        self.row,self.column = self.__MapData.shape
        #使用numpy的shape决定self.row和self.column
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
        self.ornamentationData = numpy.asarray(self.ornamentationData)
        self.__lightArea = []
        self.surface_width = int(perBlockWidth*0.9*((self.row+self.column+1)/2))
        self.surface_height = int(perBlockWidth*0.45*((self.row+self.column+1)/2)+perBlockWidth)
        self.__local_x = mapDataDic["local_x"]
        self.__local_y = mapDataDic["local_y"]
        self.__needUpdateMapSurface = True
        self.load_env_img()
    def load_env_img(self):
        global _MAP_ENV_IMAGE
        _MAP_ENV_IMAGE = EnvImagesManagement(self.__MapData,self.ornamentationData,self.backgroundImageName,self.perBlockWidth,self.darkMode)
    #控制地图放大缩小
    def changePerBlockSize(self,newPerBlockWidth,newPerBlockHeight,window_x,window_y):
        self.addPos_x((self.perBlockWidth-newPerBlockWidth)*self.column/2)
        self.addPos_y((self.perBlockHeight-newPerBlockHeight)*self.row/2)
        self.surface_width = int(newPerBlockWidth*0.9*((self.row+self.column+1)/2))
        self.surface_height = int(newPerBlockWidth*0.45*((self.row+self.column+1)/2)+newPerBlockWidth)
        self.perBlockWidth = round(newPerBlockWidth)
        self.newPerBlockHeight = round(newPerBlockHeight)
        _MAP_ENV_IMAGE.resize(self.perBlockWidth)
        if self.surface_width < window_x:
            self.surface_width = window_x
        if self.surface_height < window_y:
            self.surface_height = window_y
        self.__update_map_surface((window_x,window_y))
    #获取local坐标
    def getPos(self):
        return self.__local_x,self.__local_y
    def getPos_x(self):
        return self.__local_x
    def getPos_y(self):
        return self.__local_y
    #设置local坐标
    def setPos(self,int x, int y):
        self.setPos_x(x)
        self.setPos_y(y)
    def setPos_x(self,int value):
        if self.__local_x != value:
            self.__local_x = value
            if self.darkMode == True:
                self.__needUpdateMapSurface = True
    def setPos_y(self,int value):
        if self.__local_y != value:
            self.__local_y = value
            if self.darkMode == True:
                self.__needUpdateMapSurface = True
    #增加local坐标
    def addPos_x(self,value):
        self.setPos_x(self.__local_x+value)
    def addPos_y(self,value):
        self.setPos_y(self.__local_y+value)
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
        if self.__needUpdateMapSurface:
            self.__needUpdateMapSurface = False
            self.__update_map_surface(screen.get_size())
        if self.darkMode:
            _MAP_ENV_IMAGE.display_background_surface(screen,(0,0))
        else:
            _MAP_ENV_IMAGE.display_background_surface(screen,self.getPos())
        return (screen_to_move_x,screen_to_move_y)
    #重新绘制地图
    def __update_map_surface(self,window_size):
        cdef (int, int) posTupleTemp
        cdef unsigned int y
        cdef unsigned int yRange = self.row
        cdef unsigned int x
        cdef unsigned int xRange = self.column
        cdef int screen_min = -self.perBlockWidth
        cdef unsigned int anyBlockBlitThisLine
        cdef int window_x = window_size[0]
        cdef int window_y = window_size[1]
        if self.darkMode == True:
            mapSurface = _MAP_ENV_IMAGE.get_new_background_image(window_size,window_size)
            #画出地图
            for y in range(yRange):
                anyBlockBlitThisLine = 0
                for x in range(xRange):
                    posTupleTemp = self.calPosInMap(x,y)
                    if screen_min<=posTupleTemp[0]<window_x and screen_min<=posTupleTemp[1]<window_y:
                        anyBlockBlitThisLine = 1
                        if not self.isPosInLightArea(x,y):
                            mapSurface.blit(_MAP_ENV_IMAGE.get_env_image(self.__MapData[y][x].name,True),(posTupleTemp[0],posTupleTemp[1]))
                        else:
                            mapSurface.blit(_MAP_ENV_IMAGE.get_env_image(self.__MapData[y][x].name,False),(posTupleTemp[0],posTupleTemp[1]))
                    elif posTupleTemp[0] >= window_x or posTupleTemp[1] >= window_y:
                        break
                if anyBlockBlitThisLine == 0 and posTupleTemp[1] >= window_y:
                    break
        else:
            mapSurface = _MAP_ENV_IMAGE.get_new_background_image(window_size,(self.surface_width,self.surface_height))
            #画出地图
            for y in range(yRange):
                for x in range(xRange):
                    posTupleTemp = self.calPosInMap(x,y)
                    mapSurface.blit(_MAP_ENV_IMAGE.get_env_image(self.__MapData[y][x].name,False),(posTupleTemp[0]-self.__local_x,posTupleTemp[1]-self.__local_y))
    #把装饰物画到屏幕上
    def display_ornamentation(self,screen,characters_data,sangvisFerris_data):
        cdef (int,int) thePosInMap
        #检测角色所占据的装饰物（即需要透明化，方便玩家看到角色）
        cdef list charactersPos = []
        for name,dataDic in {**characters_data, **sangvisFerris_data}.items():
            charactersPos.append((int(dataDic.x),int(dataDic.y)))
            charactersPos.append((int(dataDic.x)+1,int(dataDic.y)+1))
        #计算offSet
        cdef int offSetX = round(self.perBlockWidth/4)
        cdef int offSetY = round(self.perBlockWidth/8)
        cdef int offSetX_tree = round(self.perBlockWidth*0.125)
        cdef int offSetY_tree = round(self.perBlockWidth*0.25)
        #计算需要画出的范围
        cdef int screen_min = -self.perBlockWidth
        cdef int screen_width = screen.get_width()
        cdef int screen_height = screen.get_height()
        #历遍装饰物列表里的物品
        for item in self.ornamentationData:
            imgToBlit = None
            thePosInMap = self.calPosInMap(item.x,item.y)
            if screen_min<=thePosInMap[0]<screen_width and screen_min<=thePosInMap[1]<screen_height:
                if self.darkMode == True and not self.inLightArea(item):
                    keyWordTemp = True
                else:
                    keyWordTemp = False
                #篝火
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
                        screen.blit(imgToBlit,(thePosInMap[0]+offSetX,thePosInMap[1]-offSetY))
                        imgToBlit = pygame.transform.scale(_MAP_ENV_IMAGE.get_ornamentation_image("campfire",int(item.imgId),False), (round(self.perBlockWidth/2),round(self.perBlockWidth/2)))
                        imgToBlit.set_alpha(item.alpha)
                        if item.imgId >= _MAP_ENV_IMAGE.get_ornamentation_num("campfire")-2:
                            item.imgId = 0
                        else:
                            item.imgId += 0.1
                #树
                elif item.type == "tree":
                    imgToBlit = pygame.transform.scale(_MAP_ENV_IMAGE.get_ornamentation_image("tree",item.image,keyWordTemp),(round(self.perBlockWidth*0.75),round(self.perBlockWidth*0.75)))
                    thePosInMap = (thePosInMap[0]-offSetX_tree,thePosInMap[1]-offSetY_tree)
                    if item.get_pos() in charactersPos:
                        if self.darkMode == False or self.inLightArea(item):
                            imgToBlit.set_alpha(100)
                #其他装饰物
                elif item.type == "decoration" or item.type == "obstacle" or item.type == "chest":
                    imgToBlit = pygame.transform.scale(_MAP_ENV_IMAGE.get_ornamentation_image(item.type,item.image,keyWordTemp),(round(self.perBlockWidth/2),round(self.perBlockWidth/2)))
                #画上装饰物
                if imgToBlit != None:
                    screen.blit(imgToBlit,(thePosInMap[0]+offSetX,thePosInMap[1]-offSetY))
    #更新方块
    def update_block(self,pos,name):
        self.__MapData[pos["y"]][pos["x"]].update(name,_BLOCKS_DATABASE[name]["canPassThrough"])
        self.__needUpdateMapSurface = True
    #是否角色能通过该方块
    def ifBlockCanPassThrough(self,pos):
        return self.__MapData[pos["y"]][pos["x"]].canPassThrough
    #计算在地图中的方块
    def calBlockInMap(self,int mouse_x,int mouse_y):
        cdef int guess_x = int(((mouse_x-self.__local_x-self.row*self.perBlockWidth*0.43)/0.43+(mouse_y-self.__local_y-self.perBlockWidth*0.4)/0.22)/2/self.perBlockWidth)
        cdef int guess_y = int((mouse_y-self.__local_y-self.perBlockWidth*0.4)/self.perBlockWidth/0.22) - guess_x
        cdef int x
        cdef int y
        cdef (int, int) posTupleTemp
        cdef float lenUnitW = self.perBlockWidth/5
        cdef float lenUnitH = self.perBlockWidth*0.8/393*214
        block_get_click = None
        for y in range(guess_y-1,guess_y+4):
            for x in range(guess_x-1,guess_x+4):
                posTupleTemp = self.calPosInMap(x,y)
                if lenUnitW<mouse_x-posTupleTemp[0]-self.perBlockWidth*0.05<lenUnitW*3 and 0<mouse_y-posTupleTemp[1]<lenUnitH:
                    block_get_click = {"x":x,"y":y}
                    break
        return block_get_click
    #计算方块被画出的位置
    def getBlockExactLocation(self,int x,int y):
        xStart,yStart = self.calPosInMap(x,y)
        return {
        "xStart": xStart,
        "xEnd": xStart + self.perBlockWidth,
        "yStart": yStart,
        "yEnd": yStart + self.perBlockWidth*0.5
        }
    #计算光亮区域
    def calculate_darkness(self,characters_data):
        cpdef list lightArea = []
        cdef int x
        cdef int y
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
                        if [x,y] not in lightArea:
                            lightArea.append([x,y])
                else:
                    for x in range(int(characters_data[each_chara].x-the_character_effective_range+(y-characters_data[each_chara].y)+1),int(characters_data[each_chara].x+the_character_effective_range-(y-characters_data[each_chara].y))):
                        if [x,y] not in lightArea:
                            lightArea.append([x,y])
        for item in self.ornamentationData:
            if item.type == "campfire" and item.triggered == True:
                for y in range(int(item.y-item.range),int(item.y+item.range)):
                    if y < item.y:
                        for x in range(int(item.x-item.range-(y-item.y)+1),int(item.x+item.range+(y-item.y))):
                            if [x,y] not in lightArea:
                                lightArea.append([x,y])
                    else:
                        for x in range(int(item.x-item.range+(y-item.y)+1),int(item.x+item.range-(y-item.y))):
                            if [x,y] not in lightArea:
                                lightArea.append([x,y])
        self.__lightArea = numpy.asarray(lightArea,dtype=numpy.int8)
        self.__needUpdateMapSurface = True
    #计算在地图中的位置
    def calPosInMap(self,float x,float y):
        cdef float widthTmp = self.perBlockWidth*0.43
        return round((x-y)*widthTmp+self.__local_x+self.row*widthTmp),round((y+x)*self.perBlockWidth*0.22+self.__local_y+self.perBlockWidth*0.4)
    #查看角色是否在光亮范围内
    def inLightArea(self,doll):
        return self.isPosInLightArea(doll.x,doll.y)
    def isPosInLightArea(self,int x,int y):
        if self.darkMode == False:
            return True
        else:
            return numpy.any(numpy.equal(self.__lightArea,[x,y]).all(1))
    #以下是A星寻路功能
    def findPath(self,startPosition,endPosition,friend_data_dict,enemies_data_dict,routeLen=None,ignoreEnemyCharacters=[]):
        cdef unsigned int startX,startY,endX,endY
        #检测起点
        if isinstance(startPosition,(list,tuple)):
            startX = startPosition[0]
            startY = startPosition[1]
        elif isinstance(startPosition,dict):
            startX = startPosition["x"]
            startY = startPosition["y"]
        else:
            startX = startPosition.x
            startY = startPosition.y
        #检测终点
        if isinstance(endPosition,(list,tuple)):
            endX = endPosition[0]
            endY = endPosition[1]
        elif isinstance(endPosition,dict):
            endX = endPosition["x"]
            endY = endPosition["y"]
        else:
            endX = endPosition.x
            endY = endPosition.y
        #建立寻路地图
        self.map2d = numpy.zeros((self.column,self.row), dtype=numpy.int8)
        #历遍地图，设置障碍方块
        """
        for y in range(theMap.row):
            for x in range(theMap.column):
                if theMap.mapData[y][x].canPassThrough == False:
                    self.map2d[x][y]=1
        """
        #历遍设施，设置障碍方块
        for item in self.ornamentationData:
            if item.type == "obstacle" or item.type == "campfire":
                self.map2d[item.x][item.y]=1
        #如果终点有我方角色，则不允许
        for key,value in friend_data_dict.items():
            if value.x == endX and value.y == endY:
                return []
        #历遍所有角色，将角色的坐标点设置为障碍方块
        for key,value in enemies_data_dict.items():
            if key != ignoreEnemyCharacters:
                self.map2d[value.x][value.y] = 1
        #如果终点是障碍物
        if self.map2d[endX][endY] != 0:
            return []
        # 开启表
        self.openList = []
        # 关闭表
        self.closeList = []
        # 起点终点
        self.startPoint = Point(startX,startY)
        self.endPoint = Point(endX,endY)
        # 可行走标记
        self.passTag = 0
        #开始寻路
        cdef list pathList = self.__startFindingPath()
        cdef list the_route = []
        #遍历路径点,讲指定数量的点放到路径列表中
        if len(pathList) > 0:
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
    def __getMinNode(self):
        """
        获得OpenList中F值最小的节点
        :return: Node
        """
        currentNode = self.openList[0]
        for node in self.openList:
            if node.g + node.h < currentNode.g + currentNode.h:
                currentNode = node
        return currentNode
    def __pointInCloseList(self, point):
        for node in self.closeList:
            if node.point == point:
                return True
        return False
    def __pointInOpenList(self, point):
        for node in self.openList:
            if node.point == point:
                return node
        return None
    def __endPointInCloseList(self):
        for node in self.openList:
            if node.point == self.endPoint:
                return node
        return None
    def __searchNear(self, minF, offSetX, offSetY):
        """
        搜索节点周围的点
        :param minF:F值最小的节点
        :param offSetX:坐标偏移量
        :param offSetY:
        :return:
        """
        # 越界检测
        mapRow,mapCol = self.map2d.shape
        if minF.point.x + offSetX < 0 or minF.point.x + offSetX > mapCol - 1 or minF.point.y + offSetY < 0 or minF.point.y + offSetY > mapRow - 1:
            return
        # 如果是障碍，就忽略
        if self.map2d[minF.point.x + offSetX][minF.point.y + offSetY] != self.passTag:
            return
        # 如果在关闭表中，就忽略
        currentPoint = Point(minF.point.x + offSetX, minF.point.y + offSetY)
        if self.__pointInCloseList(currentPoint):
            return
        # 设置单位花费
        if offSetX == 0 or offSetY == 0:
            step = 10
        else:
            step = 14
        # 如果不再openList中，就把它加入OpenList
        currentNode = self.__pointInOpenList(currentPoint)
        if not currentNode:
            currentNode = Node(currentPoint, self.endPoint, g=minF.g + step)
            currentNode.father = minF
            self.openList.append(currentNode)
            return
        # 如果在openList中，判断minF到当前点的G是否更小
        if minF.g + step < currentNode.g:  # 如果更小，就重新计算g值，并且改变father
            currentNode.g = minF.g + step
            currentNode.father = minF
    def __startFindingPath(self):
        """
        开始寻路
        :return: None或Point列表（路径）
        """
        # 判断寻路终点是否是障碍
        mapRow,mapCol = self.map2d.shape
        if self.endPoint.y < 0 or self.endPoint.y >= mapRow or self.endPoint.x < 0 or self.endPoint.x >= mapCol or self.map2d[self.endPoint.x][self.endPoint.y] != self.passTag:
            return []
        # 1.将起点放入开启列表
        startNode = Node(self.startPoint, self.endPoint)
        self.openList.append(startNode)
        # 2.主循环逻辑
        while True:
            # 找到F值最小的点
            minF = self.__getMinNode()
            # 把这个点加入closeList中，并且在openList中删除它
            self.closeList.append(minF)
            self.openList.remove(minF)
            # 判断这个节点的上下左右节点
            self.__searchNear(minF, 0, -1)
            self.__searchNear(minF, 0, 1)
            self.__searchNear(minF, -1, 0)
            self.__searchNear(minF, 1, 0)
            # 判断是否终止
            point = self.__endPointInCloseList()
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
                return []

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

# 描述AStar算法中的节点数据
class Node:
    def __init__(self, point, endPoint, g=0):
        self.point = point  # 自己的坐标
        self.father = None  # 父节点
        self.g = g  # g值，g值在用到的时候会重新算
        self.h = (abs(endPoint.x - point.x) + abs(endPoint.y - point.y)) * 10  # 计算h值