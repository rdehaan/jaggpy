#####################################################################
## The ASP solver that uses the given rule to give back the 
## outcome of the judgement aggregation. We use clingo to find the 
## correct answer sets.
#####################################################################

import clingo
from .classes import Solver
from clingo import String

class ASPSolver(Solver):
	def solve(self, scenario, rule):
		"""Given a scenario object and the name of a rule 
		this function will yield the outcomes
		of the judgement aggregation. Each outcome is yielded seperately.
		The rule should be given as a string and can be one of the 
		following lowercase commands:
			- 
			"""
		# Add the scenario to asp_program using the scenario
		# argument.
		asp_program = """
		x1 :- not x2.
		x2 :- not x1.
		"""

		# Add the consistency check for the given scenario
		asp_program += """
		"""

		# Add the rule depending on what rule we need to use
		if rule == "kemeny":
			asp_program += """
			"""
		elif rule == "maxhamming":
			asp_program += """
			"""
		elif rule == "slater":
			asp_program += """
			"""
		else:
			raise Exception (f"{rule} is not a recognized aggregation rule.")

		# Ground and solve the program
		control = clingo.Control()
		control.add("base", [], asp_program)
		control.ground([("base", [])])
		control.configuration.solve.models = 0

		# Yield the results of the program
		with control.solve(yield_=True) as handle:
			for model in handle:
				outcome = dict()
				for formula in scenario.agenda.values():
					for atom in model.symbols(shown=True):
						if formula == str(atom):
							outcome[formula] = True
						else:
							outcome[formula] = False
				yield (outcome)