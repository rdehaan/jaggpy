#####################################################################
## The simplest solver that uses the given rule to give back the 
## outcome of the judgement aggregation.
#####################################################################

from classes import Solver

class BruteForce(Solver):
	def solve(self, scenario, rule):
		"""Given a scenario object and the name of a rule 
		this function will create a list of all the outcomes
		of the judgement aggregation. """
		return ["Outcome 1", "Outcome 2", "Outcome 3"]
