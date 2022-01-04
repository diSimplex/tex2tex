
from .loadConfiguration import parseCliArgs, loadConfig, loadMappings

def tex2tex() :
  cliArgs = parseCliArgs()
  config = loadConfig(cliArgs)
  loadMappings(config)

  print("Hello world!")
