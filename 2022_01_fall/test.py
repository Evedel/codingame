from unittest.mock import MagicMock
from bot import PathSearcher, GameLogic, Unit, EntityType, Cell, InputHandler
import copy
import unittest


class TestPathSearcher(unittest.TestCase):
    def __get_empty_map(self):
        map = []
        for i in range(0, 7):
            map.append([])
            for j in range(0, 13):
                map[i].append(
                    Cell(
                        entity=EntityType.Empty,
                    )
                )
        return map

    def __get_map_case_01(self):
        map = self.__get_empty_map()
        map[1][3].entity = EntityType.Wall
        map[1][9].entity = EntityType.Wall
        map[2][0].entity = EntityType.Wall
        map[2][1].entity = EntityType.Wall
        map[2][2].entity = EntityType.Wall
        map[2][10].entity = EntityType.Wall
        map[2][11].entity = EntityType.Wall
        map[2][12].entity = EntityType.Wall
        map[4][4].entity = EntityType.Wall
        map[4][5].entity = EntityType.Wall
        map[4][7].entity = EntityType.Wall
        map[4][8].entity = EntityType.Wall
        map[5][0].entity = EntityType.Wall
        map[5][2].entity = EntityType.Wall
        map[5][10].entity = EntityType.Wall
        map[5][12].entity = EntityType.Wall
        return map

    def __add_units_to_map_case_01(self, map):
        res = copy.deepcopy(map)
        res[3][0].entity = EntityType.MyLeader
        res[3][12].entity = EntityType.EnLeader
        res[1][1].entity = EntityType.Neutral
        res[1][2].entity = EntityType.Neutral
        res[3][3].entity = EntityType.Neutral
        res[5][1].entity = EntityType.Neutral
        res[5][3].entity = EntityType.Neutral
        res[6][2].entity = EntityType.Neutral
        res[1][11].entity = EntityType.Neutral
        res[1][10].entity = EntityType.Neutral
        res[3][9].entity = EntityType.Neutral
        res[5][11].entity = EntityType.Neutral
        res[5][9].entity = EntityType.Neutral
        res[6][10].entity = EntityType.Neutral
        return res

    def __get_units_case_01(self):
        units = []
        units.append(Unit(0, EntityType.MyLeader, 0, 3))
        units.append(Unit(1, EntityType.EnLeader, 12, 3))
        units.append(Unit(2, EntityType.Neutral, 1, 1))
        units.append(Unit(3, EntityType.Neutral, 2, 1))
        units.append(Unit(4, EntityType.Neutral, 3, 3))
        units.append(Unit(5, EntityType.Neutral, 1, 5))
        units.append(Unit(6, EntityType.Neutral, 3, 5))
        units.append(Unit(7, EntityType.Neutral, 2, 6))
        units.append(Unit(8, EntityType.Neutral, 11, 1))
        units.append(Unit(9, EntityType.Neutral, 10, 1))
        units.append(Unit(10, EntityType.Neutral, 9, 3))
        units.append(Unit(11, EntityType.Neutral, 11, 5))
        units.append(Unit(12, EntityType.Neutral, 9, 5))
        units.append(Unit(13, EntityType.Neutral, 10, 6))
        return units

    def __run_turn(self, input_lines: list[str]):
        input = MagicMock()
        input.side_effect = input_lines

        map: list[list[Cell]] = []
        units: list[Unit] = []

        ih = InputHandler(input=input)

        map = ih.read_initial_input(map)
        map, units = ih.read_turn_input(map, units, map)
        gl = GameLogic()
        command = gl.make_turn(units, map)
        return command

    def test_get_possible_moves_center(self):
        ps = PathSearcher()
        map = self.__get_empty_map()

        moves = ps.get_possible_moves(1, 1, map)
        self.assertEqual(moves, [(0, 1), (2, 1), (1, 0), (1, 2)])

    def test_get_possible_moves_top_corner(self):
        ps = PathSearcher()
        map = self.__get_empty_map()
        moves = ps.get_possible_moves(0, 0, map)
        self.assertEqual(moves, [(1, 0), (0, 1)])

    def test_get_possible_moves_bottom_corner(self):
        ps = PathSearcher()
        map = self.__get_empty_map()
        moves = ps.get_possible_moves(12, 6, map)
        self.assertEqual(moves, [(11, 6), (12, 5)])

    def test_get_possible_moves_bottom_edge(self):
        ps = PathSearcher()
        map = self.__get_empty_map()
        moves = ps.get_possible_moves(0, 1, map)
        self.assertEqual(moves, [(1, 1), (0, 0), (0, 2)])

    def test_get_possible_moves_bottom_edge_with_obsticles(self):
        ps = PathSearcher()
        map = self.__get_empty_map()
        map[0][0].entity = EntityType.MyLeader
        map[2][0].entity = EntityType.EnWarior
        moves = ps.get_possible_moves(0, 1, map)
        self.assertEqual(moves, [(1, 1)])

    def test_path_search_09(self):
        ps = PathSearcher()
        map = self.__get_empty_map()
        map[0][0].entity = EntityType.MyLeader
        map[2][2].entity = EntityType.Neutral
        path = ps.path_search(0, 0, 2, 2, map, EntityType.Neutral)
        self.assertEqual(path.path, [(0, 0), (1, 0), (1, 1), (2, 1), (2, 2)])

    def test_path_search_10(self):
        ps = PathSearcher()
        map = self.__get_empty_map()
        path = ps.path_search(0, 0, 0, 2, map)
        self.assertEqual(path.path, [(0, 0), (0, 1), (0, 2)])

    def test_path_search_11(self):
        ps = PathSearcher()
        map = self.__get_empty_map()
        path = ps.path_search(0, 0, 12, 0, map)
        self.assertEqual(
            path.path,
            [
                (0, 0),
                (1, 0),
                (2, 0),
                (3, 0),
                (4, 0),
                (5, 0),
                (6, 0),
                (7, 0),
                (8, 0),
                (9, 0),
                (10, 0),
                (11, 0),
                (12, 0),
            ],
        )

    def test_path_search_12(self):
        ps = PathSearcher()
        map = self.__get_empty_map()
        path = ps.path_search(0, 0, 12, 6, map)
        self.assertEqual(
            path.path,
            [
                (0, 0),
                (1, 0),
                (2, 0),
                (3, 0),
                (4, 0),
                (5, 0),
                (6, 0),
                (7, 0),
                (7, 1),
                (8, 1),
                (8, 2),
                (9, 2),
                (9, 3),
                (10, 3),
                (10, 4),
                (11, 4),
                (11, 5),
                (12, 5),
                (12, 6),
            ],
        )

    def test_path_search_13(self):
        ps = PathSearcher()
        map = self.__get_empty_map()
        for i in range(0, 5):
            map[i][6].entity = EntityType.Wall
        path = ps.path_search(0, 0, 12, 6, map)
        self.assertEqual(
            path.path,
            [
                (0, 0),
                (1, 0),
                (2, 0),
                (3, 0),
                (4, 0),
                (5, 0),
                (5, 1),
                (5, 2),
                (5, 3),
                (5, 4),
                (5, 5),
                (6, 5),
                (7, 5),
                (8, 5),
                (9, 5),
                (10, 5),
                (11, 5),
                (12, 5),
                (12, 6),
            ],
        )

    def test_game_logic_00(self):
        units = []
        units.extend(
            [
                Unit(
                    id=0,
                    type=EntityType.MyLeader,
                    pos_x=0,
                    pos_y=0,
                ),
                Unit(
                    id=1,
                    type=EntityType.Neutral,
                    pos_x=1,
                    pos_y=1,
                ),
            ]
        )

        gl = GameLogic()
        nn = gl.find_nearest_neutral(units[0], units)
        self.assertEqual(nn, units[1])

    def test_game_logic_01(self):
        units = []
        units.extend(
            [
                Unit(
                    type=EntityType.MyLeader,
                    pos_x=0,
                    pos_y=0,
                ),
                Unit(
                    type=EntityType.EnWarior,
                    pos_x=1,
                    pos_y=1,
                ),
            ]
        )

        gl = GameLogic()
        nn = gl.find_nearest_neutral(units[0], units)
        self.assertEqual(nn, None)

    def test_game_logic_01(self):
        units = []
        units.append(
            Unit(
                id=0,
                type=EntityType.MyLeader,
                pos_x=0,
                pos_y=0,
            )
        )
        for i in range(5, 1, -1):
            units.append(
                Unit(
                    id=i,
                    type=EntityType.Neutral,
                    pos_x=i,
                    pos_y=i,
                )
            )

        gl = GameLogic()
        nn = gl.find_nearest_neutral(units[0], units)
        self.assertEqual(nn, units[-1])

    def test_game_logic_02(self):
        units = []
        map = self.__get_empty_map()
        units.append(
            Unit(
                id=0,
                type=EntityType.MyLeader,
                pos_x=0,
                pos_y=0,
            )
        )
        map[0][0].entity = EntityType.MyLeader
        for i in range(5, 1, -1):
            units.append(
                Unit(
                    id=i,
                    type=EntityType.Neutral,
                    pos_x=i,
                    pos_y=i,
                )
            )
            map[i][i].entity = EntityType.Neutral

        gl = GameLogic()
        command = gl.convert_nuetral(units, map)
        self.assertEqual(command, "0 MOVE 1 0")

    def test_game_logic_03(self):
        units = []
        map = self.__get_empty_map()
        units.append(
            Unit(
                id=0,
                type=EntityType.MyLeader,
                pos_x=1,
                pos_y=2,
            )
        )
        map[1][2].entity = EntityType.MyLeader
        for i in range(5, 1, -1):
            units.append(
                Unit(
                    id=i,
                    type=EntityType.Neutral,
                    pos_x=i,
                    pos_y=i,
                )
            )
            map[i][i].entity = EntityType.Neutral

        gl = GameLogic()
        command = gl.convert_nuetral(units, map)
        self.assertEqual(command, "0 CONVERT 2")

    def test_read_initial_input(self):
        res = [
            "0",
            "13 7",
            ".............",
            "...x.....x...",
            "xxx.......xxx",
            ".............",
            "....xx.xx....",
            "x.x.......x.x",
            ".............",
        ]
        input = MagicMock()
        input.side_effect = res

        map_expected = self.__get_map_case_01()

        map: list[list[Cell]] = []
        ih = InputHandler(input=input)
        map = ih.read_initial_input(map)

        for i in range(0, 7):
            for j in range(0, 13):
                self.assertEqual(map_expected[i][j], map[i][j], f"{i} {j}")

    def test_read_turn_input(self):
        res = [
            "14",
            "0 1 10 0 3 0",
            "1 1 10 12 3 1",
            "2 0 10 1 1 2",
            "3 0 10 2 1 2",
            "4 0 10 3 3 2",
            "5 0 10 1 5 2",
            "6 0 10 3 5 2",
            "7 0 10 2 6 2",
            "8 0 10 11 1 2",
            "9 0 10 10 1 2",
            "10 0 10 9 3 2",
            "11 0 10 11 5 2",
            "12 0 10 9 5 2",
            "13 0 10 10 6 2",
        ]
        input = MagicMock()
        input.side_effect = res

        map0: list[list[Cell]] = []
        map: list[list[Cell]] = []
        units: list[Unit] = []

        ih = InputHandler(input=input)
        map0 = self.__get_empty_map()
        map_expected = self.__add_units_to_map_case_01(map0)
        units_expected = self.__get_units_case_01()
        map, units = ih.read_turn_input(map, units, map0)

        for i in range(0, 7):
            for j in range(0, 13):
                self.assertEqual(map_expected[i][j], map[i][j], f"{i} {j}")
        for i in range(0, 14):
            self.assertEqual(units_expected[i], units[i], f"{i} {j}")

    def test_full_case_01_01(self):
        ih = InputHandler()
        map0 = self.__get_map_case_01()
        map0 = self.__add_units_to_map_case_01(map0)
        units = self.__get_units_case_01()
        gl = GameLogic()
        command = gl.make_turn(units, map0)
        self.assertEqual(command, "0 MOVE 0 4")

    def test_full_case_01_02(self):
        ih = InputHandler()
        map0 = self.__get_map_case_01()
        map0 = self.__add_units_to_map_case_01(map0)
        map0[1][4].entity = EntityType.MyLeader
        map0[0][3].entity = EntityType.Empty
        units = self.__get_units_case_01()
        units[0].pos_x = 1
        units[0].pos_y = 4
        gl = GameLogic()
        command = gl.make_turn(units, map0)
        self.assertEqual(command, "0 CONVERT 5")

    def test_full_case_02(self):
        # when pathes are too long -> code is infinitely slow
        init = [
            "0",
            "13 7",
            "x...........x",
            "x....x.x....x",
            "...x.x.x.x...",
            ".xx.......xx.",
            ".............",
            ".............",
            "...x.x.x.x...",
        ]
        turn = [
            "14",
            "0 1 10 0 3 0",
            "1 1 10 12 3 1",
            "2 0 10 4 1 2",
            "3 0 10 4 0 2",
            "4 0 10 1 2 2",
            "5 0 10 4 5 2",
            "6 0 10 2 6 2",
            "7 0 10 3 1 2",
            "8 0 10 8 1 2",
            "9 0 10 8 0 2",
            "10 0 10 11 2 2",
            "11 0 10 8 5 2",
            "12 0 10 10 6 2",
            "13 0 10 9 1 2",
        ]

        command = self.__run_turn(init + turn)

        self.assertEqual(command, "0 MOVE 0 2")

    def test_full_case_03(self):
        init = [
            "0",
            "13 7",
            "x...........x",
            "x....x.x....x",
            "...x.x.x.x...",
            ".xx.......xx.",
            ".............",
            ".............",
            "...x.x.x.x...",
        ]
        turn = [
            "14",
            "0 1 10 2 4 0",
            "1 1 10 10 5 1",
            "2 0 10 4 1 2",
            "3 0 10 4 0 2",
            "4 0 10 1 2 0",
            "5 0 10 3 4 0",
            "6 0 10 2 6 2",
            "7 0 10 2 0 2",
            "8 0 10 8 2 2",
            "9 0 10 8 0 2",
            "10 0 10 11 0 2",
            "11 0 10 8 5 2",
            "12 0 10 10 6 1",
            "13 0 10 9 1 2",
        ]

        command = self.__run_turn(init + turn)
        self.assertEqual(command, "5 MOVE 4 4")

    def test_full_case_03(self):
        init = [
            "0",
            "13 7",
            "x...........x",
            "x....x.x....x",
            "...x.x.x.x...",
            ".xx.......xx.",
            ".............",
            ".............",
            "...x.x.x.x...",
        ]
        turn = [
            "14",
            "0 1 10 2 4 0",
            "1 1 10 9 5 1",
            "2 0 10 4 1 2",
            "3 0 10 4 0 2",
            "4 0 10 1 2 0",
            "5 0 10 5 4 0",
            "6 0 10 2 6 2",
            "7 0 10 2 0 2",
            "8 0 10 8 2 2",
            "9 0 10 8 0 2",
            "10 0 10 9 0 2",
            "11 0 10 8 5 1",
            "12 0 10 10 6 1",
            "13 0 10 9 1 2",
        ]

        command = self.__run_turn(init + turn)
        self.assertEqual(command, "5 SHOOT 11")


if __name__ == "__main__":
    unittest.main()
