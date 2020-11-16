from Map import Map, Raycaster

import pygame

def _c(hex): return pygame.Color(hex << 0x8)
def _text(screen, font, text, color, pos):
    screen.blit(font.render(text, False, color), pos)
def _object(screen, font, o):
    pygame.draw.rect(screen, _c(o.color),
        pygame.Rect(o.pos[0], o.pos[1], o.size[0], o.size[1]))
    _text(screen, font, o.name, _c(o.color), (o.pos[0], o.pos[1] - font.get_height()))

pygame.init()

screensize = (320, 240)
screen = pygame.display.set_mode(screensize)
clock = pygame.time.Clock()
font = pygame.font.Font(None, 16)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT \
        or event.type == pygame.KEYDOWN \
        and event.key == pygame.K_ESCAPE:
            running = False

    screen.fill(_c(0x000000))
    # for o in objects: _object(screen, font, o)
    pygame.display.flip()
    clock.tick(60)
