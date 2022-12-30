#!/usr/bin/env python3

import random
from unittest.mock import MagicMock

from inputs import Inputs
from bot import GameLogic, InputHandler, StrategyDefault, ZoneType
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
        gl.preprocess()
        self.assertEqual(1, len(gl.zones))
        self.assertEqual(1, len(gl.zones[0].cells))
        self.assertEqual(1, gl.zones[0].cells[0].x)
        self.assertEqual(1, gl.zones[0].cells[0].y)

    def test_zone_detection_i2(self):
        inputs = Inputs()
        lines = inputs.zone_i2
        gl = self.__get_gl_from_input_w_default_strategy(lines)
        gl.preprocess()
        self.assertEqual(1, len(gl.zones))
        self.assertEqual(1, len(gl.zones[0].cells))
        self.assertEqual(0, gl.zones[0].cells[0].x)
        self.assertEqual(0, gl.zones[0].cells[0].y)

    def test_zone_detection_i3(self):
        inputs = Inputs()
        lines = inputs.zone_i3
        gl = self.__get_gl_from_input_w_default_strategy(lines)
        gl.preprocess()
        self.assertEqual(1, len(gl.zones))
        self.assertEqual(1, len(gl.zones[0].cells))
        self.assertEqual(2, gl.zones[0].cells[0].x)
        self.assertEqual(2, gl.zones[0].cells[0].y)

    def test_zone_detection_i4(self):
        inputs = Inputs()
        lines = inputs.zone_i4
        gl = self.__get_gl_from_input_w_default_strategy(lines)
        gl.preprocess()
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
        gl.preprocess()
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
        gl.preprocess()
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
        gl.preprocess()
        self.assertEqual(3, len(gl.zones))
        self.assertEqual(134, len(gl.zones[0].cells))
        self.assertEqual(1, len(gl.zones[1].cells))
        self.assertEqual(1, len(gl.zones[2].cells))

    def test_zone_detection_i7(self):
        # recycler devides zones
        inputs = Inputs()
        lines = inputs.zone_i7
        gl = self.__get_gl_from_input_w_default_strategy(lines)
        gl.preprocess()
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
        gl.preprocess()
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
        gl.preprocess()
        builds = gl.get_builds()
        self.assertEqual(["BUILD 3 4"], builds)

    def test_no_useless_spawns(self):
        inputs = Inputs()
        lines = inputs.no_useless_spawns
        gl = self.__get_gl_from_input_w_default_strategy(lines)
        gl.preprocess()
        spawns = gl.get_spawns()
        self.assertEqual(
            ["SPAWN 1 0 4", "SPAWN 9 3 4"],
            spawns,
        )

    def test_no_spawns_when_there_are_no_money(self):
        inputs = Inputs()
        lines = inputs.no_useless_spawns
        gl = self.__get_gl_from_input_w_default_strategy(lines)
        gl.preprocess()
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
        gl.preprocess()
        gl.my_matter = 11
        spawns = gl.get_spawns()
        self.assertEqual(
            ["SPAWN 1 0 4"],
            spawns,
        )

    def test_no_spawns_when_zone_is_going_to_be_destroyed_1(self):
        inputs = Inputs()
        lines = inputs.not_spawn_on_zones_that_are_going_to_be_destroyed_1
        gl = self.__get_gl_from_input_w_default_strategy(lines)
        gl.preprocess()
        gl.my_matter = 10
        spawns = gl.get_spawns()
        self.assertEqual(
            ["SPAWN 1 1 0"],
            spawns,
        )

    def test_no_spawns_when_zone_is_going_to_be_destroyed_2(self):
        inputs = Inputs()
        lines = inputs.not_spawn_on_zones_that_are_going_to_be_destroyed_2
        gl = self.__get_gl_from_input_w_default_strategy(lines)
        gl.preprocess()
        spawns = gl.get_spawns()
        self.assertEqual(
            ["SPAWN 1 1 2"],
            spawns,
        )

    def test_spawn_only_in_contact_zones_1(self):
        inputs = Inputs()
        lines = inputs.spawn_only_in_contact_zones_1
        gl = self.__get_gl_from_input_w_default_strategy(lines)
        gl.preprocess()
        spawns = gl.get_spawns()
        self.assertEqual(
            ["SPAWN 1 2 1", "SPAWN 1 0 1"],
            spawns,
        )

    def test_spawn_only_in_contact_zones_2(self):
        inputs = Inputs()
        lines = inputs.spawn_only_in_contact_zones_2
        gl = self.__get_gl_from_input_w_default_strategy(lines)
        gl.preprocess()
        spawns = gl.get_spawns()
        self.assertEqual(
            ["SPAWN 1 2 1", "SPAWN 1 0 1"],
            spawns,
        )

    def test_game_logic_deepcopy_not_affecting_original(self):
        inputs = Inputs()
        lines = inputs.smart_builds_1
        gl = self.__get_gl_from_input_w_default_strategy(lines)

        gl.preprocess()
        gl_copy = gl.deepcopy()

        gl.my_matter = 10
        gl_copy.my_matter = 0
        self.assertEqual(10, gl.my_matter)
        self.assertEqual(0, gl_copy.my_matter)

        gl.map.cells[0][0].scrap_amount = 10
        gl_copy.map.cells[0][0].scrap_amount = 0
        self.assertEqual(10, gl.map.cells[0][0].scrap_amount)
        self.assertEqual(0, gl_copy.map.cells[0][0].scrap_amount)

        gl.map.cells[1][0].scrap_amount = -1
        gl.map.cells[0][0].n_d.scrap_amount = 10
        gl_copy.map.cells[1][0].scrap_amount = -1
        gl_copy.map.cells[0][0].n_d.scrap_amount = 0
        self.assertEqual(10, gl.map.cells[0][0].n_d.scrap_amount)
        self.assertEqual(0, gl_copy.map.cells[0][0].n_d.scrap_amount)
        self.assertEqual(10, gl.map.cells[1][0].scrap_amount)
        self.assertEqual(0, gl_copy.map.cells[1][0].scrap_amount)

        gl.map.cells[0][0].n_r.scrap_amount = -1  # to clean before the next line
        gl.map.cells[0][1].scrap_amount = 10
        gl_copy.map.cells[0][0].n_r.scrap_amount = -1
        gl_copy.map.cells[0][1].scrap_amount = 0
        self.assertEqual(10, gl.map.cells[0][0].n_r.scrap_amount)
        self.assertEqual(0, gl_copy.map.cells[0][0].n_r.scrap_amount)

    def test_check_zone_split_effect_1(self):
        inputs = Inputs()
        lines = inputs.smart_builds_1
        gl = self.__get_gl_from_input_w_default_strategy(lines)
        gl.preprocess()
        new_zones = gl.check_zones_if_built(gl.map.cell(2, 0))
        self.assertEqual(2, len(new_zones))
        self.assertEqual(1, len(new_zones[0].cells))
        self.assertEqual(ZoneType.Unreachable, new_zones[0].type)
        self.assertEqual(7, len(new_zones[1].cells))
        self.assertEqual(ZoneType.FightInProgress, new_zones[1].type)

        self.assertEqual(1, len(gl.zones))
        self.assertEqual(ZoneType.FightInProgress, gl.zones[0].type)

    def test_check_zone_split_effect_2(self):
        inputs = Inputs()
        lines = inputs.smart_builds_1
        gl = self.__get_gl_from_input_w_default_strategy(lines)
        gl.preprocess()
        new_zones = gl.check_zones_if_built(gl.map.cell(4, 2))
        self.assertEqual(2, len(new_zones))
        self.assertEqual(5, len(new_zones[0].cells))
        self.assertEqual(ZoneType.GuaranteedMy, new_zones[0].type)
        self.assertEqual(3, len(new_zones[1].cells))
        self.assertEqual(ZoneType.GuaranteedEn, new_zones[1].type)

        self.assertEqual(1, len(gl.zones))
        self.assertEqual(ZoneType.FightInProgress, gl.zones[0].type)

    def test_smart_builds_1(self):
        inputs = Inputs()
        lines = inputs.smart_builds_1
        gl = self.__get_gl_from_input_w_default_strategy(lines)
        gl.preprocess()
        builds = gl.get_builds()
        self.assertEqual(
            [],
            builds,
        )


# TODO:
# - spawns:
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
