import time
import datetime
import logging
from pathlib import Path

from game import Game


def set_logging(abs_path: Path):
    log_dir = Path(abs_path, "logs")
    
    if not log_dir.is_dir():
        log_dir.mkdir()
    
    today = datetime.date.today()
    
    filename = "%s-%s.log" % (
        today.isoformat(),
        int(time.time())
    )

    log_file = Path(log_dir, filename)

    logging.basicConfig(
        level="NOTSET",
        filename=log_file,
        filemode="w",
        format="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="[%H:%M:%S]",
    )


if __name__ == "__main__":
    try:
        abs_path = Path(__file__).resolve().parent
        set_logging(abs_path)

        game = Game(abs_path)
        game.main_loop()
    except (Exception, KeyboardInterrupt) as e:
        logging.exception(e)