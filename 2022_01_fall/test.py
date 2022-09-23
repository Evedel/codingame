from unittest.mock import MagicMock
from bot import PathSearcher, GameLogic, Unit, UnitType, Cell, InputHandler
import copy
import unittest


class TestPathSearcher(unittest.TestCase):
  def __get_empty_map(self):
    map = []
    for i in range(0, 7):
      map.append([])
      for j in range(0, 13):
        map[i].append(Cell(
          entity=UnitType.Empty,
        ))
    return map

  def __get_map_case_01(self):
    map = self.__get_empty_map()
    map[1][3].entity = UnitType.Wall
    map[1][9].entity = UnitType.Wall
    map[2][0].entity = UnitType.Wall
    map[2][1].entity = UnitType.Wall
    map[2][2].entity = UnitType.Wall
    map[2][10].entity = UnitType.Wall
    map[2][11].entity = UnitType.Wall
    map[2][12].entity = UnitType.Wall
    map[4][4].entity = UnitType.Wall
    map[4][5].entity = UnitType.Wall
    map[4][7].entity = UnitType.Wall
    map[4][8].entity = UnitType.Wall
    map[5][0].entity = UnitType.Wall
    map[5][2].entity = UnitType.Wall
    map[5][10].entity = UnitType.Wall
    map[5][12].entity = UnitType.Wall
    return map

  def __add_units_to_map_case_01(self, map):
    res = copy.deepcopy(map)
    res[3][0].entity = UnitType.MyLeader
    res[3][12].entity = UnitType.EnLeader
    res[1][1].entity = UnitType.Neutral
    res[1][2].entity = UnitType.Neutral
    res[3][3].entity = UnitType.Neutral
    res[5][1].entity = UnitType.Neutral
    res[5][3].entity = UnitType.Neutral
    res[6][2].entity = UnitType.Neutral
    res[1][11].entity = UnitType.Neutral
    res[1][10].entity = UnitType.Neutral
    res[3][9].entity = UnitType.Neutral
    res[5][11].entity = UnitType.Neutral
    res[5][9].entity = UnitType.Neutral
    res[6][10].entity = UnitType.Neutral
    return res

  def __get_units_case_01(self):
    units = []
    units.append(Unit(0, UnitType.MyLeader, 0, 3))
    units.append(Unit(1, UnitType.EnLeader, 12, 3))
    units.append(Unit(2, UnitType.Neutral, 1, 1))
    units.append(Unit(3, UnitType.Neutral, 2, 1))
    units.append(Unit(4, UnitType.Neutral, 3, 3))
    units.append(Unit(5, UnitType.Neutral, 1, 5))
    units.append(Unit(6, UnitType.Neutral, 3, 5))
    units.append(Unit(7, UnitType.Neutral, 2, 6))
    units.append(Unit(8, UnitType.Neutral, 11, 1))
    units.append(Unit(9, UnitType.Neutral, 10, 1))
    units.append(Unit(10, UnitType.Neutral, 9, 3))
    units.append(Unit(11, UnitType.Neutral, 11, 5))
    units.append(Unit(12, UnitType.Neutral, 9, 5))
    units.append(Unit(13, UnitType.Neutral, 10, 6))
    return units

  def test_get_possible_moves_center(self):
    ps = PathSearcher()
    map = self.__get_empty_map()

    moves = ps.get_possible_moves(1, 1, map)
    self.assertEqual(
      moves,
      [(0, 1), (2, 1), (1, 0), (1, 2)]
    )

  def test_get_possible_moves_top_corner(self):
    ps = PathSearcher()
    map = self.__get_empty_map()
    moves = ps.get_possible_moves(0, 0, map)
    self.assertEqual(
      moves,
      [(1, 0), (0, 1)]
    )

  def test_get_possible_moves_bottom_corner(self):
    ps = PathSearcher()
    map = self.__get_empty_map()
    moves = ps.get_possible_moves(12, 6, map)
    self.assertEqual(
      moves,
      [(11, 6), (12, 5)]
    )

  def test_get_possible_moves_bottom_edge(self):
    ps = PathSearcher()
    map = self.__get_empty_map()
    moves = ps.get_possible_moves(0, 1, map)
    self.assertEqual(
      moves, 
      [(1, 1), (0, 0), (0, 2)]
    )

  def test_get_possible_moves_bottom_edge_with_obsticles(self):
    ps = PathSearcher()
    map = self.__get_empty_map()
    map[0][0].entity = UnitType.MyLeader
    map[2][0].entity = UnitType.EnWarior
    moves = ps.get_possible_moves(0, 1, map)
    self.assertEqual(
      moves,
      [(1, 1)]
    )

  def test_path_search_09(self):
    ps = PathSearcher()
    map = self.__get_empty_map()
    map[0][0].entity = UnitType.MyLeader
    map[2][2].entity = UnitType.Neutral
    path = ps.path_search(0, 0, 2, 2, map, UnitType.Neutral)
    self.assertEqual(
      path.path,
      [(0, 0), (1, 0), (1, 1), (2, 1), (2, 2)]
    )

  def test_path_search_10(self):
    ps = PathSearcher()
    map = self.__get_empty_map()
    path = ps.path_search(0, 0, 0, 2, map)
    self.assertEqual(
      path.path,
      [(0, 0), (0, 1), (0, 2)]
    )

  def test_path_search_11(self):
    ps = PathSearcher()
    map = self.__get_empty_map()
    path = ps.path_search(0, 0, 12, 0, map)
    self.assertEqual(
      path.path,
      [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (8, 0), (9, 0), (10, 0), (11, 0), (12, 0)]
    )

  def test_path_search_12(self):
    ps = PathSearcher()
    map = self.__get_empty_map()
    path = ps.path_search(0, 0, 12, 6, map)
    self.assertEqual(
      path.path,
      [
        (0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0),
        (7, 0), (7, 1), (8, 1), (8, 2), (9, 2), (9, 3),
        (10, 3), (10, 4), (11, 4), (11, 5), (12, 5), (12, 6)
      ]
    )

  def test_path_search_13(self):
    ps = PathSearcher()
    map = self.__get_empty_map()
    for i in range (0,5):
      map[i][6].entity = UnitType.Wall
    path = ps.path_search(0, 0, 12, 6, map)
    self.assertEqual(
      path.path,
      [
        (0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0),
        (5, 1), (5, 2), (5, 3), (5, 4), (5, 5),
        (6, 5), (7, 5), (8, 5), (9, 5), (10, 5), (11, 5), (12, 5), (12, 6)
      ]
    )

  def test_game_logic_00(self):
    units = []
    units.extend([
      Unit(
        id=0,
        type=UnitType.MyLeader,
        pos_x=0,
        pos_y=0,
      ),
      Unit(
        id=1,
        type=UnitType.Neutral,
        pos_x=1,
        pos_y=1,
      )
    ])

    gl = GameLogic()
    nn = gl.find_nearest_neutral(units[0], units)
    self.assertEqual(
      nn,
      units[1]
    )

  def test_game_logic_01(self):
    units = []
    units.extend([
      Unit(
        type=UnitType.MyLeader,
        pos_x=0,
        pos_y=0,
      ),
      Unit(
        type=UnitType.EnWarior,
        pos_x=1,
        pos_y=1,
      )
    ])

    gl = GameLogic()
    nn = gl.find_nearest_neutral(units[0], units)
    self.assertEqual(
      nn,
      None
    )

  def test_game_logic_01(self):
    units = []
    units.append(
      Unit(
        id=0,
        type=UnitType.MyLeader,
        pos_x=0,
        pos_y=0,
      ))
    for i in range(5, 1, -1):
      units.append(
        Unit(
          id=i,
          type=UnitType.Neutral,
          pos_x=i,
          pos_y=i,
        )
      )

    gl = GameLogic()
    nn = gl.find_nearest_neutral(units[0], units)
    self.assertEqual(
      nn,
      units[-1]
    )

  def test_game_logic_02(self):
    units = []
    map = self.__get_empty_map()
    units.append(
      Unit(
        id=0,
        type=UnitType.MyLeader,
        pos_x=0,
        pos_y=0,
      ))
    map[0][0].entity = UnitType.MyLeader
    for i in range(5, 1, -1):
      units.append(
        Unit(
          id=i,
          type=UnitType.Neutral,
          pos_x=i,
          pos_y=i,
        )
      )
      map[i][i].entity = UnitType.Neutral

    gl = GameLogic()
    command = gl.convert_nuetral(units[0], units[-1], map)
    self.assertEqual(
      command,
      '0 MOVE 1 0'
    )

  def test_game_logic_03(self):
    units = []
    map = self.__get_empty_map()
    units.append(
      Unit(
        id=0,
        type=UnitType.MyLeader,
        pos_x=1,
        pos_y=2,
      ))
    map[1][2].entity = UnitType.MyLeader
    for i in range(5, 1, -1):
      units.append(
        Unit(
          id=i,
          type=UnitType.Neutral,
          pos_x=i,
          pos_y=i,
        )
      )
      map[i][i].entity = UnitType.Neutral

    gl = GameLogic()
    command = gl.convert_nuetral(units[0], units[-1], map)
    self.assertEqual(
      command,
      '0 CONVERT 2'
    )

  def test_read_initial_input(self):
    res = [
      '0',
      '13 7',
      '.............',
      '...x.....x...',
      'xxx.......xxx',
      '.............',
      '....xx.xx....',
      'x.x.......x.x',
      '.............',
    ]
    input = MagicMock()
    input.side_effect = res

    map_expected = self.__get_map_case_01()

    map: list[list[Cell]] = []
    ih = InputHandler(
      input=input
    )
    map = ih.read_initial_input(map)

    for i in range(0, 7):
      for j in range(0, 13):
        self.assertEqual(
          map_expected[i][j],
          map[i][j],
          f'{i} {j}'
        )

  def test_read_turn_input(self):
    res = ['14',
      '0 1 10 0 3 0',
      '1 1 10 12 3 1',
      '2 0 10 1 1 2',
      '3 0 10 2 1 2',
      '4 0 10 3 3 2',
      '5 0 10 1 5 2',
      '6 0 10 3 5 2',
      '7 0 10 2 6 2',
      '8 0 10 11 1 2',
      '9 0 10 10 1 2',
      '10 0 10 9 3 2',
      '11 0 10 11 5 2',
      '12 0 10 9 5 2',
      '13 0 10 10 6 2',
    ]
    input = MagicMock()
    input.side_effect = res

    map0:list[list[Cell]] = []    
    map:list[list[Cell]] = []
    units: list[Unit] = []

    ih = InputHandler(
      input=input
    )
    map0 = self.__get_empty_map()
    map_expected = self.__add_units_to_map_case_01(map0)
    units_expected = self.__get_units_case_01()
    map, units = ih.read_turn_input(map, units, map0)

    for i in range(0, 7):
      for j in range(0, 13):
        self.assertEqual(
          map_expected[i][j],
          map[i][j],
          f'{i} {j}'
        )
    for i in range(0, 14):
      self.assertEqual(
        units_expected[i],
        units[i],
        f'{i} {j}'
      )

  def test_test(self):
    ih = InputHandler()
    map0 = self.__get_map_case_01()
    map0 = self.__add_units_to_map_case_01(map0)
    units = self.__get_units_case_01()
    gl = GameLogic()
    command = gl.make_turn(units, map0)
    self.assertEqual(
      command,
      '0 MOVE 0 4'
    )

  def test_test(self):
    ih = InputHandler()
    map0 = self.__get_map_case_01()
    map0 = self.__add_units_to_map_case_01(map0)
    map0[1][4].entity = UnitType.MyLeader
    map0[0][3].entity = UnitType.Empty
    units = self.__get_units_case_01()
    units[0].pos_x = 1
    units[0].pos_y = 4
    gl = GameLogic()
    command = gl.make_turn(units, map0)
    self.assertEqual(
      command,
      '0 CONVERT 5'
    )

if __name__ == '__main__':
  unittest.main()

