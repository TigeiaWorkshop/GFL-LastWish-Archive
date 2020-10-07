# cython: language_level=3
from Source.init import *

def battle(screen,chapter_name=None):
    #卸载音乐
    Zero.unloadBackgroundMusic()
    BATTLE = Zero.BattleSystem()
    if chapter_name != None:
        BATTLE.initialize(screen,chapter_name)
    else:
        BATTLE.load(screen)
    BATTLE.display(screen)
    #暂停声效 - 尤其是环境声
    pygame.mixer.stop()
    return BATTLE.resultInfo