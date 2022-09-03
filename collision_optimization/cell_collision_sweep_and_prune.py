import pygame
import numpy as np
from common import *
from random import randint, random

def _get_collision_pair(self):
    n = len(self.cells)
    idx = []
    idx += [(self.cells[i].pos[0] - self.cells[i].radius, 1, i) for i in range(n)]
    idx += [(self.cells[i].pos[0] + self.cells[i].radius, -1, i) for i in range(n)]
    sorted(idx)
    pairs = []
    stack = []
    for _, k, i in idx:
        if k == 1:
            for e in stack:
                pairs.append((self.cells[e], self.cells[i]))
            stack.append(i)
        else:
            stack.remove(i)
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