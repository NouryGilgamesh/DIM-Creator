import os
import logging
from logging.handlers import RotatingFileHandler
from utils import documents_dir

logger = logging.getLogger('DIMCreator')
logger.setLevel(logging.INFO)

DC_logs_dir = os.path.join(documents_dir(), "DIMCreator", "Logs")
os.makedirs(DC_logs_dir, exist_ok=True)
DC_log_file_path = os.path.join(DC_logs_dir, 'DIMCreator.log')
file_handler = RotatingFileHandler(DC_log_file_path, maxBytes=2_000_000, backupCount=3, encoding="utf-8")
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.info("DIMCreator started")
