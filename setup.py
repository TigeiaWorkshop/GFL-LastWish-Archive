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
remove_old_pyd = True
produce_html_files = False

#删除旧的pyd文件
if remove_old_pyd:
    for path in glob.glob(r'Zero3/scr_pyx/*.pyd'):
        os.remove(path)
#生成Zero引擎的c和pyd文件
open("Zero3/scr_pyx/__init__.py","w")
for path in glob.glob(r'Zero3/scr_pyx/*.pyx'):
    setup(ext_modules=cythonize(path,show_all_warnings=True,annotate=produce_html_files))
    #删除Zero引擎的c文件
    if not debug_c:
        os.remove(path.replace(".pyx",".c"))
os.remove("Zero3/scr_pyx/__init__.py")
#生成游戏本体源代码的c和pyd文件
if compile_py_files_in_Source:
    for path in glob.glob(r'Source/*.py'):
        setup(ext_modules=cythonize(path))
        if not debug_c:
            os.remove(path.replace(".pyx",".c"))
#删除build文件夹
shutil.rmtree('build')