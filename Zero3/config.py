import yaml

#加载设置配置文件
DATA = None
with open("Save/setting.yaml", "r", encoding='utf-8') as f:
    DATA = yaml.load(f.read(),Loader=yaml.FullLoader)
#获取设置配置文件
def get_setting(key=None):
    if key== None:
        return DATA
    else:
        return DATA[key]

#语言配置文件
LANG = None
with open("Lang/{}.yaml".format(DATA["Language"]), "r", encoding='utf-8') as f:
    LANG = yaml.load(f.read(),Loader=yaml.FullLoader)

#获取语言配置文件
def get_lang(key=None):
    if key == None:
        return LANG
    else:
        return LANG[key]

#重新加载语言配置文件
def reload_lang():
    global LANG
    with open("Lang/{}.yaml".format(DATA["Language"]), "r", encoding='utf-8') as f:
        LANG = yaml.load(f.read(),Loader=yaml.FullLoader)