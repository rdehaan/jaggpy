#####################################################################
## Useful python classes for the scenarios and the 
## possible solvers. 
#####################################################################

# A scenario class that will be read from a .jagg file. A scenario
# has an agenda, input constraints, output constraints and a profile.

from abc import ABC, abstractmethod
from nnf import *

class Scenario:
	def __init__(self):
		"""A Scenario object has the following properties:
			- agenda: a list of formulas
			- inputConstraints: a list of input constraints
			- outputConstraints: a list of output constraints
			- profile: a list of judgement sets """
		self.agenda = dict()
		self.inputConstraints = []
		self.outputConstraints = []
		self.profile = []
		self.variables = []
	
	def addToVariables(self, variable):
		"""The addToVariables takes a string denoting a new variable as its
		only argument. """
		self.variables.append(variable)

	def addToAgenda(self, formula):
		"""The addToAgenda function takes a formula as its only argument.
		If the formuls uses new variables, these should be added as well with
		the addToVariables(var) function.
		A formula should be in NNF and can contain the following operators:
			- The OR operator |
			- The AND operator &
			- The NOT operator ~
		The outermost parentheses can be omitted, internal parentheses must
		be explicit. For example, "((~x1 | ~x2) | ~x3) & ((~x1 | ~x3) | ~x4)" is the correct
		format, while "(~x1 | ~x2 | ~x3) & (~x1 | ~x3 | ~x4)" not work."""
		newLabel = len(self.agenda)+1
		self.agenda[newLabel] = formula

	def addToInputConstraints(self, constraint):
		"""The addToInputConstraints function takes a formula as its only argument.
		If the new constraint uses new variables, these should be added as well with
		the addToVariables(var) function.
		A formula should be in NNF and can contain the following operators:
			- The OR operator |
			- The AND operator &
			- The NOT operator ~
		The outermost parentheses can be omitted, internal parentheses must
		be explicit. For example, "((~x1 | ~x2) | ~x3) & ((~x1 | ~x3) | ~x4)" is the correct
		format, while "(~x1 | ~x2 | ~x3) & (~x1 | ~x3 | ~x4)" not work."""
		self.inputConstraints.append(constraint)
		my_string = ""
		for conjunct in self.inputConstraints:
			my_string += f"({conjunct}) & "
		my_string = my_string[:-3]
		if not self.checkConsistency(my_string):
			raise Exception ("The input constraints are inconsistent")

	def addToOutputConstraints(self, constraint):
		"""The addToOutputConstraints function takes a formula as its only argument.
		If the new constraint uses new variables, these should be added as well with
		the addToVariables(var) function.
		A formula should be in NNF and can contain the following operators:
			- The OR operator |
			- The AND operator &
			- The NOT operator ~
		The outermost parentheses can be omitted, internal parentheses must
		be explicit. For example, "((~x1 | ~x2) | ~x3) & ((~x1 | ~x3) | ~x4)" is the correct
		format, while "(~x1 | ~x2 | ~x3) & (~x1 | ~x3 | ~x4)" not work. """
		self.outputConstraints.append(constraint)
		my_string = ""
		for conjunct in self.outputConstraints:
			my_string += f"({conjunct}) & "
		my_string = my_string[:-3]
		if not self.checkConsistency(my_string):
			raise Exception ("The input constraints are inconsistent")

	def addToProfile(self, times, judgementSet):
		"""The addToProfile function takes a judgement set as its only argument.
		A judgement set should be a list of the labels of the formulas that are
		accepted. The rest is rejected. The formulas should be given by their 
		label and seperated by a semicolon. For example, "2;4;5" """
		formulaLabels = list(map(int, judgementSet.split(";")))
		acceptedFormulas = []
		for formulaLabel in formulaLabels:
			acceptedFormulas.append(self.agenda[formulaLabel])
		self.profile.append([times, acceptedFormulas])
		
		# Check consistency of the judgement set with respect # to the input constraint
		my_string = ""
		for conjunct in self.inputConstraints:
			my_string += f"({conjunct}) & "
		for formulaLabel in formulaLabels:
			my_string += f"({self.agenda[formulaLabel]}) & "
		for j in range(1, len(self.agenda)+1):
			if j not in formulaLabels:
				my_string += f"(~{self.agenda[j]}) & "
		my_string = my_string[:-3]
		self.checkConsistency(my_string)
		if not self.checkConsistency(my_string):
			raise Exception (f"The new judgement set is inconsistent"\
				"with the output constraints.")

	def loadFromFile(self, path):
		"""Load the scenario from a .jagg file given its path.
		The path should be a raw string, i.e. of the form r"path/to/file". 
		The file should have the following format, with each element being on 
		a new line:
			- var_1,..., var_n: list of all the variables
			- Number of Formulas: The number of formulas in the pre-agenda
			- X, Formula: The formula labeled by the number X  
			- In, Formula: The input constraint labeled by the text "In"
			- Out, Formula: The output constraint labeled by the text "Out"
			- Number of Judgement Sets: The total number of judgement sets
			- J, phi_1;...;phi_n: A list of the formulas phi_1 to phi_n 
				that are accepted. The rest is rejected. This profile occurs J times.
				The formulas should be given by the times they are selected 
				and seperated by a semicolon. For example, "4, 2;4;5".
		A formula should be in NNF and can contain the following operators:
			- The OR operator |
			- The AND operator &
			- The NOT operator ~
		The outermost parentheses can be omitted, internal parentheses must
		be explicit. For example, "((~x1 | ~x2) | ~x3) & ((~x1 | ~x3) | ~x4)" is the correct
		format, while "(~x1 | ~x2 | ~x3) & (~x1 | ~x3 | ~x4)" not work.
			"""
		conn = open(path)
		text = conn.read()
		lines = text.splitlines()
		conn.close()

		self.variables = lines[0].split(", ")

		# Add the formulas to the agenda dictionary using the given label
		numberOfFormulas = int(lines[1])
		for i in range(2, numberOfFormulas+2):
			currentLine = lines[i].split(", ")
			label = int(currentLine[0])
			formula = currentLine[1]
			self.agenda[label] = formula

		# Add the input constraints to the list of constraints
		lineNumber = numberOfFormulas+2
		while lines[lineNumber].split(", ")[0] == "In":
			formula = lines[lineNumber].split(", ")[1]
			self.inputConstraints.append(formula)	
			lineNumber += 1

		# Check consistency of the input constraints
		my_string = ""
		for conjunct in self.inputConstraints:
			my_string += f"({conjunct}) & "
		my_string = my_string[:-3]
		if not self.checkConsistency(my_string):
			raise Exception ("The input constraints are inconsistent")
		
		# Add the output constraints to the list of constraints
		while lines[lineNumber].split(", ")[0] == "Out":
			formula = lines[lineNumber].split(", ")[1]
			self.outputConstraints.append(formula)	
			lineNumber += 1

		# Check consistency of the output constraints
		my_string = ""
		for conjunct in self.outputConstraints:
			my_string += f"({conjunct}) & "
		my_string = my_string[:-3]
		if not self.checkConsistency(my_string):
			raise Exception ("The output constraints are inconsistent")

		# Add the list of accepted formulas to the profile dictionary
		# for each of the judgement sets.
		numberOfJS = int(lines[lineNumber].split(", ")[1])
		for i in range(lineNumber+1, lineNumber+numberOfJS+1):
			currentLine = lines[i].split(", ")
			if currentLine[1] == '':
				break
			label = int(currentLine[0])
			formulaLabels = list(map(int, currentLine[1].split(";")))
			acceptedFormulas = []
			for formulaLabel in formulaLabels:
				acceptedFormulas.append(self.agenda[formulaLabel])
			self.profile.append([label, acceptedFormulas])

			# Check consistency of the judgement set with respect 
			# to the input constraint
			my_string = ""
			for conjunct in self.inputConstraints:
				my_string += f"({conjunct}) & "
			for j in range(1, len(self.agenda)+1):
				if j not in formulaLabels:
					my_string += f"(~{self.agenda[j]}) & "
				else:
					my_string += f"({self.agenda[j]}) & "
			my_string = my_string[:-3]
			self.checkConsistency(my_string)
			if not self.checkConsistency(my_string):
				raise Exception (f"The judgement set on line {i} is inconsistent"\
					" with the input constraints.")

	def checkConsistency(self, sentence):
		my_string = sentence

		# Use a prefix to prevent variable name collisions
		# Add this prefix to all variables in the string
		var_prefix = "my_var_"
		my_string_preprocessed = my_string
		for var in self.variables:
			my_string_preprocessed = my_string_preprocessed.replace(var, var_prefix + var)

		# Declare variables (with prefix) and parse the formula with the
		# variable prefixes added
		for var in self.variables:
			exec(f"{var_prefix}{var} = Var('{var}')")
		formula = eval(my_string_preprocessed)

		# Return whether the formula is consistent
		return(formula.consistent())
		

	def prettyPrint(self):
		"""Prints the Scenario object in a readable way"""
		print("Variables: ")
		for variable in self.variables:
			print(variable)
		print("\nSub-agenda (label, formula):")
		for key in self.agenda:
			print(key, self.agenda[key])
		print("\nInput constraint:")
		for constraint in self.inputConstraints:
			print(constraint)
		print("\nOutput constraint:")
		for constraint in self.outputConstraints:
			print(constraint)
		print("\nProfile (times selected, accepted formulas):")
		for js in self.profile:
			accepted = "("
			for variable in js[1]:
				if accepted == "(":
					accepted += variable
				else:
					accepted += ", " + variable
			accepted += ")"
			print(js[0],  accepted)

# A solver class with an enumerate_outcomes function that enumerates
# all the outcomes given a scenario and an aggregation rule.
class Solver(ABC):
	@abstractmethod
	def solve(self, scenario, rule):
		pass
	
	def enumerate_outcomes(self, scenario, rule):
		for outcome in self.solve(scenario, rule):
			print(outcome)