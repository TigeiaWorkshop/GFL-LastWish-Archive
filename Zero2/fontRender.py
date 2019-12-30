import pygame

def fontRender(txt,color,mode=True):
    class the_text:
        def __init__(self, n, b):
            self.n = n
            self.b = b
            
    #文字设定
    normal_font = pygame.font.SysFont('simsunnsimsun',50)
    big_font = pygame.font.SysFont('simsunnsimsun',75)

    if color == "gray" or color == "grey" or color == "disable":
        text_out = the_text(normal_font.render(txt, mode, (105,105,105)),big_font.render(txt, mode, (105,105,105)))
    elif color == "white" or color == "enable":
        text_out = the_text(normal_font.render(txt, mode, (255, 255, 255)),big_font.render(txt, mode, (255, 255, 255)))
    else:
        text_out = the_text(normal_font.render(txt, mode, color),big_font.render(txt, mode, color))
    
    return text_out
