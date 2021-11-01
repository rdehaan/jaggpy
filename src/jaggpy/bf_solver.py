#####################################################################
## The simplest solver that uses the given rule to give back the
## outcome of the judgment aggregation.
#####################################################################

import copy
import math
from itertools import combinations
from nnf import Var, Or, And # pylint: disable=unused-import
from .classes import Solver
from .parser import Parser

class BFSolver(Solver):
    """A brute force solver for Judgment Aggregation."""
    def all_outcomes(self, scenario, rule, verbose=False):
        """Given a scenario object and the name of a rule
        this function will yield a list with all the outcomes
        of the judgment aggregation. The rule should be given
        as a string and can be one of the following lowercase commands:
            - kemeny
            - maxhamming
            - slater
        Set verbose to true if you want the program to inform you that
        it is computing with the given rule.
        """
        # Translate the agenda so that the issues are represented
        # by their labels. That labels correspond to the correct issues
        # will be achieved by adding constraints.
        parser = Parser()
        translated_agenda = parser.translate_agenda(scenario.agenda)

        # Make a list of all the judgment sets that are consistent
        # with the output constraints.
        my_string = ""
        for conjunct in scenario.output_constraints:
            my_string += f'({conjunct}) & '
        for conjunct in translated_agenda:
            my_string += f'({conjunct}) & '

        # Update what variables appear in the scenario.
        all_variables = []
        for var in scenario.variables:
            all_variables.append(var)
        for label in scenario.agenda.keys():
            all_variables.append(f'l{label}')

        # Make sure that each variable gets an assignment.
        for var in all_variables:
            my_string += f"({var} | ~{var}) & "
        my_string = my_string[:-3]

        # Preprocess the string representing the scenario.
        var_prefix = "my_var_"
        my_string_preprocessed = my_string
        for var in all_variables:
            my_string_preprocessed = my_string_preprocessed.replace(var, var_prefix + var)
        for var in all_variables:
            exec(f"{var_prefix}{var} = Var('{var}')")
        output_contstraint = eval(my_string_preprocessed)

        # List all the models that are consistent with the output constraints.
        consistent_outcomes =  list(output_contstraint.models())

        # We determine the outcome with a helper function that corresponds to the chosen rule.
        # Kemeny rule
        if rule == "kemeny":
            if verbose:
                print("Computing outcome with the brute force solver and the Kemeny rule...")
            outcomes = self.solve_kemeny(scenario, consistent_outcomes)

        # MaxHamming rule
        elif rule == "maxhamming":
            if verbose:
                print("Computing outcome with the brute force solver and the MaxHamming rule...")
            outcomes =  self.solve_max_hamming(scenario, consistent_outcomes)

        # Slater rule
        elif rule == "slater":
            if verbose:
                print("Computing outcome with the brute force solver and the Slater rule...")
            outcomes = self.solve_slater(scenario, consistent_outcomes)

        else:
            raise Exception (f"{rule} is not a recognized aggregation rule.")

        # Clean outcomes to only contain issues
        for i, outcome in enumerate(outcomes):
            translated_outcomes = {}
            for formula in outcome.keys():
                if formula[0] == 'l':
                    label = int(formula[1])
                    translation = scenario.agenda[label]
                    translated_outcomes[translation] = outcome[formula]
            outcomes[i] = translated_outcomes

        # Remove duplicates from outcomes.
        outcomes = [dict(t) for t in {tuple(outcome.items()) for outcome in outcomes}]

        return outcomes

    def support_number(self, agenda, profile):
        """The function support_number gets an agenda and profile and returns a dictionary, where each key
        is the label of a formula and each value is the number of times the issue corresponding to the
        label is voted for."""
        support_count = dict()
        for formula in agenda.values():
            support_count[formula] = 0
        for judgement_set in profile:
            times_accepted = judgement_set[0]
            accepted_formula = judgement_set[1]
            for formula in accepted_formula:
                support_count[formula] += times_accepted
        return support_count

    def solve_kemeny(self, scenario, consistent_outcomes):
        """Helper function for the solve function. Given a scenario and a list of
        consistent outcomes, returns a list of the outcomes corresponding to the
        Kemeny rule."""
        # Keep track of the maximum agreement score and initiate list of outcomes.
        max_agreement = 0
        outcomes = []

        # Check agreement score for each outcome and update list of outcomes accordingly.
        for outcome in consistent_outcomes:
            agreement_score = 0
            # For each formula in the pre-agenda, check how many agents agree
            # with the outcome and update agreement score.
            for label in scenario.agenda.keys():
                support = self.support_number(scenario.agenda, scenario.profile)
                if outcome[f'l{label}']:
                    agreement_score += support[scenario.agenda[label]]
                else:
                    agreement_score += scenario.number_voters - support[scenario.agenda[label]]

            if agreement_score == max_agreement:
                outcomes.append(outcome)
            elif agreement_score > max_agreement:
                max_agreement = agreement_score
                outcomes = [outcome]
        return outcomes

    def solve_max_hamming(self, scenario, consistent_outcomes):
        """Helper function for the solve function. Given a scenario and a list of
        consistent outcomes, returns a list of the outcomes corresponding to the
        MaxHamming rule."""
        # Keep track of minimum maximal Hamming distance and initialise list of outcomes.
        minimum_mhd = math.inf
        outcomes = []

        # Find max Hamming difference for each outcome and update
        for outcome in consistent_outcomes:
            max_hd = 0
            # Check the Hamming distance from the outcome to each judgment set
            # and track the maximal distance.
            for jud_set in scenario.profile:
                # Check Hamming distance.
                ham_dist = 0
                for key in scenario.agenda.keys():
                    if outcome[f'l{key}'] and scenario.agenda[key] not in jud_set[1]:
                        ham_dist += 1
                    elif not outcome[f'l{key}'] and scenario.agenda[key] in jud_set[1]:
                        ham_dist += 1

                # Update the maximum HD for the outcome.
                if ham_dist > max_hd:
                    max_hd = ham_dist

            # Update outcome set to include only those outcomes with the minimum
            # maximum Hamming distance (thus far).
            if max_hd == minimum_mhd:
                outcomes.append(outcome)
            elif max_hd < minimum_mhd:
                minimum_mhd = max_hd
                outcomes = [outcome]
        return outcomes

    def solve_slater(self, scenario, consistent_outcomes):
        """Helper function for the solve function. Given a scenario and a list of
        consistent outcomes, returns a list of the outcomes corresponding to the
        Slater rule."""
        # Determine the set of formulas that has a majority vote, add a
        # formula if it is accepted and add it with 'neg ' in front of
        # it when it is rejected. The 'neg ' is merely a prefix to read
        # later.
        majority_number = scenario.number_voters / 2
        majority_set = []
        support = self.support_number(scenario.agenda, scenario.profile)
        for key in scenario.agenda.keys():
            formula = scenario.agenda[key]
            if support[formula] > majority_number:
                majority_set.append(f'l{key}')
            elif support[formula] == majority_number:
                pass
            else:
                negated_formula = f'neg l{key}'
                majority_set.append(negated_formula)

        # Make a list of potential subsets to see if there are consistent subsets of
        # the current 'size'.
        potential_subsets = []
        for i in range(len(majority_set), 0, -1):
            # For a given length give all subsets of the majority_set
            # of that given length.
            subsets = list(combinations(majority_set, i))
            for subset in subsets:
                temp_outcomes = copy.deepcopy(consistent_outcomes)
                to_remove = []
                # For each formula in the subset, remove all the models
                # that do not agree with it, thereby checking which models
                # agree with all formulas in the subset.
                for formula in subset:
                    if formula[0:4] == "neg ":
                        for j, value in enumerate(temp_outcomes):
                            if value[formula[4:]]:
                                to_remove.append(j)
                    else:
                        for j, value in enumerate(temp_outcomes):
                            if not value[formula]:
                                to_remove.append(j)
                # Keep all models that have not been put in the to_remove list.
                to_keep = [index for index in range(len(temp_outcomes)) if index not in to_remove]
                consistent_list = [temp_outcomes[index] for index in to_keep]

                # If some models were kept we add this subset as a candidate.
                if consistent_list != []:
                    potential_subsets.append(subset)
            # We break out of the (decreasing) loop when we have at least one consistent subset, for
            # this/these subsets will be the largest consistent subset(s).
            if potential_subsets != []:
                break
        # Go over all maximal (consistent) subsets.
        outcomes = []
        for subset in potential_subsets:
            temp_outcomes = copy.deepcopy(consistent_outcomes)
            to_remove = []
            # For each formula remove all the models that do not agree.
            for formula in subset:
                if formula[0:4] == "neg ":
                    for j, value in enumerate(temp_outcomes):
                        if value[formula[4:]]:
                            to_remove.append(j)
                else:
                    for j, value in enumerate(temp_outcomes):
                        if not value[formula]:
                            to_remove.append(j)
            to_keep = [index for index in range(len(temp_outcomes)) if index not in to_remove]
            # Add all the extensions of the chosen subsets to the outcome.
            for index in to_keep:
                outcomes.append(temp_outcomes[index])
        return outcomes
