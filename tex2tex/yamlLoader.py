# The ComputePods YAML file loader

import logging
import pathlib
import yaml

class NoYamlFile(Exception) :
  def __init__(self, aPath, msg=None) :
    self.yamlPath = aPath
    self.message   = msg

class NoYamlDirectory(NoYamlFile) :
 def __init__(self, aPath) :
   super().__init__(aPath)

def mergeYamlData(yamlData, newYamlData, thePath) :
  """ This is a generic Python merge. It is a *deep* merge and handles
  both dictionaries and arrays """

  if type(yamlData) is None :
    logging.error("yamlData should NEVER be None ")
    logging.error("Stoping merge at {}".format(thePath))
    return

  if type(yamlData) != type(newYamlData) :
    logging.error("Incompatible types {} and {} while trying to merge YAML data at {}".format(type(yamlData), type(newYamlData), thePath))
    logging.error("Stoping merge at {}".format(thePath))
    return

  if type(yamlData) is dict :
    for key, value in newYamlData.items() :
      if key not in yamlData :
        yamlData[key] = value
      elif type(yamlData[key]) is dict :
        mergeYamlData(yamlData[key], value, thePath+'.'+key)
      elif type(yamlData[key]) is list :
        for aValue in value :
          yamlData[key].append(aValue)
      else :
        yamlData[key] = value
  elif type(yamlData) is list :
    for value in newYamlData :
      yamlData.append(value)
  else :
    logging.error("YamlData MUST be either a dictionary or an array.")
    logging.error("Stoping merge at {}".format(thePath))
    return

def loadYamlFile(theConfigData, aYamlPath, callBack=None) :
  newYamlData = {}
  with open(aYamlPath) as yamlFile :
    try :
      logging.info("loading YAML from [{}]".format(aYamlPath))
      newYamlData = yaml.safe_load(yamlFile)
      if callBack is not None : callBack(newYamlData)
      mergeYamlData(theConfigData, newYamlData, "")
    except Exception as err :
      logging.error("Could not load YAML from [{}]\n{}".format(
        aYamlPath,
        repr(err)
      ))
      raise NoYamlFile(str(aYamlPath), repr(err))

def loadYamlFrom(theConfigData, aYamlDir, yamlExtensions, callBack=None) :
  """Load YAML files in the directory provided"""

  someYaml = pathlib.Path(aYamlDir)
  if not someYaml.is_dir() :
    logging.error("No YAML directory found at [{}]".format(someYaml))
    raise NoYamlDirectory(str(someYaml))

  for aFile in someYaml.iterdir() :
    if aFile.is_dir() :
      loadYamlFrom(theConfigData, aFile, yamlExtensions, callBack)

    else:
      if aFile.suffix.upper() in yamlExtensions :
        loadYamlFile(theConfigData, aFile, callBack)