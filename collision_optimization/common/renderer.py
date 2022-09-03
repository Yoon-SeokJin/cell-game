import pygame
from pygame.locals import *
from .settings import Settings

class Renderer:
    def __init__(self):
        self.lazy_init_complete = False

    
    def lazy_init(self):
        pygame.mixer.pre_init(44100, 16, 2, 4096)
        pygame.init()
        pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP])
        self.screen = pygame.display.set_mode((Settings.WIDTH, Settings.HEIGHT), DOUBLEBUF, 16)
        self.font = pygame.font.Font(None, 24)
        self.fps_list = []
        self.clock = pygame.time.Clock()
        self.lazy_init_complete = True


    def __call__(self, step):
        def inner(f_self, *args, **kwargs):
            if not self.lazy_init_complete:
                self.lazy_init()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return True

            self.screen.fill(0)
            dt = self.clock.tick(Settings.FPS)
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

            return_value = step(f_self, self, *args, **kwargs)

            for idx, str in enumerate(self.debug_string):
                self.screen.blit(self.font.render(str, True, 'White'), (0, idx * 20))

            pygame.display.update()
            return return_value
        return inner