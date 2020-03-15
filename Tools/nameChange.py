import os
character="2b14"
kind = "character"
action=["attack","die","move","reload","set","wait"]
#action=["attack","die","move","skill","victory","victoryloop","wait"]
#action=["attack","die","move","wait"]
total_img=0
for a in range(len(action)):
    path="../Assets/img/"+kind+"/"+character+"/"+action[a]+"/"
    f=os.listdir(path)
    n=0
    for i in f:
        #设置旧文件名（就是路径+文件名）
        oldname=path+f[n]
        #设置新文件名
        newname=path+character+'_'+action[a]+'_'+str(n)+'.png'
        os.rename(oldname,newname)
        n+=1
        total_img+=1
print("Done! Total Image: "+str(total_img))
