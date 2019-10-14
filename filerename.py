import os

path="img/main_menu/"
f=os.listdir(path)
n=0
for i in f:
    #设置旧文件名（就是路径+文件名）
    oldname=path+f[n]

    #设置新文件名
    newname=path+'background_img'+str(n)+'.jpg'
    os.rename(oldname,newname)
    n+=1
