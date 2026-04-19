# ruff: noqa: ANN401

import logging
from typing import Any


class LoggerHelper:
    # Códigos ANSI para colores
    RESET = "\033[0m"
    COLORS = {
        "DEBUG": "\033[90m",  # Gris oscuro
        "INFO": "\033[94m",  # Azul claro
        "WARNING": "\033[93m",  # Amarillo
        "ERROR": "\033[91m",  # Rojo
        "SUCCESS": "\033[92m",  # Verde
    }

    SUCCESS_LEVEL = 25
    logging.addLevelName(SUCCESS_LEVEL, "SUCCESS")

    @staticmethod
    def _add_success_method() -> None:
        return None

    _logger: logging.Logger | None = None  # instancia única

    @staticmethod
    def _get_logger() -> logging.Logger:
        if LoggerHelper._logger is None:
            logger = logging.getLogger("LoggerHelper")
            logger.setLevel(logging.DEBUG)
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)

            formatter = LoggerHelper.ColoredFormatter(
                "[%(asctime)s] [%(levelname)s]: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            ch.setFormatter(formatter)

            logger.addHandler(ch)
            LoggerHelper._logger = logger
        return LoggerHelper._logger

    class ColoredFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            levelname = record.levelname
            color = LoggerHelper.COLORS.get(levelname, LoggerHelper.RESET)
            message = super().format(record)
            return f"{color}{message}{LoggerHelper.RESET}"

    @staticmethod
    def debug(msg: str, *args: object, **kwargs: Any) -> None:
        LoggerHelper._get_logger().debug(msg, *args, **kwargs)

    @staticmethod
    def info(msg: str, *args: object, **kwargs: Any) -> None:
        LoggerHelper._get_logger().info(msg, *args, **kwargs)

    @staticmethod
    def warning(msg: str, *args: object, **kwargs: Any) -> None:
        LoggerHelper._get_logger().warning(msg, *args, **kwargs)

    @staticmethod
    def error(msg: str, *args: object, **kwargs: Any) -> None:
        LoggerHelper._get_logger().error(msg, *args, **kwargs)

    @staticmethod
    def success(msg: str, *args: object, **kwargs: Any) -> None:
        LoggerHelper._get_logger().log(LoggerHelper.SUCCESS_LEVEL, msg, *args, **kwargs)


LoggerHelper._add_success_method()
