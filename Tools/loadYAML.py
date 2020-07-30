import yaml
import glob

filesToRead = []

#读取文件
for path in glob.glob(r'../Lang/*.yaml'):
    filesToRead.append(path)
for path in glob.glob(r'../Save/*.yaml'):
    filesToRead.append(path)
for path in glob.glob(r'../Data/*.yaml'):
    filesToRead.append(path)
for path in glob.glob(r'../Data/main_chapter/*.yaml'):
    filesToRead.append(path)

for path in filesToRead:
    with open(path, "r", encoding='utf-8') as f:
        chapter_info = yaml.load(f.read(),Loader=yaml.FullLoader)

    with open(path, "w", encoding='utf-8') as f:
        yaml.dump(chapter_info, f, allow_unicode=True)