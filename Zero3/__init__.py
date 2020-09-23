# cython: language_level=3
#包含basic/font/module，Zero引擎的必要组件
from Zero3.dialogSystem import *
#Zero引擎的非必要组件...推荐使用
from Zero3.battleSystem import *
try:
    from Zero3.movie import *
except BaseException:
    print('ZeroEngine-Warning: Unable to import module "movie".')

print("Zero Engine 3 (pygame {}, python {})".format(pygame.version.ver,platform.python_version()))
print("Hello from the zero engine community. http://tjygf.com/forum.php")