# A DSL to handle ConTeXt macros and environments

# inspired by:
#  https://nvbn.github.io/2015/04/04/python-html-dsl/
# and
#  https://realpython.com/primer-on-python-decorators/#decorating-functions-with-arguments

macroNames = { }

def addMacro(
  name,
  open=None, close=None, numArgs=0
) :
  if name in macroNames :
    print("Redefining the existing macro {} : new definition ignored".format(name))
  else :
    macroNames[name] = {
      'type'    : 'macro',
      'name'    : name,
      'open'    : open,
      'close'   : close,
      'numArgs' : numArgs
    }

def addEnvironment(
  name,
  open=None, close=None, numArgs=0,
  start=None, stop=None, begin=None, end=None
) :
  if name in macroNames :
    print("Redefining the existing environment {} : new definition ignored".format(name))
  else :
    macroNames[name] = {
      'type'    : 'environment',
      'name'    : name,
      'numArgs' : numArgs,
      'start'   : start,
      'stop'    : stop,
      'begin'   : begin,
      'end'     : end
    }

class MacrosType(type) :
  def __getattr__(cls, name) :
    def wrapper_macro(*args, **kwargs) :
      addMacro(name, **kwargs)
    return wrapper_macro

class Macros(metaclass=MacrosType) :
  pass

class EnvironmentsType(type) :
  def __getattr__(cls, name) :
    def wrapper_environment(*args, **kwargs) :
      addEnvironment(name, **kwargs)
    return wrapper_environment

class environments(metaclass=EnvironmentsType) :
  pass
