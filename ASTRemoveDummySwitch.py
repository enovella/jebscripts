# JEB script - demo AST API
# Remove dummy switches
# See www.android-decompiler.com/blog

import sys
import os
import time
from jeb.api import IScript
from jeb.api import EngineOption
from jeb.api.ui import View
from jeb.api.dex import Dex
from jeb.api.ast import SwitchStm, Compound, Constant, Goto, Label, Optimizer



class ASTRemoveDummySwitch(IScript):

  def run(self, jeb):
    self.jeb = jeb
    self.dex = self.jeb.getDex()

    # change or allow user-input or caret-based selection
    msig = 'Lcom/example/android/snake/TileView;->(Landroid/content/Context;Landroid/util/AttributeSet;I)V'
    r = jeb.decompileMethod(msig)

    m = jeb.getDecompiledMethodTree(msig)
    self.checkBlock(m.getBody())

    opt = Optimizer(jeb, m)
    opt.removeUselessGotos()
    opt.removeUnreferencedLabels()


  def checkBlock(self, block, level=0):
    i = 0
    while i < block.size():
      stm = block.get(i)
      #print '%s%s' % ('  '*level, stm)
      if isinstance(stm, SwitchStm):
        gotostm = self.checkDummySwitch(stm)
        if gotostm:
          block.set(i, gotostm)
          print '-> Switch replaced by goto %s' % gotostm.getLabel().getName()
          label = gotostm.getLabel()
          r = self.findFirstLabel(block, i + 1, level)
          if r and r[1] == level and r[0].getName() == label.getName():
            print '-> Removing [%d, %d)' % (i + 1, r[2])
            j = i + 1
            cnt = r[2] - j
            while cnt > 0:
              block.remove(j)
              cnt -= 1
      elif isinstance(stm, Compound):
        for b in stm.getBlocks():
          self.checkBlock(b, level+1)
      i += 1


  def findFirstLabel(self, block, begin=0, level=0):
    i = begin
    while i < block.size():
      stm = block.get(i)
      if isinstance(stm, Label):
        return (stm, level, i)
      elif isinstance(stm, Compound):
        for b in stm.getBlocks():
          r = self.findFirstLabel(b, 0, level+1)
          if r:
            return r
      i += 1
    return None
    

  def checkDummySwitch(self, sw):
    val = sw.getSwitchedExpression()
    if not isinstance(val, Constant):
      return None

    val = val.getInt()
    b = sw.getCaseBody(val)
    if not b or b.size() != 1:
      return None

    stm0 = b.get(0)
    if not isinstance(stm0, Goto):
      return None

    label = stm0.getLabel()
    return stm0