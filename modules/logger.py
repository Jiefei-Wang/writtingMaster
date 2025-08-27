import logging
module_logger = logging.getLogger("modules")
if not module_logger.hasHandlers():
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s', datefmt='%H:%M:%S')
    handler.setFormatter(formatter)
    module_logger.addHandler(handler)
module_logger.setLevel(logging.INFO)