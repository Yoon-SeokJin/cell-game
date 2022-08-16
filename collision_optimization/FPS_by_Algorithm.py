import pygame
import numpy as np
from common import *
from random import randint, random
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

from cell_collision_bruteforce import get_collision_pair as check_bruteforce
from cell_collision_sweep_and_prune import get_collision_pair as check_sweep_and_prune
from cell_collision_UGSP import get_collision_pair as check_UGSP
from cell_collision_UGSP_hashing import get_collision_pair as check_UGSP_hashing
from cell_collision_KD_Tree import get_collision_pair as check_KD_Tree
from cell_collision_KD_Tree_iteratively import get_collision_pair as check_KD_Tree_iteratively

def closure(check_func):
    def step_func(self):
        self.debug_string.append(f'Count = {len(cell)}')

        for sprite in cell.sprites():
            if sprite.control:
                sprite.input(cell)
        for sprite in cell.sprites():
            sprite.motion()
        collision_pair = check_func(cell.sprites())
        for i, j in collision_pair:
            i.drain(j)
            j.drain(i)
        for sprite in cell.sprites():
            sprite.animation()
            sprite.destroy()

        cell.draw(self.screen)
    return step_func

plot_data = pd.DataFrame(columns=['fps', 'type', 'algo'])
check_func_list = {
    'bruteforce':check_bruteforce,
    'check_sweep_and_prune':check_sweep_and_prune,
    'check_UGSP':check_UGSP,
    'check_UGSP_hashing':check_UGSP_hashing,
    'check_KD_Tree':check_KD_Tree,
    'check_KD_Tree_iteratively':check_KD_Tree_iteratively
}
for name, check_func in check_func_list.items():
    measure_count = 10
    for rp in range(measure_count):
        game_player = GamePlayer(closure(check_func))

        cell = pygame.sprite.Group()
        cell.add(Cell((Settings.WIDTH / 2, Settings.HEIGHT / 2), 40, control=True))
        for i in range(1500):
            cell.add(Cell((randint(0, Settings.WIDTH), randint(0, Settings.HEIGHT)), 2, (random() * 2 - 1, random() * 2 - 1)))

        game_player.play(120)
        fps_min = min(game_player.fps_list)
        fps_avg = sum(game_player.fps_list) / 60
        data_min = pd.Series((fps_min, 'min', name), index=plot_data.columns)
        data_avg = pd.Series((fps_avg, 'avg', name), index=plot_data.columns)
        plot_data = pd.concat([plot_data.T, data_min, data_avg], axis=1).T

plot_data.reset_index(drop=True, inplace=True)
plot_data.to_pickle('FPS_by_Collision_Algorithm.pkl')
sns.barplot(data=plot_data, x='algo', y='fps', hue='type').set(title='FPS by Collision Algorithm', xlabel='Algorithm', ylabel='FPS')
plt.show()