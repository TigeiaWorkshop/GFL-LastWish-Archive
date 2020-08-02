import glob
import yaml

with open("../Data/character_data.yaml", "r", encoding='utf-8') as f:
    loadData = yaml.load(f.read(),Loader=yaml.FullLoader)

for path in glob.glob(r'../Assets/image/character/*'):
    name = path.replace("../Assets/image/character\\","")
    if name not in loadData["griffin"]:
        loadData["griffin"][name] = {
        "action_point": 1,
        "attack_range": 1,
        "effective_range":{
            "far": [5,6],
            "middle":[3,4],
            "near":[1,2],
        },
        "kind": None,
        "magazine_capacity": 1,
        "max_damage": 1,
        "max_hp": 1,
        "min_damage": 1,
        "skill_cover_range": None,
        "skill_effective_range": None,
        }

for path in glob.glob(r'../Assets/image/sangvisFerri/*'):
    name = path.replace("../Assets/image/sangvisFerri\\","")
    if name not in loadData["sangvisFerri"]:
        loadData["sangvisFerri"][name] = {
        "action_point": 1,
        "attack_range": 1,
        "effective_range":{
            "far": [5,6],
            "middle":[3,4],
            "near":[1,2],
        },
        "kind": None,
        "magazine_capacity": 1,
        "max_damage": 1,
        "max_hp": 1,
        "min_damage": 1,
        }

with open("../Data/character_data.yaml", "w", encoding='utf-8') as f:
    yaml.dump(loadData, f, allow_unicode=True)