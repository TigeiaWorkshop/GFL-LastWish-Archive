import pygame
import cv2


stream = "../Assets/movie/SquadAR.mp4"

cap = cv2.VideoCapture(stream)

ret, img = cap.read()
if not ret:
    print("Can't read stream")
    #exit()

#img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
img = cv2.transpose(img)
print('shape:', img.shape)

pygame.init()

screen = pygame.display.set_mode((800, 600))
surface = pygame.surface.Surface((img.shape[0], img.shape[1]))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    ret, img = cap.read()
    if not ret:
        running = False
        break
    else:
        #img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        #img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        img = cv2.transpose(img)

        pygame.surfarray.blit_array(surface, img)
        screen.blit(surface, (0,0))

    pygame.display.flip()

pygame.quit()