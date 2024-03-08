# This software is licensed with the Apache 2.0 license
#
# See the LICENSE file in the top level directory of this repository for
# license terms.
#
# Copyright 2024 David Wootton

from PySide6.QtCore import QObject
from PySide6.QtCore import Signal

class ResultSignal(QObject):
    resultMessage = Signal(str)

class LogSignal(QObject):
    logMessage = Signal(str)

class Globals():

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Globals, cls).__new__(cls)
            cls._logEvent = LogSignal()
            cls._resultEvent = ResultSignal()
            cls._model = None
            cls._tokenizer = None
            cls._documentStore = None
        return cls.instance

    def getDocumentEmbeddings(self):
        return self._embeddingsFromDocuments
    
    def getDocumentStore(self):
        return self._documentStore
    
    def getModel(self):
        return self._model
    
    def getProfiles(self):
        return self._profiles
    
    def getQueryStop(self):
        return self._stopQuery 
    
    def getTokenizer(self):
        return self._tokenizer
    
    def getWorkerThread(self):
        return self._workerThread;

    def logMessage(self, message):
        self._logEvent.logMessage.emit(message)

    def postAnswer(self, answer):
        self._resultEvent.resultMessage.emit(answer)

    def setDocumentEmbeddings(self, embeddings):
        self.embeddingsFromDocuments = embeddings
        
    def setDocumentStore(self, store):
        self._documentStore = store

    def setModel(self, model):
        self._model = model

    def setProfiles(self, profiles):
        self._profiles = profiles

    def setStopQuery(self, flag):
        self._stopQuery = flag

    def setTokenizer(self, tokenizer):
        self._tokenizer = tokenizer
        
    def setWorkerThread(self, thread):
        self._workerThread = thread
