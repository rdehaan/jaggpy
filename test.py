# A file to implement and test the functions that have 
# been written until now.

# from src.jaggpy.bruteForceSolver import BruteForce
from src.jaggpy.classes import Scenario

scenario1 = Scenario()
filePath = r"testfiles/scenario1.jagg"

scenario1.loadFromFile(filePath)

scenario1.prettyPrint()

# brutus = BruteForce()
# print(brutus.solve("a", "b"))