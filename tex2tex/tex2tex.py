
import yaml

from .loadConfiguration import parseCliArgs, loadConfig, loadMappings
from .parser import CharStream
from .dsl import macroNames

def tex2tex() :
  cliArgs = parseCliArgs()
  config = loadConfig(cliArgs)
  loadMappings(config)

  cStream = CharStream("""
\This is a test
%This is another test
Yet more background

Until the end!
""")

  cStream.scanTokens()

  cStream.tokens.dumpTokens()

  print("Done!")
