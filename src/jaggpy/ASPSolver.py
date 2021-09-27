#####################################################################
## The ASP solver that uses the given rule to give back the 
## outcome of the judgement aggregation. We use clingo to find the 
## correct answer sets.
#####################################################################

import clingo
from .classes import Solver
from clingo import String
import textwrap

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
		asp_program = textwrap.dedent("""% We first add the scenario to our ASP program.
		""")

		# Issues
		asp_program += textwrap.dedent("""
		% Adding the issues.
		""")
		for key in scenario.agenda:
			asp_program += f"issue({scenario.agenda[key]}).\n"

		# Voters and judgement sets.
		asp_program += textwrap.dedent("""
		% Adding voters and specifying what they voted for sets.
		""")
		voter_count = 0
		for coalition in scenario.profile:
			for voter_index in range(1,coalition[0]+1):
				# Register new voter.
				voter = str(voter_count + voter_index)
				asp_program += f"voter({voter}).\n"
				# Register what they voted for.
				for formula in scenario.agenda.values():
					if formula in coalition[1]:
						asp_program += f"js({voter},{formula}).\n"
					else:
						asp_program += f"js({voter},-{formula}).\n"
			voter_count += coalition[0]

		# Input constraints
		asp_program += "\n% Declare input constraints (in CNF)\n"
		totalInputConstraints = ""
		for conjunct in scenario.inputConstraints:
			totalInputConstraints += f"{conjunct} & "
		totalIC = totalInputConstraints[:-3]
		conjuncts = ("".join(totalIC.split())).split("&")
		clauseNumber = 1
		for clause in conjuncts:
			conjunct = clause.split("|")
			for string in conjunct:
				if string[0] == "(":
					formula = string[1:]
				elif string[-1] == ")":
					formula = string[:-1]
				else:
					formula = string
				if formula[0] == "~":
					asp_program += f'inputClause({clauseNumber}, -{formula[1:]}).\n'
				else:
					asp_program += f'inputClause({clauseNumber}, {formula}).\n'
			clauseNumber += 1

		# Output constraints
		asp_program += "\n% Declare output constraints (in CNF)\n"
		totalOutputConstraints = ""
		for conjunct in scenario.outputConstraints:
			totalOutputConstraints += f"{conjunct} & "
		totalOC = totalOutputConstraints[:-3]
		conjuncts = ("".join(totalOC.split())).split("&")
		clauseNumber = 1
		for clause in conjuncts:
			conjunct = clause.split("|")
			for string in conjunct:
				if string[0] == "(":
					formula = string[1:]
				elif string[-1] == ")":
					formula = string[:-1]
				else:
					formula = string
				if formula[0] == "~":
					asp_program += f'outputClause({clauseNumber}, -{formula[1:]}).\n'
				else:
					asp_program += f'outputClause({clauseNumber}, {formula}).\n'
			clauseNumber += 1

		# Add the consistency check for the given scenario
		asp_program += textwrap.dedent("""
		% Consistency check with respect to the input constraint
		agent(A) :- voter(A).
		lit(X;-X) :- issue(X).
		1 { js(A,X) ; js(A,-X) } 1 :- agent(A), issue(X).
		:- voter(A), inputClause(C,_), js(A,-L) : inputClause(C,L).

		% Consistency check of the collective outcome with respect 
		% to the output constraint
		agent(col).
		:- agent(col), outputClause(C,_), js(col,-L) : outputClause(C,L).
		""")

		# Add the rule depending on what rule we need to use
		if rule == "kemeny":
			asp_program += textwrap.dedent("""
			% Kemeny rule 
			wgt(X,N) :- lit(X), N = #count { A : voter(A), js(A,X) }.
			#maximize { N@1,wgt(X,N) : wgt(X,N), js(col,X) }.
			""")
		elif rule == "leximax":
			asp_program += textwrap.dedent("""
			% Leximax rule
			wgt(X,N) :- lit(X), N = #count { A : voter(A), js(A,X) }.
			#maximize { 1@N,wgt(X,N) : wgt(X,N), js(col,X) }.
			""")
		elif rule == "young":
			asp_program += textwrap.dedent("""
			% Young rule
			in(A) ; out(A) :- voter(A).
			inwgt(X,N) :- lit(X), N = #count{ A : voter(A), in(A), js(A,X) }.
			inmaj(X) :- lit(X), inwgt(X,N), inwgt(-X,M), N > M.
			js(col,X) :- inmaj(X).
			#minimize { 1@1,out(A) : out(A) }.
			""")
		else:
			raise Exception (f"{rule} is not a recognized aggregation rule.")

		# Add the outcome predicate
		asp_program += textwrap.dedent("""
			outcome(X) :- agent(col), js(col, X).
			#show outcome/1.
				""")

		# Ground and solve the program
		control = clingo.Control(arguments=["--project"])
		control.add("base", [], asp_program)
		control.ground([("base", [])])
		control.configuration.solve.models = 0
		control.configuration.solve.opt_mode = "optN"

		# Yield the results of the program
		with control.solve(yield_=True) as handle:
			for model in handle:
				if model.optimality_proven:
					outcome = dict()
					for formula in scenario.agenda.values():
						for atom in model.symbols(shown=True):
							if f'outcome({formula})' == str(atom):
								outcome[formula] = True
								break
							else:
								outcome[formula] = False
					yield (outcome)
