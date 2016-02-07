# -*- coding: utf-8 -*-

import codecs # used for writing UTF-8 into a file

from jeb.api     import IScript
from jeb.api.ui  import View
from jeb.api.dex import Dex
from jeb.api.ast import Class, Field, Method, Call, Constant, StaticField, NewArray, Compound, Assignment, Identifier, Optimizer


class getMethodSignatures(IScript):

  def run(self, jeb):
    self.jeb = jeb
    self.dex = self.jeb.getDex()
    self.path = "/tmp/methodsignatures.txt"

    methodSigList = self.dex.getMethodSignatures(True)

    #f = codecs.open(self.path, "w", encoding="ascii", errors="ignore")
    f = codecs.open(self.path, "w", encoding="utf-8", errors="ignore")

    for method in methodSigList:
        f.write(repr(method)+'\n')
	     	
    print "[+] Output file located at %s" %(self.path)
    print "[+] Done!"
