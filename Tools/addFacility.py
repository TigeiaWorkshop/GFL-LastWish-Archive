import yaml
import glob
import os
#读取方块信息
path = "../Data/decorations.yaml"

with open(path, "r", encoding='utf-8') as f:
    decorationsData = yaml.load(f.read(),Loader=yaml.FullLoader)

all_decorations_img_list = glob.glob(r'../Assets/image/environment/decoration/*.png')

if len(all_decorations_img_list) != len(decorationsData["decorations"]):
    for i in range(len(all_decorations_img_list)):
        nameTemp = all_decorations_img_list[i].replace("../Assets/image/environment/decoration","").replace(".png","").replace("\\","").replace("/","")
        if nameTemp not in decorationsData["decorations"]:
            itType = input("What its type for "+nameTemp+" (1:decoration | 2:tree | 3:obstacle | 4:special) :")
            if itType == "1":
                decorationsData["decorations"][nameTemp] = "decoration"
            elif itType == "2":
                decorationsData["decorations"][nameTemp] = "tree"
            elif itType == "3":
                decorationsData["decorations"][nameTemp] = "obstacle"
            elif itType == "4":
                decorationsData["decorations"][nameTemp] = "special"
            elif itType == "q":
                with open(path, "w", encoding='utf-8') as f:
                    yaml.dump(decorationsData, f, allow_unicode=True)
                break
    with open(path, "w", encoding='utf-8') as f:
        yaml.dump(decorationsData, f, allow_unicode=True)