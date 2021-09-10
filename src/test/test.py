# A file to implement and test the functions that have 
# been written until now.

from jaggpy.classes import Scenario

scenario1 = Scenario()

relativeFilePath = r"./test/testfiles/scenario1.jagg"
absoluteFilePath = r"/Users/Bo/Documents/MoL/jaggpy/src/test/testfiles/scenario1.jagg"

scenario1.loadFromFile(relativeFilePath)

scenario1.prettyPrint()