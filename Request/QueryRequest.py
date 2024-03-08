# This software is licensed with the Apache 2.0 license
#
# See the LICENSE file in the top level directory of this repository for
# license terms.
#
# Copyright 2024 David Wootton

import gc
from langchain.chains import RetrievalQA
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain.schema import LLMResult
from langchain_community.llms import HuggingFacePipeline
from langchain_community.llms import LlamaCpp
from langchain_community.vectorstores import FAISS
from Request.Request import Request
from threading import Thread
from transformers import pipeline
from transformers import StoppingCriteria
from transformers import StoppingCriteriaList
from transformers import TextIteratorStreamer
from Util.Globals import Globals
import queue
import time
import torch

# This class is used to request a model stop generating output tokens
class QueryStop(StoppingCriteria):
    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
        if (Globals().getQueryStop()):
            return True
        return False

# Handle a request to query a set of documents
class QueryRequest(Request):
    def __init__(self):
        super().__init__()

    # Process a request to query documents
    def processRequest(self):
        self._documentStore = Globals().getDocumentStore()
        if (self._documentStore is None):
            Globals().logMessage('No documents loaded')
            return
        tokenizer = Globals().getTokenizer()
        streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, timeout=10.0)
        # Set up request parameters
        params = {}
        params['max_new_tokens'] = self._maxNewTokens
        params['temperature'] = self._temperature
        params['top_p'] = self._topP
        params['top_k'] = self._topK
        params['typical_p'] = self._typicalP
        params['repetition_penalty'] = self._repetitionPenalty
        params['encoder_repetition_penalty'] = self._encoderRepetitionPenalty
        params['no_repeat_ngram_size'] = self._noRepeatNGramSize
        params['min_length'] = self._minLength
        params['penalty_alpha'] = self._penaltyAlpha
        params['num_beams'] = self._beamCount
        params['length_penalty'] = self._lengthPenalty
        params['early_stopping'] = self._earlyStopping
        params['do_sample'] = self._doSample
        params['streamer'] = streamer

        # Display the query in the output window
        Globals().postAnswer(f'\n{self._query}\n')

        # Set up the pipeline
        model = Globals().getModel()
        if (isinstance(model, LlamaCpp)):
            self.runLlamaCppQuery()
        else:
            self.runHuggingFaceQuery(params)

    # Issue a query to a model in HuggingFace format
    def runHuggingFaceQuery(self, params):
        
        queryStop = StoppingCriteriaList([QueryStop()])
        Globals().setStopQuery(False)
        # Create the pipeline to process the request
        pipe = pipeline('text-generation', model=Globals().getModel(), tokenizer=Globals().getTokenizer(), stopping_criteria=queryStop, **params)
        hfPipeline = HuggingFacePipeline(pipeline=pipe)
        chain = load_qa_chain(hfPipeline, chain_type='stuff')
        Globals().logMessage('Starting similarity search')
        # Run a similarity search agains the FAISS vector store to find document fragments to use to query the model
        startTime = time.time()
        results = self._documentStore.similarity_search(self._query, k=self._numMatches)
        elapsedTime = time.time() - startTime
        Globals().logMessage(f'Completed similarity search in {elapsedTime:.3f} seconds')

        Globals().logMessage('Starting query')
        startTime = time.time()
        chainArgs = dict(input_documents=results, question=self._query)

        # Run the chain.run() function in the newly created thread. Note that as of 5/22/2023, there is a bug in the HuggingFace transformers library
        # that triggers an exception when the thread is run. This bug is solved by applying the code change described in 
        # https://github.com/huggingface/transformers/pull/23641
        gc.collect()
        torch.cuda.empty_cache()
        thread = Thread(target=chain.run, kwargs=chainArgs)
        thread.start()
        try:
            for newText in params['streamer']:
                Globals().postAnswer(newText)
                #if ((not newText == None) and (tokenizer.eos_token in newText)):
                #    break
        except queue.Empty:
            pass
        thread.join()
        elapsedTime = time.time() - startTime
        Globals().postAnswer('\n\n')
        Globals().logMessage(f'Completed query in {elapsedTime:.3f} seconds')
        del chain
        chain = None
        del hfPipeline
        hfPipeline = None
        del pipe
        pipe = None
        gc.collect()
        torch.cuda.empty_cache()

    # Run a document query against a LlamaCPP format model
    def runLlamaCppQuery(self):
        model = Globals().getModel()
        params = {}
        params['max_tokens'] = self._maxNewTokens
        params['repeat_penalty'] = self._repetitionPenalty
        params['temperature'] = self._temperature
        params['top_k'] = self._topK
        params['top_p'] = self._topP 
        params['verbose'] = True
        params['n_ctx'] = 1024
        params['n_threads'] = 20
        params['xxx'] = 'junk'
        queryStop = StoppingCriteriaList([QueryStop()])
        Globals().setStopQuery(False)
        startTime = time.time()
        Globals().logMessage('Starting query')
        chain = RetrievalQA.from_chain_type(llm=Globals().getModel(), chain_type='stuff', 
                                            retriever=Globals().getDocumentStore().as_retriever(search_kwargs={'k': self._numMatches}, kwargs=params))
        result = chain.run(query=self._query)
        del chain
        chain = None
        gc.collect()
        torch.cuda.empty_cache()

        endTime = time.time()
        elapsedTime = endTime - startTime
        Globals().logMessage(f'Completed query in {elapsedTime:.3f} seconds')

    # Set up query parameters
    def setQueryParameters(self, query, profile, maxNewTokens, numMatches):
        self._maxNewTokens = maxNewTokens
        self._query = query
        self._temperature = profile['tempurature']
        self._topP = profile['topP']
        self._topK = profile['topK']
        self._typicalP = profile['typicalP']
        self._repetitionPenalty = profile['repetitionPenalty']
        self._encoderRepetitionPenalty = profile['encoderRepetitionPenalty']
        self._noRepeatNGramSize = profile['noRepeatNGramSize']
        self._minLength = profile['minimumLength']
        self._penaltyAlpha = profile['penaltyAlpha']
        self._beamCount = profile['beamCount']
        self._lengthPenalty = profile['lengthPenalty']
        self._earlyStopping = profile['earlyStop']
        self._doSample = profile['doSample']
        self._numMatches = numMatches
