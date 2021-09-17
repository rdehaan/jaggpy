#####################################################################
## The simplest solver that uses the given rule to give back the 
## outcome of the judgement aggregation.
#####################################################################

from .classes import Solver
from nnf import *
from itertools import chain, combinations
import copy

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

			# Keep track of the maximum agreement score and initiate list of outcomes
			maxAgreement = 0
			outcomes = []

			# Check agreement score for each outcome and update list of outcomes accordingly
			for outcome in consistentOutcomes:
				agreementScore = 0
				# For each formula in the pre-agenda, check how many agents agree with the outcome and update agreement score.
				for formula in scenario.agenda.values():
					if outcome[formula]:
						agreementScore += self.supportNumber(scenario.agenda, scenario.profile)[formula]
					else:
						agreementScore += scenario.numberVoters - self.supportNumber(scenario.agenda, scenario.profile)[formula]
				
				if agreementScore == maxAgreement:
					outcomes.append(outcome)
				elif agreementScore > maxAgreement:
					maxAgreement = agreementScore
					outcomes = [outcome]
			
			return(outcomes)
				

					

		# Other rules.
		elif rule == "slater":
			print("Solving slater rule")

			# Determine the set of formulas that has a majority vote
			majorityNumber = scenario.numberVoters / 2
			majoritySet = []
			support = self.supportNumber(scenario.agenda, scenario.profile)
			for formula in scenario.agenda.values():
				if support[formula] > majorityNumber:
					majoritySet.append(formula)
				elif support[formula] == majorityNumber:
					pass
				else:
					negatedFormula = f'neg {formula}'
					majoritySet.append(negatedFormula)
			potentialSubsets = []
			for i in range(len(majoritySet), 0, -1):
				subsets = list(combinations(majoritySet, i))
				for subset in subsets:
					tempOutcomes = copy.deepcopy(consistentOutcomes)
					toRemove = []
					for formula in subset:
						if formula[0:4] == "neg ":
							for j in range(len(tempOutcomes)):
								if tempOutcomes[j][formula[4:]]:
									toRemove.append(j)
						else:
							for j in range(len(tempOutcomes)):
								if not tempOutcomes[j][formula]:
									toRemove.append(j)
					toKeep = [index for index in range(len(tempOutcomes)) if index not in toRemove]
					consistentList = [tempOutcomes[index] for index in toKeep]

					if consistentList != []:
						potentialSubsets.append(subset)
				if potentialSubsets != []:
					break
			outcomes = []
			for subset in potentialSubsets:
				tempOutcomes = copy.deepcopy(consistentOutcomes)
				toRemove = []
				for formula in subset:
					if formula[0:4] == "neg ":
						for j in range(len(tempOutcomes)):
							if tempOutcomes[j][formula[4:]]:
								toRemove.append(j)
					else:
						for j in range(len(tempOutcomes)):
							if not tempOutcomes[j][formula]:
								toRemove.append(j)
				toKeep = [index for index in range(len(tempOutcomes)) if index not in toRemove]
				consistentList = [tempOutcomes[index] for index in toKeep]
				outcomes.append(consistentList)
			return(outcomes)


			



		else:
			raise Exception ("This is not a rule that has been implemented.")

	def supportNumber(self, agenda, profile):
		"""The function supportNumber gets an agenda profile and returns a dictionary that 
		has the labels of the formulas as keys and the number of times it is suported
		as its values."""
		supportCount = dict()
		for formula in agenda.values():
			supportCount[formula] = 0
		for JS in profile:
			timesAccepted = JS[0]
			acceptedFormula = JS[1]
			for formula in acceptedFormula:
				supportCount[formula] += timesAccepted
		return supportCount

