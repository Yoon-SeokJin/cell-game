import pygame
import numpy as np
from common import *
from random import randint, random


def _get_collision_pair(self):
    tile_width = 40
    tile_height = 40
    bucket = {}
    for e in self.cells:
        x1 = int(e.pos[0] - e.radius) // tile_width
        x2 = int(e.pos[0] + e.radius) // tile_width
        y1 = int(e.pos[1] - e.radius) // tile_height
        y2 = int(e.pos[1] + e.radius) // tile_height
        for x in range(x1, x2 + 1):
            bucket.setdefault(x, {})
            for y in range(y1, y2 + 1):
                bucket[x].setdefault(y, [])
                bucket[x][y].append(e)
    pairs = []
    for x, row in bucket.items():
        for y, items in row.items():
            n = len(items)
            for i in range(n):
                for j in range(i + 1, n):
                    pairs.append((items[i], items[j]))
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