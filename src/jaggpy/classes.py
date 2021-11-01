######################################################################
## Useful python classes for the scenarios and the possible solvers.
#################################################################

# A scenario class that will allow us to create a scenario object by loading
# information from a .jagg file. A scenario has an agenda, input constraints,
# output constraints and a profile.

from abc import ABC, abstractmethod
from itertools import islice
from nnf import Var, Or, And  # pylint: disable=unused-import
from jaggpy.parser import Parser

class Scenario:
    """A Scenario object has the following properties:
            - variables: a list of occurring variables
            - agenda: a dictionary with numbers as keys and
                formulas as values
            - input_constraints: a list of input constraints
            - output_constraints: a list of output constraints
            - profile: a list of judgment sets
            - number_voters: an integer specifying the number of voters
            """
    def __init__(self):
        """A Scenario object has the following properties:
            - variables: a list of occurring variables
            - agenda: a dictionary with numbers as keys and
                formulas as values
            - input_constraints: a list of input constraints
            - output_constraints: a list of output constraints
            - profile: a list of judgment sets
            - number_voters: an integer specifying the number of voters
            """
        self.agenda = {}
        self.input_constraints = []
        self.output_constraints = []
        self.profile = []
        self.variables = []
        self.number_voters = 0

    def load_from_file(self, path):
        """Load the scenario from a .jagg file given its path.
        The path should be a raw string, i.e. of the form r"path/to/file".
        The file should have the following format, with each element being on
        a new line:
            - var_1,..., var_n: list of all the variables
            - Number of Formulas: The number of formulas in the pre-agenda
            - X, Formula: The formula labeled by the number X
            - In, Formula: The input constraint labeled by the text "In"
            - Out, Formula: The output constraint labeled by the text "Out"
            - Number of voters, Number of distinct judgment sets
            - J, l1;...;ln: A list of the labels of the formulas
                that are accepted. The rest is rejected.
                This profile occurs J times. The formulas should be
                given by the times they are selected and seperated
                by a semicolon. For example, "4, 2;4;5".
        A formula can contain the following operators:
            - The OR operator |
            - The AND operator &
            - The NOT operator ~
            - The IMPLIES operator ->
        Parentheses can be omitted where clear from context. """
        # Read the file and split all lines
        with open(path, encoding='utf-8') as conn:
            text = conn.read()
            lines = text.splitlines()

        # Remove blank lines and comments from the lines
        lines = [line for line in lines if line != "" and line[0] != "#"]

        # Create a parser object for future use
        parser = Parser()

        # Add the variables to the scenario
        self.variables = lines[0].split(", ")

        # Add the formulas to the agenda dictionary using the given label
        number_of_formulass = int(lines[1])
        for i in range(2, number_of_formulass+2):
            current_line = lines[i].split(", ")
            label = int(current_line[0])
            formula = current_line[1]
            self.agenda[label] = parser.to_nnf(formula)

        # Add the input constraints to the list of constraints
        line_number = number_of_formulass+2
        while lines[line_number].split(", ")[0] == "In":
            formula = lines[line_number].split(", ")[1]
            if formula == "":
                first_var = self.variables[0]
                formula = f'({first_var} | ~{first_var})'
            self.input_constraints.append(parser.to_nnf(formula))
            line_number += 1

        # Check consistency of the input constraints
        my_string = ""
        for conjunct in self.input_constraints:
            my_string += f"({conjunct}) & "
        my_string = my_string[:-3]
        if not self.check_consistency(my_string):
            raise Exception ("The input constraints are inconsistent")

        # Add the output constraints to the list of constraints
        while lines[line_number].split(", ")[0] == "Out":
            formula = lines[line_number].split(", ")[1]
            if formula == "":
                first_var = self.variables[0]
                formula = f'({first_var} | ~{first_var})'
            self.output_constraints.append(parser.to_nnf(formula))
            line_number += 1

        # Check consistency of the output constraints
        my_string = ""
        for conjunct in self.output_constraints:
            my_string += f"({conjunct}) & "
        my_string = my_string[:-3]
        if not self.check_consistency(my_string):
            raise Exception ("The output constraints are inconsistent")

        # Add the number of voters to the scenario
        self.number_voters += int(lines[line_number].split(", ")[0])

        # Add the list of accepted formulas to the profile dictionary
        # for each of the judgment sets.
        number_of_js = int(lines[line_number].split(", ")[1])
        for i in range(line_number+1, line_number+number_of_js+1):
            current_line = lines[i].split(", ")
            # If the list of accepted formulas is not empty continue
            if current_line[1] != '':
                label = int(current_line[0])
                formula_labels = list(map(int, current_line[1].split(";")))
                accepted_formulas = []
                for formula_label in formula_labels:
                    accepted_formulas.append(self.agenda[formula_label])

                # Check consistency of the judgment set with respect
                # to the input constraint
                my_string = ""
                for conjunct in self.input_constraints:
                    my_string += f"({conjunct}) & "
                for j in range(1, len(self.agenda)+1):
                    if j not in formula_labels:
                        my_string += f"(~{self.agenda[j]}) & "
                    else:
                        my_string += f"({self.agenda[j]}) & "
                my_string = my_string[:-3]
                self.check_consistency(my_string)
                if not self.check_consistency(my_string):
                    raise Exception (f"The judgment set on line {i} is inconsistent"\
                        " with the input constraints.")

                # Add the judgment set to the scenario
                self.profile.append([label, accepted_formulas])
            else:
                # If the all issues are rejected, add the empty list
                self.profile.append([label, []])

    def check_consistency(self, sentence):
        """The function check_consistency should receive an NNF-formula as a
        string. It return a Boolean indicating whether the formula is consistent."""
        my_string = sentence

        # Use a prefix to prevent variable name collisions
        # Add this prefix to all variables in the string
        var_prefix = "my_var_"
        my_string_preprocessed = my_string
        for var in self.variables:
            my_string_preprocessed = my_string_preprocessed.replace(var, var_prefix + var)

        # Declare variables (with prefix) and parse the formula with the
        # variable prefixes added
        for var in self.variables:
            exec(f"{var_prefix}{var} = Var('{var}')")
        formula = eval(my_string_preprocessed)

        # Return whether the formula is consistent
        return formula.consistent()


    def pretty_repr(self):
        """Returns string that represents the scenario object in a readable way"""
        scenario_string = "Variables:"
        for variable in self.variables:
            scenario_string += f"\n{variable}"
        scenario_string += "\n\nSub-agenda (label, formula):"
        for key in self.agenda:
            scenario_string += f"\n{key}, {self.agenda[key]}"
        scenario_string += "\n\nInput constraints:"
        for constraint in self.input_constraints:
            scenario_string += f"\n{constraint}"
        scenario_string +=  "\n\nOutput constraints:"
        for constraint in self.output_constraints:
            scenario_string += f"\n{constraint}"
        scenario_string += "\n\nProfile (times selected, accepted formulas):"
        for judgment_set in self.profile:
            accepted = "("
            for variable in judgment_set[1]:
                if accepted == "(":
                    accepted += variable
                else:
                    accepted += ", " + variable
            accepted += ")"
            scenario_string += (f"\n{judgment_set[0]}, " + accepted)
        return scenario_string

# A solver class with an enumerate_outcomes function that enumerates
# all the outcomes given a scenario and an aggregation rule.
class Solver(ABC):
    """The abstract class for solvers."""
    @abstractmethod
    def all_outcomes(self, scenario, rule, verbose=False):
        """Given a scenario and an aggregation rule, yields a generator
        with the corresponding outcomes."""

    def outcomes(self, scenario, rule, num=1, verbose=False):
        """Given a scenario, an aggregation rule and an integer `num`,
        yields the first `num` corresponding outcomes."""
        return islice(self.all_outcomes(scenario, rule, verbose=verbose), num)
