#####################################################################
## The ASP solver that uses the given rule to give back the
## outcome of the judgment aggregation. We use clingo to find the
## correct answer sets.
#####################################################################

import textwrap
import clingo
from clingo import String  # pylint: disable=no-name-in-module
from .classes import Solver
from .parser import Parser

class ASPSolver(Solver):
    """An 'answer set programming' solver for Judgment Aggregation."""
    def solve(self, scenario, rule, verbose=False):
        """Given a scenario object and the name of a rule
        this function will yield the outcomes
        of the judgment aggregation. Each outcome is yielded seperately.
        The rule should be given as a string and can be one of the
        following lowercase commands:
            - kemeny
            - leximax
            - young
            - slater
            - majority
            """
        parser = Parser()

        # Create a list of all variables in the scenario
        all_variables = set()
        for var in scenario.variables:
            all_variables.add(var)

        # Add the scenario to asp_program using the scenario
        # argument.
        asp_program = textwrap.dedent("""% We first add the scenario to our ASP program.
        """)

        # Issues
        asp_program += textwrap.dedent("""
        % Adding the labels that represent the issues.
        """)
        for key in scenario.agenda:
            asp_program += f"issue(l{key}).\n"
            all_variables.add(f"l{key}")

        # Voters and judgment sets
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
                for label in scenario.agenda:
                    if scenario.agenda[label] in coalition[1]:
                        asp_program += f"js({voter},l{label}).\n"
                    else:
                        asp_program += f"js({voter},-l{label}).\n"
            voter_count += coalition[0]

        # Input constraints
        asp_program += "\n% Declare input constraints (in CNF)\n"
        total_input_constraints = ""

        # Add input constraints specified in the scenario.
        for conjunct in scenario.input_constraints:
            total_input_constraints += f"{conjunct} & "

        # Add auxiliary input constraints that guarantee that labels
        # corresponds to the right formulas.
        for constraint in parser.translateAgenda(scenario.agenda):
            total_input_constraints += f"({constraint}) & "
        total_ic = total_input_constraints[:-3]

        # Translate to cnf
        cnf_object = parser.toCNF(total_ic, all_variables)
        ic_cnf = cnf_object[0]
        all_variables = all_variables.union(cnf_object[1])

        # Add the constraint clauses to the program
        conjuncts = ("".join(ic_cnf.split())).split("&")
        clause_number = 1
        for clause in conjuncts:
            prep_clause = "".join(clause.split("("))
            prep_clause = "".join(prep_clause.split(")"))
            conjunct = prep_clause.split("|")
            for string in conjunct:
                if string[0] == "(":
                    formula = string[1:]
                elif string[-1] == ")":
                    formula = string[:-1]
                else:
                    formula = string
                if formula[0] == "~":
                    asp_program += f'inputClause({clause_number}, -{formula[1:]}).\n'
                else:
                    asp_program += f'inputClause({clause_number}, {formula}).\n'
            clause_number += 1

        # Output constraints
        asp_program += "\n% Declare output constraints (in CNF)\n"
        total_output_contstraints = ""
        for conjunct in scenario.output_constraints:
            total_output_contstraints += f"{conjunct} & "

        # Add auxiliary input constraints that guarantee
        # that labels corresponds to the right formulas.
        for constraint in parser.translateAgenda(scenario.agenda):
            total_output_contstraints += f"({constraint}) & "
        total_oc = total_output_contstraints[:-3]

        # Translate to cnf
        cnf_object = parser.toCNF(total_oc, all_variables)
        oc_cnf = cnf_object[0]
        all_variables = all_variables.union(cnf_object[1])

        # Add the constraint clauses to the program
        conjuncts = ("".join(oc_cnf.split())).split("&")
        clause_number = 1
        for clause in conjuncts:
            prep_clause = "".join(clause.split("("))
            prep_clause = "".join(prep_clause.split(")"))
            conjunct = prep_clause.split("|")
            for string in conjunct:
                if string[0] == "(":
                    formula = string[1:]
                elif string[-1] == ")":
                    formula = string[:-1]
                else:
                    formula = string
                if formula[0] == "~":
                    asp_program += f'outputClause({clause_number}, -{formula[1:]}).\n'
                else:
                    asp_program += f'outputClause({clause_number}, {formula}).\n'
            clause_number += 1

        # Add variables
        asp_program += '\n'
        for variable in all_variables:
            asp_program += f'variable({variable}).\n'

        # Add the consistency check for the given scenario
        asp_program += textwrap.dedent("""
        % Consistency check with respect to the input constraint
        agent(A) :- voter(A).
        lit(X;-X) :- issue(X).
        1 { js(A,X) ; js(A,-X) } 1 :- agent(A), variable(X).
        :- voter(A), inputClause(C,_), js(A,-L) : inputClause(C,L).

        % Consistency check of the collective outcome with respect
        % to the output constraint
        agent(col).
        :- agent(col), outputClause(C,_), js(col,-L) : outputClause(C,L).
        """)

        # Add the rule depending on what rule we need to use
        if rule == "kemeny":
            if verbose:
                print("Computing outcome with ASP and the Kemeny rule...")
            asp_program += textwrap.dedent("""
            % Kemeny rule
            wgt(X,N) :- lit(X), N = #count { A : voter(A), js(A,X) }.
            #maximize { N@1,wgt(X,N) : wgt(X,N), js(col,X) }.
            """)

        elif rule == "leximax":
            if verbose:
                print("Computing outcome with ASP and the leximax rule...")
            asp_program += textwrap.dedent("""
            % Leximax rule
            wgt(X,N) :- lit(X), N = #count { A : voter(A), js(A,X) }.
            #maximize { 1@N,wgt(X,N) : wgt(X,N), js(col,X) }.
            """)

        elif rule == "young":
            if verbose:
                print("Computing outcome with ASP and the young rule...")
            asp_program += textwrap.dedent("""
            % Young rule
            in(A) ; out(A) :- voter(A).
            inwgt(X,N) :- lit(X), N = #count{ A : voter(A), in(A), js(A,X) }.
            inmaj(X) :- lit(X), inwgt(X,N), inwgt(-X,M), N > M.
            js(col,X) :- inmaj(X).
            #minimize { 1@1,out(A) : out(A) }.
            """)

        elif rule == "slater":
            if verbose:
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
            if verbose:
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
            outcome(X) :- agent(col), js(col, X), issue(X).
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
                    for label in scenario.agenda:
                        for atom in model.symbols(shown=True):
                            outcome[scenario.agenda[label]] = False
                            if f'outcome(l{label})' == str(atom):
                                outcome[scenario.agenda[label]] = True
                                break
                    yield outcome
