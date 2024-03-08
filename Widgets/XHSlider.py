# This software is licensed with the Apache 2.0 license
#
# See the LICENSE file in the top level directory of this repository for
# license terms.
#
# Copyright 2024 David Wootton

from PySide6.QtCore import QSettings
from PySide6.QtCore import Qt
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import QSlider
from PySide6.QtWidgets import QWidget


class XHSlider(QWidget):
    _SLIDER_VALUE = "Value"
    
    def __init__(self, parent, lLimit, hLimit, step, toolTip, name=None):
        super().__init__(parent)
        
        self._name = name
        self._lLimit = lLimit
        self._hLimit = hLimit
        self.setObjectName(name)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
        self._textBox = QLineEdit(self)
        self._textBox.setToolTip(toolTip)
        layout.addWidget(self._textBox)
        
        self._slider = QSlider(Qt.Horizontal, self)
        self._slider.setToolTip(toolTip)
        self._slider.setTickInterval(5)
        self._slider.setTickPosition(QSlider.TicksAbove)
        self._slider.setMinimum(lLimit)
        self._slider.setMaximum(hLimit)
        self._slider.setPageStep(step * 10)
        self._slider.setSingleStep(step * 5)
        layout.addWidget(self._slider)
        layout.setStretch(0, 0)
        layout.setStretch(1, 1)
        
        if (self._name is not None):
            settings = QSettings()
            value = settings.value(self._name + "." + self._SLIDER_VALUE, str(lLimit))
            self._textBox.setText(value)
            self._slider.setValue(int(value)) 
        
        self._slider.sliderMoved.connect(self.sliderValueChanged)
        self._slider.valueChanged.connect(self.sliderValueChanged)
        self._slider.sliderReleased.connect(self.sliderReleased)
        self._textBox.editingFinished.connect(self.editDone)
    
    def setValue(self, value):
        self._textBox.setText(str(value))
        self._slider.setValue(int(value))

    def text(self):
        return self._textBox.text()
    
    def value(self):
        return self._slider.value()
        
    @Slot()
    def editDone(self):
        try:
            n = int(self._textBox.text())
            if (n < self._lLimit):
                self._slider.setValue(self._lLimit)
                self._textBox.setText(str(self._lLimit))
            elif (n > self._hLimit):
                self._slider.setValue(self._hLimit)
                self._textBox.setText(str(self._hLimit))
            else:
                self._slider.setValue(n)
                self._textBox.setText(str(n))
        except ValueError:
            pass
        if (self._name is not None):
            settings = QSettings()
            settings.setValue(self._name + "." + self._SLIDER_VALUE, self._slider.value())
        
    @Slot()
    def sliderReleased(self):
        if (self._name is not None):
            settings = QSettings()
            settings.setValue(self._name + "." + self._SLIDER_VALUE, self._slider.value())

    @Slot(int)
    def sliderValueChanged(self, value):
        self._textBox.setText(str(value))
       
