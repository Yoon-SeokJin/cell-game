import pygame
import numpy as np
from cell import Cell
from settings import Settings
from game_player import GamePlayer
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

def step_func(self):
    self.debug_string.append(f'Count = {len(cell)}')

    for sprite in cell.sprites():
        if sprite.control:
            sprite.input(cell)
    for sprite in cell.sprites():
        sprite.motion()
    collision_pair = get_collision_pair(cell.sprites())
    for i, j in collision_pair:
        i.drain(j)
        j.drain(i)
    for sprite in cell.sprites():
        sprite.animation()
        sprite.destroy()

    cell.draw(self.screen)

if __name__ == '__main__':
    game_player = GamePlayer(step_func)

    cell = pygame.sprite.Group()
    cell.add(Cell((Settings.WIDTH / 2, Settings.HEIGHT / 2), 40, control=True))
    for i in range(1000):
        cell.add(Cell((randint(0, Settings.WIDTH), randint(0, Settings.HEIGHT)), 2, (random() * 2 - 1, random() * 2 - 1)))

    game_player.play()