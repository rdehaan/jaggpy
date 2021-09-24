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
		asp_program = ""

		# Voters
		asp_program = textwrap.dedent("""
			""")

		# Issues
		asp_program = textwrap.dedent("""
			""")

		# Judgement sets
		asp_program = textwrap.dedent("""
			""")

		# Input constraints
		asp_program += textwrap.dedent("""
		""")

		# Output constraints
		asp_program += textwrap.dedent("""
		""")

		# asp_program = textwrap.dedent("""
		# % Declare voters and issues (now only literals)
		# voter(1..11).
		# issue(x1;x2;x3;x4).

		# % Declare input constraints (in CNF)
		# inputClause(1,(-x1;-x2;-x3)). 
		# inputClause(2, (-x1;-x3;-x4)).

		# % Declare ouptut constraints (in CNF)
		# outputClause(1, (-x1;-x2;-x3)). 
		# outputClause(2, (-x1;-x3;-x4)).

		# % Encode the profile, this also needs to include the negation
		# % of the formulas that are not accepted. 
		# js(1..4, (x1;-x2;x3;-x4)).
		# js(5..7, (-x1;x2;x3;x4)).
		# js(8..10, (x1;x2;-x3;x4)).
		# js(11, (x1;x2;-x3;-x4)).
		# """)

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

		print(asp_program)

		# # Ground and solve the program
		# control = clingo.Control()
		# control.add("base", [], asp_program)
		# control.ground([("base", [])])
		# control.configuration.solve.models = 0
		# control.configuration.solve.opt_mode = "optN"

		# # Yield the results of the program
		# with control.solve(yield_=True) as handle:
		# 	for model in handle:
		# 		if model.optimality_proven:
		# 			outcome = dict()
		# 			for formula in scenario.agenda.values():
		# 				for atom in model.symbols(shown=True):
		# 					if f'outcome({formula})' == str(atom):
		# 						outcome[formula] = True
		# 						break
		# 					else:
		# 						outcome[formula] = False
		# 			yield (outcome)
