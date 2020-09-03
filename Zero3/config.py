import yaml

#加载设置配置文件
ZERO_DATA = None
with open("Save/setting.yaml", "r", encoding='utf-8') as f:
    ZERO_DATA = yaml.load(f.read(),Loader=yaml.FullLoader)
#获取设置配置文件
def get_setting(key=None):
    if key== None:
        return ZERO_DATA
    else:
        return ZERO_DATA[key]

#语言配置文件
ZERO_LANG = None
with open("Lang/{}.yaml".format(ZERO_DATA["Language"]), "r", encoding='utf-8') as f:
    ZERO_LANG = yaml.load(f.read(),Loader=yaml.FullLoader)

#获取语言配置文件
def get_lang(key=None):
    if key == None:
        return ZERO_LANG
    else:
        return ZERO_LANG[key]

#重新加载语言配置文件
def reload_lang():
    global ZERO_LANG
    with open("Lang/{}.yaml".format(ZERO_DATA["Language"]), "r", encoding='utf-8') as f:
        ZERO_LANG = yaml.load(f.read(),Loader=yaml.FullLoader)