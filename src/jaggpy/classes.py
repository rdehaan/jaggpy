#####################################################################
## Useful python classes for the scenarios and the 
## possible solvers. 
#####################################################################

# A scenario class that will be read from a .jagg file. A scenario
# has an agenda, input constraints, output constraints and a profile.

from abc import ABC, abstractmethod
from nnf import *
from jaggpy.parser import Parser
from itertools import islice

class Scenario:
	def __init__(self):
		"""A Scenario object has the following properties:
			- variables: a list of occurring variables
			- agenda: a dictionary with numbers as keys and
				formulas as values
			- inputConstraints: a list of input constraints
			- outputConstraints: a list of output constraints
			- profile: a list of judgment sets
			- numberVoters: an integer specifying the number of voters
			"""
		self.agenda = dict()
		self.inputConstraints = []
		self.outputConstraints = []
		self.profile = []
		self.variables = []
		self.numberVoters = 0

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
			- Number of voters, Number of distinct judgment sets
			- J, l1;...;ln: A list of the labels of the formulas
				that are accepted. The rest is rejected. 
				This profile occurs J times. The formulas should be 
				given by the times they are selected and seperated 
				by a semicolon. For example, "4, 2;4;5".
		A formula can contain the following operators:
			- The OR operator |
			- The AND operator &
			- The NOT operator ~
			- The IMPLIES operator ->
		Parentheses can be omitted where clear from context. """
		# Read the file and split all lines
		conn = open(path)
		text = conn.read()
		lines = text.splitlines()
		conn.close()

		# Remove blank lines and comments from the lines
		lines = [line for line in lines if line != "" and line[0] != "#"]

		# Create a parser object for future use
		parser = Parser()

		# Add the variables to the scenario
		self.variables = lines[0].split(", ")

		# Add the formulas to the agenda dictionary using the given label
		numberOfFormulas = int(lines[1])
		for i in range(2, numberOfFormulas+2):
			currentLine = lines[i].split(", ")
			label = int(currentLine[0])
			formula = currentLine[1]
			self.agenda[label] = parser.toNNF(formula)

		# Add the input constraints to the list of constraints
		lineNumber = numberOfFormulas+2
		while lines[lineNumber].split(", ")[0] == "In":
			formula = lines[lineNumber].split(", ")[1]
			if formula == "":
				firstVar = self.variables[0]
				formula = f'({firstVar} | ~{firstVar})'
			self.inputConstraints.append(parser.toNNF(formula))	
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
			if formula == "":
				firstVar = self.variables[0]
				formula = f'({firstVar} | ~{firstVar})'
			self.outputConstraints.append(parser.toNNF(formula))	
			lineNumber += 1

		# Check consistency of the output constraints
		my_string = ""
		for conjunct in self.outputConstraints:
			my_string += f"({conjunct}) & "
		my_string = my_string[:-3]
		if not self.checkConsistency(my_string):
			raise Exception ("The output constraints are inconsistent")

		# Add the number of voters to the scenario
		self.numberVoters += int(lines[lineNumber].split(", ")[0])

		# Add the list of accepted formulas to the profile dictionary
		# for each of the judgment sets.
		numberOfJS = int(lines[lineNumber].split(", ")[1])
		for i in range(lineNumber+1, lineNumber+numberOfJS+1):
			currentLine = lines[i].split(", ")
			# If the list of accepted formulas is not empty continue
			if currentLine[1] != '':
				label = int(currentLine[0])
				formulaLabels = list(map(int, currentLine[1].split(";")))
				acceptedFormulas = []
				for formulaLabel in formulaLabels:
					acceptedFormulas.append(self.agenda[formulaLabel])

				# Check consistency of the judgment set with respect 
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
					raise Exception (f"The judgment set on line {i} is inconsistent"\
						" with the input constraints.")

				# Add the judgment set to the scenario
				self.profile.append([label, acceptedFormulas])
			else:
				# If the all issues are rejected, add the empty list
				self.profile.append([label, []])

	def checkConsistency(self, sentence):
		"""The function checkConsistency should receive an NNF-formula as a 
		string. It return a Boolean indicating whether the formula is consistent."""
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
		"""Returns string that represents the scenario object in a readable way"""
		scenario_string = "Variables:"
		for variable in self.variables:
			scenario_string += f"\n{variable}"
		scenario_string += "\n\nSub-agenda (label, formula):"
		for key in self.agenda:
			scenario_string += f"\n{key}, {self.agenda[key]}"
		scenario_string += "\n\nInput constraints:"
		for constraint in self.inputConstraints:
			scenario_string += f"\n{constraint}"
		scenario_string +=  "\n\nOutput constraints:"
		for constraint in self.outputConstraints:
			scenario_string += f"\n{constraint}"
		scenario_string += "\n\nProfile (times selected, accepted formulas):"
		for js in self.profile:
			accepted = "("
			for variable in js[1]:
				if accepted == "(":
					accepted += variable
				else:
					accepted += ", " + variable
			accepted += ")"
			scenario_string += (f"\n{js[0]}, " + accepted)
		return scenario_string

# A solver class with an enumerate_outcomes function that enumerates
# all the outcomes given a scenario and an aggregation rule.
class Solver(ABC):
	@abstractmethod
	def solve(self, scenario, rule):
		"""Given a scenario and an aggregation rule, yields a generator 
		with the corresponding outcomes.""" 
		pass
	
	def enumerateOutcomes(self, scenario, rule):
		"""Given a scenario and an aggregation rule, prints all
		corresponding outcomes."""
		for outcome in self.solve(scenario, rule):
			print(outcome)

	def enumerateFirstNOutcomes(self, scenario, rule, n):
		"""Given a scenario, an aggregation rule and an integer n,
		prints the first n corresponding outcomes."""
		nOutcomes = islice(self.solve(scenario, rule), n) 
		for outcome in nOutcomes:
			print(outcome)