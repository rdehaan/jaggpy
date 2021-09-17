#####################################################################
## The simplest solver that uses the given rule to give back the 
## outcome of the judgement aggregation.
#####################################################################

from .classes import Solver
from nnf import *

class BruteForce(Solver):
	def solve(self, scenario, rule):
		"""Given a scenario object and the name of a rule 
		this function will create a list of all the outcomes
		of the judgement aggregation. The rule should be given 
		as a string and can be one of the following lowercase commands:

			- kemeny
			- slater 
			"""
		# First we make a list of all the judgement sets that are consistent
		# with the output constraints.
		my_string = ""
		for conjunct in scenario.outputConstraints:
			my_string += f"({conjunct}) & "
		my_string = my_string[:-3]
		var_prefix = "my_var_"
		my_string_preprocessed = my_string
		for var in scenario.variables:
			my_string_preprocessed = my_string_preprocessed.replace(var, var_prefix + var)
		for var in scenario.variables:
			exec(f"{var_prefix}{var} = Var('{var}')")
		outputConstraint = eval(my_string_preprocessed)
		consistentOutcomes =  list(outputConstraint.models())

		# We can see if the formula labeled by X is true in model N by using
		# print(consistentOutcomes[N][scenario.agenda[X]])

		# Kemeny rule
		if rule == "kemeny":
			print("Solving the Kemeny rule")

		# Other rules.
		elif rule == "slater":
			print("Solving slater rule")

		else:
			raise Exception ("This is not a rule that has been implemented.")

