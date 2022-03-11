from io import StringIO

import os
import sys
import yaml

from .loadConfiguration import parseCliArgs, loadConfig, loadMappings
from .parser import CharStream, buildAST
from .dsl import macroNames

def tex2tex() :
  cliArgs = parseCliArgs()
  config = loadConfig(cliArgs)
  loadMappings(config)

  print(cliArgs.texFiles)
  print(yaml.dump(cliArgs.texFiles))

  for aTeXPath in cliArgs.texFiles :
    with open(aTeXPath, 'r') as aTeXFile :
      aTeXFileStr = aTeXFile.read()

      cStream = CharStream(aTeXFileStr)

      cStream.scanTokens()

      #cStream.tokens.dumpTokens()

      tSeq = buildAST(cStream.tokens)

      #tSeq.dumpAST()

      with open(
        os.path.join(cliArgs.outputDir, aTeXPath),
        'w') as anOutFile:
        tSeq.writeTeXto(anOutFile)

  print("Done!")
