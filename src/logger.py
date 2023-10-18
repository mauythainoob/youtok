"""
A singleton logger class to be used across the codebase.
"""
import logging
import inspect

from typing import Union


class SingletonLogger:
    """
    Singleton class for logging.
    """

    _instance: Union[None, "SingletonLogger"] = None

    def __new__(cls) -> None:
        """
        Where the singleton magic happens.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__configure_logger()
        return cls._instance

    def __configure_logger(self) -> None:
        """
        Configures the logger.
        """
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        handler: logging.StreamHandler = logging.StreamHandler()
        formatter: logging.Formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] [%(caller)s] %(message)s"
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def __log_caller(self, level: str, msg: str, *args, **kwargs) -> None:
        """
        The log caller. This handles the different levels of logging. It also
        handles where the log came from (i.e a function, method, etc.)

        Args:
            level (str): The log level.
            msg (str): The log message.
        """
        caller = inspect.stack()[2]
        caller_name = caller.function
        if "self" in caller.frame.f_locals:
            caller_name = (
                f"{caller.frame.f_locals['self'].__class__.__name__}.{caller_name}"
            )
        extra = {"caller": caller_name}
        getattr(self.logger, level.lower())(msg, *args, **kwargs, extra=extra)

    def debug(self, msg, *args, **kwargs) -> None:
        """
        Debug logger.
        """
        self.__log_caller("debug", msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs) -> None:
        """
        Info logger.
        """
        self.__log_caller("info", msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs) -> None:
        """
        Warning logger.
        """
        self.__log_caller("warning", msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs) -> None:
        """
        Error logger.
        """
        self.__log_caller("error", msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs) -> None:
        """
        Critical logger.
        """
        self.__log_caller("critical", msg, *args, **kwargs)
