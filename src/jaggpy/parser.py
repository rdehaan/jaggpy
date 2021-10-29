#####################################################################
## Parser for sentences
## The function parse_sentence is heavily inspired by
## https://github.com/pyparsing/pyparsing/blob/master/examples/simpleBool.py#L16
## It has been altered for this application.
#####################################################################

from pyparsing import infixNotation, opAssoc, Keyword, Word, alphanums, ParserElement
from nnf import Var, Or, And # pylint: disable=unused-import

class Parser:
    """A parser class for parsing formulas."""
    def parse_sentence(self, sentence):
        """Given a formula as a string, parse it and return a list of
        lists with the [] representing brackets. So x1 | (x2 & ~x3)
        returns [x1, |, [x2, &, [~, x3]]] """
        # Create space between negations and atoms
        prep_sentence = sentence.split("~")
        prep_sentence = "~ ".join(prep_sentence)

        ParserElement.enablePackrat()

		# Define classes to be built at parse time, as each matching
		# expression type is parsed. Each class has a as_list method
		# that returns itself and its elements in list representation
		# (recursively).
        class BoolOperand:
            """The class BoolOperand"""
            def __init__(self, t):
                self.label = t[0]

            def __str__(self) -> str:
                return self.label

            __repr__ = __str__

            def as_list(self):
                return self.label

        class BoolNot:
            """The class for negations."""
            def __init__(self, t):
                self.arg = t[0][1]

            def __str__(self) -> str:
                return "~" + str(self.arg)

            __repr__ = __str__

            def as_list(self):
                return ["~", self.arg.as_list()]

        class BoolBinOp:
            """The parent class for binary operations."""
            repr_symbol: str = ""

            def __init__(self, t):
                self.args = t[0][0::2]

            def __str__(self) -> str:
                sep = " %s " % self.repr_symbol
                return "(" + sep.join(map(str, self.args)) + ")"


        class BoolAnd(BoolBinOp):
            """The class for conjunctions."""
            repr_symbol = "&"
            def as_list(self):
                """Returns list of conjuncts with '&' symbol."""
                result = []
                for argument in self.args:
                    result.append(argument.as_list())
                    result.append("&")
                result = result[:-1]
                return result

        class BoolOr(BoolBinOp):
            """The class disjunctions."""
            repr_symbol = "|"
            def as_list(self):
                """Return list of disjuncts with '|' symbol."""
                result = []
                for argument in self.args:
                    result.append(argument.as_list())
                    result.append("|")
                result = result[:-1]
                return result

        class BoolImplies(BoolBinOp):
            """The class for implications."""
            repr_symbol = "->"
            def as_list(self):
                """Return implications in list form with '->' symbol."""
                return [self.args[0].as_list(), "->", self.args[1].as_list()]

        # Define what the operator symbols mean
        NOT = Keyword("~")
        AND = Keyword("&")
        OR = Keyword("|")
        IMPLIES = Keyword("->")

        # Atoms can be alphanumerals
        bool_operand = Word(alphanums)
        bool_operand.setParseAction(BoolOperand).setName("bool_operand")

        bool_expr = infixNotation(
        bool_operand,
        [
            # Define precedence of operations
            (NOT, 1, opAssoc.RIGHT, BoolNot),
            (OR, 2, opAssoc.LEFT, BoolOr),
            (AND, 2, opAssoc.LEFT, BoolAnd),
            (IMPLIES, 2, opAssoc.LEFT, BoolImplies)
        ],
        )

        # Create a parse object
        parsed_sentence = bool_expr.parseString(prep_sentence)[0]

        # Return the parsed sentence as a list
        return parsed_sentence.as_list()

    def to_nnf(self, sentence):
        """Given a formula as a string, returns a string of the
        formula converted to NNF."""
        # Parse the sentence and then convert it to NNF
        parsed = self.parse_sentence(sentence)
        nnf = self.to_nnf_parsed(parsed)

        return nnf

    def to_nnf_parsed(self, sentence):
        """Helper function for the recursive proces of the to_nnf function.
        Given a formula, returns the formula partially converted
        to NNF. """
        # If the sentence is just a string, leave it be
        if isinstance(sentence, str):
            return sentence
        # If it is negated, push the negation through
        if sentence[0] == '~':
            if isinstance(sentence[1], str):
                return "".join(sentence)
            if sentence[1][1] == '&':
                return self.neg_and(sentence[1])
            if sentence[1][1] == '|':
                return self.neg_or(sentence[1])
            if sentence[1][1] == '->':
                return self.neg_implies(sentence[1])
            # Remove double negations
            if sentence[1][0] == '~':
                return self.to_nnf_parsed(sentence[1][1])
            raise Exception("There seems to be something wrong..")
        # If it is not negated, rewrite implication and
        # search for more negations
        operator = sentence[1]
        if operator == '->':
            left = self.to_nnf_parsed(['~', sentence[0]])
            right = self.to_nnf_parsed(sentence[2])
            return " ".join(['(', left, '|', right, ')'])
        result = ['(']
        for i, value in enumerate(sentence):
            if i % 2 == 0:
                element = self.to_nnf_parsed(value)
                result.append(element)
                result.append(operator)
        result = result[:-1]
        result.append(')')
        return " ".join(result)

    def neg_and(self, sentence):
        """Helper function for to_nnf_parsed. Given a negated conjunction,
        returns a disjunction with the disjuncts negated. """
        result = ['(']
        for i, value in enumerate(sentence):
            if i % 2 == 0:
                element = self.to_nnf_parsed(['~', value])
                result.append(element)
                result.append('|')
        result = result[:-1]
        result.append(')')
        return " ".join(result)

    def neg_or(self, sentence):
        """Helper function for to_nnf_parsed. Given a negated disjunction,
        returns a conjuncts with the conjuncts negated. """
        result = ['(']
        for i, value in enumerate(sentence):
            if i % 2 == 0:
                element = self.to_nnf_parsed(['~', value])
                result.append(element)
                result.append('&')
        result = result[:-1]
        result.append(')')
        return " ".join(result)

    def neg_implies(self, sentence):
        """Helper function for to_nnf_parsed. Given a negated implication,
        returns a disjunction with the antecedent negated."""
        # Negate the antecedent
        antecedent = self.to_nnf_parsed(['~', sentence[0]])
        consequent = self.to_nnf_parsed(sentence[2])

        # Return the negated implication as a conjunction
        return " ".join(['(', antecedent, '|', consequent, ')'])

    def to_cnf(self, sentence, variables):
        """
        Translate a sentence from NNF (as produced by the to_nnf function), to CNF.
        The function needs a formula/sentence as a string and a list of all
        variables occuring in the sentence. It returns the CNF formula and
        an updated list of all occurring variables.
        """
        my_string = sentence
        all_variables = set()

        # Use a prefix to prevent variable name collisions
        # Add this prefix to all variables in the string
        var_prefix = "my_var_"
        my_string_preprocessed = my_string
        for var in variables:
            my_string_preprocessed = my_string_preprocessed.replace(var, var_prefix + var)

        # Declare variables (with prefix) and parse the formula with the
        # variable prefixes added
        for var in variables:
            exec(f"{var_prefix}{var} = Var('{var}')")
            all_variables.add(var)
        formula = eval(my_string_preprocessed)

        # Translate the formula to CNF and update what variables
        # occur in the formula.
        formula = formula.to_CNF()
        for var in formula.vars():
            if not isinstance(var, str):
                all_variables.add('a' + str(var)[:4])
            else:
                all_variables.add(var)

        # Translate formula to string.
        list_of_conjuncts = []
        for conjunct in formula:
            conj = "( "
            disjunct_counter = 0
            for disjunct in conjunct:
                if str(disjunct)[-1] == '>':
                    disjunct = "a".join(str(disjunct)[:-1].split('<'))
                if disjunct_counter < len(conjunct) - 1:
                    conj = conj + str(disjunct) + " | "
                else:
                    conj = conj + str(disjunct) + " )"
                disjunct_counter += 1
            list_of_conjuncts.append(conj)
        if len(formula) == 1:
            return [list_of_conjuncts[0], all_variables]
        formula_str = "( "
        for i, value in enumerate(list_of_conjuncts):
            if i < len(list_of_conjuncts) - 1:
                formula_str = formula_str + value + " & "
            else:
                formula_str = formula_str + value + " )"
        return [formula_str, all_variables]

    def translate_agenda(self, agenda):
        """Given a (sub)-agenda returns a list of constraints. For each issue a
        constraint is added of the form (label -> formula) and (formula -> label).
        Both are made sure to be NNF formulas. """
        new_constraints = []
        for label in agenda.keys():
            label_var = f'l{label}'
            formula = agenda[label]

            # Add label -> formula
            new_constraints.append(f'~{label_var} | {formula}')

            # Add formula -> label
            neg_formula = self.to_nnf(f'~ ({formula})')
            new_constraints.append(f'{neg_formula} | {label_var}')

        return new_constraints
        