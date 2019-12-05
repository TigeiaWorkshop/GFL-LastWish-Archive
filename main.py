from Zero2_tool.mainMenu import *

#加载设置
with open("Data/setting.yaml", "r", encoding='utf-8') as f:
        setting = yaml.load(f.read(),Loader=yaml.FullLoader)
        window_x = setting['Screen_size_x']
        window_y =  setting['Screen_size_y']
        lang = setting['Language']

mainMenu(window_x,window_y,lang)