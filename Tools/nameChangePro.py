
import os
path="../Assets/image/environment/decoration/"
f=os.listdir(path)
n=0
for i in f:
    #设置旧文件名（就是路径+文件名）
    oldname=path+f[n]
    #设置新文件名
    newname=path+f[n].replace(" ","")
    os.rename(oldname,newname)
    n+=1