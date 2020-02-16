import yaml
import glob
#读取方块信息
path = "../Data/blocks.yaml"
while True:
    with open(path, "r", encoding='utf-8') as f:
        loadData = yaml.load(f.read(),Loader=yaml.FullLoader)
        dataInfo = loadData["blocks"]

    name_to_add = input("Name:")
    canPassThrough = input("canPassThrough(y/n):")
    if canPassThrough == "y" or canPassThrough == "Y":
        canPassThrough = True
    elif canPassThrough == "n" or canPassThrough == "n":
        canPassThrough = False
    img_number = len(glob.glob(r'../Assets/img/environment/'+name_to_add+'*.png'))

    if img_number != 0:
        dataInfo[len(dataInfo)] = {
            "name": name_to_add,
            "canPassThrough": canPassThrough,
            "imgNum":img_number
        }
        with open(path, "w", encoding='utf-8') as f:
            loadData["blocks"] = dataInfo
            yaml.dump(loadData, f, allow_unicode=True)
    else:
        print("Waring: cannot find the img, please try again")