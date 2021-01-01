# cython: language_level=3
#加载Zero引擎的必要组件
from .dialogSystem import *
from .battleSystemInterface import *
from .mapCreator import *
from .experimental import *
import platform

print("Zero Engine 3 (pygame {}, python {})".format(pygame.version.ver,platform.python_version()))
print("Hello from the zero engine community. http://tjygf.com/forum.php")