import sys
import pygame as pg
import pygame


def main():
    screen = pg.display.set_mode((640, 480))
    clock = pg.time.Clock()

    surface = pg.image.load("..\Assets\image\environment/block/TileSnow02.png").convert_alpha()
    #surface = pg.transform.rotozoom(surface, 0, 2)

    done = False
    while not done:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_e:
                    dark = pygame.Surface((surface.get_width(), surface.get_height()), flags=pygame.SRCALPHA)
                    dark.fill((100,100,100,0))
                    surface.blit(dark, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
                if event.key == pg.K_q:
                    dark = pygame.Surface((surface.get_width(), surface.get_height()), flags=pygame.SRCALPHA)
                    dark.fill((100,100, 100, 0))
                    surface.blit(dark, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)


        screen.fill(pg.Color('lightskyblue4'))
        #pg.draw.rect(screen, pg.Color(40, 50, 50), (210, 210, 50, 90))
        screen.blit(surface, (200, 200))

        pg.display.flip()
        clock.tick(30)


if __name__ == '__main__':
    pg.init()
    main()
    pg.quit()
    sys.exit()