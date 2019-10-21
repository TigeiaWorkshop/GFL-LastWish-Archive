import os
character="sv-98"
action=["attack","die","move","skill","victory","victoryloop","wait"]

for a in range(len(action)):
    path="img/character/"+character+"/"+action[a]+"/"
    f=os.listdir(path)
    n=0
    for i in f:
        #设置旧文件名（就是路径+文件名）
        oldname=path+f[n]

        #设置新文件名
        newname=path+character+'_'+action[a]+'_'+str(n)+'.png'
        os.rename(oldname,newname)
        n+=1
