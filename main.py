# This software is licensed with the Apache 2.0 license
#
# See the LICENSE file in the top level directory of this repository for
# license terms.
#
# Copyright 2024 David Wootton

import os
import sys
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication
from Request.TerminationRequest import TerminationRequest
from UI.MainWindow import MainWindow
from Util.Globals import Globals
from Worker.WorkerThread import WorkerThread
import torch
import json

def setupProfiles():
    try:
        profiles = json.load(open(f'{os.path.expanduser("~")}/.DocAssistantProfile.json'))
    except OSError:
        profiles = {}
        profiles['modelProfiles'] = {}
        profiles['queryProfiles'] = {}
    Globals().setProfiles(profiles)

gpuCount = torch.cuda.device_count()
for n in range(gpuCount):
    print(f'GPU {n} is {torch.cuda.get_device_name(n)}')

app = QApplication(sys.argv)
app.setApplicationName('AIDocAssistant')
app.setApplicationVersion('0.1')
app.setOrganizationName('HungryGhost')
app.setOrganizationDomain('org.oss.drw')
app.setApplicationDisplayName('AIDocAssistant')
app.setQuitOnLastWindowClosed(True)

setupProfiles()

settings = QSettings()
haveStyle = False
style = 'QWidget {'
textColor = settings.value('ApplicationTextColor', '')
if (not textColor == ''):
    style = style + f'color: {textColor.name()};'
    haveStyle = True
font = settings.value('ApplicationFont', '')
if (not font == ''):
    fontName, fontPoints = font.split(':')
    style = style + f'font: {fontPoints}pt {fontName};';
    haveStyle = True
style = style + '}'
if (haveStyle):
    app.setStyleSheet(style)

mainWindow = MainWindow(None)

workerThread = WorkerThread()
Globals.setWorkerThread(Globals(), workerThread)
workerThread.start()

app.exec()

request = TerminationRequest()
workerThread.enqueue(request)
workerThread.wait()

json.dump(Globals().getProfiles(), open(f'{os.path.expanduser("~")}/.DocAssistantProfile.json', 'w'), indent=4)

sys.exit(0)
