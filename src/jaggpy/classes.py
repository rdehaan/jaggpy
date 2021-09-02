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
		"""Load the scenario from a .jagg file """
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