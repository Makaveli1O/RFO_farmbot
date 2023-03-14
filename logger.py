"""
Define singleton class loger, that enables or disables logging
"""
class Logger:
    def __init__(self, statement = False):
        self._log = statement
    
    def enabled(self, statement):
        self._log = statement
        
    def log(self, msg, log_me = False):
        """ Only prints when logger is enabled """
        if self._log is True or log_me is True:
            print(msg)
        else:
            pass
        
    def notice(self, msg):
        """ Prints a notice message"""
        print(msg)