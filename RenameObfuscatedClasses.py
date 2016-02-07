#? name=Rename Obfuscated Classes, shortcut=Ctrl+Shift+R, author=Masata Nishida
# JEB sample script
# http://www.android-decompiler.com/
#
# RenameObfuscatedClasses.py
# Rename obfuscated class names.
#
# Copyright (c) 2013 SecureBrain
import re

from jeb.api import IScript
from jeb.api import EngineOption
from jeb.api.ui import JebUI
from jeb.api.ui import View

class RenameObfuscatedClasses(IScript):
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
            cls_name = self.dex.getType(cls.getClasstypeIndex())
            ret = self.rename_by_super_class(cls)
            ret2 = self.rename_by_accessor(cls)
            ret3 = self.rename_by_interfaces(cls)
            ret = ret or ret2 or ret3

            if ret:
                new_name = self.dex.getType(cls.getClasstypeIndex())
                print "rename from '%s' to '%s'" % (cls_name, new_name)


    def append_cls_name(self, cls, append_str):
        p = re.compile("^.*\/([\w$]+);$")
        # cls_name has package path
        cls_name = self.dex.getType(cls.getClasstypeIndex())
        if cls_name.find(append_str) == -1:
            s = re.search(p, cls_name)
            simple_new_name = s.group(1) + '_' + append_str 
            return self.jeb.renameClass(cls_name, simple_new_name)
        else:
            return False

    def rename_by_super_class(self, cls):
        rename_targets = {
            'Landroid/app/Service;': 'Service',
            'Landroid/app/Activity;': 'Activity',
            'Landroid/content/BroadcastReceiver;': 'Receiver',
            'Landroid/content/ContentProvider;': 'Provider',
            'Ljava/lang/Thread;': 'Thread',
            'Landroid/os/AsyncTask;': 'AsyncTask',
            'Ljava/util/TimerTask;': 'TimerTask',
            'Landroid/database/sqlite/SQLiteDatabase;': 'SQLiteDatabase',
            'Landroid/database/sqlite/SQLiteOpenHelper;': 'SQLiteOpenHelper',
            'Landroid/database/ContentObserver;': 'ContentObserver',
            'Landroid/os/Handler;': 'Handler',
        }
        super_cls_type = self.dex.getType(cls.getSuperclassIndex())
        if super_cls_type in rename_targets.keys():
            val = rename_targets[super_cls_type]
            self.append_cls_name(cls, val)
            return True
        else:
            return False

    def rename_by_accessor(self, cls):
        flg = cls.getAccessFlags()
        ret = False
        if flg & 0x200:
            self.append_cls_name(cls, 'Interface')
            ret = True
        if flg & 0x400:
            self.append_cls_name(cls, 'Abstract')
            ret = True
        if flg & 0x4000:
            self.append_cls_name(cls, 'Enum')
            ret = True
        return ret


    def rename_by_interfaces(self, cls):
        ret = False
        for idx in cls.getInterfaceIndexes():
            if_name = self.dex.getType(idx)
            if if_name.endswith('ClickListener;'):
                self.append_cls_name(cls, 'ClickListener')
                ret = True
            if if_name.endswith('CancelListener;'):
                self.append_cls_name(cls, 'CancelListener')
                ret = True
            if if_name == 'Ljava/lang/Runnable;':
                self.append_cls_name(cls, 'Runnable')
                ret = True
            if if_name == 'Landroid/os/IInterface;':
                self.append_cls_name(cls, 'IInterface')
                ret = True

        return ret