import logging

class Logger(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(filename='master.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level='INFO')
    
    def get_logger(self):
        return self.logger
