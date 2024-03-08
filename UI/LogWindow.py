# This software is licensed with the Apache 2.0 license
#
# See the LICENSE file in the top level directory of this repository for
# license terms.
#
# Copyright 2024 David Wootton

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QGridLayout
from PySide6.QtWidgets import QTextEdit
from PySide6.QtGui import QTextCursor
from PySide6.QtGui import QTextDocument
from Util.Globals import Globals

# Widget to display progess and status messages in a log window
class LogWindow(QFrame):
    
    # Create the widgets in the log window
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QGridLayout(self)
        self.setLayout(layout)
        self._document = QTextDocument()
        self._documentWindow = QTextEdit()
        self._documentWindow.setReadOnly(True)
        self._documentWindow.setLineWrapMode(QTextEdit.NoWrap)
        self._documentWindow.setAcceptRichText(False)
        self._documentWindow.setDocument(self._document)
        self._textCursor = QTextCursor(self._document)
        self._newLine = ''
        layout.addWidget(self._documentWindow, 0, 0)
        Globals()._logEvent.logMessage.connect(self.logMessage)

    # Add a message to the log window
    @Slot(str)
    def logMessage(self, str):
        if (self._document != None):
            self._documentWindow.moveCursor(QTextCursor.End)
            self._textCursor.insertText(self._newLine + str)
            self._newLine = '\n'
            self._documentWindow.verticalScrollBar().setValue(self._documentWindow.verticalScrollBar().maximum())
