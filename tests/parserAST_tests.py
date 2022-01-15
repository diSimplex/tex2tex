import unittest
import yaml

from tex2tex.parser import CharStream,         \
  TokenBackground, TokenComment, TokenCommand, \
  TokenStartGroup, TokenEndGroup,              \
  ASTSequence, buildAST

from tex2tex.dsl import Macros as m
from tex2tex.dsl import Environments as e
from tex2tex.dsl import macroNames

m.testMacroZero()
m.testMacroOneReq(
  numReqArgs=1
)
print("--------------------------------------------------")
print(yaml.dump(macroNames))
print("--------------------------------------------------")

class TestParserAST(unittest.TestCase) :

  def test_simpleTokens(t) :
    text = """
    This is a test
    %This is a comment
    This is another test
    %This is another comment
    This is the end!
"""
    cStream = CharStream(text)
    cStream.scanTokens()
    tStream = cStream.tokens
    t.assertIsNotNone(tStream)
    tokens = tStream.items
    t.assertIsNotNone(tokens)
    anAST = buildAST(tokens)
    t.assertIsNotNone(anAST)
    t.assertIsInstance(anAST, ASTSequence)
    items = anAST.items
    t.assertIsInstance(items, list)
    t.assertEqual(len(items), 5)
    t.assertIsInstance(items[0], TokenBackground)
    t.assertRegex(items[0].token, "This is a test")
    t.assertIsInstance(items[1], TokenComment)
    t.assertRegex(items[1].token, "This is a comment")
    t.assertIsInstance(items[2], TokenBackground)
    t.assertRegex(items[2].token, "This is another test")
    t.assertIsInstance(items[3], TokenComment)
    t.assertRegex(items[3].token, "This is another comment")
    t.assertIsInstance(items[4], TokenBackground)
    t.assertRegex(items[4].token, "This is the end")

  def test_simpleGroup(t) :
    text = """
    %This is a \test
    \\bgroup
    %This is a comment
    This is another test
    %This is another comment
    \\egroup
    This is the end!
"""
    cStream = CharStream(text)
    cStream.scanTokens()
    tStream = cStream.tokens
    t.assertIsNotNone(tStream)
    tokens = tStream.items
    t.assertIsNotNone(tokens)
    #print(yaml.dump(tokens))
    anAST = buildAST(tokens)
    t.assertIsNotNone(anAST)
    t.assertIsInstance(anAST, ASTSequence)
    items = anAST.items
    t.assertIsInstance(items, list)
    t.assertEqual(len(items), 5)
    aGroup = items[3]
    t.assertIsNotNone(anAST)
    t.assertIsInstance(aGroup, ASTSequence)
    gItems = aGroup.items
    t.assertIsInstance(gItems, list)
    t.assertEqual(len(gItems), 5)
    t.assertIsInstance(gItems[0], TokenBackground)
    t.assertEqual(gItems[0].token, "\n    ")
    t.assertIsInstance(gItems[1], TokenComment)
    t.assertRegex(gItems[1].token, "This is a comment")
    t.assertIsInstance(gItems[2], TokenBackground)
    t.assertRegex(gItems[2].token, "This is another test")
    t.assertIsInstance(gItems[3], TokenComment)
    t.assertRegex(gItems[3].token, "This is another comment")
    t.assertIsInstance(gItems[4], TokenBackground)
    t.assertEqual(gItems[4].token, "\n    ")

  def test_simpleMacro(t) :
    text = """
    This is a \\testMacroOneReq
    \\bgroup
    %This is a comment
    This is another test
    %This is another comment
    \\egroup
"""
    cStream = CharStream(text)
    cStream.scanTokens()
    tStream = cStream.tokens
    t.assertIsNotNone(tStream)
    tokens = tStream.items
    t.assertIsNotNone(tokens)
    print(yaml.dump(tokens))
    anAST = buildAST(tokens)
    print(yaml.dump(anAST))

