"""
Define singleton class loger, that enables or disables logging
"""
class Logger:
    def __init__(self, statement = False):
        self._log = statement
    
    def enabled(self, statement):
        self._log = statement
        
    def log(self, msg):
        if self._log is True:
            print(msg)
        else:
            pass