import unittest

from tex2tex.parser import CharStream, \
  TokenBackground, TokenComment, TokenCommand

class TestParser(unittest.TestCase) :

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

  def test_complex(self) :
    text = """
\\This is a test
%This is another test
Yet more background

Until the end!
"""
    cStream = CharStream(text)
    cStream.scanTokens()
    tStream = cStream.tokens
    self.assertIsNotNone(tStream)
    tokens  = tStream.items
    self.assertIsNotNone(tokens)
    self.assertEqual(len(tokens), 5)
    self.assertIsInstance(tokens[0], TokenBackground)
    self.assertEqual(tokens[0].token, "\n")
    self.assertIsInstance(tokens[1], TokenCommand)
    self.assertEqual(tokens[1].token, "\\This")
    self.assertIsInstance(tokens[2], TokenBackground)
    self.assertEqual(tokens[2].token, " is a test\n")
    self.assertIsInstance(tokens[3], TokenComment)
    self.assertEqual(tokens[3].token, "%This is another test")
    self.assertIsInstance(tokens[4], TokenBackground)
    self.assertEqual(tokens[4].token, "\nYet more background\n\nUntil the end!\n")
