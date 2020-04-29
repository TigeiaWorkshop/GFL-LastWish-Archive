import yaml
import glob
import os
#读取方块信息
path = "../Data/blocks.yaml"

with open(path, "r", encoding='utf-8') as f:
    loadData = yaml.load(f.read(),Loader=yaml.FullLoader)
    dataInfo = loadData["blocks"]


"""
path="../Assets/image/environment/block/"
f=os.listdir(path)
n=0
for i in f:
    #设置旧文件名（就是路径+文件名）
    oldname=path+f[n]
    #设置新文件名
    newname=path+f[n].replace("ISO","").replace(" ","").replace("-","").replace("_","")
    os.rename(oldname,newname)
    n+=1
"""

all_blocks_img_list = glob.glob(r'../Assets/image/environment/block/*.png')
if len(all_blocks_img_list) != len(dataInfo):
    for i in range(len(all_blocks_img_list)):
        nameTemp = all_blocks_img_list[i].replace("../Assets/image/environment/block","").replace(".png","").replace("\\","")
        if nameTemp not in dataInfo:
            dataInfo[nameTemp] = {
                "canPassThrough": True,
            }

path = "../Data/blocks.yaml"
with open(path, "w", encoding='utf-8') as f:
    loadData["blocks"] = dataInfo
    yaml.dump(loadData, f, allow_unicode=True)