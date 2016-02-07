# JEB sample script
# http://www.android-decompiler.com/
# listing all methods in dex
#
# Copyright (c) 2013 SecureBrain
import os

from jeb.api import IScript

class ListingMethods(IScript):
    def run(self, j):
        self.dex = j.getDex()
        if not self.dex:
            print 'Error! Please provide an input file.'
            j.exit()

        self.listing()

    def listing(self):
        print "listing all methods in dex..."
        for i in range(0, self.dex.getClassCount()):
            cls = self.dex.getClass(i)
            print self.dex.getType(cls.getClasstypeIndex())
            cls_data = cls.getData()
            if cls_data is None:
                continue

            for md in cls_data.getDirectMethods():
                print "\t%s" % self.method_def_str(md)

            for md in cls_data.getVirtualMethods():
                print "\t%s" % self.method_def_str(md)

            print ""

    def method_def_str(self, method_data):
        m = self.dex.getMethod(method_data.getMethodIndex())
        name = m.getName()
        proto = self.dex.getPrototype(m.getPrototypeIndex())
        proto_strs = map(lambda p: self.dex.getType(p), proto.getParameterTypeIndexes())
        ret = self.dex.getType(proto.getReturnTypeIndex())
        acc = self.accessor(method_data.getAccessFlags())
        return "%s %s %s(%s)" % (' '.join(acc), ret, name, ', '.join(proto_strs))

    def accessor(self, flg):
        accessor_strings = {
                0x1:     'public',
                0x2:     'private',
                0x4:     'protected',
                0x8:     'static',
                0x10:    'final',
                0x20:    'synchronized',
                0x40:    'bridge',
                0x80:    'varargs',
                0x100:   'native',
                0x200:   'interface',
                0x400:   'abstract',
                0x800:   'strict',
                0x1000:  'synthetic',
                0x2000:  'annotation',
                0x4000:  'enum',
                0x10000: 'constructor',
                0x20000: 'declared-synchronized',
                }
        return map(lambda i: accessor_strings[i], filter(lambda k: k&flg, accessor_strings.keys()))

