from threading import Thread
import threading
import time
import logging

class threadMonitor(Thread):

    def __init__(self,LOGER=None):
        super(threadMonitor, self).__init__()
        if LOGER is None:
            self.LOGER = logging.getLogger()
        else:
            self.LOGER=LOGER

        self.list_threads={}
        self.count = 0



    def AppendThread(self,thread_ref):
        thread_id = self.count
        self.count+=1
        self.list_threads[thread_id]=thread_ref

    def run(self):
        while(True):
            self.LOGER.debug(threading.enumerate())
            list_threads = self.list_threads.copy()
            for t_key in list_threads:
                if not self.list_threads[t_key].is_alive(): #si murió
                    #self.LOGER.error("eliminando")
                    self.list_threads[t_key].join()
                    self.list_threads[t_key].terminate()
                    self.list_threads[t_key].close()
                    #self.list_threads[t_key].kill()

                    #self.LOGER.error("ELIMINADO")
                    del self.list_threads[t_key]
                else:
                    self.LOGER.debug("aun esta vivo")
            time.sleep(10)