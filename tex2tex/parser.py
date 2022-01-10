import yaml

import re
import sys

from .dsl import macroNames

class TokenAST() :
  def __init__(self, tokenValue) :
    self.token = tokenValue

  def tokenType(self) :
    return "unknown"

  def __str__(self) :
    return "{}: [{}]\n".format(self.tokenType(), self.token)

class TokenBackground(TokenAST) :
  def tokenType(self) :
    return "background"

class TokenComment(TokenAST) :
  def tokenType(self) :
    return "comment"

class TokenCommand(TokenAST) :
  def tokenType(self) :
    return "command"

class TokenGroup(TokenAST) :
  def tokenType(self) :
    return "group"

############################
# regular expressions
commentRegExp    = re.compile(r"\%[^\n]*")
commandRegExp    = re.compile(r"\\[^\\\{\[\(\%\s]*|\\[\¬\`\!\"\£\$\%\^\&\*\(\)\-\_\+\=\:\;\@\'\~\#\<\,\>\.\?\/\|\\]")
whiteSpaceRegExp = re.compile(r"\s*")
wordRegExp       = re.compile(r"[^\\\{\[\(\%\s]*")
backgroundRegExp = re.compile(r"[^\\\{\[\(\%]*")

groupEndMarkers = {
  '[' : ']',
  '{' : '}',
  '(' : ')',
  '\\bgroup' : '\\egroup'
}
groupStartMarkers = list(groupEndMarkers.keys())

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
        self.scanUsingRegExp("command", commandRegExp, TokenCommand)
      elif curChar in groupStartMarkers :
        self.scanGroup(curChar, groupEndMarks(curChar))
      elif self.items.startswith('\\bgroup', self.curIndex) :
        self.scanGroup('\\bgroup', '\\egroup')
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

  def scanWhiteSpace(self) :
    self.scanUsingRegExp("whiteSpace", whiteSpaceRegExp)

  def scanWord(self) :
    self.scanUsingRegExp("word", wordRegExp)

class TokenStream(ItemStream) :

  def addToken(self, aToken) :
    self.items.append(aToken)

  def dumpTokens(self) :
    print("----------------------------------------------------")
    for aToken in self.items :
      print(aToken)
    print("----------------------------------------------------")

