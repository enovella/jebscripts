# -*- coding: utf-8 -*-

import sys
import os
import time
import codecs # used for writing UTF-8 into a file

from jeb.api     import IScript
from jeb.api.ui  import View
from jeb.api.dex import Dex
from jeb.api.ast import Class, Field, Method, Call, Constant, StaticField, NewArray, Compound, Assignment, Identifier, Optimizer


class getMethodsFromClass(IScript):

  def run(self, jeb):
	self.jeb            = jeb
	self.dex            = self.jeb.getDex()
	self.clsdata        = []
	self.classrequested = self.dex.getClass("k")
	
	self.clsdata        = self.classrequested.getData()
	dmethods            = clsdata.getDirectMethods()
	vmethods            = clsdata.getVirtualMethods()
    

    for method in dmethods:
        print method

    print "[+] Done!"
