import pygame
import numpy as np
from common import *
from random import randint, random

def _get_collision_pair(self):
    pairs = []
    n = len(self.cells)
    for i in range(n):
        for j in range(i + 1, n):
            if i != j:
                pairs.append((self.cells[i], self.cells[j]))
    return pairs


if __name__ == '__main__':
    Environment._get_collision_pair = _get_collision_pair
    env = Environment()
    env.reset()
    env.render()
    while True:
        if pygame.mouse.get_pressed()[0]:
            pos = pygame.mouse.get_pos()
            env.step(np.array(pos, dtype=float))
        else:
            env.step(None)
        if env.render():
            break