from Zero3.dialogSystem import *

class BattleSystem:
    def __init__(self):
        #-----需要储存的参数-----#
        #被选中的角色
        self.characterGetClick = ""
        self.enemiesGetAttack = {}
        self.action_choice = ""
        #是否不要画出用于表示范围的方块
        self.NotDrawRangeBlocks = True
        self.areaDrawColorBlock = {"green":[],"red":[],"yellow":[],"blue":[],"orange":[]}
        #是否在战斗状态-战斗loop
        self.battle = False
        #是否在等待
        self.isWaiting = True
        #谁的回合
        self.whose_round = "sangvisFerrisToPlayer"
        #用于判断是否移动屏幕的参数
        self.mouse_move_temp_x = -1
        self.mouse_move_temp_y = -1
        self.screen_to_move_x = None
        self.screen_to_move_y = None
        #是否是死亡的那个
        self.the_dead_one = {}
        #用于检测是否有方向键被按到的字典
        self.pressKeyToMove = {"up":False,"down":False,"left":False,"right":False}
        self.rightClickCharacterAlpha = None
        #战斗系统主循环判定参数
        self.battleSystemMainLoop = True
        #技能对象
        self.skill_target = None
        #被按到的按键
        self.buttonGetHover = None
        #被救助的那个角色
        self.theFriendGetHelp = None
        #AI系统正在操控的地方角色ID
        self.enemy_in_control = None
        self.enemies_in_control_id = None
        #所有敌对角色的名字列表
        self.sangvisFerris_name_list = None
        #-----不需要储存的参数，每次加载都需初始化-----#
        #用于判断战斗过场对白的程序参数是否被初始化
        self.dialog_valuable_initialized = False
        #储存角色受到伤害的文字surface
        self.damage_do_to_characters = {}
        self.txt_alpha = None
        self.stayingTime = 0