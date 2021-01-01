# cython: language_level=3
from .scene import *

class MainMenu:
    def __init__(self,screen):
        #获取屏幕的尺寸
        window_x,window_y = screen.get_size()
        #载入页面 - 渐入
        dispaly_loading_screen(screen,0,250,2)
        #是否主菜单在播放
        self.isAlive = True
        #窗口标题图标
        Zero.display.set_icon("Assets/image/UI/icon.png")
        Zero.display.set_caption(Zero.get_lang('GameTitle'))
        #设置引擎的标准文字大小
        Zero.set_standard_font_size(int(window_x/40),"medium")
        #修改控制台的位置
        Zero.console.set_pos(window_x*0.1,window_y*0.8)
        self.main_menu_txt = Zero.get_lang('MainMenu')
        #选项模块
        self.settingUI = Zero.SettingContoller(window_x,window_y,Zero.get_lang("SettingUI"))
        #当前可用的菜单选项
        disabled_option = ["6_developer_team","2_dlc","4_collection"]
        if not os.path.exists("Save/save.yaml"):
            disabled_option.append("text0_continue")
            self.continueButtonIsOn = False
        else:
            self.continueButtonIsOn = True
        #加载主菜单页面的文字设置
        txt_location = int(window_x*2/3)
        font_size = Zero.get_standard_font_size("medium")*2
        txt_y = (window_y-len(self.main_menu_txt["menu_main"])*font_size)/2
        for key,txt in self.main_menu_txt["menu_main"].items():
            if key not in disabled_option:
                mode = "enable"
            else:
                mode = "disable"
            self.main_menu_txt["menu_main"][key] = Zero.fontRenderPro(txt,mode,(txt_location,txt_y),Zero.get_standard_font_size("medium"))
            txt_y += font_size
        #加载创意工坊选择页面的文字
        self.main_menu_txt["menu_workshop_choice"]["back"] = self.main_menu_txt["other"]["back"]
        txt_y = (window_y-len(self.main_menu_txt["menu_workshop_choice"])*font_size)/2
        for key,txt in self.main_menu_txt["menu_workshop_choice"].items():
            self.main_menu_txt["menu_workshop_choice"][key] = Zero.fontRenderPro(txt,"enable",(txt_location,txt_y),Zero.get_standard_font_size("medium"))
            txt_y += font_size
        #数值初始化
        self.cover_alpha = 0
        self.menu_type = 0
        self.chapter_select = []
        self.workshop_files_text = []
        self.current_selected_workshop_collection = None
        self.exit_confirm_menu = Zero.Message(self.main_menu_txt["other"]["tip"],self.main_menu_txt["other"]["exit_confirm"],(self.main_menu_txt["other"]["confirm"],self.main_menu_txt["other"]["deny"]),True,return_button=1,escape_button=1)
        #关卡选择的封面
        self.cover_img = Zero.loadImg("Assets/image/covers/chapter1.png",window_x,window_y)
        #音效
        self.click_button_sound = Zero.loadSound("Assets/sound/ui/main_menu_click_button.ogg",Zero.get_setting("Sound","sound_effects")/100.0)
        self.hover_on_button_sound = Zero.loadSound("Assets/sound/ui/main_menu_hover_on_button.ogg",Zero.get_setting("Sound","sound_effects")/100.0)
        self.hover_sound_play_on = None
        self.last_hover_sound_play_on = None
        #加载主菜单背景
        self.videoCapture = Zero.VedioFrame("Assets/movie/SquadAR.mp4",window_x,window_y,True,True,(32,103),Zero.get_setting("Sound","background_music")/100.0)
        #载入页面 - 渐出
        dispaly_loading_screen(screen,250,0,-2)
    #当前在Data/workshop文件夹中可以读取的文件夹的名字（font的形式）
    def __reload_workshop_files_list(self,screen_size,createMode=False):
        self.workshop_files = []
        self.workshop_files_text = []
        if createMode:
            self.workshop_files.append(self.main_menu_txt["other"]["new_collection"])
        for path in glob.glob("Data/workshop/*"):
            data = Zero.loadConfig(path+"/info.yaml")
            filePath,fileName = os.path.split(path)
            self.workshop_files_text.append(fileName)
            self.workshop_files.append(data["title"][Zero.get_setting("Language")])
        self.workshop_files.append(self.main_menu_txt["other"]["back"])
        txt_location = int(screen_size[0]*2/3)
        txt_y = (screen_size[1]-len(self.workshop_files)*Zero.get_standard_font_size("medium")*2)/2
        for i in range(len(self.workshop_files)):
            self.workshop_files[i] = Zero.fontRenderPro(self.workshop_files[i],"enable",(txt_location,txt_y),Zero.get_standard_font_size("medium"))
            txt_y += Zero.get_standard_font_size("medium")*2
    #重新加载章节选择菜单的选项
    def __reload_chapter_select_list(self,screen_size,chapterType="main_chapter",createMode=False,fileType="dialogs"):
        self.chapter_select = []
        if createMode:
            self.chapter_select.append(self.main_menu_txt["other"]["new_chapter"])
        chapterTitle = Zero.get_lang("Battle_UI","numChapter")
        if fileType == "dialogs":
            fileLocation = "Data/{0}/*_dialogs_{1}.yaml".format(chapterType,Zero.get_setting("Language")) if chapterType == "main_chapter" else "Data/{0}/{1}/*_dialogs_{2}.yaml".format(chapterType,self.current_selected_workshop_collection,Zero.get_setting("Language"))
        elif fileType == "map":
            fileLocation = "Data/{0}/*_map.yaml".format(chapterType) if chapterType == "main_chapter" else "Data/{0}/{1}/*_map.yaml".format(chapterType,self.current_selected_workshop_collection)
        else:
            raise Exception('ZeroEngine-Error: fileType="{}" is not supported!'.format(fileType))
        #历遍路径下的所有章节文件
        for path in glob.glob(fileLocation):
            chapterId = self.__find_chapter_id(path)
            if fileType == "dialogs":
                titleName = Zero.loadConfig(path,"title")
            else:
                guessDialogFilePath = "Data/{0}/chapter{1}_dialogs_{2}.yaml".format(chapterType,chapterId,Zero.get_setting("Language")) if chapterType == "main_chapter" else "Data/{0}/{1}/chapter{2}_dialogs_{3}.yaml".format(chapterType,self.current_selected_workshop_collection,chapterId,Zero.get_setting("Language"))
                if os.path.exists(guessDialogFilePath):
                    titleName = Zero.loadConfig(guessDialogFilePath,"title")
                else:
                    titleName = ""
            if chapterId < 11:
                if chapterId > 0 or Zero.console.get_events("dev"):
                    if len(titleName) > 0:
                        self.chapter_select.append(chapterTitle.format(Zero.get_lang("Numbers")[chapterId])+": "+titleName)
                    else:
                        self.chapter_select.append(chapterTitle.format(Zero.get_lang("Numbers")[chapterId]))
            else:
                self.chapter_select.append(chapterTitle.format(chapterId)+": "+titleName)
        #将返回按钮放到菜单列表中
        self.chapter_select.append(self.main_menu_txt["other"]["back"])
        txt_y = (screen_size[1]-len(self.chapter_select)*Zero.get_standard_font_size("medium")*2)/2
        txt_x = int(screen_size[0]*2/3)
        #将菜单列表中的文字转换成文字surface
        for i in range(len(self.chapter_select)):
            """
            if i == 0 or i == len(self.chapter_select)-1:
                mode = "enable"
            else:
                mode = "disable"
            """
            mode = "enable"
            self.chapter_select[i] = Zero.fontRenderPro(self.chapter_select[i],mode,(txt_x,txt_y),Zero.get_standard_font_size("medium"))
            txt_y += Zero.get_standard_font_size("medium")*2
    def __draw_buttons(self,screen):
        i=0
        #主菜单
        if self.menu_type == 0:
            for key in self.main_menu_txt["menu_main"]:
                if self.main_menu_txt["menu_main"][key].display(screen):
                    self.hover_sound_play_on = i
                i+=1
        #选择主线的章节
        elif self.menu_type == 1:
            for button in self.chapter_select:
                if button.display(screen):
                    self.hover_sound_play_on = i
                i+=1
        #创意工坊选择菜单
        elif self.menu_type == 2:
            for key in self.main_menu_txt["menu_workshop_choice"]:
                if self.main_menu_txt["menu_workshop_choice"][key].display(screen):
                    self.hover_sound_play_on = i
                i+=1
        #展示合集 （3-游玩，4-地图编辑器，5-对话编辑器）
        elif 5 >= self.menu_type >= 3:
            for button in self.workshop_files:
                if button.display(screen):
                    self.hover_sound_play_on = i
                i+=1
        #选择章节（6-游玩，7-地图编辑器，8-对话编辑器）
        elif 8 >= self.menu_type >= 6:
            for button in self.chapter_select:
                if button.display(screen):
                    self.hover_sound_play_on = i
                i+=1
        #播放按钮的音效
        if self.last_hover_sound_play_on != self.hover_sound_play_on:
            self.hover_on_button_sound.play()
            self.last_hover_sound_play_on = self.hover_sound_play_on
    def __create_new_file(self):
        #如果创意工坊的文件夹目录不存在，则创建一个
        if not os.path.exists("Data/workshop"):
            os.makedirs("Data/workshop")
        #生成名称
        fileDefaultName = "example"
        avoidDuplicateId = 1
        fileName = fileDefaultName
        #循环确保名称不重复
        while os.path.exists("Data/workshop/{}".format(fileName)):
            fileName = fileDefaultName + " ({})".format(avoidDuplicateId)
            avoidDuplicateId += 1
        #创建文件夹
        os.makedirs("Data/workshop/{}".format(fileName))
        #生成要储存的数据
        example_info_data = {
            "title":{"SimplifiedChinese": "演示版本","English": "Example Chapter"},
            "author": "Put your name here",
            "link": "https://whateve you want, maybe your github link",
            "version": "0.0 (this will be loaded as string, just a reference)"
        }
        #储存数据
        Zero.saveConfig("Data/workshop/{}/info.yaml".format(fileName),example_info_data)
    #创建新的对话文件
    def __create_new_dialog(self):
        chapterId = len(glob.glob("Data/workshop/{0}/*_dialogs_{1}.yaml".format(self.current_selected_workshop_collection,Zero.get_setting("Language"))))+1
        shutil.copyfile("Data/chapter_dialogs_example.yaml","Data/workshop/{0}/chapter{1}_dialogs_{2}.yaml".format(self.current_selected_workshop_collection,chapterId,Zero.get_setting("Language")))
    #创建新的地图文件
    def __create_new_map(self):
        chapterId = len(glob.glob("Data/workshop/{0}/*_map.yaml".format(self.current_selected_workshop_collection)))+1
        shutil.copyfile("Data/chapter_map_example.yaml","Data/workshop/{0}/chapter{1}_map.yaml".format(self.current_selected_workshop_collection,chapterId))
    #根据路径判定章节的Id
    def __find_chapter_id(self,path):
        filePath,fileName = os.path.split(path)
        if fileName[0:7] == "chapter":
            return int(fileName[7:fileName.index('_')])
        else:
            raise Exception('ZeroEngine-Error: Cannot find the id of chapter because the file is not properly named!')
    #加载章节
    def __load_scene(self,chapterType,chapterId,screen):
        self.videoCapture.stop()
        collection_name = None if chapterType == "main_chapter" else self.current_selected_workshop_collection
        dialog(chapterType,chapterId,screen,"dialog_before_battle",collection_name)
        if not Zero.pause_menu.checkIfBackToMainMenu():
            battle(chapterType,chapterId,screen,collection_name)
        else:
            return
        if not Zero.pause_menu.checkIfBackToMainMenu():
            dialog(chapterType,chapterId,screen,"dialog_after_battle",collection_name)
        self.__reset_menu()
    def __continue_scene(self,screen):
        self.videoCapture.stop()
        if os.path.exists("Save/save.yaml"):
            SAVE = Zero.loadConfig("Save/save.yaml")
            startPoint = SAVE["type"]
            if startPoint == "dialog_before_battle":
                dialog(None,None,screen,None)
                if not Zero.pause_menu.checkIfBackToMainMenu():
                    battle(SAVE["chapterType"],SAVE["chapterId"],screen,SAVE["collection_name"])
                else:
                    return
                if not Zero.pause_menu.checkIfBackToMainMenu():
                    dialog(SAVE["chapterType"],SAVE["chapterId"],screen,"dialog_after_battle",SAVE["collection_name"])
            elif startPoint == "battle":
                battle(None,None,screen,)
                if not Zero.pause_menu.checkIfBackToMainMenu():
                    dialog(SAVE["chapterType"],SAVE["chapterId"],screen,"dialog_after_battle",SAVE["collection_name"])
            elif startPoint == "dialog_after_battle":
                dialog(None,None,screen,None)
        else:
            #raise Exception('ZeroEngine-Error: The save.yaml is not exist')
            pass
        self.__reset_menu()
    #更新主菜单的部分元素
    def __reset_menu(self):
        self.videoCapture = self.videoCapture.clone()
        self.videoCapture.start()
        #是否可以继续游戏了（save文件是否被创建）
        if os.path.exists("Save/save.yaml") and self.continueButtonIsOn == False:
            self.main_menu_txt["menu_main"]["0_continue"] = Zero.fontRenderPro(Zero.get_lang("MainMenu")["menu_main"]["0_continue"],"enable",self.main_menu_txt["menu_main"]["0_continue"].get_pos(),Zero.get_standard_font_size("medium"))
            self.continueButtonIsOn = True
        elif not os.path.exists("Save/save.yaml") and self.continueButtonIsOn == True:
            self.main_menu_txt["menu_main"]["0_continue"] = Zero.fontRenderPro(Zero.get_lang("MainMenu")["menu_main"]["0_continue"],"disable",self.main_menu_txt["menu_main"]["0_continue"].get_pos(),Zero.get_standard_font_size("medium"))
            self.continueButtonIsOn = False
    def display(self,screen):
        #开始播放背景视频
        self.videoCapture.start()
        # 主循环
        while self.isAlive:
            #背景视频
            self.videoCapture.display(screen)
            if self.menu_type == 1 and Zero.ifHover(self.chapter_select[0]):
                if self.cover_alpha < 255:
                    self.cover_alpha += 15
            elif self.cover_alpha >= 0:
                self.cover_alpha-=15
            #如果图片的透明度大于10则展示图片
            if self.cover_alpha > 10:
                self.cover_img.set_alpha(self.cover_alpha)
                Zero.drawImg(self.cover_img, (0,0),screen)
            #菜单选项
            self.__draw_buttons(screen)
            #展示设置UI
            if self.settingUI.display(screen) == True:
                self.click_button_sound.set_volume(Zero.get_setting("Sound","sound_effects")/100.0)
                self.hover_on_button_sound.set_volume(Zero.get_setting("Sound","sound_effects")/100.0)
                self.videoCapture.set_volume(Zero.get_setting("Sound","background_music")/100.0)
            #获取输入事件
            events = Zero.get_pygame_events()
            #展示控制台
            Zero.console.display(screen,events)
            #判断按键
            if Zero.controller.get_event(events) == "comfirm" and self.settingUI.ifDisplay != True:
                self.click_button_sound.play()
                #主菜单
                if self.menu_type == 0:
                    #继续游戏
                    if Zero.ifHover(self.main_menu_txt["menu_main"]["0_continue"]):
                        self.__continue_scene(screen)
                    #选择章节
                    elif Zero.ifHover(self.main_menu_txt["menu_main"]["1_chooseChapter"]):
                        #加载菜单章节选择页面的文字
                        self.__reload_chapter_select_list(screen.get_size())
                        self.menu_type = 1
                    #dlc
                    elif Zero.ifHover(self.main_menu_txt["menu_main"]["2_dlc"]):
                        pass
                    #创意工坊
                    elif Zero.ifHover(self.main_menu_txt["menu_main"]["3_workshop"]):
                        self.menu_type = 2
                    #收集物
                    elif Zero.ifHover(self.main_menu_txt["menu_main"]["4_collection"]):
                        pass
                    #设置
                    elif Zero.ifHover(self.main_menu_txt["menu_main"]["5_setting"]):
                        self.settingUI.ifDisplay = True
                    #制作组
                    elif Zero.ifHover(self.main_menu_txt["menu_main"]["6_developer_team"]):
                        pass
                    #退出
                    elif Zero.ifHover(self.main_menu_txt["menu_main"]["7_exit"]) and self.exit_confirm_menu.draw() == 0:
                        self.videoCapture.stop()
                        Zero.display.quit()
                #选择主线章节
                elif self.menu_type == 1:
                    if Zero.ifHover(self.chapter_select[-1]):
                        self.menu_type = 0
                    else:
                        for i in range(len(self.chapter_select)-1):
                            #章节选择
                            if Zero.ifHover(self.chapter_select[i]):
                                self.__load_scene("main_chapter",i+1,screen)
                                break
                #选择创意工坊选项
                elif self.menu_type == 2:
                    if Zero.ifHover(self.main_menu_txt["menu_workshop_choice"]["0_play"]):
                        self.__reload_workshop_files_list(screen.get_size(),False)
                        self.menu_type = 3
                    elif Zero.ifHover(self.main_menu_txt["menu_workshop_choice"]["1_mapCreator"]):
                        self.__reload_workshop_files_list(screen.get_size(),True)
                        self.menu_type = 4
                    elif Zero.ifHover(self.main_menu_txt["menu_workshop_choice"]["2_dialogCreator"]):
                        self.__reload_workshop_files_list(screen.get_size(),True)
                        self.menu_type = 5
                    elif Zero.ifHover(self.main_menu_txt["menu_workshop_choice"]["back"]):
                        self.menu_type = 0
                #创意工坊-选择想要游玩的合集
                elif self.menu_type == 3:
                    if Zero.ifHover(self.workshop_files[-1]):
                        self.menu_type = 2
                    else:
                        for i in range(len(self.workshop_files)-1):
                            #章节选择
                            if Zero.ifHover(self.workshop_files[i]):
                                self.current_selected_workshop_collection = self.workshop_files_text[i]
                                self.__reload_chapter_select_list(screen.get_size(),"workshop")
                                self.menu_type = 6
                                break
                #创意工坊-选择想要编辑地图的合集
                elif self.menu_type == 4:
                    #新建合集
                    if Zero.ifHover(self.workshop_files[0]):
                        self.__create_new_file()
                        self.__reload_workshop_files_list(screen.get_size(),True)
                    #返回创意工坊选项菜单
                    elif Zero.ifHover(self.workshop_files[-1]):
                        self.menu_type = 2
                    else:
                        for i in range(1,len(self.workshop_files)-1):
                            #章节选择
                            if Zero.ifHover(self.workshop_files[i]):
                                self.current_selected_workshop_collection = self.workshop_files_text[i-1]
                                self.__reload_chapter_select_list(screen.get_size(),"workshop",True,"map")
                                self.menu_type = 7
                                break
                #创意工坊-选择想要编辑对话的合集
                elif self.menu_type == 5:
                    #新建合集
                    if Zero.ifHover(self.workshop_files[0]):
                        self.__create_new_file()
                        self.__reload_workshop_files_list(screen.get_size(),True)
                    #返回创意工坊选项菜单
                    elif Zero.ifHover(self.workshop_files[-1]):
                        self.menu_type = 2
                    else:
                        for i in range(1,len(self.workshop_files)-1):
                            #章节选择
                            if Zero.ifHover(self.workshop_files[i]):
                                self.current_selected_workshop_collection = self.workshop_files_text[i-1]
                                self.__reload_chapter_select_list(screen.get_size(),"workshop",True)
                                self.menu_type = 8
                                break
                #创意工坊-选择当前合集想要游玩的关卡
                elif self.menu_type == 6:
                    if Zero.ifHover(self.chapter_select[-1]):
                        self.menu_type = 3
                    else:
                        for i in range(len(self.chapter_select)-1):
                            #章节选择
                            if Zero.ifHover(self.chapter_select[i]):
                                self.__load_scene("workshop",i+1,screen)
                                break
                #创意工坊-选择当前合集想要编辑地图的关卡
                elif self.menu_type == 7:
                    if Zero.ifHover(self.chapter_select[0]):
                        self.__create_new_map()
                        self.__reload_chapter_select_list(screen.get_size(),"workshop",True,"map")
                    elif Zero.ifHover(self.chapter_select[-1]):
                        self.menu_type = 4
                    else:
                        for i in range(1,len(self.chapter_select)-1):
                            #章节选择
                            if Zero.ifHover(self.chapter_select[i]):
                                self.videoCapture.stop()
                                mapCreator("workshop",i,screen,self.current_selected_workshop_collection)
                                self.videoCapture = self.videoCapture.clone()
                                self.videoCapture.start()
                                break
                #创意工坊-选择当前合集想要编辑对话的关卡
                elif self.menu_type == 8:
                    if Zero.ifHover(self.chapter_select[0]):
                        self.__create_new_dialog()
                        self.__reload_chapter_select_list(screen.get_size(),"workshop",True)
                    elif Zero.ifHover(self.chapter_select[-1]):
                        self.menu_type = 5
                    else:
                        for i in range(1,len(self.chapter_select)-1):
                            #章节选择
                            if Zero.ifHover(self.chapter_select[i]):
                                self.videoCapture.stop()
                                dialogCreator("workshop",i,screen,"dialog_before_battle",self.current_selected_workshop_collection)
                                self.videoCapture = self.videoCapture.clone()
                                self.videoCapture.start()
                                break
            Zero.display.flip()