#####################################################################
## Useful python classes for the scenarios and the 
## possible solvers. 
#####################################################################

# A scenario class that will be read from a .jagg file. A scenario
# has an agenda, input constraints, output constraints and a profile.
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

# A solver class with an enumerate_outcomes function that enumerates
# all the outcomes given a scenario and an aggregation rule.
class Solver:
	def __init__(self, name, solve):
		self.name = name
		self.solve = solve
	
	def enumerate_outcomes(self, scenario, rule):
		for outcome in self.solve(scenario, rule):
			print(outcome)