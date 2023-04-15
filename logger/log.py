from sanic.log import logger


class Log():
    def __init__(self) -> None:
        self.log_obj = logger()
    def log_action(self, function, *args, **kwargs):
        self.log_obj()

