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
			- kemeny
			- leximax
			- young
			- reversal
			- slater
			- majority
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

		# Variables
		asp_program+= "\n% Declare variables\n"
		for variable in scenario.variables:
			asp_program += f"variable({variable}).\n"
		asp_program += textwrap.dedent("""
		% Check consistency for the variables, extra variables included
		1 {js(cons, X); js(cons, -X)} 1 :- variable(X).
		:- inputClause(C,_), js(cons,-L) : inputClause(C,L).
		:- outputClause(C,_), js(cons,-L) : outputClause(C,L).\n""")

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
			print("Computing outcome with ASP and the Kemeny rule...")
			asp_program += textwrap.dedent("""
			% Kemeny rule 
			wgt(X,N) :- lit(X), N = #count { A : voter(A), js(A,X) }.
			#maximize { N@1,wgt(X,N) : wgt(X,N), js(col,X) }.
			""")
		elif rule == "leximax":
			print("Computing outcome with ASP and the leximax rule...")
			asp_program += textwrap.dedent("""
			% Leximax rule
			wgt(X,N) :- lit(X), N = #count { A : voter(A), js(A,X) }.
			#maximize { 1@N,wgt(X,N) : wgt(X,N), js(col,X) }.
			""")
		elif rule == "young":
			print("Computing outcome with ASP and the young rule...")
			asp_program += textwrap.dedent("""
			% Young rule
			in(A) ; out(A) :- voter(A).
			inwgt(X,N) :- lit(X), N = #count{ A : voter(A), in(A), js(A,X) }.
			inmaj(X) :- lit(X), inwgt(X,N), inwgt(-X,M), N > M.
			js(col,X) :- inmaj(X).
			#minimize { 1@1,out(A) : out(A) }.
			""")
		elif rule == "reversal":
			print("Computing outcome with ASP and the reversal rule...")
			asp_program+= textwrap.dedent("""
			% Reversal scoring
			agent(vrt(A,X)) :- voter(A), lit(X). 
			js(vrt(A,X),-X) :- voter(A), lit(X), js(A,X).

			disagree(A,X,Y) :- voter(A), lit(X), lit(Y), js(A,Y), js(vrt(A,X),-Y).
			disagreement(A,X,D) :- voter(A), lit(X), D = #count { Y : disagree(A,X,Y) }.
			#minimize { D@2,disagreemt(A,X,D) : disagreement(A,X,D) }.

			score(A,X,D) :- js(col,X), disagreement(A,X,D).
			score(E) :- E = #sum { D,score(A,X,D) : score(A,X,D) }.
			#maximize { E@1,score(E) : score(E) }.""")
		elif rule == "slater":
			print("Computing outcome with ASP and the slater rule...")
			asp_program += textwrap.dedent("""
			% Slater rule
			% determine the majority outcome
			pc(X,N) :- lit(X), N = #count { A : voter(A), js(A,X) }.
			maj(X) :- lit(X), pc(X,N), pc(-X,M), N > M.
			% maximize agreement with the majority outcome
			#minimize { 1@10,maj(X) : maj(X), js(col,-X) }.
			""")
		elif rule == "majority":
			print("Computing outcome with ASP and the majority rule...")
			asp_program += textwrap.dedent("""
			% Majority rule
			% require that the collective outcome agrees with all issues
			% that have strictly more support than their negation
			pc(X,N) :- lit(X), N = #count { A : voter(A), js(A,X) }.
			maj(X) :- lit(X), pc(X,N), pc(-X,M), N > M.
			js(col,X) :- maj(X).
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
