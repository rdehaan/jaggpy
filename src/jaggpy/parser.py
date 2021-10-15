#####################################################################
## Parser for sentences
## The function parseSentence is heavily inspired by
## https://github.com/pyparsing/pyparsing/blob/master/examples/simpleBool.py#L16
## It has been altered for this application.
#####################################################################
from typing import Callable, Iterable
from pyparsing import infixNotation, opAssoc, Keyword, Word, alphas, alphanums, ParserElement
from nnf import *

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
				result = []
				for argument in self.args:
					result.append(argument.as_list())
					result. append("&")
				result = result[:-1]
				return result
				# return [self.args[0].as_list(), "&", self.args[1].as_list()]

		class BoolOr(BoolBinOp):
			repr_symbol = "|"
			def as_list(self):
				result = []
				num = len(self.args)
				for argument in self.args:
					result.append(argument.as_list())
					result.append("|")
				result = result[:-1]
				return result
				# return [self.args[0].as_list(), "|", self.args[1].as_list()]

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
			(OR, 2, opAssoc.LEFT, BoolOr),
			(AND, 2, opAssoc.LEFT, BoolAnd),
			(IMPLIES, 2, opAssoc.LEFT, BoolImplies)
		],
		)

		parsedSentence = boolExpr.parseString(prepSentence)[0]

		return parsedSentence.as_list()

	def toNNF(self, sentence):
		# Parse the sentence and then convert it to NNF
		parsed = self.parseSentence(sentence)
		nnf = self.toNNFParsed(parsed)

		return nnf

	# Recursively convert the sentence to NNF
	def toNNFParsed(self, sentence):
		# If the sentence is just a string, leave it be
		if type(sentence) == str:
			return sentence 
		# If it is negated, push the negation through
		elif sentence[0] == '~':
			if type(sentence[1]) == str:
				return "".join(sentence)
			elif sentence[1][1] == '&':
				return self.negAnd(sentence[1])
			elif sentence[1][1] == '|':
				return self.negOr(sentence[1])
			elif sentence[1][1] == '->':
				return self.negImplies(sentence[1])
			# Remove double negations
			elif sentence[1][0] == '~':
				return self.toNNFParsed(sentence[1][1])
			else:
				raise Exception("There seems to be something wrong..")
		else:
			# If it is not negated, rewrite implication and
			# search for more negations
			operator = sentence[1]
			if operator == '->':
				left = self.toNNFParsed(['~', sentence[0]])
				right = self.toNNFParsed(sentence[2])
				return " ".join(['(', left, '|', right, ')'])
			else:
				result = ['(']
				for i in range(len(sentence)):
					if i % 2 == 0:
						element = self.toNNFParsed(sentence[i])
						result.append(element)
						result.append(operator)
				result = result[:-1]
				result.append(')')
				return " ".join(result)

	def negAnd(self, sentence):
		result = ['(']
		for i in range(len(sentence)):
			if i % 2 == 0:
				element = self.toNNFParsed(['~', sentence[i]])
				result.append(element)
				result.append('|')
		result = result[:-1]
		result.append(')')
		return " ".join(result)

	def negOr(self, sentence):
		result = ['(']
		for i in range(len(sentence)):
			if i % 2 == 0:
				element = self.toNNFParsed(['~', sentence[i]])
				result.append(element)
				result.append('&')
		result = result[:-1]
		result.append(')')
		return " ".join(result)

	def negImplies(self, sentence):
		# Negate the antecedent
		antecedent = self.toNNFParsed(['~', sentence[0]])
		consequent = self.toNNFParsed(sentence[2])

		# Return the negated implication as a conjunction
		return " ".join(['(', antecedent, '|', consequent, ')'])

	def toCNF(self, sentence, variables):
		"""
		Translate a sentence from NNF (as produced by the toNNF function), to CNF.
		"""
		my_string = sentence
		allVariables = set()

		# Use a prefix to prevent variable name collisions
		# Add this prefix to all variables in the string
		var_prefix = "my_var_"
		my_string_preprocessed = my_string
		for var in variables:
			my_string_preprocessed = my_string_preprocessed.replace(var, var_prefix + var)

		# Declare variables (with prefix) and parse the formula with the
		# variable prefixes added
		for var in variables:
			exec(f"{var_prefix}{var} = Var('{var}')")
			allVariables.add(var)
		formula = eval(my_string_preprocessed)

		# Change nothing if formula already in CNF, else convert to CNF using to_CNF method from nnf package.
		if formula.is_CNF():
			print("Formula is already in CNF.")
			return sentence
		else:

			formula = formula.to_CNF()
			for var in formula.vars():
				if type(var) != str:
					allVariables.add('a' + str(var)[:4])
				else:
					allVariables.add(var)
			# Translate formula to string.
			list_of_conjuncts = []
			for conjunct in formula:
				conj = "( "
				disjunct_counter = 0
				for disjunct in conjunct:
					if str(disjunct)[-1] == '>':
						disjunct = "a".join(str(disjunct)[:-1].split('<'))
					if disjunct_counter < len(conjunct) - 1:
						conj = conj + str(disjunct) + " | "
					else:
						conj = conj + str(disjunct) + " )"
					disjunct_counter += 1
				list_of_conjuncts.append(conj)
			
			if len(formula) == 1:
				return [list_of_conjuncts[0], allVariables]
			else:
				formula_str = "( "
				for i in range(len(list_of_conjuncts)):
					if i < len(list_of_conjuncts) - 1:
						formula_str = formula_str + list_of_conjuncts[i] + " & "
					else:
						formula_str = formula_str + list_of_conjuncts[i] + " )"
				return [formula_str, allVariables]

	def translateAgenda(self, agenda):
		newConstraints = []
		for label in agenda.keys():
			labelVar = f'l{label}'
			formula = agenda[label]

			# Add label -> formula
			newConstraints.append(f'~{labelVar} | {formula}')

			# Add formula -> label
			negFormula = self.toNNF(f'~ ({formula})')
			newConstraints.append(f'{negFormula} | {labelVar}')

		return newConstraints