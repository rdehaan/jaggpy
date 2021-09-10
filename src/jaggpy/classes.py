#####################################################################
## Useful python classes for the scenarios and the 
## possible solvers. 
#####################################################################

# A scenario class that will be read from a .jagg file. A scenario
# has an agenda, input constraints, output constraints and a profile.

from abc import ABC, abstractmethod

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
		self.profile = dict()

	def addToAgenda(self, formula):
		"""The addToAgenda function takes a formula as its only argument.
		A formula should be build by lowercase atoms and the following operators:
			- not
			- and 
			- or
		The outermost parentheses can be omitted, but internal parentheses must
		be explicit. For example, "(not x1 or not x2) or not x3" is the correct
		format, while "not x1 or not x2 or not x3 will" not work. """
		newLabel = len(self.agenda)+1
		self.agenda[newLabel] = formula
		self.checkConsistency()

	def addToInputConstraints(self, constraint):
		"""The addToInputConstraints function takes a formula as its only argument.
		A formula should be build by lowercase atoms and the following operators:
			- not
			- and 
			- or
		The outermost parentheses can be omitted, but internal parentheses must
		be explicit. For example, "(not x1 or not x2) or not x3" is the correct
		format, while "not x1 or not x2 or not x3 will" not work. """
		self.inputConstraints.append(constraint)
		self.checkConsistency()

	def addToOutputConstraints(self, constraint):
		"""The addToOutputConstraints function takes a formula as its only argument.
		A formula should be build by lowercase atoms and the following operators:
			- not
			- and 
			- or
		The outermost parentheses can be omitted, but internal parentheses must
		be explicit. For example, "(not x1 or not x2) or not x3" is the correct
		format, while "not x1 or not x2 or not x3 will" not work. """
		self.outputConstraints.append(constraint)
		self.checkConsistency()

	def addToProfile(self, judgementSet):
		"""The addToProfile function takes a judgement set as its only argument.
		A judgement set should be a list of the labels of the formula that are
		accepted. The rest is rejected. The formulas should be given by their 
		label and seperated by a semicolon. For example, "4, 2;4;5" """
		newLabel = len(self.profile)+1
		formulaLabels = list(map(int, judgementSet.split(";")))
		acceptedFormulas = []
		for formulaLabel in formulaLabels:
			acceptedFormulas.append(self.agenda[formulaLabel])
		self.profile[newLabel] = acceptedFormulas
		self.checkConsistency()

	def loadFromFile(self, path):
		"""Load the scenario from a .jagg file given its path.
		The path should be a raw string, i.e. of the form r"path/to/file". 
		The file should have the following format, with each element being on 
		a new line:
			- Number of Formulas: The number of formulas in the pre-agenda
			- X, Formula: The formula labeled by the number X  
			- In, Formula: The input constraint labeled by the text "In"
			- Out, Formula: The output constraint labeled by the text "Out"
			- Number of Judgement Sets: The total number of judgement sets
			- J, phi_1;...;phi_n: A list of the formulas phi_1 to phi_n 
				that are accepted labelled by the number J. The rest is rejected.
				The formulas should be given by their label and seperated 
				by a semicolon. For example, "4, 2;4;5"
		A formula should be build by lowercase atoms and the following operators:
			- not
			- and 
			- or
		The outermost parentheses can be omitted, internal parentheses must
		be explicit. For example, "(not x1 or not x2) or not x3" is the correct
		format, while "not x1 or not x2 or not x3 will" not work.
			"""
		conn = open(path)
		text = conn.read()
		lines = text.splitlines()
		conn.close()

		# Add the formulas to the agenda dictionary using the given label
		numberOfFormulas = int(lines[0])
		for i in range(1, numberOfFormulas+1):
			currentLine = lines[i].split(", ")
			label = int(currentLine[0])
			formula = currentLine[1]
			self.agenda[label] = formula

		# Add the input constraints to the list of constraints
		lineNumber = numberOfFormulas+1
		while lines[lineNumber].split(", ")[0] == "In":
			formula = lines[lineNumber].split(", ")[1]
			self.inputConstraints.append(formula)	
			lineNumber += 1
		
		# Add the output constraints to the list of constraints
		while lines[lineNumber].split(", ")[0] == "Out":
			formula = lines[lineNumber].split(", ")[1]
			self.outputConstraints.append(formula)	
			lineNumber += 1
			
		# Add the list of accepted formulas to the profile dictionary
		# for each of the judgement sets.
		numberOfJS = int(lines[lineNumber])
		for i in range(lineNumber+1, lineNumber+numberOfJS+1):
			currentLine = lines[i].split(", ")
			label = int(currentLine[0])
			formulaLabels = list(map(int, currentLine[1].split(";")))
			acceptedFormulas = []
			for formulaLabel in formulaLabels:
				acceptedFormulas.append(self.agenda[formulaLabel])
			self.profile[label] = acceptedFormulas

		self.checkConsistency()

	def checkConsistency(self):
		print("Checking consistency...")

	def prettyPrint(self):
		"""Prints the Scenario object in a readable way"""
		print("Sub-agenda (label, formula):")
		for key in self.agenda:
			print(key, self.agenda[key])
		print("\nInput constraint:")
		for constraint in self.inputConstraints:
			print(constraint)
		print("\nOutput constraint:")
		for constraint in self.outputConstraints:
			print(constraint)
		print("\nProfile (label, accepted formulas):")
		for js in self.profile:
			accepted = "("
			for variable in self.profile[js]:
				if accepted == "(":
					accepted += variable
				else:
					accepted += ", " + variable
			accepted += ")"
			print(js,  accepted)

# A solver class with an enumerate_outcomes function that enumerates
# all the outcomes given a scenario and an aggregation rule.
class Solver(ABC):
	@abstractmethod
	def solve(self, scenario, rule):
		pass
	
	def enumerate_outcomes(self, scenario, rule):
		for outcome in self.solve(scenario, rule):
			print(outcome)