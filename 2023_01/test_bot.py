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
        lines = inputs.I_00
        inputs.generate_I_00_expected_map()
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


if __name__ == "__main__":
    random.seed(89819011)
    unittest.main()
