# This software is licensed with the Apache 2.0 license
#
# See the LICENSE file in the top level directory of this repository for
# license terms.
#
# Copyright 2024 David Wootton

import json
import os
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QCheckBox
from PySide6.QtWidgets import QDialog
from PySide6.QtWidgets import QDialogButtonBox
from PySide6.QtWidgets import QGridLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QSpacerItem
from Util.Globals import Globals
from Widgets.XHFloatSlider import XHFloatSlider
from Widgets.XHSlider import XHSlider


class QueryParametersDialog(QDialog):

    # Initialize the dialog that allows the user to add or edit a LLM query profile
    def __init__(self, parent=None, profileName=None, profile=None):
        super().__init__(parent)
        self._profileName = profileName
        self._profile = profile

        self.setWindowTitle("Query Parameters")

        # Set up the dialog layout
        layout = QGridLayout(self)
        self.setLayout(layout)

        # Add the widgets to the layout
        row = 0
        label = QLabel('Profile name', self)
        layout.addWidget(label, row, 0)
        self._profileNameWidget = QLineEdit(self)
        if (self._profileName is not None):
            self._profileNameWidget.setReadOnly(True)
        layout.addWidget(self._profileNameWidget, row, 1, 1, 2)
        row = row + 1

        label = QLabel('Temperature', self)
        layout.addWidget(label, row, 0)
        self._temperatureWidget = XHFloatSlider(self, 1000.0, 0.0, 1.0, .1, 'Specify tempurature')
        layout.addWidget(self._temperatureWidget, row, 1, 1, 2)
        row = row + 1

        label = QLabel('Top P', self)
        layout.addWidget(label, row, 0)
        self._topPWidget = XHFloatSlider(self, 1000.0, 0.0, 1.0, .1, 'Specify top p')
        layout.addWidget(self._topPWidget, row, 1, 1, 2)
        row = row + 1

        label = QLabel('Top K', self)
        layout.addWidget(label, row, 0)
        self._topKWidget = XHSlider(self, 0, 200, 20,'Specify top k')
        layout.addWidget(self._topKWidget, row, 1, 1, 2)
        row = row + 1

        label = QLabel('Typical P', self)
        layout.addWidget(label, row, 0)
        self._typicalPWidget = XHFloatSlider(self, 1000.0, 0.0, 1.0, .1, 'Specify typical p')
        layout.addWidget(self._typicalPWidget, row, 1, 1, 2)                                                                                                                                     
        row = row + 1

        label = QLabel('Repetition Penalty', self)
        layout.addWidget(label, row, 0)
        self._repetitionPenaltyWidget = XHFloatSlider(self, 1000.0, 0.0, 1.5, .1, 'Specify repetition penalty')
        layout.addWidget(self._repetitionPenaltyWidget, row, 1, 1, 2)
        row = row + 1

        label = QLabel('Encoder Repetition Penalty', self)
        layout.addWidget(label, row, 0)
        self._encoderRepetitionPenaltyWidget = XHFloatSlider(self, 1000.0, 0.0, 1.5, .1, 'Specify encoder repetition penalty') 
        layout.addWidget(self._encoderRepetitionPenaltyWidget, row, 1, 1, 2)
        row = row + 1

        label = QLabel('No Repeat NGramSize', self)
        layout.addWidget(label, row, 0)
        self._noRepeatNGramSizeWidget = XHSlider(self, 0, 200, 20, 'Specify no repeat ngram size')
        layout.addWidget(self._noRepeatNGramSizeWidget, row, 1, 1, 2)
        row = row + 1

        label = QLabel('Minimum Length', self)
        layout.addWidget(label, row, 0)
        self._minimumLengthWidget = XHSlider(self, 0, 2000, 200, 'Specify minimum length')
        layout.addWidget(self._minimumLengthWidget, row, 1, 1, 2)
        row = row + 1

        label = QLabel('Penalty Alpha', self)
        layout.addWidget(label, row, 0)
        self._penaltyAlphaWidget = XHFloatSlider(self, 1000.0, 0.0, 5.0, .1, 'Specify penalty alpha')
        layout.addWidget(self._penaltyAlphaWidget, row, 1, 1, 2)
        row = row + 1

        label = QLabel('Beam count', self)
        layout.addWidget(label, row, 0)
        self._beamCountWidget = XHSlider(self, 1, 20, 5, 'Specify beam count')
        layout.addWidget(self._beamCountWidget, row, 1, 1, 2)
        row = row + 1

        label = QLabel('Length penalty', self)
        layout.addWidget(label, row, 0)
        self._lengthPenaltyWidget = XHFloatSlider(self, 10.0, -5.0, 5.0, .1, 'Specify length penalty')
        layout.addWidget(self._lengthPenaltyWidget, row, 1, 1, 2)
        row = row + 1

        self._doSampleWidget = QCheckBox('Do sample', self)
        self._doSampleWidget.setToolTip('Do sampling')
        layout.addWidget(self._doSampleWidget, row, 0)
        row = row + 1

        self._earlyStopWidget = QCheckBox('Early Stop', self)
        self._earlyStopWidget.setToolTip('Early Stop')
        layout.addWidget(self._earlyStopWidget, row, 0)
        row = row + 1

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        layout.addWidget(buttonBox, row, 0, 1, 3)
        buttonBox.accepted.connect(self.onLoad)
        buttonBox.rejected.connect(self.reject)
        row = row + 1

        spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout.addItem(spacer, row, 0, 1, 3)
        layout.setRowStretch(row, 1)

        # If a query profile is being edited, fill in the widgets with the current profile values
        if (self._profile is not None):
            self._profileNameWidget.setText(profileName)
            self._temperatureWidget.setValue(self._profile['tempurature'])
            self._topPWidget.setValue(self._profile['topP'])
            self._topKWidget.setValue(self._profile['topK'])
            self._typicalPWidget.setValue(self._profile['typicalP'])
            self._repetitionPenaltyWidget.setValue(self._profile['repetitionPenalty'])
            self._encoderRepetitionPenaltyWidget.setValue(self._profile['encoderRepetitionPenalty'])
            self._noRepeatNGramSizeWidget.setValue(self._profile['noRepeatNGramSize'])
            self._minimumLengthWidget.setValue(self._profile['minimumLength'])
            self._penaltyAlphaWidget.setValue(self._profile['penaltyAlpha'])
            self._beamCountWidget.setValue(self._profile['beamCount'])
            self._lengthPenaltyWidget.setValue(self._profile['lengthPenalty'])
            self._doSampleWidget.setChecked(self._profile['doSample'])
            self._earlyStopWidget.setChecked(self._profile['earlyStop'])

    # Get the name of this widget
    def getProfileName(self):
        return self._profileNameWidget.text().strip()
    
    # Validate a floating point number
    def isFloat(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False
            
    # Handle request to add or update a queryb profile. Validate the fields in the dialog, and if fields are valid then create a query profile or update
    # the current profile
    @Slot(bool)
    def onLoad(self):
        if (self._profile is None):
            if (self._profileNameWidget.text().strip() == ''):
                QMessageBox.critical(self, 'Error', 'Profile name is empty')
                return
        if (not self.isFloat(self._temperatureWidget.text())):
            QMessageBox.critical(self, 'Error', 'Tempurature value is not valid')
            return
        if (not self.isFloat(self._topPWidget.text())):
            QMessageBox.critical(self, 'Error', 'Top P value is not valid')
            return
        if (not self._topKWidget.text().isnumeric()):
            QMessageBox.critical(self, 'Error', 'Top K value is not valid')
            return
        if (not self.isFloat(self._typicalPWidget.text())):
            QMessageBox.critical(self, 'Error', 'Typical P value is not valid')
            return
        if (not self.isFloat(self._repetitionPenaltyWidget.text())):
            QMessageBox.critical(self, 'Error', 'Repetition Penalty value is not valid')
            return
        if (not self.isFloat(self._encoderRepetitionPenaltyWidget.text())):
            QMessageBox.critical(self, 'Error', 'Encoder Repetition Penalty value is not valid')
            return
        if (not self._noRepeatNGramSizeWidget.text().isnumeric()):
            QMessageBox.critical(self, 'Error', 'No Repeat NGramSize value is not valid')
            return
        if (not self._minimumLengthWidget.text().isnumeric()):
            QMessageBox.critical(self, 'Error', 'Minimum Length value is not valid')
            return
        if (not self.isFloat(self._penaltyAlphaWidget.text())):
            QMessageBox.critical(self, 'Error', 'Penalty Alpha value is not valid')
            return
        if (not self._beamCountWidget.text().isnumeric()):
            QMessageBox.critical(self, 'Error', 'Beam count value is not valid')
            return
        if (not self.isFloat(self._lengthPenaltyWidget.text())):
            QMessageBox.critical(self, 'Error', 'Length penalty value is not valid')
            return
        # Save query settings in the query profile object
        profiles = Globals().getProfiles()
        queryName = self._profileNameWidget.text().strip()
        if (self._profile is None):
            if (queryName  in profiles['queryProfiles']):
                QMessageBox.critical(self, 'Duplicate query', f'Profile {queryName} already exists')
                return
            self._profile = {}
        self._profile['tempurature'] = float(self._temperatureWidget.text())
        self._profile['topP'] = float(self._topPWidget.text())
        self._profile['topK'] = int(self._topKWidget.text())
        self._profile['typicalP'] = float(self._typicalPWidget.text())
        self._profile['repetitionPenalty'] = float(self._repetitionPenaltyWidget.text())
        self._profile['encoderRepetitionPenalty'] = float(self._encoderRepetitionPenaltyWidget.text())
        self._profile['noRepeatNGramSize'] = int(self._noRepeatNGramSizeWidget.text())
        self._profile['minimumLength'] = int(self._minimumLengthWidget.text())
        self._profile['penaltyAlpha'] = float(self._penaltyAlphaWidget.text())
        self._profile['beamCount'] = int(self._beamCountWidget.text())
        self._profile['lengthPenalty'] = float(self._lengthPenaltyWidget.text())
        self._profile['doSample'] = self._doSampleWidget.isChecked()
        self._profile['earlyStop'] = self._earlyStopWidget.isChecked()
        queryProfiles = profiles['queryProfiles']
        queryProfiles[queryName] = self._profile
        json.dump(Globals().getProfiles(), open(f'{os.path.expanduser("~")}/.DocAssistantProfile.json', 'w'), indent=4)
        self.accept()
