import random
import pygame
import numpy as np
from decimal import Decimal
from sys import exit
from random import randint

pygame.init()

WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('cell')
font = pygame.font.Font(None, 24)


class Cell(pygame.sprite.Sprite):
    def __init__(self, pos, radius, velocity=(0, 0), control=False):
        super().__init__()
        self.frame = [pygame.image.load(f'assets/cell{1 if control else 2}.png').convert_alpha()]
        pos = (Decimal(pos[0]), Decimal(pos[1]))
        radius = Decimal(radius)
        velocity = Decimal(velocity[0]), Decimal(velocity[1])
        self.pos = np.array(pos)
        self.velocity = np.array(velocity)
        self.radius = radius
        self.click = True
        self.speed = Decimal(1)
        self.image = self.frame[0]
        self.rect = self.image.get_rect(center=self.pos.astype(float))
        self.ratio = Decimal(99 / 100)
        self.control = control
        self.update()


    def input(self):
        if pygame.mouse.get_pressed()[0] and not self.click:
            self.click = True
            vec = self.pos - pygame.mouse.get_pos()
            vec /= (vec[0] * vec[0] + vec[1] * vec[1]).sqrt()
            dr = ((self.ratio).sqrt() - 1) * self.radius
            dv = vec * self.speed
            prop_r = (-2 * self.radius * dr - dr * dr).sqrt()
            prop_v = self.velocity + -(self.radius + dr) * (self.radius + dr) * dv / (prop_r * prop_r) / 10
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
                    k = (dpos[0] * dpos[0] + dpos[1] * dpos[1]).sqrt()
                    a = self.radius
                    b = sprite.radius
                    if k >= a + b:
                        continue
                    c = (k + (2 * a * a + 2 * b * b - k * k).sqrt()) / 2
                    d = k - c
                    if k < c:
                        c = (a * a + b * b).sqrt()
                        d = 0
                    self.velocity = (a * a * self.velocity + (c * c - a * a) * sprite.velocity) / (c * c)
                    self.radius = c
                    sprite.radius = d


    def animation(self):
        self.rect.size = (float(self.radius) * 2, float(self.radius) * 2)
        self.rect.center = self.pos.astype(float)
        self.image = pygame.transform.scale(self.frame[0], self.rect.size)


    def destroy(self):
        if self.radius <= 0:
            self.kill()

    
    def update(self):
        if self.control:
            self.input()
        self.motion()
        self.drain()
        self.animation()
        self.destroy()


clock = pygame.time.Clock()
dt = 0
cell = pygame.sprite.Group()
cell.add(Cell((WIDTH / 2, HEIGHT / 2), 40, control=True))
for i in range(1000):
    cell.add(Cell((randint(0, WIDTH), randint(0, HEIGHT)), 1, (0, 0)))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    screen.fill(0)
    dt = clock.tick(60)
    screen.blit(font.render(f'FPS = {1000 / dt:.2f}', True, 'White'), (0, 0))
    screen.blit(font.render(f'Count = {len(cell)}', True, 'White'), (0, 20))
    cell.draw(screen)
    cell.update()

    pygame.display.update()