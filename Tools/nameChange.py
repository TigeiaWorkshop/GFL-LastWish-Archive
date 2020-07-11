import os
import glob
import sys, zipfile, shutil
#所有动作
actions = ["attack","attack2","die","die2","die3","move","wait","wait2","skill","victory","victoryloop","reload","repair","set","spine"]
#总共处理的图片
total_img = 0
#所有种类：比如铁血啊格里芬啊
kinds = ["sangvisFerri","character"]

def unzip_single(src_file, dest_dir):
    zf = zipfile.ZipFile(src_file)
    try:
        zf.extractall(dest_dir)
    except RuntimeError as e:
        print(e)
    zf.close()

def checkNameAndAction(FileName):
    for i in range(len(FileName)):
        if FileName[i] == "_":
            break
    for a in range(i+1,len(FileName)):
        if FileName[a] == "_":
            break
    return FileName[:i],FileName[i+1:a]

for kind in kinds:
    #读取当前种类下所有类型的角色
    path = "../Assets/image/"+kind
    #检测是否有需要解压的解压包
    zip_waitingForUnzip = glob.glob(path+"/*.zip")
    for zipfileTemp in zip_waitingForUnzip:
        nameTemp,actionTemp = checkNameAndAction(zipfileTemp.replace(path,"").replace("/","").replace(".zip","").replace("\\",""))
        unZipPath = path+"/"+nameTemp
        if not os.path.exists(unZipPath):
            os.makedirs(unZipPath)
        unzip_single(zipfileTemp,unZipPath+"/"+actionTemp+"1")
        targetPathNameTemp = unZipPath+"/"+actionTemp+"1"+"/"+nameTemp+"_images"
        allActionImages = glob.glob(targetPathNameTemp+"/*.png")
        targetFinalPath = unZipPath+"/"+actionTemp
        os.makedirs(targetFinalPath)
        for eachImg in allActionImages:
            fpath,fname=os.path.split(eachImg)
            shutil.move(eachImg,targetFinalPath+"/"+fname)
        shutil.rmtree(unZipPath+"/"+actionTemp+"1")
        os.remove(zipfileTemp)
    #修改图片名称
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
