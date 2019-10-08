import os
character="gsh-18"
action="move"
path="img/character/"+character+"/"+action+"/"

f=os.listdir(path)

n=0
for i in f:
    #设置旧文件名（就是路径+文件名）
    oldname=path+f[n]

    #设置新文件名
    newname=path+'gsh-18_'+action+'_'+str(n)+'.png'
    os.rename(oldname,newname)
    n+=1
