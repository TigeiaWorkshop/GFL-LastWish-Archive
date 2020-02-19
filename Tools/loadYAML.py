import yaml
#读取地图
path = "../lang/zh_cn.yaml"
#path = "../Data/main_chapter/chapter1_map.yaml"

with open(path, "r", encoding='utf-8') as f:
    chapter_info = yaml.load(f.read(),Loader=yaml.FullLoader)

with open(path, "w", encoding='utf-8') as f:
    yaml.dump(chapter_info, f, allow_unicode=True)