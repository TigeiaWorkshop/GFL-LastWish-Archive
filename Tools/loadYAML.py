import yaml
#读取文件

filesToRead = {
    "1": "../Lang/English.yaml",
    "2": "../Lang/SimplifiedChinese.yaml",
    "3": "../Data/main_chapter/chapter1_dialogs_SimplifiedChinese.yaml",
    "4": "../Data/main_chapter/chapter1_map.yaml",
    "5": "../Assets/image/character/asval/skel/asval.skel.yaml",
    "6": "../Data/producersList.yaml"
}

for key,path in filesToRead.items():
    with open(path, "r", encoding='utf-8') as f:
        chapter_info = yaml.load(f.read(),Loader=yaml.FullLoader)

    with open(path, "w", encoding='utf-8') as f:
        yaml.dump(chapter_info, f, allow_unicode=True)