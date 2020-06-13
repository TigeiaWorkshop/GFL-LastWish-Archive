# cython: language_level=3
from Zero3.module import *

#图片加载模块：接收图片路径,长,高,返回对应图片
def loadImg(path,width=None,height=None,setAlpha=None,ifConvertAlpha=True):
    img = None
    if isinstance(path,str):
        if ifConvertAlpha == False:
            img = pygame.image.load(os.path.join(path))
        else:
            img = pygame.image.load(os.path.join(path)).convert_alpha()
    else:
        img = path
    if setAlpha != None:
        img.set_alpha(setAlpha)
    if width == None and height == None:
        pass
    elif height!= None and height >= 0 and width == None:
        img = pygame.transform.scale(img,(round(height/img.get_height()*img.get_width()), round(height)))
    elif height == None and width!= None and width >= 0:
        img = pygame.transform.scale(img,(round(width), round(width/img.get_width()*img.get_height())))
    elif width >= 0 and height >= 0:
        img = pygame.transform.scale(img, (int(width), int(height)))
    elif width < 0 or height < 0:
        raise Exception('Both width and height must be positive interger!')
    return img
        
#图片blit模块：接受图片，位置（列表格式），屏幕，如果不是UI层需要local_x和local_y
def drawImg(img,position,screen,local_x=0,local_y=0):
    screen.blit(img,(position[0]+local_x,position[1]+local_y))

#调整图片亮度
def changeDarkness(surface,value):
    dark = pygame.Surface((surface.get_width(), surface.get_height()), flags=pygame.SRCALPHA)
    dark.fill((abs(int(value)),abs(int(value)),abs(int(value)),0))
    if value > 0:
        surface.blit(dark, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    elif value < 0:
        surface.blit(dark, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    return surface

#重新编辑尺寸
def resizeImg(img,imgSize=(None,None)):
    if imgSize[1]!= None and imgSize[1] >= 0 and imgSize[0] == None:
        img = pygame.transform.scale(img,(round(imgSize[1]/img.get_height()*img.get_width()), round(imgSize[1])))
    elif imgSize[1] == None and imgSize[0]!= None and imgSize[0] >= 0:
        img = pygame.transform.scale(img,(round(imgSize[0]), round(imgSize[0]/img.get_width()*img.get_height())))
    elif imgSize[0] >= 0 and imgSize[1] >= 0:
        img = pygame.transform.scale(img, (round(imgSize[0]), round(imgSize[1])))
    elif imgSize[0] < 0 or imgSize[1] < 0:
        raise Exception('Both width and height must be positive interger!')
    return img

#高级图片加载模块：接收图片路径（或者已经载入的图片）,位置:[x,y],长,高,返回对应的图片class
def loadImage(path,the_object_position,width=None,height=None,description="Default",ifConvertAlpha=True):
    if isinstance(path,str):
        if ifConvertAlpha == False:
            return ImageSurface(pygame.image.load(os.path.join(path)),the_object_position[0],the_object_position[1],width,height,description)
        else:
            return ImageSurface(pygame.image.load(os.path.join(path)).convert_alpha(),the_object_position[0],the_object_position[1],width,height,description)
    else:
        return ImageSurface(path,the_object_position[0],the_object_position[1],width,height,description)

#字体
with open("Save/setting.yaml", "r", encoding='utf-8') as f:
    DATA = yaml.load(f.read(),Loader=yaml.FullLoader)
    FONT = DATA["Font"]
    MODE = DATA["Antialias"]

#文字制作模块：接受文字，颜色，文字大小，文字样式，模式，返回制作完的文字
def fontRender(txt,color,size=50,ifBold=False,ifItalic=False):
    normal_font = pygame.font.SysFont(FONT,int(size),ifBold,ifItalic)
    if color == "gray" or color == "grey" or color == "disable":
        text_out = normal_font.render(txt, MODE, (105,105,105))
    elif color == "white" or color == "enable":
        text_out = normal_font.render(txt, MODE, (255, 255, 255))
    elif color == "black":
        text_out = normal_font.render(txt, MODE, (0, 0, 0))
    elif color == "green":
        text_out = normal_font.render(txt, MODE, (0,255,0))
    elif color == "red":
        text_out = normal_font.render(txt, MODE, (255, 0, 0))
    else:
        text_out = normal_font.render(txt, MODE, color)
    return text_out

#高级文字制作模块：接受文字，颜色，文字大小，文字样式，模式，返回制作完的文字Class，该Class具有一大一普通的字号
def fontRenderPro(txt,color,size=50,ifBold=False,ifItalic=False):
    class TextSurface:
        def __init__(self, n, b):
            self.n = n
            self.b = b
    #文字设定
    normal_font = pygame.font.SysFont(FONT,int(size),ifBold,ifItalic)
    big_font = pygame.font.SysFont(FONT,int(size*1.5),ifBold,ifItalic)
    if color == "gray" or color == "grey" or color == "disable":
        text_out = TextSurface(normal_font.render(txt, MODE, (105,105,105)),big_font.render(txt, MODE, (105,105,105)))
    elif color == "white" or color == "enable":
        text_out = TextSurface(normal_font.render(txt, MODE, (255, 255, 255)),big_font.render(txt, MODE, (255, 255, 255)))
    else:
        text_out = TextSurface(normal_font.render(txt, MODE, color),big_font.render(txt, MODE, color))
    return text_out

#检测是否被点击
def isHoverOn(the_object,the_object_position,local_x=0,local_y=0):
    mouse_x,mouse_y=pygame.mouse.get_pos()
    if the_object_position[0]<mouse_x-local_x<the_object_position[0]+the_object.get_width() and the_object_position[1]<mouse_y-local_y<the_object_position[1]+the_object.get_height():
        return True
    else:
        return False

#检测是否鼠标在物体上
def isHover(theImgClass,local_x=0,local_y=0):
    mouse_x,mouse_y=pygame.mouse.get_pos()
    if theImgClass.x<mouse_x-local_x<theImgClass.x+theImgClass.width and theImgClass.y<mouse_y-local_y<theImgClass.y+theImgClass.height:
        return True
    else:
        return False

#中心展示模块1：接受两个item和item2的x和y，将item1展示在item2的中心位置,但不展示item2：
def displayInCenter(item1,item2,x,y,screen,local_x=0,local_y=0):
    added_x = (item2.get_width()-item1.get_width())/2
    added_y = (item2.get_height()-item1.get_height())/2
    screen.blit(item1,(x+added_x+local_x,y+added_y+local_y))

#中心展示模块2：接受两个item和item2的x和y，展示item2后，将item1展示在item2的中心位置：
def displayWithInCenter(item1,item2,x,y,screen,local_x=0,local_y=0):
    added_x = (item2.get_width()-item1.get_width())/2
    added_y = (item2.get_height()-item1.get_height())/2
    screen.blit(item2,(x+local_x,y+local_y))
    screen.blit(item1,(x+added_x+local_x,y+added_y+local_y))

#字典合并
def dicMerge(dict1, dict2): 
    res = {**dict1, **dict2} 
    return res

#加载路径下的所有图片，储存到一个list当中，然后返回
def loadAllImgInFile(pathRule,width=None,height=None):
    allImg = glob.glob(pathRule)
    for i in range(len(allImg)):
        allImg[i] = loadImg(allImg[i],width,height)
    return allImg

#增加图片暗度
def addDarkness(img,value):
    newImg = pygame.transform.scale(img,(img.get_width(), img.get_height()))
    dark = pygame.Surface((img.get_width(), img.get_height()), flags=pygame.SRCALPHA)
    dark.fill((value,value,value))
    newImg.blit(dark, (0, 0), special_flags=pygame.BLEND_RGB_SUB)
    return newImg

#减少图片暗度
def removeDarkness(img,value):
    newImg = pygame.transform.scale(img,(img.get_width(), img.get_height()))
    dark = pygame.Surface((img.get_width(), img.get_height()), flags=pygame.SRCALPHA)
    dark.fill((value,value,value))
    newImg.blit(dark, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
    return newImg
