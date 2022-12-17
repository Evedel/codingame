#!/usr/bin/env python3

from unittest.mock import MagicMock

from z_2022_02.inputs import Inputs
from z_2022_02.bot import GameLogic, InputHandler
import unittest


class TestBot(unittest.TestCase):
    def test_read_initial_input(self):
        inputs = Inputs()
        lines = inputs.I1
        map = inputs.I1_MAP

        input = MagicMock()
        input.side_effect = lines

        ih = InputHandler(input=input)
        gl = GameLogic()
        gl = ih.read_initial_input(gl)
        gl = ih.read_turn_input(gl)

        for i in range(gl.height):
            for j in range(gl.width):
                self.assertTrue(
                    gl.map.cells[i][j].same(map.cells[i][j]),
                    f"{i} {j} {gl.map.cells[i][j]} {map.cells[i][j]}",
                )

    def __get_gl_from_input(self, input_lines: list[str]):
        input = MagicMock()
        input.side_effect = input_lines

        ih = InputHandler(input=input)
        gl = GameLogic()
        gl = ih.read_initial_input(gl)
        gl = ih.read_turn_input(gl)

        return gl

    def test_zone_detection_i1(self):
        inputs = Inputs()
        lines = inputs.zone_i1
        gl = self.__get_gl_from_input(lines)
        gl.detect_zones()
        self.assertEqual(1, len(gl.zones))
        self.assertEqual(1, len(gl.zones[0].cells))
        self.assertEqual(1, gl.zones[0].cells[0].x)
        self.assertEqual(1, gl.zones[0].cells[0].y)

    def test_zone_detection_i2(self):
        inputs = Inputs()
        lines = inputs.zone_i2
        gl = self.__get_gl_from_input(lines)
        gl.detect_zones()
        self.assertEqual(1, len(gl.zones))
        self.assertEqual(1, len(gl.zones[0].cells))
        self.assertEqual(0, gl.zones[0].cells[0].x)
        self.assertEqual(0, gl.zones[0].cells[0].y)

    def test_zone_detection_i3(self):
        inputs = Inputs()
        lines = inputs.zone_i3
        gl = self.__get_gl_from_input(lines)
        gl.detect_zones()
        self.assertEqual(1, len(gl.zones))
        self.assertEqual(1, len(gl.zones[0].cells))
        self.assertEqual(2, gl.zones[0].cells[0].x)
        self.assertEqual(2, gl.zones[0].cells[0].y)

    def test_zone_detection_i4(self):
        inputs = Inputs()
        lines = inputs.zone_i4
        gl = self.__get_gl_from_input(lines)
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
        gl = self.__get_gl_from_input(lines)
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
        gl = self.__get_gl_from_input(lines)
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
        gl = self.__get_gl_from_input(lines)
        gl.detect_zones()
        self.assertEqual(3, len(gl.zones))
        self.assertEqual(134, len(gl.zones[0].cells))
        self.assertEqual(1, len(gl.zones[1].cells))
        self.assertEqual(1, len(gl.zones[2].cells))

    def test_zone_detection_i7(self):
        # recycler devides zones
        inputs = Inputs()
        lines = inputs.zone_i7
        gl = self.__get_gl_from_input(lines)
        gl.detect_zones()
        self.assertEqual(2, len(gl.zones))
        self.assertEqual(1, len(gl.zones[0].cells))
        self.assertEqual(1, len(gl.zones[1].cells))
        self.assertEqual(1, gl.zones[0].cells[0].x)
        self.assertEqual(0, gl.zones[0].cells[0].y)
        self.assertEqual(1, gl.zones[1].cells[0].x)
        self.assertEqual(2, gl.zones[1].cells[0].y)


# TODO:
# [ ] do not place recyclers in owned zones

if __name__ == "__main__":
    unittest.main()
