from PIL import Image
import os
import sys
import glob

def create_gif(pathList, action_name, durationForGif=0.025):
    frames = []
    for path in pathList:
        frames.append(Image.open(path))
    frames[0].save(action_name, save_all=True, append_images=frames[1:],durationForGif=durationForGif,transparency=0,loop=0,disposal=3)

for path in glob.glob("..\Assets\image\character\*"):
    for action in os.listdir(path):
        imgPathList = []
        characterName = path
        for i in range(len(characterName)-1,0,-1):
            if characterName[i] == "\\" or characterName[i] == "/":
                break
        characterName = characterName[i+1:]
        for i in range(len(glob.glob(path+"/"+action+"/*.png"))):
            imgPathList.append(path+"/"+action+"/"+characterName+"_"+action+"_"+str(i)+".png")
        create_gif(imgPathList,path+"/"+action+".gif")
        print("已完成角色{}动作{}".format(characterName,action))
    break

