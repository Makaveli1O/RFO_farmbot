from threading import Thread, Lock

class ThreadInterface:
    
    def update(self, screenshot):
        pass
    
    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()
        
    def stop(self):
        self.stopped = True
        
    def run(self):
        """Implementation of the run method"""
        pass