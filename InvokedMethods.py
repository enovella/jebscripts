# JEB sample script
# http://www.android-decompiler.com/
#
# InvokedMethods.py
# listing invoked method by the method which the caret focus on.
#
# Copyright (c) 2013 SecureBrain
import re

from jeb.api import IScript
from jeb.api import EngineOption
from jeb.api.ui import JebUI
from jeb.api.ui import View
from jeb.api.dex import DexDalvikInstruction

class InvokedMethods(IScript):
    def run(self, j):
        self.dex = j.getDex()
        ui = j.getUI()

        if not self.dex:
            print 'Error! Please provide an input file.'
            j.exit()

        # collect method information in dex.
        self.collect_method_data()

        # get caret information on assembly window
        asm_view = ui.getView(View.Type.ASSEMBLY)
        cp = asm_view.getCodePosition()
        sig = cp.getSignature()

        if sig in self.method_dict:
            print "caret is on '%s'." % sig
            invoked = self.invoked_method(self.method_dict[sig])
            for meth in invoked:
                print "\t%s" % meth
            print "%d methods are invoked." % len(invoked)
        else:
            print "caret is not foucused on method..."


    # collect method information in dex.
    def collect_method_data(self):
        self.method_dict = {} # key is method name(partial sig)

        # each class
        for i in range(0, self.dex.getClassCount()):
            cls = self.dex.getClass(i)
            cls_name = self.dex.getType(cls.getClasstypeIndex())
            cls_data = cls.getData()
            if cls_data is None:
                continue

            # about static method
            for md in cls_data.getDirectMethods():
                m = self.dex.getMethod(md.getMethodIndex())
                self.method_dict[self.method_def(m)] = md

            # about instance method
            for md in cls_data.getVirtualMethods():
                m = self.dex.getMethod(md.getMethodIndex())
                self.method_dict[self.method_def(m)] = md


    def method_def(self, dex_method):
        name = dex_method.getName()
        cls_name = self.dex.getType(dex_method.getClassTypeIndex())
        proto = self.dex.getPrototype(dex_method.getPrototypeIndex())
        proto_strs = map(lambda p: self.dex.getType(p), proto.getParameterTypeIndexes())
        ret = self.dex.getType(proto.getReturnTypeIndex())

        # 'clas name'->'method name'('arguments'...)'return type'
        return "%s->%s(%s)%s" % (cls_name, name, ''.join(proto_strs), ret)


    def invoked_method(self, method_data):
        code_item = method_data.getCodeItem()
        invoked = []
        p = re.compile('^invoke-')

        for inst in code_item.getInstructions():
            if p.match(inst.getMnemonic()):
                # if instruction opcode starts with 'invoke-...'
                for param in inst.getParameters():
                    # get the arcument operand
                    if param.getType() == DexDalvikInstruction.TYPE_IDX:
                        m = self.dex.getMethod(param.getValue()) # invoked method
                        invoked.append(self.method_def(m))

        invoked = list(set(invoked)) # uniq array
        invoked.sort()
        return invoked

