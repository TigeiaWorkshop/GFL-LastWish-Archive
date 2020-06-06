from Zero2.basic import *
class RoundSwitch:
    def __init__(self,window_x,window_y,battleUiTxt):
        self.lineRedDown = loadImg("Assets/image/UI/lineRed.png",window_x,window_y/50)
        self.lineRedUp = pygame.transform.rotate(self.lineRedDown, 180)
        self.lineGreenDown = loadImg("Assets/image/UI/lineGreen.png",window_x,window_y/50)
        self.lineGreenUp = pygame.transform.rotate(self.lineGreenDown, 180)
        self.baseImg = loadImg("Assets/image/UI/roundSwitchBase.png",window_x,window_y/5)
        self.baseImg.set_alpha(0)
        self.x = -window_x
        self.y = int((window_y - self.baseImg.get_height())/2)
        self.y2 = self.y+self.baseImg.get_height()-self.lineRedDown.get_height()
        self.baseAlphaUp = True
        self.TxtAlphaUp = True
        self.idleTime = 60
        self.now_total_rounds_text = battleUiTxt["numRound"]
        self.now_total_rounds_surface = None
        self.your_round_txt_surface = fontRender(battleUiTxt["yourRound"], "white",window_x/36)
        self.your_round_txt_surface.set_alpha(0)
        self.enemy_round_txt_surface = fontRender(battleUiTxt["enemyRound"], "white",window_x/36)
        self.enemy_round_txt_surface.set_alpha(0)
    def display(self,screen,whose_round,total_rounds):
        if self.now_total_rounds_surface == None:
            self.now_total_rounds_surface = fontRender(self.now_total_rounds_text.replace("NaN",str(total_rounds)), "white",screen.get_width()/38)
            self.now_total_rounds_surface.set_alpha(0)
        if self.baseAlphaUp == True:
            alphaTemp = self.baseImg.get_alpha()
            if alphaTemp > 250:
                if self.x >= 0:
                    self.baseAlphaUp = False
            else:
                self.baseImg.set_alpha(alphaTemp+5)
            
        elif self.baseAlphaUp == False:
            if self.TxtAlphaUp == True:
                alphaTemp = self.now_total_rounds_surface.get_alpha()
                if alphaTemp < 250:
                    self.now_total_rounds_surface.set_alpha(alphaTemp+10)
                else:
                    if whose_round == "playerToSangvisFerris":
                        alphaTemp = self.enemy_round_txt_surface.get_alpha()
                        if alphaTemp < 250:
                            self.enemy_round_txt_surface.set_alpha(alphaTemp+10)
                        else:
                            self.TxtAlphaUp = False
                    if whose_round == "sangvisFerrisToPlayer":
                        alphaTemp = self.your_round_txt_surface.get_alpha()
                        if alphaTemp < 250:
                            self.your_round_txt_surface.set_alpha(alphaTemp+10)
                        else:
                            self.TxtAlphaUp = False
            elif self.idleTime > 0:
                self.idleTime -= 1
            else:
                alphaTemp = self.baseImg.get_alpha()
                if alphaTemp > 0:
                    alphaTemp -= 10
                    self.baseImg.set_alpha(alphaTemp)
                    self.now_total_rounds_surface.set_alpha(alphaTemp)
                    if whose_round == "playerToSangvisFerris":
                        self.lineRedUp.set_alpha(alphaTemp)
                        self.lineRedDown.set_alpha(alphaTemp)
                        self.enemy_round_txt_surface.set_alpha(alphaTemp)
                    elif whose_round == "sangvisFerrisToPlayer":
                        self.lineGreenUp.set_alpha(alphaTemp)
                        self.lineGreenDown.set_alpha(alphaTemp)
                        self.your_round_txt_surface.set_alpha(alphaTemp)
                else:
                    if whose_round == "playerToSangvisFerris":
                        self.lineRedUp.set_alpha(255)
                        self.lineRedDown.set_alpha(255)
                    elif whose_round == "sangvisFerrisToPlayer":
                        self.lineGreenUp.set_alpha(255)
                        self.lineGreenDown.set_alpha(255)
                    self.x = -screen.get_width()
                    self.baseAlphaUp = True
                    self.TxtAlphaUp = True
                    self.idleTime = 60
                    self.now_total_rounds_surface = None
                    return True

        if self.x < 0:
            self.x += screen.get_width()/35

        drawImg(self.baseImg,(0,self.y),screen)
        drawImg(self.now_total_rounds_surface,(screen.get_width()/2-self.now_total_rounds_surface.get_width(),self.y+screen.get_width()/36),screen)
        if whose_round == "playerToSangvisFerris":
            drawImg(self.lineRedUp,(abs(self.x),self.y),screen)
            drawImg(self.lineRedDown,(self.x,self.y2),screen)
            drawImg(self.enemy_round_txt_surface,(screen.get_width()/2,self.y+screen.get_width()/18),screen)
        elif whose_round == "sangvisFerrisToPlayer":
            drawImg(self.lineGreenUp,(abs(self.x),self.y),screen)
            drawImg(self.lineGreenDown,(self.x,self.y2),screen)
            drawImg(self.your_round_txt_surface,(screen.get_width()/2,self.y+screen.get_width()/18),screen)
            
        return False

