from threading import Thread, Lock

class ThreadInterface:
    
    def update(self, screenshot):
        pass
    
    def start(self):
        """
        Starts separate thread for extended class behaviour
        """
        self.stopped = False
        t = Thread(target=self.run)
        t.start()
        
    def stop(self):
        """
        Shops threaed from execution in the becaground after program
        finishes
        """
        self.stopped = True
        
    def run(self):
        """Logic of the thread work"""
        pass