import pygame
from common import *
from random import randint, random

def get_collision_pair(sprites):
    tile_width = 40
    tile_height = 40
    bucket = {}
    for e in sprites:
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