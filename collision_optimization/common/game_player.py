import pygame
from pygame.locals import *
from .settings import Settings

class GamePlayer:
    def __init__(self, step_func):
        self.step_func = step_func
        pygame.mixer.pre_init(44100, 16, 2, 4096)
        pygame.init()
        pygame.display.set_caption('cell')
        pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP])
        self.screen = pygame.display.set_mode((Settings.WIDTH, Settings.HEIGHT), FULLSCREEN | DOUBLEBUF, 16)
        self.font = pygame.font.Font(None, 24)


    def play(self, frame_count=-1):
        clock = pygame.time.Clock()
        dt = 0
        self.fps_list = []
        frame_number = 0
        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            self.screen.fill(0)
            dt = clock.tick(Settings.FPS)
            fps = 1000 / dt
            self.fps_list.append(fps)
            if len(self.fps_list) > 60:
                self.fps_list.pop(0)
            fps_min = min(self.fps_list)
            fps_avg = sum(self.fps_list) / len(self.fps_list)
            self.debug_string = []
            self.debug_string.append(f'FPS = {fps:.2f}')
            self.debug_string.append(f'FPS min while 60 = {fps_min:.2f}')
            self.debug_string.append(f'FPS avg while 60 = {fps_avg:.2f}')

            self.step_func(self)

            for idx, str in enumerate(self.debug_string):
                self.screen.blit(self.font.render(str, True, 'White'), (0, idx * 20))

            pygame.display.update()

            if frame_count != -1:
                if frame_count == frame_number:
                    pygame.quit()
                    return
                else:
                    frame_number += 1