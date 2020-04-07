from distutils.core import setup
from Cython.Build import cythonize
import glob
import os
import shutil

#python setup.py build_ext
#pyinstaller -F -i main.ico main.py

#生成c和pyd文件
all_Zero2_py_files = glob.glob(r'Zero2/*.py')
for i in range(len(all_Zero2_py_files)):
    setup(ext_modules=cythonize(all_Zero2_py_files[i]))
#删除c文件
all_Zero2_c_files = glob.glob(r'Zero2/*.c')
for i in range(len(all_Zero2_c_files)):
    os.remove(all_Zero2_c_files[i])
#先检测Zero2_pyd有没有pyd文件
all_Zero2_pyd_files = glob.glob(r'Zero2_pyd/*.pyd')
if len(all_Zero2_pyd_files)>0:
    for i in range(len(all_Zero2_pyd_files)):
        os.remove(all_Zero2_pyd_files[i])
#移动pyd文件
all_Zero2_pyd_files = glob.glob(r'build/lib.win-amd64-3.7/*.pyd')
for i in range(len(all_Zero2_pyd_files)):
    shutil.move(all_Zero2_pyd_files[i],"Zero2_pyd/")
#删除build文件夹
shutil.rmtree('build')