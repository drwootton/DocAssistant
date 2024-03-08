# This software is licensed with the Apache 2.0 license
#
# See the LICENSE file in the top level directory of this repository for
# license terms.
#
# Copyright 2024 David Wootton

from PySide6.QtCore import QSettings
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QCheckBox


class XCheckBox(QCheckBox):
    _WIDGET_ATTR = "_checked"
    
    def __init__(self, text, parent, name):
        super().__init__(text, parent)
        self._name = name
        settings = QSettings()
        checked = settings.value(name + self._WIDGET_ATTR, "false")
        if (checked == "true"):
            self.setChecked(True)
        else:
            self.setChecked(False)
        self.clicked.connect(self.doClick)
        
    @Slot(bool)
    def doClick(self, checked):
        settings = QSettings()
        settings.setValue(self._name + self._WIDGET_ATTR, self.isChecked())
