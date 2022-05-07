import pygame


class Window:
    def __init__(self, config: dict) -> None:
        # load values from display
        self._title = config.get("title", "Game")
        self._frame_cap = config.get("frame_cap", 60)
        
        # init pygame module
        pygame.init()

        # use render_target from config
        self._resolution = config.get("resolution", [1280, 720])
        
        # create scaled pygame window in fullscreen. this way we can use one
        # resolution for the game and have it automatically scale up whenever
        # the pygame display gets updated.
        self._display = pygame.display.set_mode(self._resolution, pygame.FULLSCREEN | pygame.SCALED)

        # convert to improve performance
        self._display.convert_alpha()

        # create clock to limit game framerate
        self._clock = pygame.time.Clock()


    @property
    def title(self) -> str:
        return self._title
    
    
    @property
    def frame_cap(self) -> int:
        return self._frame_cap
    
    
    @frame_cap.setter
    def frame_cap(self, value) -> None:
        if not isinstance(value, int):
            raise TypeError("frame_cap value must be an int")
        if value <= 0:
            raise ValueError("frame_cap must be a value of 0 or higher")
        
        self._frame_cap = value


    @property
    def resolution(self) -> list:
        return self._resolution


    def get_surface(self) -> pygame.Surface:
        return self._display


    def get_fps(self) -> int:
        return self._clock.get_fps()


    def update(self) -> None:
        pygame.display.update()
        self._clock.tick(self._frame_cap)