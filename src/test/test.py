# A file to implement and test the functions that have 
# been written until now.

# To test this file, run "python3 -m unittest test.test" in the terminal.

from jaggpy.classes import Scenario
from jaggpy.bruteForceSolver import BruteForce
from jaggpy.ASPSolver import ASPSolver
from jaggpy.parser import Parser

scenario1 = Scenario()
relativeFilePath = r"./test/testfiles/scenario1.jagg"
absoluteFilePath = r"/Users/Bo/Documents/MoL/jaggpy/src/test/testfiles/scenario1.jagg"
scenario1.loadFromFile(relativeFilePath)

scenario2 = Scenario()
relativeFilePath2 = r"./test/testfiles/scenario2.jagg"
absoluteFilePath2 = r"/Users/Bo/Documents/MoL/jaggpy/src/test/testfiles/scenario2.jagg"
scenario2.loadFromFile(relativeFilePath2)

scenario3 = Scenario()
relativeFilePath3 = r"./test/testfiles/scenario3.jagg"
absoluteFilePath3 = r"/Users/Bo/Documents/MoL/jaggpy/src/test/testfiles/scenario3.jagg"
scenario3.loadFromFile(relativeFilePath3)

scenario4 = Scenario()
relativeFilePath4 = r"./test/testfiles/scenario4.jagg"
absoluteFilePath4 = r"/Users/Bo/Documents/MoL/jaggpy/src/test/testfiles/scenario4.jagg"
scenario4.loadFromFile(relativeFilePath4)

# print(scenario4.toNNF("(~x1 -> x2) & (x2 | x3)"))

brutus = BruteForce()

# brutus.enumerateOutcomes(scenario1, "kemeny")
# brutus.enumerateOutcomes(scenario1, "slater")
# brutus.enumerateOutcomes(scenario2, "slater")
# brutus.enumerateOutcomes(scenario2, "kemeny")
# brutus.enumerateOutcomes(scenario3, "kemeny")
# brutus.enumerateOutcomes(scenario3, "slater")

asp = ASPSolver()
# asp.enumerateOutcomes(scenario1, "kemeny")
# asp.enumerateOutcomes(scenario1, "leximax")
# asp.enumerateOutcomes(scenario1, "young")

# asp.enumerateOutcomes(scenario2, "kemeny")
# asp.enumerateOutcomes(scenario2, "leximax")
# asp.enumerateOutcomes(scenario2, "young")
# asp.enumerateOutcomes(scenario2, "reversal") 
# asp.enumerateOutcomes(scenario2, "slater")
# asp.enumerateOutcomes(scenario2, "majority")

# asp.enumerateOutcomes(scenario3, "kemeny")
# asp.enumerateOutcomes(scenario3, "slater")

parser = Parser()
sentence = ("(i1 -> ~(i2 & i3)) & (i1 -> ~(i3 & i4))")
nnfSentence = parser.toNNF(sentence)
