# app/logger.py
import logging
import sys
from pythonjsonlogger import jsonlogger  # Thư viện hỗ trợ format JSON (cài qua pip)

from app import config


def setup_logging():
    """Cấu hình logging cho ứng dụng."""
    log_level = config.LOG_LEVEL

    # Tạo logger gốc
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Cấu hình handler gửi log ra stdout
    handler = logging.StreamHandler(sys.stdout)
    # Định dạng log: ở đây dùng JSONFormatter để phù hợp với ELK
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Ví dụ log ban đầu
    logging.info("Logging is configured. Level: %s", log_level)
