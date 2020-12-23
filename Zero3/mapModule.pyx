# cython: language_level=3
from Zero3.basic import addDarkness, loadImg, resizeImg
import pygame

#地图场景模块
class EnvImagesManagement:
    def __init__(self,theMap,ornamentationData,bgImgName,theWidth,darkMode,darkness=150):
        self.__ENV_IMAGE_DICT_ORIGINAL = {}
        self.__ENV_IMAGE_DICT_ORIGINAL_DARK = None
        self.__ENV_IMAGE_DICT = {}
        self.__ENV_IMAGE_DICT_DARK = None
        self.__ORNAMENTATION_IMAGE_DICT = {}
        self.__ORNAMENTATION_IMAGE_DICT_DARK = None
        self.__BACKGROUND_IMAGE = loadImg("Assets/image/dialog_background/{}".format(bgImgName),ifConvertAlpha=False).convert() if bgImgName != None else None
        self.__BACKGROUND_SURFACE = None
        self.__MAP_SURFACE = None
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
        self.__MAP_SURFACE = pygame.Surface(map_size,flags=pygame.SRCALPHA).convert_alpha()
        return self.__MAP_SURFACE
    def display_background_surface(self,screen,pos):
        screen.blit(self.__BACKGROUND_SURFACE,(0,0))
        screen.blit(self.__MAP_SURFACE,pos)

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