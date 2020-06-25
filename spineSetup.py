from distutils.core import setup
from Cython.Build import cythonize
import glob
import shutil

#python spineSetup.py build_ext

#生成c和pyd文件
all_pyx_files = glob.glob(r'Spine/*.pyx')
for path in all_pyx_files:
    setup(ext_modules=cythonize(path))

#移动pyd文件
all_Zero3_pyd_files = glob.glob(r'build/lib.win-amd64-3.8/*.pyd')
for i in range(len(all_Zero3_pyd_files)):
    shutil.move(all_Zero3_pyd_files[i],"Spine/")
