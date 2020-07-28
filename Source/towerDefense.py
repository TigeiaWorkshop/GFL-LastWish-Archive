# cython: language_level=3
from Zero3.basic import *
from Zero3.characterDataManager import *
from Zero3.map import *

def towerDefense(chapter_name,screen,setting):
    """初始化基础数据"""
    #控制器输入组件
    InputController = GameController(screen)
    #获取屏幕的尺寸
    window_x,window_y = screen.get_size()
    #卸载音乐
    pygame.mixer.music.unload()
    #帧率控制器
    Display = DisplayController(setting['FPS'])
    #加载按钮的文字
    with open("Lang/"+setting['Language']+".yaml", "r", encoding='utf-8') as f:
        loadData = yaml.load(f.read(),Loader=yaml.FullLoader)
        selectMenuUI = SelectMenu(loadData["SelectMenu"])
        battleUiTxt = loadData["Battle_UI"]
        warnings_to_display = WarningSystem(loadData["Warnings"])
        loading_info = loadData["LoadingTxt"]
        resultTxt = loadData["ResultBoard"]
    #加载剧情
    with open("Data/main_chapter/"+chapter_name+"_dialogs_"+setting['Language']+".yaml", "r", encoding='utf-8') as f:
        loadData = yaml.load(f.read(),Loader=yaml.FullLoader)
        chapter_title = loadData["title"]
        battle_info = loadData["battle_info"]
        dialog_during_battle = loadData["dialog_during_battle"]
        chapterDesc = loadData["description"]
    #章节标题显示
    infoToDisplayDuringLoading = LoadingTitle(window_x,window_y,battleUiTxt["numChapter"],chapter_name,chapter_title,chapterDesc)