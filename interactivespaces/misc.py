import logging

class Logger(object):
    """
        @summary: A common logger for this library
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(filename='master.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level='INFO')
    
    def get_logger(self):
        return self.logger
