import os
import glob
import sys, zipfile
#所有动作
actions = ["attack","attack2","die","die2","die3","move","wait","wait2","skill","victory","victoryloop","reload","repair","set"]
#总共处理的图片
total_img = 0
#所有种类：比如铁血啊格里芬啊
kinds = ["sangvisFerri","character"]

def unzip_single(src_file, dest_dir):
    zf = zipfile.ZipFile(src_file)
    try:
        zf.extractall(path=dest_dir)
    except RuntimeError as e:
        print(e)
    zf.close()

for kind in kinds:
    #读取当前种类下所有类型的角色
    path = "../Assets/image/"+kind
    characters = glob.glob(path+"/*")
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
                    characterName = characterPath.replace(".","").replace("\\","").replace("/","").replace("Assets","").replace("image","").replace(kind,"")
                    newname=path + characterName+'_'+action+'_'+str(n)+'.png'
                    try:
                        os.rename(oldname,newname)
                    except BaseException:
                        break
                    total_img+=1
                    n+=1

print("Done! Total Image: "+str(total_img))
