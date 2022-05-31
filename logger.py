def init_logger():
    import datetime
    import logging

    log_path = '.'
    file_name = f'{datetime.datetime.now().strftime("%Y-%m-%d")}'
    log_formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    new_logger = logging.getLogger('vimeo_logger')
    new_logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(f"{log_path}/{file_name}.log")
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(logging.CRITICAL)
    new_logger.addHandler(file_handler)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    new_logger.addHandler(console_handler)
    return new_logger


