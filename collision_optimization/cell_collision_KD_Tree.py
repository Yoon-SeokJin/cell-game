import pygame
import numpy as np
from common import *
from random import randint, random

def get_collision_pair(sprites, axis=0):
    n = len(sprites)
    if n < 2:
        return []
    val = [sprite.pos[axis] for sprite in sprites]
    idx = np.argpartition(val, n // 2)
    vl = sprites[idx[n//2 - 1]].pos[axis]
    vr = sprites[idx[n//2]].pos[axis]
    lseg = [sprite for sprite in sprites if sprite.pos[axis] - sprite.radius <= vl]
    rseg = [sprite for sprite in sprites if sprite.pos[axis] + sprite.radius >= vr]
    if n == len(lseg):
        return [(lseg[i], lseg[j]) for i in range(n) for j in range(i + 1, n)]
    if n == len(rseg):
        return [(rseg[i], rseg[j]) for i in range(n) for j in range(i + 1, n)]
    return get_collision_pair(lseg, 0 if axis else 1) + get_collision_pair(rseg, 0 if axis else 1)


def _get_collision_pair(self):
    return get_collision_pair(self.cells)


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