from typing import Sequence

import pygame


class Surface:
    """A static image or an animation to render in pygame.

    Creates a staic or animated surface object. The surface requires at least
    1 frame to be initialized and if given 1 frame it will default it's state 
    to a non-animated surface. The animated property can be changed at any given
    time true or false. If true the surface will engage in an internal counter
    which will update the current frame based on the speed parameter. If the
    animated property is false the counter will never change and the `get`
    method will only return the first frame.
    
    Exceptions:
        - `ValueError` will be raised the frames parameter contains no elements.
    
    Args: 
        - `frames` (list): a sequence of `pygame.Surface` objects.
        - `animated` (bool): a boolean to decide whether image is static or to be animated.
        - `speed` (int): a integer to determine the speed of the animation.
        - `looped` (bool): a boolean to make animation continuous.
    """
    def __init__(self,
            frames: Sequence[pygame.Surface],
            animated: bool,
            speed: int = 15,
            looped: bool = True,
        ) -> None:
        
        if len(frames) == 0:
            raise ValueError("frames must contain at least 1 item")

        # stores parameters
        self._frames = frames
        self._animated = animated
        self._speed = speed
        self._looped = looped
        
        # for changing the frame returned by get
        # since the counter is incremented before return the
        # counter must start at -1 to include the first frame.
        self._counter = -1
        self._current_frame = 0
        
        # count the available frames
        self._frame_count = len(self._frames)

        # Checks if it can be animated
        if self._frame_count == 1:
            self._animated = False


    @property
    def animated(self) -> bool:
        return self._animated


    @animated.setter
    def animated(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise TypeError("animated must be a bool")
        self._animated = value


    @property
    def loop(self) -> bool:
        return self._looped
    

    @loop.setter
    def loop(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError("animated must be a bool")
        self._looped = value


    def reset(self) -> None:
        self._current_frame = 0
        self._counter = 0


    def get_frame(self) -> pygame.Surface:
        """Returns the current frame of animation

        This method returns the current frame of the surface
        and by doing so increments the counter by 1 and checks
        if the frame changes if it extends the speed value. If
        the frame is not animated the first frame the surface 
        was initialized will always be returned.

        Returns:
            `pygame.Surface` : The surface of the current frame
        """
        if not self._animated:
            return self._frames[0]

        self._counter += 1
        if self._counter >= self._speed:
            if self._current_frame == self._frame_count - 1:
                if self._looped:
                    self._current_frame = 0
                    self._counter = 0
            else:
                self._current_frame += 1
                self._counter = 0
        
        return self._frames[self._current_frame]