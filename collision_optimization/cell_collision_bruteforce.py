from math import hypot
import random
import pygame
import numpy as np
from decimal import Decimal
from sys import exit
from random import randint
from pygame.locals import *

pygame.mixer.pre_init(44100, 16, 2, 4096)
pygame.init()
WIDTH = 1920
HEIGHT = 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT), FULLSCREEN | DOUBLEBUF, 16)
pygame.display.set_caption('cell')
pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP])
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


    def collision(self, other):
        dpos = other.pos - self.pos
        k = (dpos[0] * dpos[0] + dpos[1] * dpos[1]).sqrt()
        a = self.radius
        b = other.radius
        return k < a + b


    def drain(self, other):
        if other is not self and other.radius < self.radius and self.collision(other):
            dpos = other.pos - self.pos
            k = (dpos[0] * dpos[0] + dpos[1] * dpos[1]).sqrt()
            a = self.radius
            b = other.radius
            c = (k + (2 * a * a + 2 * b * b - k * k).sqrt()) / 2
            d = k - c
            if k < c:
                c = (a * a + b * b).sqrt()
                d = 0
            self.velocity = (a * a * self.velocity + (c * c - a * a) * other.velocity) / (c * c)
            self.radius = c
            other.radius = d


    def animation(self):
        self.rect.size = (float(self.radius) * 2, float(self.radius) * 2)
        self.rect.center = self.pos.astype(float)
        self.image = pygame.transform.scale(self.frame[0], self.rect.size)


    def destroy(self):
        if self.radius <= 0:
            self.kill()


clock = pygame.time.Clock()
dt = 0
cell = pygame.sprite.Group()
cell.add(Cell((WIDTH / 2, HEIGHT / 2), 40, control=True))
for i in range(1000):
    cell.add(Cell((randint(0, WIDTH), randint(0, HEIGHT)), 1, (0, 0)))


def get_collision_pair(sprites):
    pairs = []
    for i in sprites:
        for j in sprites:
            if i is not j and i.collision(j):
                pairs.append((i, j))
    return pairs


while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    screen.fill(0)
    dt = clock.tick(60)
    screen.blit(font.render(f'FPS = {1000 / dt:.2f}', True, 'White'), (0, 0))
    screen.blit(font.render(f'Count = {len(cell)}', True, 'White'), (0, 20))

    for sprite in cell.sprites():
        if sprite.control:
            sprite.input()
    for sprite in cell.sprites():
        sprite.motion()
    collision_pair = get_collision_pair(cell.sprites())
    print(len(collision_pair))
    for i, j in collision_pair:
        i.drain(j)
        j.drain(i)
    for sprite in cell.sprites():
        sprite.animation()
        sprite.destroy()

    cell.draw(screen)

    pygame.display.update()