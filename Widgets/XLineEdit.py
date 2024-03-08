# This software is licensed with the Apache 2.0 license
#
# See the LICENSE file in the top level directory of this repository for
# license terms.
#
# Copyright 2024 David Wootton

from PySide6.QtCore import QSettings
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QLineEdit


class XLineEdit(QLineEdit):

    def __init__(self, parent, name):
        super().__init__(parent)
        self.setObjectName(name)
        settings = QSettings()
        self.setText(settings.value(name, ""))
        self.editingFinished.connect(self.fieldEditDone)
        
    @Slot()
    def fieldEditDone(self):
        settings = QSettings()
        settings.setValue(self.objectName(), self.text().strip())
