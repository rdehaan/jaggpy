#####################################################################
## Useful python classes for the scenarios and the 
## possible solvers. 
#####################################################################

# A scenario class that will be read from a .jagg file. A scenario
# has an agenda, input constraints, output constraints and a profile.

from abc import ABC, abstractmethod

class Scenario:
	def __init__(self):
		self.agenda = []
		self.inputConstraints = []
		self.outputConstraints = []
		self.profile = []

	def addToAgenda(self, formula):
		self.agenda.append(formula)

	def addToInputConstraints(self, constraint):
		self.inputConstraints.append(constraint)

	def addToOutputConstraints(self, constraint):
		self.outputConstraints.append(constraint)

	def addToProfile(self, judgementSet):
		self.profile.append(judgementSet)

	def loadFromFile(self, file):
		"""Load the scenario from a .jagg file. The file should
		have the following format, with each element being on 
		a new line:
			- Number of Formulas: The number of formulas in the pre-agenda
			- X, Formula: The formula labeled by the number X  
			- In, Formula: The input constraint labeled by the text "In"
			- Out, Formula: The output constraint labeled by the text "Out"
			- Number of Judgement Sets: The total number of judgement sets
			- J, [Phi_1,...,Phi_n]: A list of the formulas phi_1 to phi_n 
				that are accepted labelled by the number J. The formulas 
				should be given by their label. The rest is rejected.
		A formula should be build by lowercase atoms and the following operators:
			- not
			- and 
			- or
		The outermost parentheses can be omitted, but internal parentheses must
		be explicit. For example, "(not x1 or not x2) or not x3" is the correct
		format, while "not x1 or not x2 or not x3 will" not work.
			"""
		raise NotImplementedError

# A solver class with an enumerate_outcomes function that enumerates
# all the outcomes given a scenario and an aggregation rule.
class Solver(ABC):
	@abstractmethod
	def solve(self, scenario, rule):
		pass
	
	def enumerate_outcomes(self, scenario, rule):
		for outcome in self.solve(scenario, rule):
			print(outcome)