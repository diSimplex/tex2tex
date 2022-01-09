# An example tex2tex remapping

from tex2tex.dsl import Macros as m
from tex2tex.dsl import environments as e

m.usebtxdataset(
  open='[',
  close=']',
  numArgs=1
)

m.usemodule()

m.diSimpEnvironment()

m.diSimpComonent()

e.diSimplexComponent(
  numArgs=1
)

e.group(
  start='b',
  stop='e'
)

m.placefigure(
  open='[{',
  close=']}',
  numArgs=3,
)

e.MPcode(
  begin='\begin{comment}',
  end='\end{comment}'
)

e.itemize(
  open='[',
  close=']',
  numArgs=1
)
