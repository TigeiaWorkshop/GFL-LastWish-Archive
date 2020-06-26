import os
import glob

#kind = "character"
kind = "sangvisFerri"
path = "../Assets/image/"+kind
characters = glob.glob(path+"/*")

actions = ["attack","attack2","die","die2","die3","move","wait","wait2","skill","victory","victoryloop","reload","repair","set"]

total_img=0
for characterPath in characters:
    for action in actions:
        path = characterPath+"/"+action+"/"
        if os.path.exists(path):
            f=os.listdir(path)
            n=0
            for i in f:
                #设置旧文件名（就是路径+文件名）
                oldname=path+f[n]
                #设置新文件名
                newname=path+characterPath.replace("../Assets/image/sangvisFerri","").replace("\\","")+'_'+action+'_'+str(n)+'.png'
                try:
                    os.rename(oldname,newname)
                    total_img+=1
                except BaseException:
                    break
                n+=1
                

print("Done! Total Image: "+str(total_img))
