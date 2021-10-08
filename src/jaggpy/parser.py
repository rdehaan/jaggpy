#####################################################################
## Parser for sentences
## Taken from https://github.com/pyparsing/pyparsing/blob/master/examples/simpleBool.py#L16
## Altered for own use by returning a parsed list
#####################################################################
from typing import Callable, Iterable
from pyparsing import infixNotation, opAssoc, Keyword, Word, alphas, alphanums, ParserElement

class Parser:
	def parseSentence(self, sentence):
		prepSentence = sentence.split("~")
		prepSentence = "~ ".join(prepSentence)

		ParserElement.enablePackrat()

		# define classes to be built at parse time, as each matching
		# expression type is parsed
		class BoolOperand:
			def __init__(self, t):
				self.label = t[0]

			def __str__(self) -> str:
				return self.label

			__repr__ = __str__

			def as_list(self):
				return self.label

		class BoolNot:
			def __init__(self, t):
				self.arg = t[0][1]

			def __str__(self) -> str:
				return "~" + str(self.arg)

			__repr__ = __str__

			def as_list(self):
				return ["~", self.arg.as_list()]

		class BoolBinOp:
			repr_symbol: str = ""

			def __init__(self, t):
				self.args = t[0][0::2]

			def __str__(self) -> str:
				sep = " %s " % self.repr_symbol
				return "(" + sep.join(map(str, self.args)) + ")"


		class BoolAnd(BoolBinOp):
			repr_symbol = "&"
			def as_list(self):
				return [self.args[0].as_list(), "&", self.args[1].as_list()]

		class BoolOr(BoolBinOp):
			repr_symbol = "|"
			def as_list(self):
				return [self.args[0].as_list(), "|", self.args[1].as_list()]

		class BoolImplies(BoolBinOp):
			repr_symbol = "->"
			def as_list(self):
				return [self.args[0].as_list(), "->", self.args[1].as_list()]

		NOT = Keyword("~")
		AND = Keyword("&")
		OR = Keyword("|")
		IMPLIES = Keyword("->")

		boolOperand = Word(alphanums)
		boolOperand.setParseAction(BoolOperand).setName("bool_operand")

		# define expression, based on expression operand and
		# list of operations in precedence order
		boolExpr = infixNotation(
		boolOperand,
		[
			(NOT, 1, opAssoc.RIGHT, BoolNot),
			(AND, 2, opAssoc.LEFT, BoolAnd),
			(OR, 2, opAssoc.LEFT, BoolOr),
			(IMPLIES, 2, opAssoc.LEFT, BoolImplies)
		],
		)

		parsedSentence = boolExpr.parseString(prepSentence)[0]

		return parsedSentence.as_list()

	def toNNF(self, sentence):
		listSentence = self.toNNFList(sentence)
		return listSentence

	def toNNFList(self, sentence):
		if type(sentence) == str:
			return sentence 
		elif sentence[0] == '~':
			if type(sentence[1]) == str:
				return sentence
			elif sentence[1][1] == '&':
				return self.negAnd(sentence[1])
			elif sentence[1][1] == '|':
				return self.negOr(sentence[1])
			elif sentence[1][1] == '->':
				return self.negImplies(sentence[1])
			elif sentence[1][0] == '~':
				return self.toNNFList(sentence[1][1])
			else:
				raise Exception("There seems to be something wrong..")
		else:
			operator = sentence[1]
			if operator == '->':
				left = self.toNNFList(['~', sentence[0]])
			else:
				left = self.toNNFList(sentence[0])
			right = self.toNNFList(sentence[2])
			return [left, '|', right]

	def negAnd(self, sentence):
		# Negate the first and second conjunct
		firstConjunct = self.toNNFList(['~', sentence[0]])
		secondConjunct = self.toNNFList(['~', sentence[2]])

		# Return the negated conjunction
		return [firstConjunct, '|', secondConjunct]

	def negOr(self, sentence):
		# Negate the first and second disjunct
		firstDisjunct = self.toNNFList(['~', sentence[0]])
		secondDisjunct = self.toNNFList(['~', sentence[2]])

		# Return the negated disjunction
		return [firstDisjunct, '&', secondDisjunct]
		return sentence

	def negImplies(self, sentence):
		# Negate the first
		antecedent = self.toNNFList(['~', sentence[0]])
		consequent = self.toNNFList(sentence[2])

		# Return the negated implication as a conjunction
		return [antecedent, '|', consequent]
		return sentence

