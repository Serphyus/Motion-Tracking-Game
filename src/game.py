import json
import logging
from pathlib import Path

import pygame

from window import Window


class Game:
    def __init__(self, abs_path: Path) -> None:
        with open(Path(abs_path, "..", "config", "default.json"), "r") as file:
            self._game_config = json.load(file)
        
        self._window = Window(self._game_config["window"])
    

    def main_loop(self) -> None:
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    logging.debug("exiting game main loop")
                    running = False
            
            self._window.update()