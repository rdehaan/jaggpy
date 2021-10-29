# A file to implement and test the functions that have 
# been written until now.

# To test this file, run "python3 -m unittest test.test" in the terminal.

from jaggpy.classes import Scenario
from jaggpy.bruteForceSolver import BruteForce
from jaggpy.ASPSolver import ASPSolver
from jaggpy.parser import Parser

scenario1 = Scenario()
relativeFilePath = "./test/testfiles/scenario1.jagg"
scenario1.loadFromFile(relativeFilePath)

scenario2 = Scenario()
relativeFilePath2 = "./test/testfiles/scenario2.jagg"
scenario2.loadFromFile(relativeFilePath2)

scenario3 = Scenario()
relativeFilePath3 = "./test/testfiles/scenario3.jagg"
scenario3.loadFromFile(relativeFilePath3)

scenario4 = Scenario()
relativeFilePath4 = "./test/testfiles/scenario4.jagg"
scenario4.loadFromFile(relativeFilePath4)

scenario5 = Scenario()
relativeFilePath5 = "./test/testfiles/scenario5.jagg"
scenario5.loadFromFile(relativeFilePath5)

scenario6 = Scenario()
relativeFilePath6 = "./test/testfiles/scenario6.jagg"
scenario6.loadFromFile(relativeFilePath6)

scenario7 = Scenario()
relativeFilePath7 = "./test/testfiles/scenario7.jagg"
scenario7.loadFromFile(relativeFilePath7)

scenario8 = Scenario()
relativeFilePath8 = "./test/testfiles/scenario8.jagg"
scenario8.loadFromFile(relativeFilePath8)

brutus = BruteForce()

# brutus.enumerateOutcomes(scenario1, "kemeny")
# brutus.enumerateOutcomes(scenario1, "slater")
# brutus.enumerateOutcomes(scenario2, "kemeny")
# brutus.enumerateOutcomes(scenario2, "slater")
# brutus.enumerateOutcomes(scenario3, "kemeny")
# brutus.enumerateOutcomes(scenario3, "slater")
# brutus.enumerateOutcomes(scenario4, "kemeny")
# brutus.enumerateOutcomes(scenario4, "slater")
# brutus.enumerateOutcomes(scenario5, "kemeny")
# brutus.enumerateOutcomes(scenario5, "slater")
# brutus.enumerateOutcomes(scenario6, "kemeny")

asp = ASPSolver()

asp.enumerateOutcomes(scenario1, "kemeny")
# asp.enumerateOutcomes(scenario1, "leximax")
# asp.enumerateOutcomes(scenario1, "young")

# asp.enumerateOutcomes(scenario2, "kemeny")
# asp.enumerateOutcomes(scenario2, "leximax")
# asp.enumerateOutcomes(scenario2, "young")
# asp.enumerateOutcomes(scenario2, "slater")
# asp.enumerateOutcomes(scenario2, "majority")

# asp.enumerateOutcomes(scenario3, "kemeny")
# asp.enumerateOutcomes(scenario3, "slater")

# asp.enumerateOutcomes(scenario4, "kemeny")
# asp.enumerateOutcomes(scenario4, "slater")

# asp.enumerateOutcomes(scenario5, "kemeny")
# asp.enumerateOutcomes(scenario5, "slater")

# asp.enumerateOutcomes(scenario5, "kemeny")
# asp.enumerateOutcomes(scenario5, "slater")

# brutus.enumerateOutcomes(scenario6, "kemeny")
# asp.enumerateOutcomes(scenario6, "kemeny")
# brutus.enumerateOutcomes(scenario6, "slater")
# asp.enumerateOutcomes(scenario6, "slater")

asp.enumerateOutcomes(scenario8, "kemeny")