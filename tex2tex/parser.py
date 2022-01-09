
import re
import sys

from .dsl import macroNames

class TokenAST() :
  pass

class TokenWhiteSpace(TokenAST) :
  pass

class TokenComment(TokenAST) :
  pass

class TokenCommand(TokenAST) :
  pass

class TokenGroup(TokenAST) :
  pass

############################
# regular expressions
commentRegExp    = re.compile(r"\%[^\n]*")
commandRegExp    = re.compile(r"\\[^\\\{\[\(\%\s]*")
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

class CharStream() :
  def __init__(self, text='') :
    self.text     = text
    self.numChars = len(text)
    self.curIndex = 0

  def hasMore(self) :
    return self.curIndex < self.numChars

  def curChar(self) :
    if self.numChars <= self.curIndex :
      return None
    return self.text[self.curIndex]

  def nextChar(self) :
    print("nextChar[{}] '{}'->'{}'".format(
      self.curIndex, self.text[self.curIndex], self.text[self.curIndex+1]
    ))
    if self.numChars <= self.curIndex :
      return None
    aChar = self.text[self.curIndex]
    self.curIndex += 1
    return aChar

  def previousChar(self) :
    if self.curIndex <= 0 :
      return None
    self.curIndex -= 1
    return self.text[self.curIndex]

  def scanTokens(self) :
    curChar = self.curChar()
    while curChar :
      print("\ncurChar: [{}]".format(curChar))
      if curChar == "%" :
        self.scanUsingRegExp("comment", commentRegExp)
      elif curChar == "\\" :
        self.scanUsingRegExp("command", commandRegExp)
      elif curChar in groupStartMarkers :
        self.scanGroup(curChar, groupEndMarks(curChar))
      elif self.text.startswith('\\bgroup', self.curIndex) :
        self.scanGroup('\\bgroup', '\\egroup')
      else :
        self.scanUsingRegExp("background", backgroundRegExp)
      curChar = self.curChar()

  def reportCurChar(self, msg) :
    print("{} text[{}] = '{}'".format(
      msg, self.curIndex, self.text[self.curIndex]
    ))

  def reportFailure(self, tokenType) :
    print("Could not parse a {}:".format(tokenType))
    self.reportCurChar("  looking at")
    reportStart = self.curIndex - 10
    if reportStart < 0 : reportStart = 0
    reportEnd   = self.curIndex + 10
    if self.numChars <= reportEnd : reportEnd   = self.numChars - 1
    print("  [{}]".format(self.text[reportStart:reportEnd]))
    sys.exit(-1)

  def reportStr(self, tokenType, strStart, strEnd) :
    print("{} start: {} end: {}".format(tokenType, strStart, strEnd))
    print("[{}]".format(self.text[strStart:strEnd]))

  def scanUsingRegExp(self, tokenType, tokenRegExp) :
    self.reportCurChar("looking for {} at".format(tokenType))
    tokenStart = self.curIndex
    aMatch = tokenRegExp.match(self.text, self.curIndex)
    if not aMatch : self.reportFailure(tokenType)
    print(aMatch)
    tokenEnd = aMatch.end()
    self.curIndex = tokenEnd
    self.reportStr(tokenType, tokenStart, tokenEnd)

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
