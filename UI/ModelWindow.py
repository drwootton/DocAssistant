# This software is licensed with the Apache 2.0 license
#
# See the LICENSE file in the top level directory of this repository for
# license terms.
#
# Copyright 2024 David Wootton

import gc
import torch
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QComboBox
from PySide6.QtWidgets import QGridLayout
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QSpacerItem
from PySide6.QtWidgets import QWidget
from Request.LoadModelRequest import LoadModelRequest
from Dialogs.ModelDialog import ModelDialog
from Request.LoadModelRequest import LoadModelRequest
from Util.Globals import Globals
from Worker.WorkerThread import WorkerThread

# Window class containing widgets to manage loading LLM models
class ModelWindow(QFrame):

    # Create the widgets in the model window
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        
        # Set up the layout
        layout = QGridLayout(self)
        self.setLayout(layout)

        # Add the widgets to the layout
        row = 0
        layout.addWidget(QLabel("Model  profile", self), row, 0)
        self._modelProfileCombo = QComboBox(self)
        self._modelProfileCombo.addItems(Globals().getProfiles()['modelProfiles'].keys())
        self._modelProfileCombo.model().sort(0)
        self._modelProfileCombo.setToolTip('Select model profile')
        layout.addWidget(self._modelProfileCombo, row, 1)
        row += 1

        buttonBox = QWidget(self)
        buttonLayout = QHBoxLayout(buttonBox)
        buttonLayout.setContentsMargins(0, 0, 0, 0)
        buttonBox.setLayout(buttonLayout)
        addButton = QPushButton('Add', buttonBox)
        addButton.setToolTip('Click to add model profile')
        buttonLayout.addWidget(addButton)
        editButton = QPushButton('Edit', buttonBox)
        editButton.setToolTip('Click to edit model profile')
        buttonLayout.addWidget(editButton)
        deleteButton = QPushButton('Delete', buttonBox)
        deleteButton.setToolTip('Click to delete model profile')
        buttonLayout.addWidget(deleteButton)
        layout.addWidget(buttonBox, row, 1)
        row += 1

        loadUnloadBox = QWidget(self)
        buttonLayout = QHBoxLayout(loadUnloadBox)
        loadUnloadBox.setLayout(buttonLayout)
        buttonLayout.setContentsMargins(0, 0, 0, 0)
        loadUnloadBox.setLayout(buttonLayout)
        loadButton = QPushButton('Load', loadUnloadBox)
        loadButton.setToolTip('Click to load model profile')
        buttonLayout.addWidget(loadButton)
        unloadButton = QPushButton('Unload', loadUnloadBox)
        unloadButton.setToolTip('Click to unload current model')
        buttonLayout.addWidget(unloadButton)
        layout.addWidget(loadUnloadBox, row, 1)
        row += 1

        space = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addItem(space, row, 1, 2)
        layout.setRowStretch(1, 0)
        layout.setRowStretch(2, 0)
        layout.setRowStretch(row, 1)
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 0)

        try:
            self._modelProfileCombo.setCurrentText(Globals().getProfiles()['selectedModel'])
        except KeyError:
            pass

        # Set up button click event handlers
        addButton.clicked.connect(self.addModel)
        deleteButton.clicked.connect(self.deleteModel)
        editButton.clicked.connect(self.editModel)
        loadButton.clicked.connect(self.loadModel)
        unloadButton.clicked.connect(self.unloadModel)
        self._modelProfileCombo.currentTextChanged.connect(self.modelSelected)

    # Handle a request to add a model profile
    @Slot(bool)
    def addModel(self, checked):
        dialog = ModelDialog(self)
        if dialog.exec():
            self._modelProfileCombo.addItem(dialog.getProfileName())
            self._modelProfileCombo.model().sort(0)

    # Handle a request to edit a model profile
    @Slot(bool)
    def editModel(self, checked):
        selection = self._modelProfileCombo.currentText()
        if (selection == ''):
            QMessageBox.critical(self, 'Error', 'No model profile selected')
            return
        dialog = ModelDialog(self, selection, Globals().getProfiles()['modelProfiles'][selection])
        dialog.exec()

    # Handle a request to delete a model profile
    @Slot(bool)
    def deleteModel(self, checked):
        selection = self._modelProfileCombo.currentText()
        if (selection == ''):
            QMessageBox.critical(self, 'Error', 'No model profile selected')
            return
        self._modelProfileCombo.removeItem(self._modelProfileCombo.findText(selection))
        Globals().getProfiles()['modelProfiles'].pop(selection)     

    # Handle a request to load a model
    @Slot(bool)
    def loadModel(self, checked):
        selection = self._modelProfileCombo.currentText()
        if (selection == ''):
            QMessageBox.critical(self, 'Error', 'No model profile selected')
            return
        profile = Globals().getProfiles()['modelProfiles'][selection]
        request = LoadModelRequest()
        request.setModelParameters(profile)                           
        workerThread = Globals.getWorkerThread(Globals())
        workerThread.enqueue(request)

    # Set the selected model
    @Slot(str)
    def modelSelected(self, selection):
        Globals().getProfiles()['selectedModel'] = selection

    # Handle a request to unload a model
    @Slot(bool)
    def unloadModel(self, checked):
        model = Globals().getModel()
        if (not model == None):
            del model
        Globals().setModel(None)
        gc.collect()
        torch.cuda.empty_cache()
        tokenizer = Globals().getTokenizer()
        if (not tokenizer == None):
            del tokenizer
        Globals().setTokenizer(None)
        gc.collect()
        torch.cuda.empty_cache()
