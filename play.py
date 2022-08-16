import pygame
import numpy as np
from common import *
from random import randint, random

def get_collision_pair(sprites):
    tile_width = 40
    tile_height = 40
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
                if 0 <= y < tile_hcount and 0 <= x < tile_wcount:
                    bucket[y][x].append(e)
    pairs = []
    for row in bucket:
        for items in row:
            n = len(items)
            for i in range(n):
                for j in range(i + 1, n):
                    pairs.append((items[i], items[j]))
    return pairs

def step_func(self):
    self.debug_string.append(f'Count = {len(cells)}')
    volume = 0
    for cell in cells:
        volume += cell.radius * cell.radius * cell.radius
    self.debug_string.append(f'Volume = {volume}')

    for sprite in cells:
        if sprite.control:
            sprite.input(cells)
    for sprite in cells:
        sprite.motion()
    collision_pair = get_collision_pair(cells)
    for i, j in collision_pair:
        i.drain(j)
        j.drain(i)
    for sprite in cells:
        color = '#55AEAE' if sprite.control else '#AE5555'
        pygame.draw.circle(self.screen, color, sprite.pos.astype(float), float(sprite.radius))

    cells[:] = [e for e in cells if e.radius > 0]

def place_extra_cells(cells, radius_list, try_count=100):
    sorted(radius_list, reverse=True)
    for radius in radius_list:
        for _ in range(try_count):
            r = int(radius)
            pos = (randint(r, Settings.WIDTH - r), randint(r, Settings.HEIGHT - r))
            for cell in cells:
                dpos = cell.pos - pos
                k = (dpos[0] * dpos[0] + dpos[1] * dpos[1]).sqrt()
                a = int(radius)
                b = cell.radius
                if k < a + b:
                    break
            else:
                cells.append(Cell(pos, radius, (0, 0)))
                break

def relocate_no_overlap(cells, iter_num=100, extra_radius=10):
    for cell in cells:
        cell.radius += extra_radius
    for _ in range(iter_num):
        collision_pair = get_collision_pair(cells)
        if len(collision_pair) == 0:
            break
        for i, j in collision_pair:
            dpos = j.pos - i.pos
            k = (dpos[0] * dpos[0] + dpos[1] * dpos[1]).sqrt()
            a = i.radius
            b = j.radius
            force = a + b - k
            if force > 0:
                force = force * force / 10000
                i.pos -= dpos * force
                j.pos += dpos * force
        for cell in cells:
            cell.motion()
    for cell in cells:
        cell.radius -= extra_radius

if __name__ == '__main__':
    game_player = GamePlayer(step_func)

    cells = []
    cells.append(Cell((Settings.WIDTH / 2, Settings.HEIGHT / 2), 20, control=True))

    radius_list = np.geomspace(10, 100, 100)

    # radius_list = np.concatenate([
    #     np.ones(shape=8) * 100,
    #     np.ones(shape=16) * 75,
    #     np.ones(shape=64) * 50,
    #     np.ones(shape=128) * 25,
    #     np.ones(shape=128) * 12.5,
    # ])
    
    for r in radius_list:
        r = int(r)
        pos = (randint(r, Settings.WIDTH - r), randint(r, Settings.HEIGHT - r))
        cells.append(Cell(pos, r))

    relocate_no_overlap(cells)

    game_player.play()