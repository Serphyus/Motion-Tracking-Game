import logging
from rich.logging import RichHandler


logging.basicConfig(
    level="NOTSET",
    format="%(message)s",
    datefmt="[%H:%M:%S.%f]",
    handlers=[RichHandler()]
)


class Console:
    _logger = logging.getLogger("rich")

    @classmethod
    def debug_msg(cls, msg: str) -> None:
        cls._logger.debug("%s" % msg)
    

    @classmethod
    def warning_msg(cls, msg: str) -> None:
        cls._logger.warning("%s" % msg)


    @classmethod
    def error_msg(cls, msg: str) -> None:
        cls._logger.error("%s" % msg)