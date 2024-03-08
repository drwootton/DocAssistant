# This software is licensed with the Apache 2.0 license
#
# See the LICENSE file in the top level directory of this repository for
# license terms.
#
# Copyright 2024 David Wootton

import json
import os
from PySide6.QtCore import QFileInfo
from PySide6.QtCore import Qt
from PySide6.QtCore import QSettings
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QCheckBox
from PySide6.QtWidgets import QDialog
from PySide6.QtWidgets import QDialogButtonBox
from PySide6.QtWidgets import QFileDialog
from PySide6.QtWidgets import QGridLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QSpacerItem
from Util.Globals import Globals
from Widgets.XHSlider import XHSlider
import torch


class ModelDialog(QDialog):
    
    # Create the dialog that can create or edit a LLM model profile
    def __init__(self, parent=None, profileName=None, profile=None):
        super().__init__(parent)
        self._profile = profile

        self.setWindowTitle('Specify Model Parameters')

        # Set up the dialog's layout
        layout = QGridLayout(self)
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 0)
        self.setLayout(layout)

        # Add the widgets to the layout
        row = 0
        label = QLabel('Profile name', self)
        layout.addWidget(label, row, 0)
        self._profileNameWidget = QLineEdit(self)
        layout.addWidget(self._profileNameWidget, row, 1)
        if (profileName is not None):
            self._profileNameWidget.setReadOnly(True)
            self._profileNameWidget.setText(profileName)
        row = row + 1

        label = QLabel('Model path', self)
        layout.addWidget(label, row, 0)
        self._modelPathWidget = QLineEdit(self)
        self._modelPathWidget.setToolTip('Specify path to model directory or model file')
        layout.addWidget(self._modelPathWidget, row, 1)
        browseButton = QPushButton('Browse', self)
        browseButton.clicked.connect(self.onBrowse)
        layout.addWidget(browseButton, row, 2)
        row = row + 1

        label = QLabel('Model overflow path', self)
        layout.addWidget(label, row, 0)
        self._overflowPathWidget = QLineEdit(self)
        self._overflowPathWidget.setToolTip('Specify directory for model overflow to disk')
        layout.addWidget(self._overflowPathWidget, row, 1)
        browseButton = QPushButton('Browse', self)
        browseButton.clicked.connect(self.onModelOverflow)
        layout.addWidget(browseButton, row, 2)
        row = row + 1

        label = QLabel('Max CPU memory(MB)', self)
        layout.addWidget(label, row, 0)
        self._maxCpuMemoryWidget = XHSlider(self, 0, 128000, 5000, 'Specify maximum CPU memory to use')
        layout.addWidget(self._maxCpuMemoryWidget, row, 1, 1, 2)
        row = row + 1

        self._gpuWidgets = []
        self._gpuCount = torch.cuda.device_count()
        for i in range(self._gpuCount):
            gpuName = torch.cuda.get_device_name(i)
            idx = gpuName.upper().find('RTX')
            if idx > 0:
                gpuName = gpuName[idx:]
            else:
                gpuName = f'GPU {i}'
            label = QLabel(f'Max GPU {gpuName} memory(MB)', self)
            layout.addWidget(label, row, 0)
            maxMemoryWidget = XHSlider(self, 0, 80000, 5000, f'Specify {gpuName} memory to use')
            layout.addWidget(maxMemoryWidget, row, 1, 1, 2)
            self._gpuWidgets.append(maxMemoryWidget)
            row = row + 1

        self._autoDevice = QCheckBox('Auto device', self)
        self._autoDevice.setToolTip('Click to use automatic device allocation')
        layout.addWidget(self._autoDevice, row, 0, 1, 1)
        row = row + 1

        self._OverflowToDisk = QCheckBox('Overflow to disk', self)
        self._OverflowToDisk.setToolTip('Click to overflow model to disk')
        layout.addWidget(self._OverflowToDisk, row, 0, 1, 1)
        row = row + 1

        self._useTriton = QCheckBox('Use Triton', self)
        self._useTriton.setToolTip('Click to use Triton for inference')
        layout.addWidget(self._useTriton, row, 0, 1, 1)
        row = row + 1

        self._useCPU = QCheckBox('Use CPU', self)
        self._useCPU.setToolTip('Click to use CPU for inference')
        layout.addWidget(self._useCPU, row, 0, 1, 1)
        row = row + 1

        self._use16Bit = QCheckBox('Use 16-bit', self)
        self._use16Bit.setToolTip('Click to use 16-bit floating point for inference')
        layout.addWidget(self._use16Bit, row, 0, 1, 1)
        row = row + 1

        self.use8Bit = QCheckBox('Use 8-bit', self)
        self.use8Bit.setToolTip('Click to use 8-bit floating point for inference')
        layout.addWidget(self.use8Bit, row, 0, 1, 1)
        row = row + 1

        self._use4Bit = QCheckBox('Use 4-bit', self)
        self._use4Bit.setToolTip('Click to use 4-bit quantization for inference')
        layout.addWidget(self._use4Bit, row, 0, 1, 1)
        row = row + 1

        self.trustRemoteCode = QCheckBox('Trust remote code', self)
        self.trustRemoteCode.setToolTip('Click to trust execution of remote code')
        layout.addWidget(self.trustRemoteCode, row, 0, 1, 1)
        row = row + 1

        self._useSafeTensors = QCheckBox('Use safe tensors', self)
        self._useSafeTensors.setToolTip('Click to use safe tensors file format')
        layout.addWidget(self._useSafeTensors, row, 0, 1, 1)
        row = row + 1

        label = QLabel('WBits', self)
        layout.addWidget(label, row, 0)
        self._wBits = QLineEdit(self)
        self._wBits.setToolTip('Specify number of bits to use for floating point values')
        layout.addWidget(self._wBits, row, 1, 1, 1)
        row = row + 1

        label = QLabel('Group size', self)
        layout.addWidget(label, row, 0)
        self._groupSize = QLineEdit(self)
        self._groupSize.setToolTip('Specify number of elements in a group')
        layout.addWidget(self._groupSize, row, 1, 1, 1)
        row = row + 1

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        layout.addWidget(buttonBox, row, 0, 1, 3)
        buttonBox.accepted.connect(self.onLoad)
        buttonBox.rejected.connect(self.reject)
        row = row + 1

        spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout.addItem(spacer, row, 0, 1, 3)
        layout.setRowStretch(row, 1)

        # If the user is editing a profile then fill in the widgets with current profile values
        if (self._profile is not None):
            self._modelPathWidget.setText(self._profile['modelPath'])
            self._overflowPathWidget.setText(self._profile['overflowPath'])
            self._maxCpuMemoryWidget.setValue(self._profile['maxCpuMemory'])
            gpuMemory = self._profile['gpuMemory']
            for i in range(self._gpuCount):
                self._gpuWidgets[i].setValue(str(gpuMemory[str(i)]))
            self._autoDevice.setChecked(self._profile['autoDevice'])
            self._OverflowToDisk.setChecked(self._profile['overflowToDisk'])
            self._useTriton.setChecked(self._profile['useTriton'])
            self._useCPU.setChecked(self._profile['useCPU'])
            self._use16Bit.setChecked(self._profile['use16Bit'])
            self.use8Bit.setChecked(self._profile['use8Bit'])
            self._use4Bit.setChecked(self._profile['use4Bit'])
            self.trustRemoteCode.setChecked(self._profile['trustRemoteCode'])
            self._useSafeTensors.setChecked(self._profile['useSafeTensors'])
            self._wBits.setText(str(self._profile['wBits']))
            self._groupSize.setText(str(self._profile['groupSize']))

    # Get the name of the current profilew
    def getProfileName(self):
        return self._profileNameWidget.text().strip()

    # Handle the browse button being clicked, where a direcxtory selection dialog is displayed so the use can select a model directory
    @Slot(bool)
    def onBrowse(self, checked):
        settings = QSettings()
        modelDirectory  = settings.value('ModelWindow.ModelDirectory', '/')
        path = QFileDialog.getExistingDirectory(self, 'Select Model Directory', modelDirectory)
        if path:
            self._modelPathWidget.setText(path)
            fileInfo = QFileInfo(path)
            # Save both the full model path for the model path widget and the model directory for the model selection dialog
            settings.setValue('ModelWindow.ModelPath', path)
            settings.setValue('ModelWindow.ModelDirectory', fileInfo.dir().absolutePath())

    # Handle the browse button being clicked, where a direcxtory selection dialog is displayed so the use can select a model overflow
    # directory
    @Slot(bool)
    def onModelOverflow(self, checked):
        settings = QSettings()
        overflowPath = settings.value('ModelWindow.ModelOverflowDirectory', '/')
        path = QFileDialog.getExistingDirectory(self, 'Select Model Overflow Directory', overflowPath)
        if path:
            self._overflowPathWidget.setText(path)
            settings.setValue('ModelWindow.ModelOverflowDirectory', path)
            settings.setValue('ModelWindow.ModelOverflowDirectory', path)

    # Handle the OK button being clicked, where the user has specified all the required information for the profile. Validate dialog
    # parameters then save the model profile.
    @Slot(bool)
    def onLoad(self):
        if (self._profile is None):
            if (self._profileNameWidget.text().strip() == ''):
                QMessageBox.critical(self, 'Invalid Profile Name', 'No profile name specified')
                return
        modelPath = self._modelPathWidget.text().strip()
        if (len(modelPath) == 0):
            QMessageBox.critical(self, 'Invalid Model Path', 'No model path specified')
            return
        overflowPath = self._overflowPathWidget.text().strip()
        if (not os.path.exists(modelPath)):
            QMessageBox.critical(self, 'Invalid Model Path', f'Model path {modelPath} does not exist')
            return
        if (self._OverflowToDisk.isChecked()):
            if (not os.path.exists(overflowPath)):
                QMessageBox.critical(self, 'Invalid Model Overflow Path', f'Model overflow path {overflowPath} does not exist')
                return
            if (not os.path.isdir(overflowPath)):
                QMessageBox.critical(self, 'Invalid Model Overflow Path', f'Model overflow path {overflowPath} is not a directory')
                return
        if (not self._maxCpuMemoryWidget.text().isnumeric()):
            QMessageBox.critical(self,
                                 'Invalid CPU Memory', f'Non-numeric value {self._maxCpuMemoryWidget.text()} for CPU Memory specified')
            return
        for widget in self._gpuWidgets:
            if (not widget.text().isnumeric()):
                QMessageBox.critical(self, 'Invalid GPU Memory', f'Non-numeric value {widget.text()} for GPU Memory specified')
                return
        wbitsText =  self._wBits.text().strip()
        if (len(wbitsText) > 0):
            if (not wbitsText.isnumeric()):
                QMessageBox.critical(self, 'Invalid WBits', f'Non-numeric value {wbitsText} for WBits specified')
                return
            wbits = int(wbitsText)
        else:
            wbits = 0
        
        groupSizeText = self._groupSize.text().strip()
        if (len(groupSizeText) > 0):
            if (not groupSizeText.isnumeric()):
                QMessageBox.critical(self, 'Invalid Group Size', f'Non-numeric value {groupSizeText} for Group Size specified')
                return
            groupSize = int(groupSizeText)
        else:
            groupSize = 0
        profiles = Globals().getProfiles()
        modelName = self._profileNameWidget.text().strip()
        # Save the model profile in a model profile object
        if (self._profile is None):
            if (modelName  in profiles['modelProfiles']):
                QMessageBox.critical(self, 'Duplicate Profile', f'Profile {modelName} already exists')
                return
        profileData = {}
        profileData['modelPath'] = modelPath
        profileData['overflowPath'] = overflowPath
        profileData['maxCpuMemory'] = self._maxCpuMemoryWidget.value()
        profileData['overflowToDisk'] = self._OverflowToDisk.isChecked()
        profileData['gpuCount'] = self._gpuCount
        profileData['gpuMemory'] = {}
        for i in range(self._gpuCount):
            profileData['gpuMemory'][str(i)] = self._gpuWidgets[i].value() 
        profileData['autoDevice'] = self._autoDevice.isChecked()
        profileData['useTriton'] = self._useTriton.isChecked()
        profileData['useCPU'] = self._useCPU.isChecked()
        profileData['use16Bit'] = self._use16Bit.isChecked()
        profileData['use8Bit'] = self.use8Bit.isChecked()
        profileData['use4Bit'] = self._use4Bit.isChecked()
        profileData['trustRemoteCode'] = self.trustRemoteCode.isChecked()
        profileData['useSafeTensors'] = self._useSafeTensors.isChecked()
        profileData['wBits'] = wbits
        profileData['groupSize'] = groupSize
        modelProfiles = profiles['modelProfiles']
        modelProfiles[modelName] = profileData
        json.dump(Globals().getProfiles(), open(f'{os.path.expanduser("~")}/.DocAssistantProfile.json', 'w'), indent=4)
        self.accept()
