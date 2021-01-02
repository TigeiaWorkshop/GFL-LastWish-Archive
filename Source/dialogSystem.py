from .battleSystem import *

class DialogSystem(linpg.DialogSystem):
    def __init__(self):
        DialogSystem.__init__(self)
    #保存数据
    def save_process(self):
        DataTmp = {
            "chapterType": self.chapterType,
            "chapterId": self.chapterId,
            "type": self.part,
            "id": self.dialogId,
            "dialog_options": self.dialog_options,
            "collection_name": self.collection_name
        }
        #别忘了看看Save文件夹是不是都不存在
        if not os.path.exists("Save"):
            os.makedirs("Save")
        #存档数据
        linpg.saveConfig("Save/save.yaml",DataTmp)
        #检查global.yaml配置文件
        if not os.path.exists("Save/global.yaml"):
            DataTmp = {"chapter_unlocked":1}
            linpg.saveConfig("Save/global.yaml",DataTmp)