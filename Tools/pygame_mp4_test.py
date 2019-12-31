import pygame
import cv2


stream = '../Assets/movie/SquadAR.mov'

# open stream
cap = cv2.VideoCapture(stream)

# read one frame and check if there was no problem
ret, img = cap.read()
if not ret:
    print("Can't read stream")
    #exit()

# transpose/rotate frame 
#img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
img = cv2.transpose(img)

pqr=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

# display its width, height, color_depth
print('shape:', img.shape)

pygame.init()

# create window with the same size as frame
screen = pygame.display.set_mode((img.shape[0], img.shape[1]))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # read one frame and check if there was no problem
    ret, img = cap.read()
    if not ret:
        running = False
        break
    else:
        # transpose/rotate frame
        #img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        #img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        img = cv2.transpose(img,cv2.COLOR_BGR2GRAY)

        # blit directly on screen         
        pygame.surfarray.blit_array(screen, img)

    pygame.display.flip()

pygame.quit()