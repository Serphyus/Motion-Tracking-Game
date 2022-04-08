from pathlib import Path
from game import Game


game = Game(Path(__file__).resolve().parent)
game.main_loop()