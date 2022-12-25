#!/usr/bin/env python3

import random
from unittest.mock import MagicMock

from z_2022_02.inputs import Inputs
from z_2022_02.bot import GameLogic, InputHandler, StrategyDefault, ZoneType
import unittest


class TestBot(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        random.seed(18081991)

    def test_read_initial_input(self):
        inputs = Inputs()
        lines = inputs.I1
        map = inputs.I1_MAP

        input = MagicMock()
        input.side_effect = lines

        ih = InputHandler(input=input)
        gl = GameLogic(StrategyDefault())
        gl = ih.read_initial_input(gl)
        gl = ih.read_turn_input(gl)

        for i in range(gl.height):
            for j in range(gl.width):
                self.assertTrue(
                    gl.map.cells[i][j].same(map.cells[i][j]),
                    f"{i} {j} {gl.map.cells[i][j]} {map.cells[i][j]}",
                )

    def __get_gl_from_input_w_default_strategy(self, input_lines: list[str]):
        input = MagicMock()
        input.side_effect = input_lines

        ih = InputHandler(input=input)
        gl = GameLogic(StrategyDefault())
        gl = ih.read_initial_input(gl)
        gl = ih.read_turn_input(gl)

        return gl

    def test_zone_detection_i1(self):
        inputs = Inputs()
        lines = inputs.zone_i1
        gl = self.__get_gl_from_input_w_default_strategy(lines)
        gl.detect_zones()
        self.assertEqual(1, len(gl.zones))
        self.assertEqual(1, len(gl.zones[0].cells))
        self.assertEqual(1, gl.zones[0].cells[0].x)
        self.assertEqual(1, gl.zones[0].cells[0].y)

    def test_zone_detection_i2(self):
        inputs = Inputs()
        lines = inputs.zone_i2
        gl = self.__get_gl_from_input_w_default_strategy(lines)
        gl.detect_zones()
        self.assertEqual(1, len(gl.zones))
        self.assertEqual(1, len(gl.zones[0].cells))
        self.assertEqual(0, gl.zones[0].cells[0].x)
        self.assertEqual(0, gl.zones[0].cells[0].y)

    def test_zone_detection_i3(self):
        inputs = Inputs()
        lines = inputs.zone_i3
        gl = self.__get_gl_from_input_w_default_strategy(lines)
        gl.detect_zones()
        self.assertEqual(1, len(gl.zones))
        self.assertEqual(1, len(gl.zones[0].cells))
        self.assertEqual(2, gl.zones[0].cells[0].x)
        self.assertEqual(2, gl.zones[0].cells[0].y)

    def test_zone_detection_i4(self):
        inputs = Inputs()
        lines = inputs.zone_i4
        gl = self.__get_gl_from_input_w_default_strategy(lines)
        gl.detect_zones()
        self.assertEqual(1, len(gl.zones))
        self.assertEqual(3, len(gl.zones[0].cells))
        self.assertEqual(0, gl.zones[0].cells[0].x)
        self.assertEqual(2, gl.zones[0].cells[0].y)
        self.assertEqual(1, gl.zones[0].cells[1].x)
        self.assertEqual(2, gl.zones[0].cells[1].y)
        self.assertEqual(2, gl.zones[0].cells[2].x)
        self.assertEqual(2, gl.zones[0].cells[2].y)

    def test_zone_detection_i5(self):
        inputs = Inputs()
        lines = inputs.zone_i5
        gl = self.__get_gl_from_input_w_default_strategy(lines)
        gl.detect_zones()
        self.assertEqual(1, len(gl.zones))
        self.assertEqual(3, len(gl.zones[0].cells))
        self.assertEqual(0, gl.zones[0].cells[0].x)
        self.assertEqual(0, gl.zones[0].cells[0].y)
        self.assertEqual(0, gl.zones[0].cells[1].x)
        self.assertEqual(1, gl.zones[0].cells[1].y)
        self.assertEqual(0, gl.zones[0].cells[2].x)
        self.assertEqual(2, gl.zones[0].cells[2].y)

    def test_zone_detection_i6(self):
        inputs = Inputs()
        lines = inputs.zone_i6
        gl = self.__get_gl_from_input_w_default_strategy(lines)
        gl.detect_zones()
        self.assertEqual(3, len(gl.zones))
        self.assertEqual(1, len(gl.zones[0].cells))
        self.assertEqual(1, len(gl.zones[1].cells))
        self.assertEqual(1, len(gl.zones[2].cells))
        self.assertEqual(0, gl.zones[0].cells[0].x)
        self.assertEqual(0, gl.zones[0].cells[0].y)
        self.assertEqual(1, gl.zones[1].cells[0].x)
        self.assertEqual(1, gl.zones[1].cells[0].y)
        self.assertEqual(2, gl.zones[2].cells[0].x)
        self.assertEqual(2, gl.zones[2].cells[0].y)

    def test_zone_detection_real_i1(self):
        inputs = Inputs()
        lines = inputs.I1
        gl = self.__get_gl_from_input_w_default_strategy(lines)
        gl.detect_zones()
        self.assertEqual(3, len(gl.zones))
        self.assertEqual(134, len(gl.zones[0].cells))
        self.assertEqual(1, len(gl.zones[1].cells))
        self.assertEqual(1, len(gl.zones[2].cells))

    def test_zone_detection_i7(self):
        # recycler devides zones
        inputs = Inputs()
        lines = inputs.zone_i7
        gl = self.__get_gl_from_input_w_default_strategy(lines)
        gl.detect_zones()
        self.assertEqual(2, len(gl.zones))
        self.assertEqual(1, len(gl.zones[0].cells))
        self.assertEqual(1, len(gl.zones[1].cells))
        self.assertEqual(1, gl.zones[0].cells[0].x)
        self.assertEqual(0, gl.zones[0].cells[0].y)
        self.assertEqual(1, gl.zones[1].cells[0].x)
        self.assertEqual(2, gl.zones[1].cells[0].y)

    def test_zone_detection_types_i1(self):
        inputs = Inputs()
        lines = inputs.zone_types_i1
        gl = self.__get_gl_from_input_w_default_strategy(lines)
        gl.detect_zones()
        self.assertEqual(7, len(gl.zones))
        self.assertEqual(ZoneType.CapturedMy, gl.zones[0].type)
        self.assertEqual(ZoneType.CapturedEn, gl.zones[1].type)
        self.assertEqual(ZoneType.FightInProgress, gl.zones[2].type)
        self.assertEqual(ZoneType.Unreachable, gl.zones[3].type)
        self.assertEqual(ZoneType.GuaranteedEn, gl.zones[4].type)
        self.assertEqual(ZoneType.GuaranteedMy, gl.zones[5].type)
        self.assertEqual(ZoneType.FightInProgress, gl.zones[6].type)

    def test_no_builds_in_captured_zones(self):
        inputs = Inputs()
        lines = inputs.no_builds_in_captured_zones
        gl = self.__get_gl_from_input_w_default_strategy(lines)
        gl.detect_zones()
        builds = gl.get_builds()
        self.assertEqual(["BUILD 3 4"], builds)

    def test_no_useless_spawns(self):
        inputs = Inputs()
        lines = inputs.no_useless_spawns
        gl = self.__get_gl_from_input_w_default_strategy(lines)
        gl.detect_zones()
        spawns = gl.get_spawns()
        self.assertEqual(
            ["SPAWN 2 0 4", "SPAWN 8 3 4"],
            spawns,
        )

    def test_no_spawns_when_there_are_no_money(self):
        inputs = Inputs()
        lines = inputs.no_useless_spawns
        gl = self.__get_gl_from_input_w_default_strategy(lines)
        gl.detect_zones()
        gl.my_matter = 0
        spawns = gl.get_spawns()
        self.assertEqual(
            [],
            spawns,
        )

    def test_no_spawns_when_there_are_no_money_2(self):
        inputs = Inputs()
        lines = inputs.no_useless_spawns
        gl = self.__get_gl_from_input_w_default_strategy(lines)
        gl.detect_zones()
        gl.my_matter = 11
        spawns = gl.get_spawns()
        self.assertEqual(
            ["SPAWN 1 0 3"],
            spawns,
        )


# TODO:
# - spawn bots only:
#   - on border cells
#   - do not spawn bots on the recycler destruction zones
# - bot movement
#   - lots rework needed
#   - move bots to capture cells in the same zone only and more intentionally
#   - move bots out of the recycler destruction zone
# - recyclers
#   - do not place recyclers so that it creates unreachable zones
#   - do not place recyclers in the mid of my zones
#   - need to ensure can spawn more recyclers than enemy
#   - build recyclers to cut off enemy zones
if __name__ == "__main__":
    random.seed(18081991)
    unittest.main()
