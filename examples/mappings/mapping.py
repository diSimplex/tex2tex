# An example tex2tex remapping

from tex2tex.dsl import Macros as m
from tex2tex.dsl import Environments as e

m.usebtxdataset(
  open='[',
  close=']',
  numOptArgs=1
)

m.usemodule()

m.diSimpEnvironment()

m.diSimpComonent()

e.diSimplexComponent(
  numReqArgs=1
)

e.group(
  start='b',
  stop='e'
)

m.placefigure(
  open='[{',
  close=']}',
  numReqArgs=3,
)

e.MPcode(
  begin='\begin{comment}',
  end='\end{comment}'
)

e.itemize(
  open='[',
  close=']',
  numOptArgs=1
)
