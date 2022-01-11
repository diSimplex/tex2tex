import yaml

import re
import sys

from .dsl import macroNames

class TokenBase() :
  def __init__(self, tokenValue) :
    self.token = tokenValue

  def tokenType(self) :
    return "unknown"

  def __str__(self) :
    return "{}: [{}]\n".format(self.tokenType(), self.token)

class TokenBackground(TokenBase) :
  def tokenType(self) :
    return "background"

class TokenComment(TokenBase) :
  def tokenType(self) :
    return "comment"

class TokenCommand(TokenBase) :
  def tokenType(self) :
    return "command"

class TokenStartGroup(TokenBase) :
  def tokenType(self) :
    return "startGroup"

class TokenEndGroup(TokenBase) :
  def tokenType(self) :
    return "endGroup"

############################
# regular expressions
commentRegExp    = re.compile(r"\%[^\n]*")
commandRegExp    = re.compile(r"\\[^\\\{\[\(\%\s]*|\\[\¬\`\!\"\£\$\%\^\&\*\(\)\-\_\+\=\:\;\@\'\~\#\<\,\>\.\?\/\|\\]")
backgroundRegExp = re.compile(r"[^\\\{\}\[\]\(\)\%]*")

bGroupMarker = '\\bgroup'
startGroupMarkers = [ "[", "(", "{" ]

eGroupMarker = '\\egroup'
endGroupMarkers   = [ "}", ")", "]" ]

start2endGroupMapping = {
  bGroupMarker : eGroupMarker,
  "[" : "]",
  "(" : ")",
  "{" : "}"
}

class ItemStream() :
  def __init__(self, items=[]) :
    self.items    = items
    self.numItems = len(items)
    self.curIndex = 0

  def hasMore(self) :
    return self.curIndex < self.numItems

  def curItem(self) :
    if self.numItems <= self.curIndex :
      return None
    return self.items[self.curIndex]

  def nextItem(self) :
    print("nextItem[{}] '{}'->'{}'".format(
      self.curIndex, self.items[self.curIndex], self.items[self.curIndex+1]
    ))
    if self.numItems <= self.curIndex :
      return None
    anItem = self.items[self.curIndex]
    self.curIndex += 1
    return anItem

  def previousItem(self) :
    if self.curIndex <= 0 :
      return None
    self.curIndex -= 1
    return self.items[self.curIndex]

class CharStream(ItemStream) :
  def __init__(self, text) :
    super(CharStream, self).__init__(text)
    self.tokens = TokenStream()

  def scanTokens(self) :
    curChar = self.curItem()
    while curChar :
      #print("\ncurChar: [{}]".format(curChar))
      if curChar == "%" :
        self.scanUsingRegExp("comment", commentRegExp, TokenComment)
      elif curChar == "\\" :
        if self.items.startswith('\\bgroup') :
          self.tokens.addToken(TokenStartGroup('\\bgroup'))
          self.curIndex += len('\\bgroup')
        elif self.items.startswith('\\egroup') :
          self.tokens.addToken(TokenStartGroup('\\bgroup'))
        else :
          self.scanUsingRegExp("command", commandRegExp, TokenCommand)
      elif curChar in startGroupMarkers :
        self.tokens.addToken(TokenStartGroup(curChar))
        self.curIndex += 1
      elif curChar in endGroupMarkers :
        self.tokens.addToken(TokenEndGroup(curChar))
        self.curIndex += 1
      else :
        self.scanUsingRegExp("background", backgroundRegExp, TokenBackground)
      curChar = self.curItem()

  def reportCurChar(self, msg) :
    print("{} text[{}] = '{}'".format(
      msg, self.curIndex, self.items[self.curIndex]
    ))

  def reportFailure(self, tokenType) :
    print("Could not parse a {}:".format(tokenType))
    self.reportCurChar("  looking at")
    reportStart = self.curIndex - 10
    if reportStart < 0 : reportStart = 0
    reportEnd   = self.curIndex + 10
    if self.numItems <= reportEnd : reportEnd   = self.numItems - 1
    print("  [{}]".format(self.items[reportStart:reportEnd]))
    sys.exit(-1)

  def reportStr(self, tokenType, strStart, strEnd) :
    print("{} start: {} end: {}".format(tokenType, strStart, strEnd))
    print("[{}]".format(self.items[strStart:strEnd]))

  def scanUsingRegExp(self, tokenType, tokenRegExp, tokenCls) :
    #self.reportCurChar("looking for {} at".format(tokenType))
    tokenStart = self.curIndex
    aMatch = tokenRegExp.match(self.items, self.curIndex)
    if not aMatch : self.reportFailure(tokenType)
    tokenEnd = aMatch.end()
    self.curIndex = tokenEnd
    theToken = object.__new__(tokenCls)
    theToken.__init__(self.items[tokenStart:tokenEnd])
    self.tokens.addToken(theToken)
    #self.reportStr(tokenType, tokenStart, tokenEnd)

  def scanGroup(self, groupStart, groupEnd) :
    self.reportCurChar("looking for '{}'/'{}' group at".format(
      groupStart, groupEnd
    ))
    #self.reportStr('group', groupStart, groupEnd)
    pass

class TokenStream(ItemStream) :

  def __init__(self) :
    super().__init__([])

  def addToken(self, aToken) :
    self.items.append(aToken)

  def dumpTokens(self) :
    print("----------------------------------------------------")
    for aToken in self.items :
      print(aToken)
    print("----------------------------------------------------")

class ASTSequence() :
  def __init__(self) :
    self.items = []

  def addToken(self, aToken) :
    self.items.append(aToken)

class ASTCommand() :
  def __init__(self, aCommand) :
    self.command  = aCommand
    self.optArgs  = None
    self.reqArgs  = None
    self.sequence = None
    self.macroDef = None

  def addArguments(self, tSeq, optArgs, reqArgs) :
    self.sequence = tSeq
    self.optArgs  = optArgs
    self.reqArgs  = reqArgs

class ASTGroup() :
  def __init__(self, startToken) :
    self.startToken = startToken
    self.endToken   = start2endGroupMapping[startToken]
    self.sequence   = ASTSequence()

  def addToken(self, aToken) :
    self.sequence.addToken(aToken)

class NotEnoughArgumentsFound() :
  def __init__(self, numArgFound, numArgsExpected, areOptional, tokens) :
    self.numArgFound     = numArgFound
    self.numArgsExpected = numArgsExpected
    self.areOptional     = areOptional
    self.tokens          = tokens

  def __str__(self) :
    optWord = ""
    if self.areOptional : optWord = "optional "
    print("Not enough {}arguments found while parsing TeX file".format(optWord))
    print(" expected: {}".format(self.numArgsExpected))
    print("    found: {}".format(self.numArgsFound))
    print(" while reading: [{}]".format("".join(tokens)))

class NoEndGroupFound() :
  def __init__(self, endGroupToken, tokens) :
    self.endGroupToken = endGroupToken
    self.tokens        = tokens

  def __str__(self) :
    print("No end group found while parsing TeX file")
    print(" expected: {}".format(self.endGroupToken))
    print(" while reading: [{}]".format("".join(tokens)))

def buildCommand(aCommand, tokens) :
  tCmd = ASTCommand(aCommand)
  if aCommand.token not in macroNames : return tCmd

  macroDef = macroNames[aCommand.token]
  tCmd.macroDef = macroDef

  if macroDef.numOptArgs + macroDef.numReqArgs < 1 : return tCmd

  tCmd.addArguments(buildSequence(
    macroDef.numOptArgs, macroDef.numReqArgs, tokens
  ))

  return tCmd

def buildGroup(startToken, tokens) :
  endGroup = start2endGroupMappiing[startToken.token]
  (tSeq, optArgs, reqArgs) = buildSequence(
    None, None, endGroup, tokens
  )
  return tSeq

def buildInnerSequence(tSeq, numArgs, areOptional, endGroup, tokens) :
  theArgs = []
  while 0 < len(tokens) :
    if endGroup is None and   \
      numArgs is not None and \
      numArgs <= len(theArgs) :
      return theArgs
    curToken = tokens.pop(0)
    if isinstance(curToken, TokenCommand) :
      tSeq.addToken(buildCommand(curToken, tokens))
    elif isInstance(curToken, TokenStartGroup) :
      if areOptional and curToken.token != '[' :
        tokens.insert(0, curToken)
        return theArgs
      tSeq.addToken(buildGroup(curToken, tokens))
      numArgs.append(len(tSeq.items))
    elif isInstance(curToken, TokenEndGroup) :
      if endGroup is not None and curToken.token == endGroup :
        if not areOptional and    \
          numArgs is not None and \
          len(theArgs) < numArgs  :
          raise NotEnoughArgumentsFound(len(theArgs), numArgs, areOptional)
        return theArgs
    else :
      tSeq.addToken(curToken)
  if endGroup is not None : raise NoEndGroupFound(endGroup)
  if not areOptional and    \
    numArgs is not None and \
    len(theArgs) < numArgs  :
    raise NotEnoughArgumentsFound(len(theArgs), numArgs, areOptional)
  return theArgs

def buildSequence(numOptArgs, numReqArgs, endGroup, tokens) :
  tSeq = ASTSequence()

  optArgs = buildInnerSequence(tSeq, numOptArgs, True,  endGroup, tokens)
  reqArgs = buildInnerSequence(tSeq, numReqArgs, False, endGroup, tokens)
  return (tSeq, optArgs, reqArgs)
