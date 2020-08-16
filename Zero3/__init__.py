# cython: language_level=3
#包含basic/font/module，Zero引擎的必要组件
from Zero3.dialogSystem import *
#Zero引擎的非必要组件...推荐使用
try:
    from Zero3.AI import *
except BaseException:
    print('ZeroEngine-Warning: Unable to import module "AI".')
try:
    from Zero3.battleUI import *
except BaseException:
    print('ZeroEngine-Warning: Unable to import module "battleUI".')
try:
    from Zero3.characterDataManager import *
except BaseException:
    print('ZeroEngine-Warning: Unable to import module "characterDataManager".')
try:
    from Zero3.map import *
except BaseException:
    print('ZeroEngine-Warning: Unable to import module "map".')
try:
    from Zero3.movie import *
except BaseException:
    print('ZeroEngine-Warning: Unable to import module "movie".')
#初始化常用模块
console = Console(0,0)
def get_console():
    return console
def display_console(screen):
    console.display(screen)

print("Zero Engine 3 (pygame {}, python {})".format(pygame.version.ver,platform.python_version()))
print("Hello from the zero engine community. http://tjygf.com/forum.php")