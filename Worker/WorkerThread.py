# This software is licensed with the Apache 2.0 license
#
# See the LICENSE file in the top level directory of this repository for
# license terms.
#
# Copyright 2024 David Wootton

from multiprocessing import Queue
import sys
import traceback

from PySide6.QtCore import QThread


class WorkerThread(QThread):

    def __init__(self):
        super().__init__(None)
        self._instance = self
        self._requestQueue = Queue()
        self._shutdownRequested = False
        self._instance = None
        
    def __new__(cls):
        if (not hasattr(cls, 'instance')):
            cls.instance = super(WorkerThread, cls).__new__(cls)
        return cls.instance
    
    def dequeue(self):
        return self._requestQueue.get()
        
    def enqueue(self, request):
        self._requestQueue.put(request)
        
    def requestShutdown(self):
        self._shutdownRequested = True
            
    def run(self):
        while (not self._shutdownRequested):
            request = self.dequeue()
            try:
                request.processRequest()
            except Exception as err:
                print(f"Worker thread request handling encountered an exception with type {type(err)}, traceback is")
                traceback.print_exc(file=sys.stdout)
