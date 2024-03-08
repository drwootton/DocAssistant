# This software is licensed with the Apache 2.0 license
#
# See the LICENSE file in the top level directory of this repository for
# license terms.
#
# Copyright 2024 David Wootton

from Dialogs.QueryParametersDialog import QueryParametersDialog
from PySide6.QtCore import Qt
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QComboBox
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QGridLayout
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QSpacerItem
from PySide6.QtWidgets import QTextEdit
from PySide6.QtWidgets import QWidget
from Request.QueryRequest import QueryRequest
from Util.Globals import Globals
from Widgets.XHSlider import XHSlider

# Class to handle user prompts to query documents
class PromptWindow(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setLineWidth(1)
        self.setMidLineWidth(0)

        # Set up the layout
        layout = QGridLayout(self)
        self.setLayout(layout)

        # Set up widgets in this window
        row = 0
        label = QLabel('Prompt', self)
        layout.addWidget(label, row, 0, 1, 1, Qt.AlignTop)
        self._input = QTextEdit(self)
        self._input.setAlignment(Qt.AlignLeft)
        self._input.setToolTip('Enter question to query document')
        layout.addWidget(self._input, row, 1, 1, 2)
        row = row + 1

        label = QLabel('Profile', self)
        layout.addWidget(label, row, 0)
        self._profileCombo = QComboBox(self)
        self._profileCombo.setToolTip('Select query parameter profile')
        self._profileCombo.addItems(Globals().getProfiles()['queryProfiles'].keys())
        self._profileCombo.model().sort(0)
        layout.addWidget(self._profileCombo, row, 1, 1, 2)
        row = row + 1

        buttonBox = QWidget(self)
        buttonLayout = QHBoxLayout(buttonBox)
        buttonLayout.setContentsMargins(0, 0, 0, 0)
        buttonBox.setLayout(buttonLayout)
        addButton = QPushButton('Add', buttonBox)
        addButton.setToolTip('Click to add new query profile')
        buttonLayout.addWidget(addButton)
        editButton = QPushButton('Edit', buttonBox)
        editButton.setToolTip('Click to edit selected query profile')
        buttonLayout.addWidget(editButton)
        deleteButton = QPushButton('Delete', buttonBox)
        deleteButton.setToolTip('Click to delete selected profile')
        buttonLayout.addWidget(deleteButton)
        layout.addWidget(buttonBox, row, 1, 1, 2)
        row = row + 1

        label = QLabel('Max new tokens', self)
        layout.addWidget(label, row, 0)
        self._maxNewTokensWidget = XHSlider(self, 1, 8192, 100, 'Specify maximum number of new tokens to add', 'ModelWindow_MaxNewTokens')
        layout.addWidget(self._maxNewTokensWidget, row, 1, 1, 2)
        row = row + 1

        label = QLabel('Number of document matches', self)
        layout.addWidget(label, row, 0)
        self._matchesWidget = XHSlider(self, 1, 20, 2,  'Specify number of document matches', 'ModelWindow_Matches')
        layout.addWidget(self._matchesWidget, row, 1, 1, 2)
        row = row + 1

        submitButton = QPushButton('Submit', self)
        submitButton.setToolTip('Click to submit query')
        layout.addWidget(submitButton, row, 1, 1, 1)
        stopButton = QPushButton('Stop', self)
        stopButton.setToolTip('Click to stop query')
        layout.addWidget(stopButton, row, 2, 1, 1)
        row = row + 1

        spacer = QSpacerItem(0, 0)
        layout.addItem(spacer, row, 0, 1, 1)
        layout.setRowStretch(row, 1)

        try:
            self._profileCombo.setCurrentText(Globals().getProfiles()['selectedQueryProfile'])
        except KeyError:
            pass

        # Connect signals to slots
        addButton.clicked.connect(self.doAddProfile)
        deleteButton.clicked.connect(self.doDeleteProfile)
        editButton.clicked.connect(self.doEditProfile)
        submitButton.clicked.connect(self.doSubmit)
        stopButton.clicked.connect(self.doQueryStop)
        self._profileCombo.currentTextChanged.connect(self.profileSelected) 

    # Slot to add new query profile
    @Slot(bool)
    def doAddProfile(self, checked):
        dialog = QueryParametersDialog(self)
        if (dialog.exec()):
            self._profileCombo.addItem(dialog.getProfileName())
            self._profileCombo.model().sort(0)

    # Slot to delete query profile
    @Slot(bool)
    def doDeleteProfile(self, checked):
        selection = self._profileCombo.currentText()
        if (selection == ''):
            QMessageBox.critical(self, 'Error', 'No query profile selected')
            return
        self._profileCombo.removeItem(self._profileCombo.findText(selection))
        Globals().getProfiles()['queryProfiles'].pop(selection)     
    
    # Slot to edit query profile
    @Slot(bool)
    def doEditProfile(self, checked):
        selection = self._profileCombo.currentText()
        if (selection == ''):
            QMessageBox.critical(self, 'Error', 'No query profile selected')
            return
        dialog = QueryParametersDialog(self, selection, Globals().getProfiles()['queryProfiles'][selection])
        dialog.exec()


    @Slot(bool)
    def doQueryStop(self, checked):
        Globals().setStopQuery(True)

    # Submit query request
    @Slot(bool)
    def doSubmit(self, checked):
        request = QueryRequest()
        request.setQueryParameters(self._input.toPlainText(), Globals().getProfiles()['queryProfiles'][self._profileCombo.currentText()],
                                   self._maxNewTokensWidget.value(), self._matchesWidget.value())
                                   
        workerThread = Globals.getWorkerThread(Globals())
        workerThread.enqueue(request)

    # record which profile is selected
    @Slot(str)
    def profileSelected(self, selection):
        Globals().getProfiles()['selectedQueryProfile'] = selection
