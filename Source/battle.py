# cython: language_level=3
from Source.init import *

def battle(chapter_name,screen):
    BATTLE = Zero.BattleSystem()
    BATTLE.process_data(screen,chapter_name)
    BATTLE.display(screen)
    #暂停声效 - 尤其是环境声
    pygame.mixer.stop()
    return BATTLE.resultInfo