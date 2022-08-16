import pygame
import numpy as np
from common import *
from random import randint, random
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

def get_collision_pair(sprites):
    tile_width = TILE_SIZE
    tile_height = TILE_SIZE
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

plot_data = pd.DataFrame(columns=['min', 'avg'])
for ts in range(10, 100, 1):
    fps_min = []
    fps_avg = []
    measure_count = 10
    for rp in range(measure_count):
        TILE_SIZE = ts
        game_player = GamePlayer(step_func)

        cell = pygame.sprite.Group()
        cell.add(Cell((Settings.WIDTH / 2, Settings.HEIGHT / 2), 40, control=True))
        for i in range(1500):
            cell.add(Cell((randint(0, Settings.WIDTH), randint(0, Settings.HEIGHT)), 2, (random() * 2 - 1, random() * 2 - 1)))

        game_player.play(120)
        fps_min.append(min(game_player.fps_list))
        fps_avg.append(sum(game_player.fps_list) / 60)
    fps_min_avg = sum(fps_min) / measure_count
    fps_avg_avg = sum(fps_avg) / measure_count
    data = pd.Series((fps_min_avg, fps_avg_avg), index=plot_data.columns, name=ts)
    plot_data = pd.concat([plot_data.T, data], axis=1).T

plot_data.to_pickle('FPS_by_Tile_Size.pkl')
sns.lineplot(data=plot_data, markers=True, dashes=False).set(title='FPS by Tile Size', xlabel='Tile Size', ylabel='FPS')
plt.show()