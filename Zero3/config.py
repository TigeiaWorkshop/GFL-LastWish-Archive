import yaml
import os

#加载设置配置文件
ZERO_DATA = None
#如果配置文件setting.yaml存在
if os.path.exists("Save/setting.yaml"):
    with open("Save/setting.yaml", "r", encoding='utf-8') as f:
        ZERO_DATA = yaml.load(f.read(),Loader=yaml.FullLoader)
#如果不存在就创建一个
else:
    #导入local,查看默认语言
    import locale
    ZERO_DATA = {
        "Antialias": True,
        "FPS": 60,
        "Font": "MicrosoftYaHei-2",
        "FontType": "custom",
        "Language": locale.getdefaultlocale(),
        "MouseIconWidth": 18,
        "MouseMoveSpeed": 30,
        "ReadingSpeed": 0.5,
        "Screen_size_x": 1920,
        "Screen_size_y": 1080,
        "Sound":{
            "background_music": 100,
            "sound_effects": 100,
            "sound_environment": 100,
        }
    }
    if ZERO_DATA["Language"][0] == "zh_CN":
        ZERO_DATA["Language"] = "SimplifiedChinese"
    else:
        ZERO_DATA["Language"] = "English"
    #别忘了看看Save文件夹是不是都不存在
    if not os.path.exists("Save"):
        os.makedirs("Save")
    with open("Save/setting.yaml", "w", encoding='utf-8') as f:
        yaml.dump(ZERO_DATA, f, allow_unicode=True)

#获取设置配置文件
def get_setting(key=None,key2=None):
    if key == None:
        return ZERO_DATA
    elif key2 == None:
        return ZERO_DATA[key]
    else:
        return ZERO_DATA[key][key2]

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