# JEB sample script
# http://www.android-decompiler.com/
#
# AlertMarker.py
# Set(unset) alert marker to focued method.
#
# Copyright (c) 2013 SecureBrain
from jeb.api import IScript
from jeb.api.dex import Dex
from jeb.api.ui import View

import string

class AlertMarker(IScript):

    def run(self, jeb):
        self.jeb = jeb
        self.dex = jeb.getDex()
        self.ui = jeb.getUI()
        success = self.start()

    def start(self):
        view = self.ui.getView(View.Type.ASSEMBLY)
        msig = view.getCodePosition().getSignature()
        md = self.dex.getMethodData(msig)
        if not md:
            print 'caret is not in method.'
            return

        f = md.getUserFlags()
        print 'target:' + msig
        if (f & Dex.FLAG_ALERT) == 0:
            print 'set alert marker'
            md.setUserFlags(f | Dex.FLAG_ALERT)
        else:
            print 'unset alert'
            md.setUserFlags(f & ~Dex.FLAG_ALERT)

        view.refresh()
