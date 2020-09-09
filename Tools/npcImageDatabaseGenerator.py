import os
import yaml

Database = {"Data":{}}

def get_kind(fileName):
    fileName = os.path.splitext(fileName)[0]
    if "_" not in fileName:
        return fileName
    else:
        for i in range(len(fileName)):
            if fileName[i] == "_":
                return fileName[:i]

all_npc_img_files = os.listdir("../Assets/image/npc/")
for eachFileName in all_npc_img_files:
    kindOfImg = get_kind(eachFileName)
    if kindOfImg not in Database["Data"]:
        Database["Data"][kindOfImg] = []
    Database["Data"][kindOfImg].append(eachFileName)

with open("../Data/npcImageDatabase.yaml", "w", encoding='utf-8') as f:
        yaml.dump(Database, f, allow_unicode=True)