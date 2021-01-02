from distutils.core import setup
from Cython.Build import cythonize
import glob
import os
import shutil

#pyinstaller -i icon.ico main.py
#pip list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1  | xargs -n1 pip install -U

#是否编译Source中的游戏本体
compile_py_files_in_Source = False
debug_c = False

#生成游戏本体源代码的c和pyd文件
if compile_py_files_in_Source:
    for path in glob.glob(r'Source/*.py'):
        setup(ext_modules=cythonize(path))
        if not debug_c:
            os.remove(path.replace(".pyx",".c"))
#删除build文件夹
shutil.rmtree('build')