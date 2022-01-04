""" Load and normalize the tex2tex configuration """

import argparse
import importlib
import logging
import os
import pkgutil
import sys
import traceback
import yaml

import tex2tex.yamlLoader

def parseCliArgs() :
  argparser = argparse.ArgumentParser(
    description="A simple tool to transliterate TeX macros."
  )
  argparser.add_argument("-c", "--config", action='append',
    default=[], help="overlay configuration from file"
  )
  argparser.add_argument("-m", "--mappings", action='append',
    default=[], help="add a directory of macro and environment mappings"
  )
  argparser.add_argument("-v", "--verbose", default=False,
    action=argparse.BooleanOptionalAction,
    help="show the loaded configuration"
  )
  argparser.add_argument("-d", "--debug", default=False,
    action=argparse.BooleanOptionalAction,
    help="provide debugging output"
  )
  return argparser.parse_args()

def loadConfig(cliArgs) :

  """

  Load the configuration by merging any `tex2texConfig.yaml` found in the
  current working directory, and then any other configuration files
  specified on the command line.

  Then perform the following normalisation:

  """
  print("Hello from loadConfig")

  config = {
    'verbose' : False,
    'debug'   : False,
    'mappingDirs' : [ ]
  }

  if cliArgs.verbose :
    config['verbose'] = cliArgs.verbose

  if cliArgs.debug :
    config['debug'] = cliArgs.debug

  unLoadedConfig = cliArgs.config.copy()
  unLoadedConfig.insert(0,'tex2texConfig.yaml')
  print(yaml.dump(unLoadedConfig))
  while 0 < len(unLoadedConfig) :
    aConfigPath = unLoadedConfig[0]
    del unLoadedConfig[0]
    if os.path.exists(aConfigPath) :
      try :
        cputils.yamlLoader.loadYamlFile(config, aConfigPath)
        if 'include' in config :
          unLoadedConfig.extend(config['include'])
          del config['include']
      except Exception as err :
        print("Could not load configuration from [{}]".format(aConfigPath))
        print(err)

  if cliArgs.mappings :
    config['mappingDirs'] = cliArgs.mappings
  config['mappingDirs'].insert(0, 'tex2tex/mappings/common')

  if config['verbose'] :
    print("--------------------------------------------------------------")
    print(yaml.dump(config))
    print("--------------------------------------------------------------")

  return config

def loadMappings(config) :
  print("Hello from loadMappings")
  for aMappingDir in config['mappingDirs'] :
    aPkgPath = aMappingDir.replace('/','.')
    if aMappingDir.startswith('tex2tex') :
      aMappingDir = os.path.join(os.path.dirname(__file__), aMappingDir.replace('tex2tex/', ''))
    if not aMappingDir.startswith('/') :
      currentWD = os.path.abspath(os.getcwd())
      if currentWD not in sys.path :
        sys.path.insert(0, currentWD)
    print("loading from {}".format(aMappingDir))
    for (_, module_name, _) in pkgutil.iter_modules([aMappingDir]) :
      print("Importing the {} mapping".format(module_name))
      theMapping = importlib.import_module(aPkgPath+'.'+module_name)
      if hasattr(theMapping, 'registerMapping') :
        logging.info("Registering the {} mapping".format(module_name))
        theMapping.registerMapping(config)
      else:
        logging.info("Mapping {} has no registerMapping method!".format(module_name))
