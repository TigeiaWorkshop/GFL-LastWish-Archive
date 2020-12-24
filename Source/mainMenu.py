# cython: language_level=3
from Source.scene import *
import os
import glob

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
        self.chapter_select = Zero.get_lang('Chapter')
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
        txt_y = (window_y-len(self.main_menu_txt["menu_workshop_choice"])*font_size)/2
        for key,txt in self.main_menu_txt["menu_workshop_choice"].items():
            self.main_menu_txt["menu_workshop_choice"][key] = Zero.fontRenderPro(txt,"enable",(txt_location,txt_y),Zero.get_standard_font_size("medium"))
            txt_y += font_size
        self.main_menu_txt["menu_workshop_choice"]["back"] = Zero.fontRenderPro(self.main_menu_txt["other"]["back"],"enable",(txt_location,txt_y),Zero.get_standard_font_size("medium"))
        #加载菜单章节选择页面的文字
        self.chapter_select.append(self.main_menu_txt["other"]["back"])
        txt_y = (window_y-len(self.chapter_select)*font_size)/2
        for i in range(len(self.chapter_select)):
            if i == 0 or i == len(self.chapter_select)-1:
                mode = "enable"
            else:
                mode = "disable"
            self.chapter_select[i] = Zero.fontRenderPro(self.chapter_select[i],mode,(txt_location,txt_y),Zero.get_standard_font_size("medium"))
            txt_y += font_size
        #数值初始化
        self.cover_alpha = 0
        self.menu_type = 0
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
        if createMode:
            self.workshop_files.append(self.main_menu_txt["other"]["new"])
        for path in glob.glob("Data/workshop/*"):
            data = Zero.loadConfig(path+"/info.yaml")
            self.workshop_files.append(data["name"][Zero.get_setting("Language")])
        self.workshop_files.append(self.main_menu_txt["other"]["back"])
        txt_location = int(screen_size[0]*2/3)
        font_size = Zero.get_standard_font_size("medium")*2
        txt_y = (screen_size[1]-len(self.workshop_files)*font_size)/2
        for i in range(len(self.workshop_files)):
            self.workshop_files[i] = Zero.fontRenderPro(self.workshop_files[i],"enable",(txt_location,txt_y),Zero.get_standard_font_size("medium"))
            txt_y += font_size
    def __draw_buttons(self,screen):
        i=0
        if self.menu_type == 0:
            for key in self.main_menu_txt["menu_main"]:
                if self.main_menu_txt["menu_main"][key].display(screen):
                    self.hover_sound_play_on = i
                i+=1
        elif self.menu_type == 1:
            for button in self.chapter_select:
                if button.display(screen):
                    self.hover_sound_play_on = i
                i+=1
        elif self.menu_type == 2:
            for key in self.main_menu_txt["menu_workshop_choice"]:
                if self.main_menu_txt["menu_workshop_choice"][key].display(screen):
                    self.hover_sound_play_on = i
                i+=1
        elif self.menu_type == 3:
            for button in self.workshop_files:
                if button.display(screen):
                    self.hover_sound_play_on = i
                i+=1
        #播放按钮的音效
        if self.last_hover_sound_play_on != self.hover_sound_play_on:
            self.hover_on_button_sound.play()
            self.last_hover_sound_play_on = self.hover_sound_play_on
    def display(self,screen):
        #开始播放背景视频
        self.videoCapture.start()
        # 主循环
        while self.isAlive:
            #背景视频
            self.videoCapture.display(screen)
            if self.menu_type == 2 and Zero.ifHover(self.chapter_select[0]):
                if self.cover_alpha < 255:
                    self.cover_alpha+=15
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
                        if os.path.exists("Save/save.yaml"):
                            SAVE = Zero.loadConfig("Save/save.yaml")
                            if SAVE["type"] == "battle":
                                SAVE["id"] = "head"
                                SAVE["dialog_options"] = {}
                            self.videoCapture.stop()
                            scene(SAVE["chapterType"],SAVE["chapterName"],screen,SAVE["type"],SAVE["id"],SAVE["dialog_options"])
                            self.videoCapture = self.videoCapture.clone()
                            self.videoCapture.start()
                            #是否可以继续游戏了（save文件是否被创建）
                            if os.path.exists("Save/save.yaml") and self.continueButtonIsOn == False:
                                self.main_menu_txt["menu_main"]["0_continue"] = Zero.fontRenderPro(Zero.get_lang("MainMenu")["menu_main"]["0_continue"],"enable",self.main_menu_txt["menu_main"]["0_continue"].get_pos(),Zero.get_standard_font_size("medium"))
                                self.continueButtonIsOn = True
                            elif not os.path.exists("Save/save.yaml") and self.continueButtonIsOn == True:
                                self.main_menu_txt["menu_main"]["0_continue"] = Zero.fontRenderPro(Zero.get_lang("MainMenu")["menu_main"]["0_continue"],"disable",self.main_menu_txt["menu_main"]["0_continue"].get_pos(),Zero.get_standard_font_size("medium"))
                                self.continueButtonIsOn = False
                        else:
                            #raise Exception('ZeroEngine-Error: The save.yaml is not exist')
                            pass
                    #选择章节
                    elif Zero.ifHover(self.main_menu_txt["menu_main"]["1_chooseChapter"]):
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
                    #7_exit
                    elif Zero.ifHover(self.main_menu_txt["menu_main"]["7_exit"]):
                        self.videoCapture.stop()
                        Zero.display.quit()
                #选择主线章节
                elif self.menu_type == 1:
                    for i in range(len(self.chapter_select)):
                        if i == len(self.chapter_select)-1 and Zero.ifHover(self.chapter_select[-1]):
                            self.menu_type = 0
                        #章节选择
                        elif Zero.ifHover(self.chapter_select[i]) and i==0:
                            self.videoCapture.stop()
                            scene("main_chapter","chapter"+str(i+1),screen)
                            self.videoCapture = self.videoCapture.clone()
                            self.videoCapture.start()
                            #是否可以继续游戏了（save文件是否被创建）
                            if os.path.exists("Save/save.yaml") and self.continueButtonIsOn == False:
                                self.main_menu_txt["menu_1"]["text0_continue"] = Zero.fontRenderPro(Zero.get_lang("MainMenu")["menu_1"]["text0_continue"],"enable",self.main_menu_txt["menu_1"]["text0_continue"].get_pos(),Zero.get_standard_font_size("medium"))
                                self.continueButtonIsOn = True
                            elif not os.path.exists("Save/save.yaml") and self.continueButtonIsOn == True:
                                self.main_menu_txt["menu_1"]["text0_continue"] = Zero.fontRenderPro(Zero.get_lang("MainMenu")["menu_1"]["text0_continue"],"disable",self.main_menu_txt["menu_1"]["text0_continue"].get_pos(),Zero.get_standard_font_size("medium"))
                                self.continueButtonIsOn = False
                            break
                #选择创意工坊选项
                elif self.menu_type == 2:
                    if Zero.ifHover(self.main_menu_txt["menu_workshop_choice"]["0_play"]):
                        self.__reload_workshop_files_list(screen.get_size(),False)
                        self.menu_type = 3
                    elif Zero.ifHover(self.main_menu_txt["menu_workshop_choice"]["1_mapCreator"]):
                        self.videoCapture.stop()
                        mapCreator("main_chapter","chapter1",screen)
                        self.videoCapture = self.videoCapture.clone()
                        self.videoCapture.start()
                    elif Zero.ifHover(self.main_menu_txt["menu_workshop_choice"]["2_dialogCreator"]):
                        self.videoCapture.stop()
                        dialogCreator("main_chapter","chapter1",screen,"dialog_before_battle")
                        self.videoCapture = self.videoCapture.clone()
                        self.videoCapture.start()
                    elif Zero.ifHover(self.main_menu_txt["menu_workshop_choice"]["back"]):
                        self.menu_type = 0
                elif self.menu_type == 3:
                    if Zero.ifHover(self.workshop_files[-1]):
                        self.menu_type = 2
            Zero.display.flip()