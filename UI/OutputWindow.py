# This software is licensed with the Apache 2.0 license
#
# See the LICENSE file in the top level directory of this repository for
# license terms.
#
# Copyright 2024 David Wootton

from PySide6.QtCore import Slot
from PySide6.QtGui import QTextCursor
from PySide6.QtGui import QTextDocument
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QGridLayout
from PySide6.QtWidgets import QTextEdit
from Util.Globals import Globals

# Class to display LLM putput
class OutputWindow(QFrame):

    # Set up the widgets in the output window
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QGridLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self.setLayout(layout)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.outputDocument = QTextDocument()
        self.outputText = QTextEdit(self)
        self.outputText.setReadOnly(True)
        self.outputText.setDocument(self.outputDocument)
        self.textCursor = QTextCursor(self.outputDocument)
        layout.addWidget(self.outputText, 0, 0)
        Globals()._resultEvent.resultMessage.connect(self.appendOutput)

    # Append text to the output window
    @Slot(str)
    def appendOutput(self, text):
        if (self.outputDocument != None):
            self.outputText.moveCursor(QTextCursor.End)
            self.textCursor.insertText(text)
            self.outputText.verticalScrollBar().setValue(self.outputText.verticalScrollBar().maximum())
