from pathlib import Path
from game import Game


if __name__ == '__main__':
    game = Game(Path(__file__).resolve().parent)
    game.main_loop()