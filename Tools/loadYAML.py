import yaml
#读取地图
#path = "../lang/en_us.yaml"
path = "../Data/main_chapter/chapter1_dialogs_zh_cn.yaml"
info = "battle_info"
with open(path, "r", encoding='utf-8') as f:
    chapter_info = yaml.load(f.read(),Loader=yaml.FullLoader)
    chapter = chapter_info[info]

with open(path, "w", encoding='utf-8') as f:
    chapter_info[info] = chapter
    yaml.dump(chapter_info, f, allow_unicode=True)