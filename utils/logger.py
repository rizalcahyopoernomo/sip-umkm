# utils/logger.py

import logging
import os


# =========================================
# BASE DIRECTORY
# =========================================
BASE_DIR = os.path.abspath(
    os.path.dirname(
        os.path.dirname(__file__)
    )
)


# =========================================
# LOG DIRECTORY
# =========================================
LOG_DIR = os.path.join(
    BASE_DIR,
    'logs'
)

os.makedirs(
    LOG_DIR,
    exist_ok=True
)


# =========================================
# LOG FILE
# =========================================
LOG_FILE = os.path.join(
    LOG_DIR,
    'system.log'
)


# =========================================
# LOGGER CONFIGURATION
# =========================================
logging.basicConfig(

    level=logging.INFO,

    format=(

        '[%(asctime)s] '

        '%(levelname)s | '

        '%(message)s'
    ),

    datefmt='%Y-%m-%d %H:%M:%S',

    handlers=[

        # =====================================
        # FILE LOGGER ONLY
        # =====================================
        logging.FileHandler(

            LOG_FILE,

            encoding='utf-8'
        )
    ]
)


# =========================================
# LOGGER INSTANCE
# =========================================
logger = logging.getLogger(
    'SIP-UMKM'
)


# =========================================
# LOGGER LEVEL
# =========================================
logger.setLevel(
    logging.INFO
)


# =========================================
# DISABLE TERMINAL PROPAGATION
# =========================================
logger.propagate = False


# =========================================
# PREVENT DUPLICATE HANDLER
# =========================================
if logger.hasHandlers():

    logger.handlers.clear()


# =========================================
# CUSTOM FILE HANDLER
# =========================================
file_handler = logging.FileHandler(

    LOG_FILE,

    encoding='utf-8'
)

file_handler.setLevel(
    logging.INFO
)


# =========================================
# LOG FORMATTER
# =========================================
formatter = logging.Formatter(

    '[%(asctime)s] '

    '%(levelname)s | '

    '%(message)s',

    datefmt='%Y-%m-%d %H:%M:%S'
)

file_handler.setFormatter(
    formatter
)


# =========================================
# ATTACH HANDLER
# =========================================
logger.addHandler(
    file_handler
)


# =========================================
# LOGGER STARTUP TEST
# =========================================
logger.info(
    'Logger initialized successfully'
)