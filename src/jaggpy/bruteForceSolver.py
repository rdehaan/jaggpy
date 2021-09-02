#####################################################################
## The simplest solver that uses the given rule to give back the 
## outcome of the judgement aggregation.
#####################################################################

import jaggpy.classes

def solve(scenario, rule):
	"""Given a scenario and a rule we give back the outcome of the
	judgement aggregation in the simplest possible way."""

bruteForce = jaggpy.classes.Solver("Brute Force Solver", solve)
