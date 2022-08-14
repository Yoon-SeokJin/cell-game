import pygame
import numpy as np
from cell import Cell
from settings import Settings
from game_player import GamePlayer
from random import randint, random

def get_collision_pair(sprites):
    n = len(sprites)
    idx = []
    idx += [(sprites[i].pos[0] - sprites[i].radius, 1, i) for i in range(n)]
    idx += [(sprites[i].pos[0] + sprites[i].radius, -1, i) for i in range(n)]
    sorted(idx)
    pairs = []
    stack = []
    for _, k, i in idx:
        if k == 1:
            for e in stack:
                pairs.append((sprites[e], sprites[i]))
            stack.append(i)
        else:
            stack.remove(i)
    return pairs

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