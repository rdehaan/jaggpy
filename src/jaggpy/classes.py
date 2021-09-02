# We set up useful python classes for the scenarios and the 
# possible solvers. 

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
