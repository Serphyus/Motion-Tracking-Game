from pathlib import Path

from game import Game
from console import Console


if __name__ == '__main__':
    try:
        game = Game(Path(__file__).resolve().parent)
        game.main_loop()
    except Exception as e:
        Console.error_msg('%s | %s' % (e.__class__.__name__, e))