# This software is licensed with the Apache 2.0 license
#
# See the LICENSE file in the top level directory of this repository for
# license terms.
#
# Copyright 2024 David Wootton

from Request.Request import Request
from Util.Globals import Globals
from Worker.WorkerThread import WorkerThread

# Class to request background request processing thread terminate
class TerminationRequest(Request):

    def __init__(self):
        super().__init__()
        
    def processRequest(self):
        worker = Globals.getWorkerThread(Globals())
        worker.requestShutdown()
            
