# This software is licensed with the Apache 2.0 license
#
# See the LICENSE file in the top level directory of this repository for
# license terms.
#
# Copyright 2024 David Wootton

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import CSVLoader
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import UnstructuredHTMLLoader
from langchain_community.document_loaders import UnstructuredPowerPointLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores.faiss import FAISS
from Request.Request import Request
import time
import torch
from Util.Globals import Globals

class LoadDocumentsRequest(Request):
    def __init__(self):
        super().__init__()

# Process a request to convert a set of one or more input documents into a FAISS index
    def processRequest(self):
        documentText = ''
        # Load all documents using appropriate document loader and extract all text in the document into a single string.
        Globals().logMessage('Loading documents')
        startTime = time.time()
        for n in range(len(self._documentList)):
            doc = self._documentList[n]
            if (doc.endswith('.pdf')):
                loader = PyPDFLoader(doc)
                pages = loader.load_and_split()
                for page in pages:
                    documentText = documentText + page.page_content
            elif (doc.endswith('.doc') or doc.endswith('docx') or doc.endswith('odt')):
                loader = Docx2txtLoader(doc)
                dataBlock = loader.load()
                for data in dataBlock:
                    documentText = documentText + data.page_content
            elif (doc.endswith('.html') or doc.endswith('.htm') or doc.startswith('http')):
                loader = UnstructuredHTMLLoader(doc)
                dataBlock = loader.load()
                for data in dataBlock:
                    documentText = documentText + data.page_content
            elif (doc.endswith('.ppt') or doc.endswith('.pptx') or doc.endswith('.odp')):
                loader = UnstructuredPowerPointLoader(doc)
                dataBlock = loader.load()
                for data in dataBlock:
                    documentText = documentText + data.page_content
            elif (doc.endswith('.csv')):
                loader = CSVLoader(doc)
                dataBlock = loader.load()
                for data in dataBlock:
                    documentText = documentText + data.page_content

        elapsedTime = time.time() - startTime
        Globals().logMessage(f'Loaded documents in {elapsedTime:.3f} seconds')
        # Split the text string into chunks small enough that they can be processed in generating the vectorstore and used by the language model.
        textSplitter = RecursiveCharacterTextSplitter(chunk_size=self._chunkSize, chunk_overlap=self._overlap)
        # Split the text into chunks
        Globals().logMessage('Splitting text into chunks')
        startTime = time.time()
        texts = textSplitter.split_text(documentText)
        elapsedTime = time.time() - startTime
        Globals().logMessage(f'Split text in {elapsedTime:.3f} seconds')
        # Convert the text chunks into a vectorstore
        Globals().logMessage("Converting text chunks to vectorstore")
        startTime = time.time()
        if (len(self._sentenceTransformer) > 0):
            embeddings = HuggingFaceEmbeddings(model_name=self._sentenceTransformer)
        else:
            embeddings = HuggingFaceEmbeddings()
        vectorStore = FAISS.from_texts(texts, embeddings)
        elapsedTime = time.time() - startTime
        # clean up storage allocations no longert needed
        del embeddings
        embeddings = None
        torch.cuda.empty_cache()
        Globals().logMessage(f'Converted text chunks to vectorstore in {elapsedTime:.3f} seconds')
        Globals().setDocumentStore(vectorStore)

    # Get the attributes used to load the documents
    def setDocumentList(self, documents, chunkSize, overlap, sentenceTransformer):
        self._documentList = documents
        self._chunkSize = chunkSize
        self._overlap = overlap
        self._sentenceTransformer = sentenceTransformer
