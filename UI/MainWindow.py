# This software is licensed with the Apache 2.0 license
#
# See the LICENSE file in the top level directory of this repository for
# license terms.
#
# Copyright 2024 David Wootton

from PySide6.QtCore import QCoreApplication
from PySide6.QtCore import Qt
from PySide6.QtCore import QSettings
from PySide6.QtCore import Slot
from PySide6.QtGui import QColor
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QColorDialog
from PySide6.QtWidgets import QDockWidget
from PySide6.QtWidgets import QFontDialog
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QMenu
from UI.DocumentsWindow import DocumentsWindow
from UI.LogWindow import LogWindow
from UI.ModelWindow import ModelWindow
from UI.OutputWindow import OutputWindow
from UI.PromptWindow import PromptWindow

class MainWindow(QMainWindow):
    _MAIN_WINDOW_STATE = 'MainWindowState'
    _MAIN_WINDOW_GEOMETRY = 'MainWindowGeometry'
    
    # Create the main window and the widgets in the window
    def __init__(self, parent):
        super().__init__(parent)
        settings = QSettings()
        self.setWindowTitle("Document Assistant")
        self.restoreGeometry(settings.value(self._MAIN_WINDOW_GEOMETRY))
        self.restoreState(settings.value(self._MAIN_WINDOW_STATE))
        self._promptDockWidget = QDockWidget(self)
        self._promptDockWidget.setObjectName('PromptDockWidget')
        self._promptDockWidget.setWindowTitle('Prompt')
        self._promptDockWidget.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self._promptDockWidget.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        self._promptWindow = PromptWindow(self._promptDockWidget)
        self._promptDockWidget.setWidget(self._promptWindow)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self._promptDockWidget)

        self._modelDockWidget = QDockWidget(self)
        self._modelDockWidget.setObjectName('ModelDockWidget')
        self._modelDockWidget.setWindowTitle('Model')
        self._modelDockWidget.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self._modelDockWidget.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        self._modelWindow = ModelWindow(self._modelDockWidget)
        self._modelDockWidget.setWidget(self._modelWindow)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self._modelDockWidget)

        self._documentsDockWidget = QDockWidget(self)
        self._documentsDockWidget.setObjectName('DocumentsDockWidget')
        self._documentsDockWidget.setWindowTitle('Documents')
        self._documentsDockWidget.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self._documentsDockWidget.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        self._documentsWindow = DocumentsWindow(self._documentsDockWidget)
        self._documentsDockWidget.setWidget(self._documentsWindow)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self._documentsDockWidget)

        self._logDockWidget = QDockWidget(self)
        self._logDockWidget.setObjectName('LogDockWidget')
        self._logDockWidget.setWindowTitle('Log')
        self._logDockWidget.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea)
        self._logDockWidget.setFeatures(QDockWidget.DockWidgetFloatable)
        self._logWindow = LogWindow(self._logDockWidget)
        self._logDockWidget.setWidget(self._logWindow)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self._logDockWidget)

        self._outputWindow = OutputWindow(self)
        self.setCentralWidget(self._outputWindow)
        self.restoreDockWidgetState(self._promptDockWidget, settings, self.dockWidgetArea(self._promptDockWidget))
        self.restoreDockWidgetState(self._modelDockWidget, settings, self.dockWidgetArea(self._modelDockWidget))
        self.restoreDockWidgetState(self._documentsDockWidget, settings, self.dockWidgetArea(self._documentsDockWidget))
        self.restoreDockWidgetState(self._logDockWidget, settings, self.dockWidgetArea(self._logDockWidget))

        fileMenu = QMenu('File', self)
        fileLoadDocIndex = fileMenu.addAction('Load Document Index')
        fileLoadDocIndex.triggered.connect(self._documentsWindow.loadDocumentIndex)
        fileSaveDocIndex = fileMenu.addAction('Save Document Index')
        fileSaveDocIndex.triggered.connect(self._documentsWindow.saveDocumentIndex)
        fileQuit = fileMenu.addAction('Exit')
        fileQuit.triggered.connect(self.doExit)
        self.menuBar().addMenu(fileMenu)

        settingsMenu = QMenu('Settings', self)
        settingsFont = settingsMenu.addAction('Font')
        settingsFont.triggered.connect(self.doFont)
        settingsTextColor = settingsMenu.addAction('Text Color')
        settingsTextColor.triggered.connect(self.doTextColor)
        self.menuBar().addMenu(settingsMenu)

        self.show()

    # Save the state of the main window and the dock widgets when the application is closed.
    def closeEvent(self, event):
        self.saveMainWindowState()
        event.accept()

    # Restore the state and position of the dock widget.    
    def restoreDockWidgetState(self, dockWidget, settings, defaultDock):
        settingsName = 'MainWindow_' + dockWidget.objectName() + '_settings'
        settingsValue = settings.value(settingsName)
        if (settingsValue):
            parts = settingsValue.split(':')
            if (parts[0] == '1'):
                dockWidget.setFloating(True)
                dockWidget.move(int(parts[2]), int(parts[3]))
            else:
                dockWidget.setFloating(False)
                self.addDockWidget(Qt.DockWidgetArea(int(parts[1])), dockWidget)
    
    # Save the state of the dock widget.
    def saveDockWidgetState(self, dockWidget, settings):
        settingsName = 'MainWindow_' + dockWidget.objectName() + '_settings'
        settingsValue = ''  
        if (dockWidget.isFloating()):
            widgetPos = dockWidget.pos()
            settingsValue = '1:-1:' + str(widgetPos.x()) + ':' + str(widgetPos.y())
        else:
            # Get the actual numeric value for the DockWidgetArea enumeration, not the string with the enumeration name.
            settingsValue = '0:' + str(self.dockWidgetArea(dockWidget).value) + ':-1:-1'            
        settings.setValue(settingsName, settingsValue)

    # Save the state of the main window.
    def saveMainWindowState(self):
        state = self.saveState()
        settings = QSettings()
        settings.setValue(self._MAIN_WINDOW_STATE, state)
        settings.setValue(self._MAIN_WINDOW_GEOMETRY, self.saveGeometry())
        self.saveDockWidgetState(self._promptDockWidget, settings)
        self.saveDockWidgetState(self._modelDockWidget, settings)
        self.saveDockWidgetState(self._documentsDockWidget, settings)
        self.saveDockWidgetState(self._logDockWidget, settings)

    # Handle request to exit the application
    @Slot(bool)
    def doExit(self, checked):
        self.saveMainWindowState()
        QCoreApplication.instance().quit()

    # Handle request to change the font
    @Slot(bool)
    def doFont(self, checked):
        settings = QSettings()
        currentFontData = settings.value('ApplicationFont', '')
        if (not currentFontData == ''):
            fontName, pointSize = currentFontData.split(':')
            print(fontName, pointSize)
            currentFont = QFont(fontName, int(pointSize))
            ok, font = QFontDialog(currentFont, self).getFont()
        else:
            ok, font = QFontDialog(self).getFont()
        if (ok):
            QApplication.instance().setFont(font)
            fontSetting = f'{font.family()}:{font.pointSize()}'
            settings = QSettings()
            settings.setValue('ApplicationFont', fontSetting)

    # Handle request to change the text color
    @Slot(bool)
    def doTextColor(self, checked):
        settings = QSettings()
        color = QColor(settings.value('ApplicationTextColor', '#cccc00'))
        color = QColorDialog.getColor(color, self)
        if (color.isValid()):
            settings = QSettings()
            settings.setValue('ApplicationTextColor', color)
    
