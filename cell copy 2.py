import pygame
import numpy as np
from sys import exit

pygame.init()

WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('cell')
clock = pygame.time.Clock()


class Cell(pygame.sprite.Sprite):
    def __init__(self, pos, radius, velocity=(0, 0), control=False):
        super().__init__()
        self.frame = [pygame.image.load('assets/cell1.png').convert_alpha()]
        self.pos = np.array(pos, dtype=float)
        self.velocity = np.array(velocity, dtype=float)
        self.radius = radius
        self.click = True
        self.speed = 1
        self.image = self.frame[0]
        self.rect = self.image.get_rect(center=self.pos.astype(float))
        self.ratio = 90 / 100
        self.control = control
        self.update()


    def input(self):
        if pygame.mouse.get_pressed()[0] and not self.click:
            self.click = True
            vec = self.pos - pygame.mouse.get_pos()
            vec /= np.hypot(*vec.astype(float))
            dr = (np.sqrt(self.ratio) - 1) * self.radius
            dv = vec * self.speed
            prop_r = np.sqrt(-2 * self.radius * dr - dr * dr)
            prop_v = -(self.radius + dr) * (self.radius + dr) * dv / (prop_r * prop_r)
            self.velocity += dv
            self.radius += dr
            cell.add(Cell(self.pos + -vec * (self.radius + prop_r), prop_r, prop_v))
        elif not pygame.mouse.get_pressed()[0] and self.click:
            self.click = False
    

    def motion(self):
        self.pos += self.velocity

        if self.pos[0] - self.radius < 0:
            self.velocity[0] = -self.velocity[0]
            self.pos[0] = -self.pos[0] + self.radius * 2
        if self.pos[0] + self.radius >= WIDTH:
            self.velocity[0] = -self.velocity[0]
            self.pos[0] = WIDTH * 2 - self.pos[0] - self.radius * 2
        if self.pos[1] - self.radius < 0:
            self.velocity[1] = -self.velocity[1]
            self.pos[1] = -self.pos[1] + self.radius * 2
        if self.pos[1] + self.radius >= HEIGHT:
            self.velocity[1] = -self.velocity[1]
            self.pos[1] = HEIGHT * 2 - self.pos[1] - self.radius * 2


    def drain(self):
        for sprite in cell.sprites():
            if sprite is not self:
                if sprite.radius < self.radius:
                    dpos = sprite.pos - self.pos
                    k = np.sqrt(dpos[0] * dpos[0] + dpos[1] * dpos[1])
                    a = self.radius
                    b = sprite.radius
                    if k < a:
                        c = np.sqrt(a * a + b * b)
                        d = 0
                    elif k < a + b:
                        c = min(k, (k + np.sqrt(2 * a * a + 2 * b * b - k * k)) / 2)
                        d = k - c
                    else:
                        continue
                    self.velocity = (a * a * self.velocity + (b * b - d * d) * sprite.velocity) / (c * c)
                    self.radius = c
                    sprite.radius = d


    
    def destroy(self):
        if self.radius <= 0:
            self.kill()


    def animation(self):
        self.rect.size = (float(self.radius) * 2, float(self.radius) * 2)
        self.rect.center = self.pos.astype(float)
        self.image = pygame.transform.scale(self.frame[0], self.rect.size)

    
    def update(self):
        if self.control:
            self.input()
            # print(self.radius)
        self.motion()
        self.drain()
        self.animation()
        self.destroy()


cell = pygame.sprite.Group()
cell.add(Cell((400, 300), 40, control=True))
cell.add(Cell((400, 300), 30))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    screen.fill(0)
    cell.draw(screen)
    cell.update()
    
    area = 0
    for sprite in cell.sprites():
        area += sprite.radius * sprite.radius
    print(np.sqrt(area))

    pygame.display.update()
    clock.tick(60)