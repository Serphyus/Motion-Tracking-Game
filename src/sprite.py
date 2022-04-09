import pygame


class Sprite:
    def __init__(self, surface: pygame.Surface, rect: pygame.Rect) -> None: 
        self._surface = surface
        self._rect = rect

    def get_surface(self) -> pygame.Surface:
        return self._surface

    def get_rect(self) -> pygame.Surface:
        return self._rect

    def render(self, dest_surface: pygame.Surface) -> None:
        dest_surface.blit(self._surface, self._rect)
        self._surface = dest_surface
