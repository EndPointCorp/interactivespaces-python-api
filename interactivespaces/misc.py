import logging

class PathLogger(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logging.basicConfig(filename='path.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level='INFO')
    
    def get_logger(self):
        return self.logger
    
class ExceptionLogger(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logging.basicConfig(filename='exception.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level='INFO')
    
    def get_logger(self):
        return self.logger
    
class MasterLogger(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logging.basicConfig(filename='master.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level='INFO')
    
    def get_logger(self):
        return self.logger