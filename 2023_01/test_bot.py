#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# TODO:
import random
import unittest
from unittest.mock import MagicMock

from bot import InputHandler, GameLogic, StrategyDefault
from test_inputs import Inputs


class TestBot(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        random.seed(89819011)

    def test_read_initial_input(self):
        inputs = Inputs()
        lines = inputs.I_000
        inputs.generate_I_000_expected_map()
        map = inputs.I_00_MAP

        input = MagicMock()
        input.side_effect = lines

        ih = InputHandler(input=input)
        gl = GameLogic(StrategyDefault())
        gl = ih.read_initial_input(gl)

        for i in range(gl.map.size):
            self.assertTrue(
                map.cells[i].same(gl.map.cells[i]),
                f"{i} {gl.map.cells[i]} {map.cells[i]}",
            )

    def test_read_turn_input(self):
        inputs = Inputs()
        lines = inputs.I_001
        inputs.generate_I_001_expected_map()
        map = inputs.I_01_MAP

        input = MagicMock()
        input.side_effect = lines

        ih = InputHandler(input=input)
        gl = GameLogic(StrategyDefault())
        gl = ih.read_turn_input(gl)

        for i in range(gl.map.size):
            self.assertTrue(
                map.cells[i].same(gl.map.cells[i]),
                f"{i} {gl.map.cells[i]} {map.cells[i]}",
            )

    def input_mock(self, lines):
        input = MagicMock()
        input.side_effect = lines
        return input

    def test_solve_over_I010(self):
        random.seed(89819011)
        ih = InputHandler()
        ih.input = self.input_mock(Inputs().I_021)
        gl = GameLogic(StrategyDefault())
        gl = ih.read_initial_input(gl)
        gl.Strategy.pre_game()
        ih.input = self.input_mock(Inputs().I_022)
        gl = ih.read_turn_input(gl)

        print()
        gl.map.print_map()
        gl.Strategy.solve()


if __name__ == "__main__":
    random.seed(89819011)
    unittest.main()
