import unittest

from tex2tex.parser import CharStream, \
  TokenBackground, TokenComment, TokenCommand, \
  TokenStartGroup, TokenEndGroup

class TestParserTokens(unittest.TestCase) :

  def test_background(self) :
    text = """
This is a test
This is another test
Yet more background

Until the end!
"""
    cStream = CharStream(text)
    cStream.scanTokens()
    tStream = cStream.tokens
    self.assertIsNotNone(tStream)
    tokens  = tStream.items
    self.assertIsNotNone(tokens)
    self.assertEqual(len(tokens), 1)
    self.assertIsInstance(tokens[0], TokenBackground)
    self.assertEqual(tokens[0].token, text)

  def test_comment(self) :
    text = "%this is a comment"
    cStream = CharStream(text)
    cStream.scanTokens()
    tStream = cStream.tokens
    self.assertIsNotNone(tStream)
    tokens  = tStream.items
    self.assertIsNotNone(tokens)
    self.assertEqual(len(tokens), 1)
    self.assertIsInstance(tokens[0], TokenComment)
    self.assertEqual(tokens[0].token, text)

  def test_command(self) :
    text = "\\thisIsACommand"
    cStream = CharStream(text)
    cStream.scanTokens()
    tStream = cStream.tokens
    self.assertIsNotNone(tStream)
    tokens  = tStream.items
    self.assertIsNotNone(tokens)
    self.assertEqual(len(tokens), 1)
    self.assertIsInstance(tokens[0], TokenCommand)
    self.assertEqual(tokens[0].token, text)

  def test_startGroup(self) :
    text = "[{("
    cStream = CharStream(text)
    cStream.scanTokens()
    tStream = cStream.tokens
    self.assertIsNotNone(tStream)
    tokens  = tStream.items
    self.assertIsNotNone(tokens)
    self.assertEqual(len(tokens), 3)
    self.assertIsInstance(tokens[0], TokenStartGroup)
    self.assertEqual(tokens[0].token, "[")
    self.assertIsInstance(tokens[1], TokenStartGroup)
    self.assertEqual(tokens[1].token, "{")
    self.assertIsInstance(tokens[2], TokenStartGroup)
    self.assertEqual(tokens[2].token, "(")

  def test_endGroup(self) :
    text = "]})"
    cStream = CharStream(text)
    cStream.scanTokens()
    tStream = cStream.tokens
    self.assertIsNotNone(tStream)
    tokens  = tStream.items
    self.assertIsNotNone(tokens)
    self.assertEqual(len(tokens), 3)
    self.assertIsInstance(tokens[0], TokenEndGroup)
    self.assertEqual(tokens[0].token, "]")
    self.assertIsInstance(tokens[1], TokenEndGroup)
    self.assertEqual(tokens[1].token, "}")
    self.assertIsInstance(tokens[2], TokenEndGroup)
    self.assertEqual(tokens[2].token, ")")

  def test_complex(self) :
    text = """
\\This[ is ]{a}(test)
%This is another test
Yet more background

Until the end!
"""
    cStream = CharStream(text)
    cStream.scanTokens()
    tStream = cStream.tokens
    self.assertIsNotNone(tStream)
    #tStream.dumpTokens()
    tokens  = tStream.items
    self.assertIsNotNone(tokens)
    self.assertEqual(len(tokens), 14)
    self.assertIsInstance(tokens[0], TokenBackground)
    self.assertEqual(tokens[0].token, "\n")
    self.assertIsInstance(tokens[1], TokenCommand)
    self.assertEqual(tokens[1].token, "\\This")
    self.assertIsInstance(tokens[2], TokenStartGroup)
    self.assertEqual(tokens[2].token, "[")
    self.assertIsInstance(tokens[3], TokenBackground)
    self.assertEqual(tokens[3].token, " is ")
    self.assertIsInstance(tokens[4], TokenEndGroup)
    self.assertEqual(tokens[4].token, "]")
    self.assertIsInstance(tokens[5], TokenStartGroup)
    self.assertEqual(tokens[5].token, "{")
    self.assertIsInstance(tokens[6], TokenBackground)
    self.assertEqual(tokens[6].token, "a")
    self.assertIsInstance(tokens[7], TokenEndGroup)
    self.assertEqual(tokens[7].token, "}")
    self.assertIsInstance(tokens[8], TokenStartGroup)
    self.assertEqual(tokens[8].token, "(")
    self.assertIsInstance(tokens[9], TokenBackground)
    self.assertEqual(tokens[9].token, "test")
    self.assertIsInstance(tokens[10], TokenEndGroup)
    self.assertEqual(tokens[10].token, ")")
    self.assertIsInstance(tokens[11], TokenBackground)
    self.assertEqual(tokens[11].token, "\n")
    self.assertIsInstance(tokens[12], TokenComment)
    self.assertEqual(tokens[12].token, "%This is another test")
    self.assertIsInstance(tokens[13], TokenBackground)
    self.assertEqual(tokens[13].token, "\nYet more background\n\nUntil the end!\n")
