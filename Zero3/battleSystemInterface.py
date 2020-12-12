# cython: language_level=3
from Zero3.characterDataManager import *
from Zero3.map import MapObject
from Zero3.battleUI import *
from Zero3.AI import *
from Zero3.skill import *

#战斗系统接口，请勿实例化
class BattleSystemInterface:
    def __init__(self):
        #-----需要储存的参数-----#
        #被选中的角色
        self.characterGetClick = None
        self.enemiesGetAttack = {}
        self.action_choice = None
        #是否不要画出用于表示范围的方块
        self.NotDrawRangeBlocks = True
        self.areaDrawColorBlock = {"green":[],"red":[],"yellow":[],"blue":[],"orange":[]}
        #是否在战斗状态-战斗loop
        self.battleMode = False
        #是否在等待
        self.isWaiting = True
        #谁的回合
        self.whose_round = "sangvisFerrisToPlayer"
        #用于判断是否移动屏幕的参数
        self.__mouse_move_temp_x = -1
        self.__mouse_move_temp_y = -1
        self.screen_to_move_x = None
        self.screen_to_move_y = None
        #是否是死亡的那个
        self.the_dead_one = {}
        #用于检测是否有方向键被按到的字典
        self.__pressKeyToMove = {"up":False,"down":False,"left":False,"right":False}
        self.rightClickCharacterAlpha = None
        #战斗系统主循环判定参数
        self.isPlaying = True
        #技能对象
        self.skill_target = None
        #被按到的按键
        self.buttonGetHover = None
        #被救助的那个角色
        self.friendGetHelp = None
        #AI系统正在操控的地方角色ID
        self.enemy_in_control = None
        self.enemies_in_control_id = None
        #所有敌对角色的名字列表
        self.sangvisFerris_name_list = None
        #战斗状态数据
        self.resultInfo = {
            "total_rounds" : 1,
            "total_kills" : 0,
            "total_time" : time.time(),
            "times_characters_down" : 0
        }
        #储存角色受到伤害的文字surface
        self.damage_do_to_characters = {}
        self.txt_alpha = None
        self.stayingTime = 0
        # 移动路径
        self.the_route = []
        #上个回合因为暴露被敌人发现的角色
        #格式：角色：[x,y]
        self.the_characters_detected_last_round = {}
        #敌人的状态
        self.enemy_action = None
        #战斗系统进行时的输入事件
        self.__events = None
        self.right_click = False
        #角色数据
        self.characters_data = None
        self.sangvisFerris_data = None
        #地图数据
        self.MAP = None
        #对话数据
        self.dialogData = None
        #对话-动作是否被设置
        self.dialog_ifPathSet = False
        #是否从存档中加载的数据-默认否
        self.loadFromSave = False
        #积分栏的UI模块
        self.ResultBoardUI = None
    def create_map(self,MapData):
        self.MAP = MapObject(MapData,round(self.window_x/10),round(self.window_y/10))
    #检测手柄事件
    def _check_jostick_events(self):
        if controller.joystick.get_init() == True:
            if round(controller.joystick.get_axis(4)) == -1:
                self.__pressKeyToMove["up"]=True
            else:
                self.__pressKeyToMove["up"]=False
            if round(controller.joystick.get_axis(4)) == 1:
                self.__pressKeyToMove["down"]=True
            else:
                self.__pressKeyToMove["down"]=False
            if round(controller.joystick.get_axis(3)) == 1:
                self.__pressKeyToMove["right"]=True
            else:
                self.__pressKeyToMove["right"]=False
            if round(controller.joystick.get_axis(3)) == -1:
                self.__pressKeyToMove["left"]=True
            else:
                self.__pressKeyToMove["left"]=False
    def _check_key_down(self,event):
        if event.key == pygame.K_w:
            self.__pressKeyToMove["up"]=True
        if event.key == pygame.K_s:
            self.__pressKeyToMove["down"]=True
        if event.key == pygame.K_a:
            self.__pressKeyToMove["left"]=True
        if event.key == pygame.K_d:
            self.__pressKeyToMove["right"]=True
    def _check_key_up(self,event):
        if event.key == pygame.K_w:
            self.__pressKeyToMove["up"]=False
        if event.key == pygame.K_s:
            self.__pressKeyToMove["down"]=False
        if event.key == pygame.K_a:
            self.__pressKeyToMove["left"]=False
        if event.key == pygame.K_d:
            self.__pressKeyToMove["right"]=False
    def _check_right_click_move(self,mouse_x,mouse_y):
        #移动屏幕
        if pygame.mouse.get_pressed()[2]:
            if self.__mouse_move_temp_x == -1 and self.__mouse_move_temp_y == -1:
                self.__mouse_move_temp_x = mouse_x
                self.__mouse_move_temp_y = mouse_y
            else:
                if self.__mouse_move_temp_x != mouse_x or self.__mouse_move_temp_y != mouse_y:
                    if self.__mouse_move_temp_x != mouse_x:
                        self.MAP.addPos_x(self.__mouse_move_temp_x-mouse_x)
                    if self.__mouse_move_temp_y != mouse_y:
                        self.MAP.addPos_y(self.__mouse_move_temp_y-mouse_y)
                    self.__mouse_move_temp_x = mouse_x
                    self.__mouse_move_temp_y = mouse_y
        else:
            self.__mouse_move_temp_x = -1
            self.__mouse_move_temp_y = -1
    def __move_screen(self):
        #根据按键情况设定要移动的数值
        if self.__pressKeyToMove["up"] == True:
            if self.screen_to_move_y == None:
                self.screen_to_move_y = self.perBlockHeight/4
            else:
                self.screen_to_move_y += self.perBlockHeight/4
        if self.__pressKeyToMove["down"] == True:
            if self.screen_to_move_y == None:
                self.screen_to_move_y = -self.perBlockHeight/4
            else:
                self.screen_to_move_y -= self.perBlockHeight/4
        if self.__pressKeyToMove["left"] == True:
            if self.screen_to_move_x == None:
                self.screen_to_move_x = self.MAP.perBlockWidth/4
            else:
                self.screen_to_move_x += self.MAP.perBlockWidth/4
        if self.__pressKeyToMove["right"] == True:
            if self.screen_to_move_x == None:
                self.screen_to_move_x = -self.MAP.perBlockWidth/4
            else:
                self.screen_to_move_x -= self.MAP.perBlockWidth/4
        #如果需要移动屏幕
        if self.screen_to_move_x != None and self.screen_to_move_x != 0:
            temp_value = int(self.MAP.getPos_x() + self.screen_to_move_x*0.2)
            if self.window_x-self.MAP.surface_width<=temp_value<=0:
                self.MAP.setPos_x(temp_value)
                self.screen_to_move_x*=0.8
                if int(self.screen_to_move_x) == 0:
                    self.screen_to_move_x = 0
            else:
                self.screen_to_move_x = 0
        if self.screen_to_move_y != None and self.screen_to_move_y !=0:
            temp_value = int(self.MAP.getPos_y() + self.screen_to_move_y*0.2)
            if self.window_y-self.MAP.surface_height<=temp_value<=0:
                self.MAP.setPos_y(temp_value)
                self.screen_to_move_y*=0.8
                if int(self.screen_to_move_y) == 0:
                    self.screen_to_move_y = 0
            else:
                self.screen_to_move_y = 0
    def _get_event(self):
        return self.__events
    def _display_map(self,screen):
        self.__move_screen()
        self.screen_to_move_x,self.screen_to_move_y = self.MAP.display_map(screen,self.screen_to_move_x,self.screen_to_move_y)
    def _display(self):
        #更新游戏事件
        self.__events = pygame.event.get()