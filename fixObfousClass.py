#? name=fix Obfous Class, author=frozenrain
# A JEB python script
# fixObfous.py
# Rename obfuscated class name with source name.

import re

from jeb.api import IScript
from jeb.api import EngineOption
from jeb.api.ui import JebUI
from jeb.api.ui import View


class fixObfousClass(IScript):
    def run(self, j):
        self.dex = j.getDex()
        self.jeb = j
        ui = j.getUI()

        # rename obfuscated class names
        self.rename_classes()

        # refresh view
        ui.getView(View.Type.ASSEMBLY).refresh()
        ui.getView(View.Type.JAVA).refresh()
        ui.getView(View.Type.CLASS_HIERARCHY).refresh()


    def rename_classes(self):
        for i in range(0, self.dex.getClassCount()):
            cls = self.dex.getClass(i)
            src_name = self.dex.getString(cls.getSourceIndex())
            cls_name = self.dex.getType(cls.getClasstypeIndex())
            ret = self.rename_from_source(cls_name, src_name)
            if ret:
                new_name = self.dex.getType(cls.getClasstypeIndex())
                print "rename from '%s' to '%s'" % (cls_name, new_name)

    def is_nest_class(self, className):
        return className != None and className.rfind("$") != -1

    def should_rename_class(self, className, sourceName):
        if not className or not sourceName:
            return False
        if self.is_nest_class(className):
            return False
        if(len(className)> 3):
            return False
        for i in range(len(className)):
            if (className[i] < 'a'):
                return False
        return True

    def get_true_class_name(self, className):
        if (self.is_nest_class(className)):
            return None
        if className != None:
            pos = className.rfind("/")
            if pos != -1:
               return className[pos+1:len(className)-1]
        return None

    def fix_class_name(self, className, sourceName):
       pos = className.rfind("/")
       if pos != -1:
          return className[::-1].replace(self.get_true_class_name(className)[::-1], sourceName[::-1], 1)[::-1] + ';'

    def rename_from_source(self,cls_name, src_name):
        if (src_name != None and len(src_name) > 0 ):
           src_name = src_name[:src_name.rfind(".")]
           cls_name = cls_name[:len(cls_name)]
           if (self.should_rename_class(self.get_true_class_name(cls_name), src_name)):
              #fixedClassName = self.fix_class_name(cls_name, src_name);
              if(self.jeb.renameClass(cls_name, src_name)):
                 print "rename " , cls_name , " to " , src_name
              else:
                 print "error rename " , cls_name , " to " , src_name



