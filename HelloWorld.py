# JEB sample script
# http://www.android-decompiler.com/
# display MessageBox and get pressed button value
#
# Copyright (c) 2013 SecureBrain
import os

from jeb.api import IScript
from jeb.api.ui import JebUI
from jeb.api.ui.JebUI import ButtonGroupType
from jeb.api.ui.JebUI import IconType

class HelloWorld(IScript):
    def run(self, j):
        ui = j.getUI()
        ret = ui.displayMessageBox("question", "Hello World?", IconType.QUESTION, ButtonGroupType.YES_NO_CANCEL)
        wp = { 0: 'Cancel', 1: 'OK', 2:'Yes', 3:'No' }
        print "'%s'is pressed!!" % wp[ret]

