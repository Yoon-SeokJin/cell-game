import pygame
import numpy as np
from random import randint, random
from common import *

class Environment:
    def reset(self):
        self.cells = []
        self.cells.append(Cell((Settings.WIDTH / 2, Settings.HEIGHT / 2), 40, control=True))
        for i in range(1000):
            self.cells.append(Cell((randint(0, Settings.WIDTH), randint(0, Settings.HEIGHT)), 2, (random() * 2 - 1, random() * 2 - 1)))


    def step(self, action):
        self.clicked = isinstance(action, np.ndarray) 
        if self.clicked:
            self.cells[0].propel(self.cells, action)
        for sprite in self.cells:
            sprite.motion()
        collision_pair = self._get_collision_pair()
        for i, j in collision_pair:
            i.drain(j)
            j.drain(i)

        self.cells[:] = [e for e in self.cells if e.radius > 0]


    @Renderer()
    def render(self, renderer):
        renderer.debug_string.append(f'Count = {len(self.cells)}')
        volume = 0
        for cell in self.cells:
            volume += cell.radius * cell.radius * cell.radius
        renderer.debug_string.append(f'Volume = {volume}')
        for sprite in self.cells:
            if sprite.radius < self.cells[0].radius:
                color = '#AEAE55'
            elif sprite.radius > self.cells[0].radius:
                color = '#AE5555'
            else:
                color = '#55AEAE'
            pygame.draw.circle(renderer.screen, color, sprite.pos.astype(float), float(sprite.radius))


    def _get_collision_pair(self):
        tile_width = 40
        tile_height = 40
        tile_wcount = Settings.WIDTH // tile_width + 1
        tile_hcount = Settings.HEIGHT // tile_height + 1
        bucket = [[[] for _ in range(tile_wcount)] for _ in range(tile_hcount)]
        for e in self.cells:
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