#####################################################################
## The simplest solver that uses the given rule to give back the 
## outcome of the judgement aggregation.
#####################################################################

from .classes import Solver
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
			print("Computing outcome with brute force and the Kemeny rule...")

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
			
			yield(outcomes)

		# MaxHamming rule
		elif rule == "maxhamming":
			print("Computing outcome with the brute force and MaxHamming rule...")

			# Keep track of minimum maximal Hamming distance and initialise list of outcomes.
			minimumMHD = math.inf
			outcomes = []

			# Find max Hamming difference for each outcome and update 
			for outcome in consistentOutcomes:
				# Reset max Hamming Distance
				maxHD = 0
				# Check the Hamming distance from the outcome to each judgement set and track the maximal distance.
				for judSet in scenario.profile:
					# Check Hamming distance. NOT CORRECT YET
					hamDist = 0
					for formula in scenario.agenda.values():
						if outcome[formula] and formula not in judSet[1]:
							hamDist += 1
						elif not outcome[formula] and formula in judSet[1]:
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
			
			yield(outcomes)
	

		# Other rules.
		elif rule == "slater":
			print("Computing outcome with the brute force and Slater rule...")

			# Determine the set of formulas that has a majority vote, add a 
			# formula if it is accepted and add it with 'neg ' in front of
			# it when it is rejected. The 'neg ' is merely a prefix to read
			# later.
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
			yield(outcomes)
		else:
			raise Exception (f"{rule} is not a recognized aggregation rule.")

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

