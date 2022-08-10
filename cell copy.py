import pygame
import sympy
from sys import exit

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption('cell')
clock = pygame.time.Clock()

def add_tuple(a : tuple, b : tuple) -> tuple:
    return tuple(sum(x) for x in zip(a, b))

class Cell(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image_origin = pygame.image.load('assets/cell1.png').convert_alpha()
        self.pos = sympy.Point(400.0, 300.0)
        self.velocity = sympy.Point(0.0, 0.0)
        self.radius = 100
        self.click = False
        self.update()
    
    def update(self):
        if pygame.mouse.get_pressed()[0] and not self.click:
            self.click = True
            self.velocity += (sympy.Point(pygame.mouse.get_pos()) - self.pos)
        elif not pygame.mouse.get_pressed()[0] and self.click:
            self.click = False

        self.pos += self.velocity
        self.image = pygame.transform.scale(self.image_origin, (self.radius, self.radius))
        
        self.rect = self.image.get_rect(center=self.pos)

cell = pygame.sprite.GroupSingle()
cell.add(Cell())

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    screen.fill(0)
    cell.draw(screen)
    cell.update()

    pygame.display.update()
    clock.tick(60)