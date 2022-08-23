import pygame
import numpy as np
from decimal import Decimal
from .settings import Settings

class Cell:
    def __init__(self, pos, radius, velocity=(0, 0), control=False):
        pos = (Decimal(pos[0]), Decimal(pos[1]))
        radius = Decimal(radius)
        velocity = Decimal(velocity[0]), Decimal(velocity[1])
        self.pos = np.array(pos)
        self.velocity = np.array(velocity)
        self.radius = radius
        self.speed = Decimal(1)
        self.ratio = Decimal(0.99)
        self.control = control
        self.click = True


    def propel(self, cells, pos):
        vec = self.pos - np.array([Decimal(pos[0]), Decimal(pos[1])])
        vec /= (vec[0] * vec[0] + vec[1] * vec[1]).sqrt()
        r = self.radius
        nr = r + (self.ratio ** Decimal(1/3) - 1) * self.radius
        v = self.velocity
        nv = v + vec * self.speed
        prop_r = (r * r * r - nr * nr * nr) ** Decimal(1/3)
        prop_v = v - (nv - v) * (r * r * r - nr * nr * nr) / (prop_r * prop_r * prop_r)
        self.radius = nr
        self.velocity = nv
        cells.append(Cell(self.pos - vec * (self.radius + prop_r), prop_r, prop_v))


    def motion(self):
        self.pos += self.velocity * Decimal(Settings.SPEED)

        if self.pos[0] - self.radius < 0:
            self.velocity[0] = -self.velocity[0]
            self.pos[0] = -self.pos[0] + self.radius * 2
        if self.pos[0] + self.radius >= Settings.WIDTH:
            self.velocity[0] = -self.velocity[0]
            self.pos[0] = Settings.WIDTH * 2 - self.pos[0] - self.radius * 2
        if self.pos[1] - self.radius < 0:
            self.velocity[1] = -self.velocity[1]
            self.pos[1] = -self.pos[1] + self.radius * 2
        if self.pos[1] + self.radius >= Settings.HEIGHT:
            self.velocity[1] = -self.velocity[1]
            self.pos[1] = Settings.HEIGHT * 2 - self.pos[1] - self.radius * 2


    def drain(self, other):
        if other is not self and other.radius < self.radius:
            dpos = other.pos - self.pos
            k = (dpos[0] * dpos[0] + dpos[1] * dpos[1]).sqrt()
            a = self.radius
            b = other.radius
            if k < a + b:
                c = ((12 * a * a * a * k + 12 * b * b * b * k - 3 * k * k * k * k).sqrt() + 3 * k * k) / (6 * k)
                d = k - c
                if k < c:
                    c = (a * a * a + b * b * b) ** Decimal(1/3)
                    d = 0
                self.velocity = (a * a * a * self.velocity + (c * c * c - a * a * a) * other.velocity) / (c * c * c)
                self.radius = c
                other.radius = d