import pygame


class Window:
    def __init__(self, config: dict) -> None:
        # load values from display
        self._title = config.get('title', "Game")
        self.frame_cap = config.get('frame_cap', 60)
        
        # init pygame module
        pygame.init()
        
        # default window size to monitor size
        self._resolution = pygame.display.get_desktop_sizes()[0]

        # create pygame display surface
        self._display = pygame.display.set_mode(self._resolution, pygame.FULLSCREEN)

        # create clock to limit game framerate
        self._clock = pygame.time.Clock()

    @property
    def title(self) -> str:
        return self._title
    
    @property
    def frame_cap(self) -> int:
        return self.frame_cap
    
    @frame_cap.setter
    def frame_cap(self, value) -> None:
        if not isinstance(value, int):
            raise TypeError('frame_cap value must be an int')
        if value <= 0:
            raise ValueError('frame_cap must be a value of 0 or higher')

    @property
    def resolution(self) -> list:
        return self._resolution

    def get_fps(self) -> int:
        return self._clock.get_fps()

    def update(self) -> None:
        pygame.display.update()
        self._clock.tick(self.frame_cap)