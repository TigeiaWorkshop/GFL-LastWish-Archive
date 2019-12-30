import pygame
import cv2
pygame.init()
cap = cv2.VideoCapture('../Assets/movie/SquadAR.mp4')
ret, img = cap.read()
img = cv2.transpose(img)



screen = pygame.display.set_mode((192, 108))
surface = pygame.surface.Surface((img.shape[0], img.shape[1]))

while True:
    ret, img = cap.read()
    img = cv2.transpose(img)
    pygame.surfarray.blit_array(surface, img)
    screen.blit(surface, (0,0))
    pygame.display.flip()

pygame.quit()
