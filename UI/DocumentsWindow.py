# This software is licensed with the Apache 2.0 license
#
# See the LICENSE file in the top level directory of this repository for
# license terms.
#
# Copyright 2024 David Wootton

import pathlib
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from PySide6.QtCore import QFileInfo
from PySide6.QtCore import QSettings
from PySide6.QtCore import Qt
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QFileDialog
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QGridLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QSpacerItem
from PySide6.QtWidgets import QTableWidget
from PySide6.QtWidgets import QTableWidgetItem
from Request.LoadDocumentsRequest import LoadDocumentsRequest
from Util.Globals import  Globals
from Widgets.XLineEdit import XLineEdit
from Widgets.XHSlider import XHSlider
from pathlib import Path

# UI class to contain widgets used to load a set of documents
class DocumentsWindow(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Documents")
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)

        # Set up the window layout
        layout = QGridLayout(self)
        layout.setSpacing(8)

        # Create the widgets for this window
        row = 0
        layout.addWidget(QLabel('Index loaded:', self), row, 0)
        self._indexName = QLabel('', self)
        layout.addWidget(self._indexName, row, 1)
        row = row + 1

        layout.addWidget(QLabel('Document Path', self), row, 0)
        self._documentPathWidget = QLineEdit(self) 
        self._documentPathWidget.setToolTip('Enter the path to the document')
        layout.addWidget(self._documentPathWidget, row, 1)
        browseButton = QPushButton('Browse', self)
        browseButton.setToolTip('Browse for the document')
        layout.addWidget(browseButton, 0, 2)
        browseButton.clicked.connect(self.onBrowseButtonClicked)
        layout.addWidget(browseButton, row, 2)
        addDocument = QPushButton('Add', self)
        addDocument.setToolTip('Add the document')
        addDocument.clicked.connect(self.onAddButtonClicked)
        self._documentCount = 0
        layout.addWidget(addDocument, row, 3)
        row = row + 1

        layout.addWidget(QLabel('Documents', self), row, 0)
        self._documentsWidget = QTableWidget(5, 1, self)
        self._documentsWidget.setToolTip('Select the documents')
        self._documentsWidget.setSelectionBehavior(QTableWidget.SelectRows)
        self._documentsWidget.setSelectionMode(QTableWidget.SingleSelection)
        self._documentsWidget.horizontalHeader().setStretchLastSection(True)
        self._documentsWidget.horizontalHeader().setVisible(False)
        self._documentsWidget.verticalHeader().setVisible(False)
        self._documentsWidget.setAlternatingRowColors(True)
        layout.addWidget(self._documentsWidget, row, 1)
        deleteDocument = QPushButton('Delete', self)
        deleteDocument.setToolTip('Delete the selected documents')
        layout.addWidget(deleteDocument, row, 2)
        deleteDocument.clicked.connect(self.onDeleteButtonClicked)
        row = row + 1

        label = QLabel('Chunk size', self)
        layout.addWidget(label, row, 0)
        self._chunkSizeSlider = XHSlider(self,  1, 2000, 100, 'Specify size of chunks',  'Document.chunkSize')
        layout.addWidget(self._chunkSizeSlider, row, 1, 1, 2)
        row = row + 1

        label = QLabel('Chunk overlap', self)
        layout.addWidget(label, row, 0)
        self._overlapSlider = XHSlider(self, 1, 500, 50, 'Specify chunk overlap', 'Document.overlap')
        layout.addWidget(self._overlapSlider, row, 1, 1, 2)
        row = row + 1

        label = QLabel('Sentence transformer', self)
        layout.addWidget(label, row, 0)
        self._sentenceTransformerWidget = XLineEdit(self, 'Document.sentenceTransformer')
        self._sentenceTransformerWidget.setToolTip('Specify the sentence transformer')
        layout.addWidget(self._sentenceTransformerWidget, row, 1)
        transformerBrowseButton = QPushButton('Browse', self)
        transformerBrowseButton.setToolTip('Browse for the sentence transformer')
        layout.addWidget(transformerBrowseButton, row, 2)
        transformerBrowseButton.clicked.connect(self.onTransformerBrowseButtonClicked)
        row = row + 1

        loadButton = QPushButton('Load Documents', self)
        loadButton.setToolTip('Load the documents')
        loadButton.clicked.connect(self.onLoadButtonClicked)
        layout.addWidget(loadButton, row, 1)
        row = row + 1

        spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout.addItem(spacer, 5, 0, 1, 4)
        layout.setRowStretch(row, 1)

    # Handle a request to load a previously generated FAISS index
    @Slot(bool)
    def loadDocumentIndex(self, checked):
        settings = QSettings()
        documentPath = settings.value('DocumentsWindow.DocumentIndexPath', '/')
        selectedDirectory = QFileDialog.getExistingDirectory(self, 'Select the document index', documentPath)
        if (not selectedDirectory == ''):
            transformerPath = settings.value('DocumentsWindow.SentenceTransformer', '')
            if (not transformerPath == ''):
                embeddings = HuggingFaceEmbeddings(model_name=transformerPath)
            else:
                embeddings = HuggingFaceEmbeddings()
            indexPath = Path(selectedDirectory)
            settings.setValue('DocumentsWindow.DocumentIndexPath', str(indexPath.parent))
            self._indexName.setText(indexPath.name)
            vectorStore = FAISS.load_local(selectedDirectory, embeddings)
            Globals().setDocumentStore(vectorStore)

    # Handle request to add a selected document to the list of documents to load
    @Slot(bool)
    def onAddButtonClicked(self, checked):
            selectedFile = self._documentPathWidget.text().strip()
            if(selectedFile == ''):
                return
            fileInfo = QFileInfo(selectedFile)
            found = False
            tableItem = QTableWidgetItem(fileInfo.fileName())
            tableItem.setData(Qt.UserRole,  selectedFile)
            if (self._documentCount == 0):
                self._documentsWidget.setItem(0, 0, tableItem)
                self._documentCount = self._documentCount + 1
            else:
                for n in range(self._documentCount):
                    if(self._documentsWidget.item(n, 0).text() == fileInfo.fileName()):
                        found = True
                        break
                if(not found):
                    if (self._documentCount == self._documentsWidget.model().rowCount()):
                        self._documentsWidget.setRowCount(self._documentCount + 1)
                    self._documentsWidget.setItem(self._documentCount, 0, tableItem)
                    self._documentsWidget.sortItems(0, Qt.AscendingOrder)
                    self._documentCount = self._documentCount + 1

    # Let user select a document to load using a file selector dialog
    @Slot(bool)
    def onBrowseButtonClicked(self, checked):
        settings = QSettings()
        docDirectory = settings.value('DocumentsWindow.DocumentPath', '/')
        selectedFile = QFileDialog.getOpenFileName(self, 'Select a document', docDirectory, 
                       'PDF Document (*.pdf);;Word document (*.doc *.docx *.odt);;Power Point (*.ppt *.odp *.pptx);; HTML file (*.htm *.html);;CSV file (*.csv));All files (*.*)')
        if (not selectedFile[0] == ''):
            self._documentPathWidget.setText(selectedFile[0])
            fileInfo = QFileInfo(selectedFile[0])
            settings.setValue('DocumentsWindow.DocumentPath', fileInfo.dir().absolutePath())
        

    # Handle a request to delete a document from the list of documents to load
    @Slot(bool)
    def onDeleteButtonClicked(self, checked):
        selectedItems = self._documentsWidget.selectedItems()
        for item in selectedItems:
            self._documentsWidget.removeRow(item.row())
            self._documentCount = self._documentCount - 1
            if(self._documentCount == 0):
                self._documentsWidget.setRowCount(1)
            else:
                self._documentsWidget.setRowCount(self._documentCount)

    # Handle a request to load the selected documents into the FAISS index
    @Slot(bool)
    def onLoadButtonClicked(self, checked):
        if (self._documentCount == 0):
            QMessageBox.critical(self, 'Error', 'No documents loaded')
            return
        documents = {}
        for n in range(self._documentCount):
            documents[n] = self._documentsWidget.item(n, 0).data(Qt.UserRole)
        request = LoadDocumentsRequest()
        request.setDocumentList(documents, self._chunkSizeSlider.value(), self._overlapSlider.value(),
                                self._sentenceTransformerWidget.text().strip())
        workerThread = Globals.getWorkerThread(Globals())
        workerThread.enqueue(request)
        self._indexName.setText('')

    # Handle request to select a sentence transformer using a file selector dialog
    @Slot(bool)
    def onTransformerBrowseButtonClicked(self, checked):
        settings = QSettings()
        transformerDirectory = settings.value('DocumentsWindow.SentenceTransformerPath', '/')
        selectedDirectory = QFileDialog.getExistingDirectory(self, 'Select a sentence transformer', transformerDirectory)
        if (not selectedDirectory == ''):
            self._sentenceTransformerWidget.setText(selectedDirectory)
            settings.setValue('DocumentsWindow.SentenceTransformerPath', selectedDirectory)

    # Handle a request to save the FAISS index to disk
    @Slot(bool)
    def saveDocumentIndex(self, checked):
        index =  Globals().getDocumentStore()
        if (index == None):
            QMessageBox.critical(self, 'Error', 'No document index loaded')
            return
        settings = QSettings()
        documentPath = settings.value('DocumentsWindow.DocumentIndexPath', '/')
        selectedFile = QFileDialog.getSaveFileName(self, 'Select the document index', documentPath, 'FAISS index (*.faiss)')
        if (not selectedFile[0] == ''):
            fileInfo = QFileInfo(selectedFile[0])
            settings.setValue('DocumentsWindow.DocumentIndexPath', fileInfo.dir().absolutePath())
            index.save_local(selectedFile[0])
