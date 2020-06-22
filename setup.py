from distutils.core import setup
from Cython.Build import cythonize
import glob
import os
import shutil

#python setup.py build_ext
#pyinstaller -i icon.ico main.py
#pip list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1  | xargs -n1 pip install -U

#生成c和pyd文件
all_Zero3_py_files = glob.glob(r'Zero3/*.py')
for i in range(len(all_Zero3_py_files)):
    setup(ext_modules=cythonize(all_Zero3_py_files[i]))
#删除c文件
all_Zero3_c_files = glob.glob(r'Zero3/*.c')
for i in range(len(all_Zero3_c_files)):
    os.remove(all_Zero3_c_files[i])
#先检测Zero3_pyd有没有pyd文件
if not os.path.exists("Zero3_pyd"):
    os.makedirs("Zero3_pyd")
else:
    all_Zero3_pyd_files = glob.glob(r'Zero3_pyd/*.pyd')
    if len(all_Zero3_pyd_files)>0:
        for i in range(len(all_Zero3_pyd_files)):
            os.remove(all_Zero3_pyd_files[i])
#移动pyd文件
all_Zero3_pyd_files = glob.glob(r'build/lib.win-amd64-3.8/*.pyd')
for i in range(len(all_Zero3_pyd_files)):
    shutil.move(all_Zero3_pyd_files[i],"Zero3_pyd/")
#删除build文件夹
shutil.rmtree('build')