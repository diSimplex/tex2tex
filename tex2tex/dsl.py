# A DSL to handle ConTeXt macros and environments

# inspired by:
#  https://nvbn.github.io/2015/04/04/python-html-dsl/

class macrosBase(type) :
  def __getattr__(cls, name) :
    return cls(name)

class macros(metaclass=macrosBase) :
  def __init__(self, name) :
    self.name = name

class environmentsBase(type) :
  def __getattr__(cls, name) :
    return cls(name)

class environments(metaclass=environmentsBase) :
  def __init__(self, name) :
    self.name = name
