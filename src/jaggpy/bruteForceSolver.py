#####################################################################
## The simplest solver that uses the given rule to give back the 
## outcome of the judgement aggregation.
#####################################################################

from .classes import Solver
from .parser import Parser
from nnf import *
from itertools import chain, combinations
import copy
import math

class BruteForce(Solver):
	def solve(self, scenario, rule):
		"""Given a scenario object and the name of a rule 
		this function will yield a list with all the outcomes
		of the judgement aggregation. The rule should be given 
		as a string and can be one of the following lowercase commands:
			- kemeny
			- maxhamming
			- slater 
			"""
		# Translate the agenda so that the issues are represented 
		# by their labels. These representations will be added to
		# the constraints.
		parser = Parser()
		translatedAgenda = parser.translateAgenda(scenario.agenda)

		# Make a list of all the judgement sets that are consistent
		# with the output constraints.
		my_string = ""
		for conjunct in scenario.outputConstraints:
			my_string += f'({conjunct}) & '
		for conjunct in translatedAgenda:
			my_string += f'({conjunct}) & '

		# Update what variables appear in the scenario
		allVariables = []
		for var in scenario.variables:
			allVariables.append(var)
		for label in scenario.agenda.keys():
			allVariables.append(f'l{label}')

		# Make sure that each variable gets an assignment
		for var in allVariables:
			my_string += f"({var} | ~{var}) & "
		my_string = my_string[:-3]

		# Preprocess the string representing the scenario
		var_prefix = "my_var_"
		my_string_preprocessed = my_string
		for var in allVariables:
			my_string_preprocessed = my_string_preprocessed.replace(var, var_prefix + var)
		for var in allVariables:
			exec(f"{var_prefix}{var} = Var('{var}')")
		outputConstraint = eval(my_string_preprocessed)

		# List all the models that are consistent with the output constraints
		consistentOutcomes =  list(outputConstraint.models())

		# Depending on the given rule we use helper functions to determine the outcomes
		# Kemeny rule
		if rule == "kemeny":
			print("Computing outcome with brute force and the Kemeny rule...")
			outcomes = self.solveKemeny(scenario, consistentOutcomes)

		# MaxHamming rule
		elif rule == "maxhamming":
			print("Computing outcome with the brute force and MaxHamming rule...")
			outcomes =  self.solveMaxHamming(scenario, consistentOutcomes)

		# Slater rule
		elif rule == "slater":
			print("Computing outcome with the brute force and Slater rule...")
			outcomes = self.solveSlater(scenario, consistentOutcomes)

		else:
			raise Exception (f"{rule} is not an implemented aggregation rule.")
		
		# Clean outcomes to only contain issues
		for i in range(len(outcomes)):
			outcome = outcomes[i]
			translatedOutcomes = {}
			for formula in outcome.keys():
				if formula[0] == 'l':
					label = int(formula[1])
					translation = scenario.agenda[label]
					translatedOutcomes[translation] = outcome[formula]
			outcomes[i] = translatedOutcomes
			
		# Remove duplicates from outcomes
		outcomes = [dict(t) for t in {tuple(outcome.items()) for outcome in outcomes}]

		yield outcomes

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

	def solveKemeny(self, scenario, consistentOutcomes):
		"""Helper function for the solve function. Given a scenario and the list of
		consistent outcomes, returns a list of the outcomes corresponding to the
		Kemeny rule."""
		# Keep track of the maximum agreement score and initiate list of outcomes
		maxAgreement = 0
		outcomes = []

		# Check agreement score for each outcome and update list of outcomes accordingly
		for outcome in consistentOutcomes:
			agreementScore = 0
			# For each formula in the pre-agenda, check how many agents agree with the outcome and update agreement score.
			for label in scenario.agenda.keys():
				support = self.supportNumber(scenario.agenda, scenario.profile)
				if outcome[f'l{label}']:
					agreementScore += support[scenario.agenda[label]]
				else:
					agreementScore += scenario.numberVoters - support[scenario.agenda[label]] 
			
			if agreementScore == maxAgreement:
				outcomes.append(outcome)
			elif agreementScore > maxAgreement:
				maxAgreement = agreementScore
				outcomes = [outcome]
		return outcomes	

	def solveMaxHamming(self, scenario, consistentOutcomes):
		"""Helper function for the solve function. Given a scenario and the list of
		consistent outcomes, returns a list of the outcomes corresponding to the
		maxHamming rule."""
		# Keep track of minimum maximal Hamming distance and initialise list of outcomes.
		minimumMHD = math.inf
		outcomes = []

		# Find max Hamming difference for each outcome and update 
		for outcome in consistentOutcomes:
			# Reset max Hamming Distance
			maxHD = 0
			# Check the Hamming distance from the outcome to each judgement set and track the maximal distance.
			for judSet in scenario.profile:
				# Check Hamming distance.
				hamDist = 0
				for key in scenario.agenda.keys():
					if outcome[f'l{key}'] and scenario.agenda[key] not in judSet[1]:
						hamDist += 1
					elif not outcome[f'l{key}'] and scenario.agenda[key] in judSet[1]: 
						hamDist += 1

				# Update the maximum HD for the outcome.
				if hamDist > maxHD:
					maxHD = hamDist

			# Update outcome set to include only those outcomes with the minimum maximum Hamming distance (thus far)
			if maxHD == minimumMHD:
				outcomes.append(outcome)
			elif maxHD < minimumMHD:
				minimumMHD = maxHD
				outcomes = [outcome]
		return outcomes

	def solveSlater(self, scenario, consistentOutcomes):
		"""Helper function for the solve function. Given a scenario and the list of
		consistent outcomes, returns a list of the outcomes corresponding to the
		Slater rule."""
		# Determine the set of formulas that has a majority vote, add a 
		# formula if it is accepted and add it with 'neg ' in front of
		# it when it is rejected. The 'neg ' is merely a prefix to read
		# later.
		majorityNumber = scenario.numberVoters / 2
		majoritySet = []
		support = self.supportNumber(scenario.agenda, scenario.profile)
		for key in scenario.agenda.keys():
			formula = scenario.agenda[key]
			if support[formula] > majorityNumber:
				majoritySet.append(f'l{key}')
			elif support[formula] == majorityNumber:
				pass
			else:
				negatedFormula = f'neg l{key}'
				majoritySet.append(negatedFormula)

		# Make a list of potential subsets to see if the current 
		# 'size' of subsets has consistent ones.
		potentialSubsets = []
		for i in range(len(majoritySet), 0, -1):
			# For a given length give all subsets of the majorityset
			# of that given length.
			subsets = list(combinations(majoritySet, i))
			for subset in subsets:
				tempOutcomes = copy.deepcopy(consistentOutcomes)
				toRemove = []
				# For each formula in the subset, remove all the models
				# that do not agree with it. Hence looking if some model
				# agrees with all formulas in the subset
				for formula in subset:
					if formula[0:4] == "neg ":
						for j in range(len(tempOutcomes)):
							if tempOutcomes[j][formula[4:]]:
								toRemove.append(j)
					else:
						for j in range(len(tempOutcomes)):
							if not tempOutcomes[j][formula]:
								toRemove.append(j)
				# Keep all models that have not been put in the toRemove list
				toKeep = [index for index in range(len(tempOutcomes)) if index not in toRemove]
				consistentList = [tempOutcomes[index] for index in toKeep]

				# If some models were kept we add this subset as a candidate
				if consistentList != []:
					potentialSubsets.append(subset)
			# If at least one subset has been chosen this length of subsets
			# has the greatest consistent sets.
			if potentialSubsets != []:
				break
		# Go over all chosen subsets in max(m(J),<=)
		outcomes = []
		for subset in potentialSubsets:
			tempOutcomes = copy.deepcopy(consistentOutcomes)
			toRemove = []
			# For each formula remove all the models that do not agree
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
			# Add all the extensions of the chosen subsets to the outcome
			for index in toKeep:
				outcomes.append(tempOutcomes[index])
		return outcomes
