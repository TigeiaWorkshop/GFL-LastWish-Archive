from distutils.core import setup
from Cython.Build import cythonize
import glob
import os
import shutil

#python setup.py build_ext
#pyinstaller -i icon.ico main.py
#pip list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1  | xargs -n1 pip install -U

#生成Zero引擎的c和pyd文件
all_Zero_py_files = glob.glob(r'Zero3/*.py')
for i in range(len(all_Zero_py_files)):
    if "__init__" not in all_Zero_py_files[i]:
        setup(ext_modules=cythonize(all_Zero_py_files[i]))
#删除Zero引擎的c文件
all_Zero_c_files = glob.glob(r'Zero3/*.c')
for i in range(len(all_Zero_c_files)):
    os.remove(all_Zero_c_files[i])

#生成游戏本体源代码的c和pyd文件
all_Source_py_files = glob.glob(r'Source/*.py')
for i in range(len(all_Source_py_files)):
    setup(ext_modules=cythonize(all_Source_py_files[i]))
#删除游戏本体源代码的c文件
all_Source_c_files = glob.glob(r'Source/*.c')
for i in range(len(all_Source_c_files)):
    os.remove(all_Source_c_files[i])
"""
#先检测有没有用于储存代码的main文件
if os.path.exists("main"):
    shutil.rmtree('main')
os.makedirs("main")
#移动文件
shutil.move("build/lib.win-amd64-3.8/Zero3","main")
shutil.move("build/lib.win-amd64-3.8/Source","main")
#删除build文件夹
shutil.rmtree('build')
"""