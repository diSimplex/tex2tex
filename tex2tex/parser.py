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

class TokenWord(TokenBase) :
  def tokenType(self) :
    return "word"

class TokenStartGroup(TokenBase) :
  def tokenType(self) :
    return "startGroup"

class TokenEndGroup(TokenBase) :
  def tokenType(self) :
    return "endGroup"

############################
# regular expressions
commentRegExp    = re.compile(r"\%[^\n]*")
commandRegExp    = re.compile(r"\\[^\\\{\[\(\%\s]+|\\[ \¬\`\!\"\£\$\%\^\&\*\(\)\-\_\+\=\:\;\@\'\~\#\<\,\>\.\?\/\|\\]")
backgroundRegExp = re.compile(r"[^\\\{\}\[\]\(\)\%]*")

backgroundWordRegExp       = re.compile(r"\S+")
backgroundWhiteSpaceRegExp = re.compile(r"\s+")

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
        if self.items.startswith(bGroupMarker, self.curIndex) :
          self.tokens.addToken(TokenStartGroup(bGroupMarker))
          self.curIndex += len(bGroupMarker)
        elif self.items.startswith(eGroupMarker, self.curIndex) :
          self.tokens.addToken(TokenEndGroup(eGroupMarker))
          self.curIndex += len(eGroupMarker)
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

class NotEnoughArgumentsFound(Exception) :
  def __init__(self, numArgFound, numArgsExpected, areOptional, tokens) :
    self.numArgFound     = numArgFound
    self.numArgsExpected = numArgsExpected
    self.areOptional     = areOptional
    self.tokens          = tokens

  def __str__(self) :
    optWord = ""
    if self.areOptional : optWord = "optional "
    return "\n".join([
      "\nNot enough {}arguments found while parsing TeX file".format(optWord),
      " expected: {}".format(self.numArgsExpected),
      "    found: {}".format(self.numArgsFound),
      " while reading: [{}]".format("".join(self.tokens))
    ])

class NoEndGroupFound(Exception) :
  def __init__(self, endGroupToken, tokens) :
    self.endGroupToken = endGroupToken
    self.tokens        = tokens

  def __str__(self) :
    return "\n".join([
      "\nNo end group found while parsing TeX file",
      " expected: '{}'".format(self.endGroupToken),
      " while reading: [{}]".format("".join(self.tokens))
    ])

class NoBackgroundWordFound(Exception) :
  def __init__(self, theToken, tokens) :
    self.theToken = theToken
    self.tokens   = tokens

  def __str__(self) :
    return "\n".join([
      "\nNo background word found while parsing TeX file (should NOT get here!)",
      " the remaining background token: '{}'".format(self.theToken),
      " while reading: [{}]".format("".join(self.tokens))
    ])

def buildCommand(aCommand, tokens) :
  tCmd = ASTCommand(aCommand)
  #print("found command [{}]".format(aCommand))
  if aCommand.token not in macroNames : return tCmd

  macroDef = macroNames[aCommand.token]
  tCmd.macroDef = macroDef
  #print(yaml.dump(macroDef))
  numOptArgs = 0
  if 'numOptArgs' in macroDef and       \
    macroDef['numOptArgs'] is not None  \
    : numOptArgs = macroDef['numOptArgs']
  numReqArgs = 0
  if 'numReqArgs' in macroDef and       \
    macroDef['numReqArgs'] is not None  \
    : numReqArgs = macroDef['numReqArgs']
  if numOptArgs + numReqArgs < 1 : return tCmd

  tCmd.addArguments(*buildSequence(numOptArgs, numReqArgs, None, tokens))

  return tCmd

def buildGroup(startToken, tokens) :
  endGroup = start2endGroupMapping[startToken.token]
  (tSeq, optArgs, reqArgs) = buildSequence(None, None, endGroup, tokens)
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
    elif isinstance(curToken, TokenStartGroup) :
      if areOptional and curToken.token != '[' :
        tokens.insert(0, curToken)
        return theArgs
      tSeq.addToken(buildGroup(curToken, tokens))
      theArgs.append(len(tSeq.items))
    elif isinstance(curToken, TokenEndGroup) :
      if endGroup is not None and curToken.token == endGroup :
        if not areOptional and    \
          numArgs is not None and \
          len(theArgs) < numArgs  :
          raise NotEnoughArgumentsFound(len(theArgs), numArgs, areOptional, tokens)
        return theArgs
    elif isinstance(curToken, TokenBackground) :
      while not areOptional and numArgs is not None and \
        len(theArgs) < numArgs :
        theToken = curToken.token
        aBackgroundWordMatch = backgroundWordRegExp.search(theToken)
        if not aBackgroundWordMatch : break
        someWhiteSpace = backgroundWhiteSpaceRegExp.match(theToken)
        if someWhiteSpace :
          tSeq.addToken(TokenBackground(
            theToken[someWhiteSpace.start():someWhiteSpace.end()]
          ))
          theToken = theToken[someWhiteSpace.end() : len(theToken)]
        theWord = backgroundWordRegExp.match(theToken)
        if theWord :
          tSeq.addToken(TokenWord(theToken[theWord.start():theWord.end()]))
          theArgs.append(len(tSeq.items))
          theToken = theToken[theWord.end() : len(theToken)]
        else : raise NoBackgroundWordFound(theToken, tokens)
        curToken.token = theToken
      tSeq.addToken(curToken)
    else :
      tSeq.addToken(curToken)
  if endGroup is not None : raise NoEndGroupFound(endGroup, tokens)
  if not areOptional and    \
    numArgs is not None and \
    len(theArgs) < numArgs  :
    raise NotEnoughArgumentsFound(len(theArgs), numArgs, areOptional, tokens)
  return theArgs

def buildSequence(numOptArgs, numReqArgs, endGroup, tokens) :
  tSeq = ASTSequence()

  optArgs = []
  if numOptArgs is not None and 0 < numOptArgs :
    optArgs = buildInnerSequence(tSeq, numOptArgs, True,  endGroup, tokens)
  reqArgs = buildInnerSequence(tSeq, numReqArgs, False, endGroup, tokens)
  return (tSeq, optArgs, reqArgs)

def buildAST(tokens) :
  (tSeq, optArgs, reqArgs) = buildSequence(None, None, None, tokens)
  return tSeq
