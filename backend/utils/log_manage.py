import logging
import os
from config.base_config import settings
import datetime
from pythonjsonlogger import jsonlogger
from contextvars import ContextVar


_logger = None

# 新增 context_var
trace_id_var = ContextVar("trace_id", default="-")


# 新增 filter：把 trace_id 注入日志 record
class TraceIDFilter(logging.Filter):
    def filter(self, record):
        try:
            record.trace_id = trace_id_var.get()
        except LookupError:
            record.trace_id = "-"
        return True


class DailyRotatingFileHandler(logging.FileHandler):
    def __init__(self, log_dir, encoding=None):
        self.log_dir = log_dir
        self.current_date = datetime.date.today()
        self.current_month = self.current_date.strftime("%Y-%m")
        super().__init__(self._get_filename(), encoding=encoding)

    def _get_filename(self):
        month_dir = os.path.join(self.log_dir, self.current_month)
        os.makedirs(month_dir, exist_ok=True)
        return os.path.join(month_dir, f"{self.current_date}.log")

    def _update_file(self):
        new_date = datetime.date.today()
        new_month = new_date.strftime("%Y-%m")

        if new_date != self.current_date or new_month != self.current_month:
            self.current_date = new_date
            self.current_month = new_month
            new_filename = self._get_filename()

            if self.stream:
                self.stream.close()
                self.stream = None

            self.baseFilename = new_filename
            self.stream = self._open()

    def emit(self, record):
        self._update_file()
        super().emit(record)


def init_logger():
    global _logger
    if _logger is not None:
        return _logger

    level = settings.LOG_LEVEL
    log_dir = settings.LOG_DIR
    os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger()
    logger.setLevel(level)

    # 清除现有的 handler，防止重复添加
    if logger.hasHandlers():
        logger.handlers.clear()

    file_handler = DailyRotatingFileHandler(log_dir, encoding='utf-8')
    console_handler = logging.StreamHandler()

    # 在这里加入 trace_id 字段
    json_formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(threadName)s %(levelname)s %(trace_id)s %(message)s",
        datefmt='%Y-%m-%d %H:%M:%S',
        json_ensure_ascii=False,
    )

    file_handler.setFormatter(json_formatter)
    console_handler.setFormatter(json_formatter)

    # 给 handler 绑定 trace_id 过滤器
    file_handler.addFilter(TraceIDFilter())
    console_handler.addFilter(TraceIDFilter())

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    _logger = logger
    return _logger


def get_logger():
    if _logger is None:
        raise RuntimeError("日志未初始化，请先调用init_logger()")
    return _logger
