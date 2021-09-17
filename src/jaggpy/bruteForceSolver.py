#####################################################################
## The simplest solver that uses the given rule to give back the 
## outcome of the judgement aggregation.
#####################################################################

from .classes import Solver

class BruteForce(Solver):
	def solve(self, scenario, rule):
		"""Given a scenario object and the name of a rule 
		this function will create a list of all the outcomes
		of the judgement aggregation. """
		print(["Outcome 1", "Outcome 2", "Outcome 3"])

		# Kemeny rule
		if rule == "kemeny":
	
		# Other rules.
		# elif rule == :

		else:
			raise Exception

