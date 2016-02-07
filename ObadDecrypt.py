# JEB script - demo AST API
# Obad, Part 1: Decrypt Obad strings before performing unreflection
# See www.android-decompiler.com/blog

import sys
import os
import time
from jeb.api import IScript
from jeb.api import EngineOption
from jeb.api.ui import View
from jeb.api.dex import Dex
from jeb.api.ast import Class, Field, Method, Call, Constant, StaticField, NewArray



class ObadDecrypt(IScript):

  def run(self, jeb):
    self.jeb = jeb
    self.dex = self.jeb.getDex()
    self.cstbuilder = Constant.Builder(jeb)

    self.csig = 'Lcom/android/system/admin/OclIIOlC;'
    self.encbytes = []
    self.mname_decrypt = None
    # the encryption keys could be determined by analyzing the decryption method
    self.keys = [33, 96, -2]  # (added to 'length', added to 'curChar', delta)

    r = jeb.decompileClass(self.csig)
    if not r:
      print 'Could not find class "%s"' % csig
      return

    c = jeb.getDecompiledClassTree(self.csig)

    wanted_flags = Dex.ACC_PRIVATE|Dex.ACC_STATIC|Dex.ACC_FINAL
    for f in c.getFields():
      fsig = f.getSignature()
      if fsig.endswith(':[B'):
        fd = self.dex.getFieldData(fsig)
        if fd.getAccessFlags() & wanted_flags == wanted_flags:
          print 'Found field:', fsig

          findex = fd.getFieldIndex()
          for mindex in self.dex.getFieldReferences(findex):
            mname = self.dex.getMethod(mindex).getName(False)
            if mname != '':
              self.mname_decrypt = mname

          for m2 in c.getMethods():
            if m2.getName() == '':
              s0 = m2.getBody().get(0)
              if isinstance(s0.getLeft(), StaticField) and s0.getLeft().getField().getSignature() == f.getSignature():
                array = s0.getRight()
                if isinstance(array, NewArray):
                  for v in array .getInitialValues():
                    self.encbytes.append(v.getByte())
              break
          break

    if len(self.encbytes) == 0:
      print 'Encrypted strings byte array not found'
      return

    if not self.mname_decrypt:
      print 'Decryption method was not found'
      return

    for m in c.getMethods():
      print 'Decrypting strings in method: %s' % m.getName()
      self.decryptMethodStrings(m)


  def decryptMethodStrings(self, m):
    block = m.getBody()
    i = 0
    while i < block.size():
      stm = block.get(i)
      self.checkElement(block, stm)
      i += 1


  def checkElement(self, parent, e):
    if isinstance(e, Call):
      mname = e.getMethod().getName()
      if mname == self.mname_decrypt:
        v = []
        for arg in e.getArguments():
          if isinstance(arg, Constant):
            v.append(arg.getInt())
        if len(v) == 3:
          decrypted_string = self.decrypt(v[2], v[0], v[1])
          parent.replaceSubElement(e, self.cstbuilder.buildString(decrypted_string))
          print '  Decrypted string: %s' % repr(decrypted_string)

    for subelt in e.getSubElements():
      if isinstance(subelt, Class) or isinstance(subelt, Field) or isinstance(subelt, Method):
        continue
      self.checkElement(e, subelt)


  def decrypt(self, length, curChar, pos):
    length += self.keys[0]
    curChar += self.keys[1]
    r = ''
    for i in range(length):
      r += chr(curChar & 0xFF)
      if pos >= len(self.encbytes):
        break
      curEncodedChar = self.encbytes[pos]
      pos += 1
      curChar = curChar + curEncodedChar + self.keys[2]
    return r