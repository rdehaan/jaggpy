# A file to implement and test the functions that have 
# been written until now.

from jaggpy.classes import Scenario
from jaggpy.bruteForceSolver import BruteForce

scenario1 = Scenario()

relativeFilePath = r"./test/testfiles/scenario1.jagg"
absoluteFilePath = r"/Users/Bo/Documents/MoL/jaggpy/src/test/testfiles/scenario1.jagg"

scenario1.loadFromFile(relativeFilePath)

brutus = BruteForce()


# print(brutus.solve(scenario1, "kemeny"))
# print(brutus.solve(scenario1, "slater"))
brutus.enumerateOutcomes(scenario1, "slater")
# print("Outcome according to maxhamming rule is: " + str(brutus.solve(scenario1, "maxhamming")))
