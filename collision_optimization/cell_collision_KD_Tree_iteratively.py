import pygame
import numpy as np
from common import *
from random import randint, random

def _get_collision_pair(self, axis=0):
    pairs = []
    stack = []
    stack.append((self.cells, 0))
    while len(stack):
        sprites, axis = stack[-1]
        stack.pop(-1)
        
        n = len(sprites)
        if n < 2:
            continue
        val = [sprite.pos[axis] for sprite in sprites]
        idx = np.argpartition(val, n // 2)
        vl = sprites[idx[n//2 - 1]].pos[axis]
        vr = sprites[idx[n//2]].pos[axis]
        lseg = [sprite for sprite in sprites if sprite.pos[axis] - sprite.radius <= vl]
        rseg = [sprite for sprite in sprites if sprite.pos[axis] + sprite.radius >= vr]
        if n == len(lseg):
            pairs += [(lseg[i], lseg[j]) for i in range(n) for j in range(i + 1, n)]
            continue
        if n == len(rseg):
            pairs += [(rseg[i], rseg[j]) for i in range(n) for j in range(i + 1, n)]
            continue

        stack.append((lseg, 0 if axis else 1))
        stack.append((rseg, 0 if axis else 1))
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