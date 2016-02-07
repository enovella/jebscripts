# JEB script - demo AST API
# Obad, Part 2: Replace reflection calls by direct method calls
# See www.android-decompiler.com/blog

import sys
import os
import time
from jeb.api import IScript
from jeb.api.ui import View
from jeb.api.dex import Dex
from jeb.api.ast import Class, Field, Method, Call, Constant, StaticField, NewArray, Compound, Assignment, Identifier, Optimizer



class ObadUnreflect(IScript):

  def run(self, jeb):
    self.jeb = jeb
    self.dex = self.jeb.getDex()

    v = self.jeb.getUI().getView(View.Type.JAVA)
    if not v:
      print 'Switch to the Java view, position the caret somewhere inside the method to be decompiled'
      return

    self.msig = v.getCodePosition().getSignature()
    print 'Cursor: %s' % self.msig
    
    r = jeb.decompile(self.msig, False, False)
    if not r:
      print 'Could not find method'
      return

    m = jeb.getDecompiledMethodTree(self.msig)
    self.revertReflection(m.getBody())


  def revertReflection(self, block):
    i = 0
    while i < block.size():
      stm = block.get(i)
      if isinstance(stm, Assignment):
        if stm.isSimpleAssignment() and isinstance(stm.getRight(), Call):
          self.processCall(stm, stm.getRight())
      elif isinstance(stm, Call):
        self.processCall(block, stm)
      elif isinstance(stm, Compound):
        for b in stm.getBlocks():
          self.revertReflection(b)
      i += 1


  # note: could add support for instantiation, eg, Class.forName().getConstructor().newInstance()
  def processCall(self, parent, elt0):
    m = elt0.getMethod()
    if m.getSignature() == 'Ljava/lang/reflect/Method;->invoke(Ljava/lang/Object;[Ljava/lang/Object;)Ljava/lang/Object;':
      elt1 = elt0.getArguments().get(0)
      if isinstance(elt1, Call):
        if elt1.getMethod().getSignature() == 'Ljava/lang/Class;->getMethod(Ljava/lang/String;[Ljava/lang/Class;)Ljava/lang/reflect/Method;':
          elt2 = elt1.getArguments().get(0)
          if isinstance(elt2, Call):
            if elt2.getMethod().getSignature() == 'Ljava/lang/Class;->forName(Ljava/lang/String;)Ljava/lang/Class;':
              print 'Found match: Class.forName(...).getMethod(...).invoke(...)'
              new_elt0 = self.check(elt2, elt1, elt0)
              if new_elt0:
                print '  Removing relection'
                parent.replaceSubElement(elt0, new_elt0)


  def check(self, c0, c1, c2):
    arg = c0.getArguments().get(0)
    if self.isConstantString(arg):
      cname = arg.getString()

    arg = c1.getArguments().get(1)
    if self.isConstantString(arg):
      mname = arg.getString()

    if not cname or not mname:
      return False

    sig = 'L%s;->%s' % (cname.replace('.', '/'), mname)

    sig += '('
    i = 2
    while i < c1.getArguments().size():
      arg = c1.getArguments().get(i)
      v = self.processTypeIdentifier(arg)
      if not v:
        break
      sig += v
      i += 1
    # simplification: assume no return value
    # would need to be either infered (from code), or fetched from doc
    sig += ')V'

    print '  %s' % sig

    is_static = False
    args = []
    i = 1
    while i < c2.getArguments().size():
      arg = c2.getArguments().get(i)
      if isinstance(arg, Constant) and arg.isNull():
        if i == 1:
          is_static = True
        elif i == 2 and c2.getArguments().size() == 3:
          break
        else:
          args.append(arg)
      else:
        args.append(arg)
      i += 1

    m2 = self.dex.addMethodReference(sig)
    index = m2.getIndex()
    mb = Method.Builder(self.jeb)
    ast_method = mb.build(index, is_static)
    #print ast_method

    # TODO: primitive arguments should be auto-unboxed
    ast_call = Call.build(ast_method, False, args)
    #print ast_call
    return ast_call


  def isConstantString(self, e):
    return isinstance(e, Constant) and e.getType() == 'Ljava/lang/String;'


  def processTypeIdentifier(self, arg):
    primtypes = {
      'Ljava/lang/Boolean;->TYPE:Ljava/lang/Class;':  'Z',
      'Ljava/lang/Byte;->TYPE:Ljava/lang/Class;':     'B',
      'Ljava/lang/Character;->TYPE:Ljava/lang/Class;':'C',
      'Ljava/lang/Word;->TYPE:Ljava/lang/Class;':     'W',
      'Ljava/lang/Integer;->TYPE:Ljava/lang/Class;':  'I',
      'Ljava/lang/Float;->TYPE:Ljava/lang/Class;':    'F',
      'Ljava/lang/Double;->TYPE:Ljava/lang/Class;':   'D',
    }

    if isinstance(arg, StaticField):
      return primtypes.get(arg.getField().getSignature())

    elif isinstance(arg, Call):
      if arg.getMethod().getSignature() == 'Ljava/lang/Class;->forName(Ljava/lang/String;)Ljava/lang/Class;':
        c = arg.getArguments().get(0)
        if self.isConstantString(c):
          return 'L%s;' % c.getString().replace('.', '/')

    elif isinstance(arg, Constant) and arg.isNull():
      # (simplification) assume no var-arg: getMethod(name, null)
      # -> no argument
      return None

    raise '  Cannot process UNKNOWN type: %s' % arg