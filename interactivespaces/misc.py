import logging

class Logger(object):
    """
        @summary: A common logger for this library
    """
    def __init__(self, logfile_path='ispaces-client.log'):
        self.logger = logging.getLogger(__name__)
        self.logfile_path = logfile_path
        logging.basicConfig(filename=self.logfile_path,
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level='INFO')

    def get_logger(self):
        return self.logger
