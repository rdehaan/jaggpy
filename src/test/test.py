#############################################################################
# A file to implement and test the functions that have
# been written until now.
# To test this file, run "python3 -m unittest test.test" in the terminal.
#############################################################################

from jaggpy.classes import Scenario
from jaggpy.bf_solver import BFSolver
from jaggpy.asp_solver import ASPSolver

scenario1 = Scenario()
RELATIVE_FILE_PATH = "./test/testfiles/scenario1.jagg"
scenario1.load_from_file(RELATIVE_FILE_PATH)

scenario2 = Scenario()
RELATIVE_FILE_PATH2 = "./test/testfiles/scenario2.jagg"
scenario2.load_from_file(RELATIVE_FILE_PATH2)

scenario3 = Scenario()
RELATIVE_FILE_PATH3 = "./test/testfiles/scenario3.jagg"
scenario3.load_from_file(RELATIVE_FILE_PATH3)

scenario4 = Scenario()
RELATIVE_FILE_PATH4 = "./test/testfiles/scenario4.jagg"
scenario4.load_from_file(RELATIVE_FILE_PATH4)

scenario5 = Scenario()
RELATIVE_FILE_PATH5 = "./test/testfiles/scenario5.jagg"
scenario5.load_from_file(RELATIVE_FILE_PATH5)

scenario6 = Scenario()
RELATIVE_FILE_PATH6 = "./test/testfiles/scenario6.jagg"
scenario6.load_from_file(RELATIVE_FILE_PATH6)

scenario7 = Scenario()
RELATIVE_FILE_PATH7 = "./test/testfiles/scenario7.jagg"
scenario7.load_from_file(RELATIVE_FILE_PATH7)

scenario8 = Scenario()
RELATIVE_FILE_PATH8 = "./test/testfiles/scenario8.jagg"
scenario8.load_from_file(RELATIVE_FILE_PATH8)

brutus = BFSolver()

brutus.enumerate_outcomes(scenario1, "kemeny")
brutus.enumerate_outcomes(scenario1, "slater")
brutus.enumerate_outcomes(scenario2, "kemeny")
brutus.enumerate_outcomes(scenario2, "slater")
brutus.enumerate_outcomes(scenario3, "kemeny")
brutus.enumerate_outcomes(scenario3, "slater")
brutus.enumerate_outcomes(scenario4, "kemeny")
brutus.enumerate_outcomes(scenario4, "slater")
brutus.enumerate_outcomes(scenario5, "kemeny")
brutus.enumerate_outcomes(scenario5, "slater")
brutus.enumerate_outcomes(scenario6, "kemeny")

asp = ASPSolver()

asp.enumerate_outcomes(scenario1, "leximax")
asp.enumerate_outcomes(scenario1, "young")
asp.enumerate_first_n_outcomes(scenario1, "young", True, n=5)


asp.enumerate_outcomes(scenario2, "kemeny")
asp.enumerate_outcomes(scenario2, "leximax")
asp.enumerate_outcomes(scenario2, "young")
asp.enumerate_outcomes(scenario2, "slater")
asp.enumerate_outcomes(scenario2, "majority")

asp.enumerate_outcomes(scenario3, "kemeny")
asp.enumerate_outcomes(scenario3, "slater")

asp.enumerate_outcomes(scenario4, "kemeny")
asp.enumerate_outcomes(scenario4, "slater")

asp.enumerate_outcomes(scenario5, "kemeny")
asp.enumerate_outcomes(scenario5, "slater")

asp.enumerate_outcomes(scenario5, "kemeny")
asp.enumerate_outcomes(scenario5, "slater")

brutus.enumerate_outcomes(scenario6, "kemeny")
asp.enumerate_outcomes(scenario6, "kemeny")
brutus.enumerate_outcomes(scenario6, "slater")
asp.enumerate_outcomes(scenario6, "slater")

asp.enumerate_outcomes(scenario8, "kemeny")
asp.enumerate_outcomes(scenario8, "kemeny")

scenario1.pretty_repr()
