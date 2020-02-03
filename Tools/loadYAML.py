import yaml
#读取地图
path = "../lang/en_us.yaml"
with open(path, "r", encoding='utf-8') as f:
    chapter_info = yaml.load(f.read(),Loader=yaml.FullLoader)
    chapter = chapter_info["chapter"]

with open(path, "w", encoding='utf-8') as f:
    chapter_info["chapter"] = chapter
    yaml.dump(chapter_info, f, allow_unicode=True)