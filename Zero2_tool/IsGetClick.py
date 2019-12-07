import pygame
def IsGetClick(the_object,the_object_position):
    mouse_x,mouse_y=pygame.mouse.get_pos()
    if the_object_position[0]<mouse_x<the_object_position[0]+the_object.get_width() and the_object_position[1]<mouse_y<the_object_position[1]+the_object.get_height():
        return True
    else:
        return False
