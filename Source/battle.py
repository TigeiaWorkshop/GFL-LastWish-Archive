# cython: language_level=3
from Source.init import *

def battle(chapter_name,screen,setting):
    BATTLE = Zero.BattleSystem(chapter_name,setting)
    BATTLE.process_data(screen)
    BATTLE.display(chapter_name,screen,setting)
    #暂停声效 - 尤其是环境声
    pygame.mixer.stop()
    return BATTLE.resultInfo