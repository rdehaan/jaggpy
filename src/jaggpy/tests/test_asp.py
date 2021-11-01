"""Unit tests for ASPSolver."""

import unittest
import os
from jaggpy import Scenario, ASPSolver

class TestASPSolverScenario1(unittest.TestCase):
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
        self.solver = ASPSolver()

    def test_kemeny(self):
        """Test Kemeny ASP solver with scenario1.jagg."""
        outcomes = list(self.solver.all_outcomes(self.scenario, "kemeny"))
        self.assertEqual(
            len(outcomes), 1,
            "Incorrect number of outcomes (ASPSolver, Kemeny, scenario1.jagg)"
        )

    def test_slater(self):
        """Test Slater ASP solver with scenario1.jagg."""
        outcomes = list(self.solver.all_outcomes(self.scenario, "slater"))
        self.assertEqual(
            len(outcomes), 2,
            "Incorrect number of outcomes (ASPSolver, Slater, scenario1.jagg)"
        )

    def test_young(self):
        """Test Young ASP solver with scenario1.jagg."""
        outcomes = list(self.solver.all_outcomes(self.scenario, "young"))
        self.assertEqual(
            len(outcomes), 4,
            "Incorrect number of outcomes " + \
            "(ASPSolver, Young, scenario1.jagg)"
        )

    def test_leximax(self):
        """Test Leximax ASP solver with scenario1.jagg."""
        outcomes = list(self.solver.all_outcomes(self.scenario, "leximax"))
        self.assertEqual(
            len(outcomes), 1,
            "Incorrect number of outcomes " + \
            "(ASPSolver, Young, scenario1.jagg)"
        )
