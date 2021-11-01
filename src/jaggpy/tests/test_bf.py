"""Unit tests for BFSolver."""

import unittest
import os
from jaggpy import Scenario, BFSolver

class TestBFSolverScenario1(unittest.TestCase):
    """Test the brute force solver."""

    def __init__(self, *args, **kwargs):
        """Load scenario1.jagg and create solver."""
        super().__init__(*args, **kwargs)

        # Load scenario1.jagg from test files
        current_dir = os.path.dirname(__file__)
        file_path = os.sep.join([current_dir, "files/scenario1.jagg"])
        self.scenario = Scenario()
        self.scenario.load_from_file(file_path)

        # Create solver
        self.solver = BFSolver()

    def test_kemeny(self):
        """Test Kemeny brute force solver with scenario1.jagg."""
        outcomes = list(self.solver.all_outcomes(self.scenario, "kemeny"))
        self.assertEqual(
            len(outcomes), 1,
            "Incorrect number of outcomes (BFSolver, Kemeny, scenario1.jagg)"
        )

    def test_slater(self):
        """Test Slater brute force solver with scenario1.jagg."""
        outcomes = list(self.solver.all_outcomes(self.scenario, "slater"))
        self.assertEqual(
            len(outcomes), 2,
            "Incorrect number of outcomes (BFSolver, Slater, scenario1.jagg)"
        )

    def test_maxhamming(self):
        """Test Max-Hamming brute force solver with scenario1.jagg."""
        outcomes = list(self.solver.all_outcomes(self.scenario, "maxhamming"))
        self.assertEqual(
            len(outcomes), 9,
            "Incorrect number of outcomes " + \
            "(BFSolver, Max-Hamming, scenario1.jagg)"
        )
