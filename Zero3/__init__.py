# cython: language_level=3
#加载Zero引擎的必要组件
from Zero3.dialogSystem import *
from Zero3.battleSystemInterface import *
from Zero3.mapCreator import *
from Zero3.movie import *
import platform

print("Zero Engine 3 (pygame {}, python {})".format(pygame.version.ver,platform.python_version()))
print("Hello from the zero engine community. http://tjygf.com/forum.php")