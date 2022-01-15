import io
import unittest
import yaml

from tex2tex.parser import CharStream,         \
  TokenBackground, TokenComment, TokenCommand, \
  TokenWord, TokenStartGroup, TokenEndGroup,   \
  ASTSequence, ASTGroup, ASTCommand, buildAST

from tex2tex.dsl import Macros as m
from tex2tex.dsl import Environments as e
from tex2tex.dsl import macroNames

m.testMacroZero()
m.testMacroOneReq(
  numReqArgs=1
)
m.testMacro(
  numOptArgs=1,
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
    t.assertIsInstance(aGroup, ASTGroup)
    gItems = aGroup.sequence.items
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
    This is a \\testMacroZero\\ with a \\testMacroOneReq
    \\bgroup
    %This is a comment
    This is another test
    %This is another comment
    \\egroup
    This is the last \\testMacroZero
"""
    cStream = CharStream(text)
    cStream.scanTokens()
    tStream = cStream.tokens
    t.assertIsNotNone(tStream)
    tokens = tStream.items
    t.assertIsNotNone(tokens)
    #print(yaml.dump(tokens))
    anAST = buildAST(tokens)
    #print(yaml.dump(anAST))
    items = anAST.items
    t.assertIsInstance(items, list)
    t.assertEqual(len(items), 8)
    t.assertIsInstance(items[1], ASTCommand)
    t.assertEqual(items[1].command.token, '\\testMacroZero')
    t.assertIsInstance(items[2], ASTCommand)
    t.assertEqual(items[2].command.token, '\\ ')
    t.assertIsInstance(items[4], ASTCommand)
    t.assertEqual(items[4].command.token, '\\testMacroOneReq')
    cSeq = items[4].sequence.items
    t.assertIsNotNone(cSeq)
    t.assertEqual(len(cSeq), 2)
    gSeq = cSeq[1].items
    t.assertIsNotNone(gSeq)
    t.assertEqual(len(gSeq), 5)
    t.assertEqual(len(items[4].reqArgs), 1)
    t.assertEqual(items[4].reqArgs[0], 2)
    t.assertIsInstance(items[6], ASTCommand)
    t.assertEqual(items[6].command.token, '\\testMacroZero')

  def test_simpleMacro(t) :
    text = """
    This is a \\testMacro
    {This is a required argument}
    This is a \\testMacro
    [this is an optional argument]
    {this is another required argument}
    This is the last line
"""
    cStream = CharStream(text)
    cStream.scanTokens()
    tStream = cStream.tokens
    t.assertIsNotNone(tStream)
    tokens = tStream.items
    t.assertIsNotNone(tokens)
    #print(yaml.dump(tokens))
    anAST = buildAST(tokens)
    #print(yaml.dump(anAST))
    items = anAST.items
    t.assertIsInstance(items, list)
    t.assertEqual(len(items), 5)

    t.assertIsInstance(items[1], ASTCommand)
    t.assertEqual(items[1].command.token, '\\testMacro')
    cSeq = items[1].sequence.items
    t.assertIsNotNone(cSeq)
    t.assertEqual(len(cSeq), 2)
    gSeq = cSeq[1].sequence.items
    t.assertIsNotNone(gSeq)
    t.assertEqual(len(gSeq), 1)
    t.assertRegex(gSeq[0].token, "This is a required argument")
    t.assertEqual(len(items[1].reqArgs), 1)
    t.assertEqual(items[1].reqArgs[0], 2)

    t.assertIsInstance(items[3], ASTCommand)
    t.assertEqual(items[3].command.token, '\\testMacro')
    t.assertEqual(len(items[3].optArgs), 1)
    t.assertEqual(items[3].optArgs[0], 2)
    t.assertEqual(len(items[3].reqArgs), 1)
    t.assertEqual(items[3].reqArgs[0], 4)
    cSeq = items[3].sequence.items
    t.assertIsNotNone(cSeq)
    t.assertEqual(len(cSeq), 4)
    gSeq = cSeq[1].sequence.items
    t.assertIsNotNone(gSeq)
    t.assertEqual(len(gSeq), 1)
    t.assertRegex(gSeq[0].token, "this is an optional argument")
    gSeq = cSeq[3].sequence.items
    t.assertIsNotNone(gSeq)
    t.assertEqual(len(gSeq), 1)
    t.assertRegex(gSeq[0].token, "this is another required argument")

  def test_nonGroupArgument(t) :
    text = """
    This is a \\testMacroOneReq
    argument
    This is the last line
"""
    cStream = CharStream(text)
    cStream.scanTokens()
    tStream = cStream.tokens
    t.assertIsNotNone(tStream)
    tokens = tStream.items
    t.assertIsNotNone(tokens)
    #print(yaml.dump(tokens))
    anAST = buildAST(tokens)
    #print(yaml.dump(anAST))
    items = anAST.items
    t.assertIsInstance(items, list)
    t.assertEqual(len(items), 2)
    t.assertIsInstance(items[1], ASTCommand)
    t.assertEqual(items[1].command.token, '\\testMacroOneReq')
    t.assertEqual(len(items[1].optArgs), 0)
    t.assertEqual(len(items[1].reqArgs), 1)
    t.assertEqual(items[1].reqArgs[0], 2)
    cSeq = items[1].sequence.items
    t.assertIsNotNone(cSeq)
    t.assertEqual(len(cSeq), 3)
    t.assertIsInstance(cSeq[1], TokenWord)
    t.assertRegex(cSeq[1].token, "argument")

  def test_writeTeXtoFile(t) :
    text = """
    This is a \\testMacroOneReq
    argument
    This is a \\testMacro
    {This is a required argument}
    This is a \\testMacro
    [this is an optional argument]
    {this is another required argument}
    This is the last line
"""
    cStream = CharStream(text)
    cStream.scanTokens()
    tStream = cStream.tokens
    t.assertIsNotNone(tStream)
    tokens = tStream.items
    t.assertIsNotNone(tokens)
    #print(yaml.dump(tokens))
    anAST = buildAST(tokens)
    print(yaml.dump(anAST))
    aStrIO = io.StringIO()
    anAST.writeTeXto(aStrIO)
    texText = aStrIO.getvalue()
    print(texText)
    t.assertEqual(text, texText)
