import pygame
import numpy as np
from cell import Cell
from settings import Settings
from game_player import GamePlayer
from random import randint, random

def get_collision_pair(sprites):
    tile_width = 30
    tile_height = 30
    tile_wcount = Settings.WIDTH // tile_width + 1
    tile_hcount = Settings.HEIGHT // tile_height + 1
    bucket = [[[] for _ in range(tile_wcount)] for _ in range(tile_hcount)]
    for e in sprites:
        x1 = int(e.pos[0] - e.radius) // tile_width
        x2 = int(e.pos[0] + e.radius) // tile_width
        y1 = int(e.pos[1] - e.radius) // tile_height
        y2 = int(e.pos[1] + e.radius) // tile_height
        for x in range(x1, x2 + 1):
            for y in range(y1, y2 + 1):
                bucket[y][x].append(e)
    pairs = []
    for row in bucket:
        for items in row:
            n = len(items)
            for i in range(n):
                for j in range(n):
                    pairs.append((items[i], items[j]))
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