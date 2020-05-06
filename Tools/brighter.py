import sys
import pygame as pg
import pygame


def main():
    screen = pg.display.set_mode((640, 480))
    clock = pg.time.Clock()

    surface = pg.image.load("..\Assets\image\environment/block/TileSnow02.png").convert_alpha()
    #surface = pg.transform.rotozoom(surface, 0, 2)
    surface2 = pg.image.load("..\Assets\image\environment/block/TileSnow02.png").convert_alpha()
    value = 255
    done = False
    while not done:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_e:
                    if value < 255:
                        dark = pygame.Surface((surface.get_width(), surface.get_height()), flags=pygame.SRCALPHA)
                        dark.fill((10,10,10,0))
                        surface.blit(dark, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
                        value += 10
                if event.key == pg.K_q:
                    if value > 150:
                        dark = pygame.Surface((surface.get_width(), surface.get_height()), flags=pygame.SRCALPHA)
                        dark.fill((10,10,10,0))
                        surface.blit(dark, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
                        value -= 10


        screen.fill(pg.Color('lightskyblue4'))
        #pg.draw.rect(screen, pg.Color(40, 50, 50), (210, 210, 50, 90))
        screen.blit(surface, (200, 200))
        screen.blit(surface2, (350, 200))

        pg.display.flip()
        clock.tick(30)


if __name__ == '__main__':
    pg.init()
    main()
    pg.quit()
    sys.exit()