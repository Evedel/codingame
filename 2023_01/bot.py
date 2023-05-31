#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from abc import ABC, abstractmethod
import copy
from enum import Enum
import math
import random
import sys


class CellType(Enum):
    Empty = 0
    Egg = 1
    Crystal = 2
    Base = 3


class Cell:
    def __init__(self):
        self.type = CellType.Empty
        self.resource: int = 0
        self.id: int = 0
        self.my_ants: int = 0
        self.opp_ants: int = 0
        self.my_base: bool = False
        self.opp_base: bool = False
        self.neighbours: list[Cell] = []
        self.distance_to_base: int = 0
        self.x: int = 0
        self.y: int = 0

    def dist(self, cell2: "Cell"):
        if abs(self.x - cell2.x) < 2:
            return abs(self.y - cell2.y)
        return (abs(self.x - cell2.x) + abs(self.y - cell2.y)) / 2

    def to_map(self):
        if self.my_base:
            return "M"
        if self.opp_base:
            return "E"
        if (
            self.type == CellType.Egg or self.type == CellType.Crystal
        ) and self.resource > 0:
            return str(self.resource)
        return "x"

    def deepcopy(self):
        return copy.deepcopy(self)

    def same(self, other: "Cell") -> bool:
        return (
            self.type == other.type
            and self.resource == other.resource
            and self.id == other.id
            and self.my_ants == other.my_ants
            and self.opp_ants == other.opp_ants
            and self.my_base == other.my_base
            and self.opp_base == other.opp_base
            and self.x == other.x
            and self.y == other.y
            and all(
                [
                    (n1 == None and n2 == None) or (n1.id == n2.id)
                    for n1, n2 in zip(self.neighbours, other.neighbours)
                ]
            )
        )

    def __str__(self):
        n_ids = "|".join([str(n.id) if n else "x" for n in self.neighbours])
        return f"Cell({self.type}, {self.resource}, {self.id}, {self.my_ants}, {self.opp_ants}, {self.my_base}, {self.opp_base}, {n_ids}, {self.x}, {self.y})"


class Map:
    def __init__(self, size: int = 0):
        self.size: int = size
        self.cells: list[Cell] = [Cell() for _ in range(self.size)]
        self.matrix: list[list[Cell]] = None
        self.initial_crystals: int = 0
        self.crystals_collected: int = 0
        self.my_ants_total: int = 0
        self.opp_ants_total: int = 0

    def get_by_type(self, cell_type: CellType) -> list[Cell]:
        if cell_type == CellType.Base:
            return [cell for cell in self.cells if cell.my_base]
        return [cell for cell in self.cells if cell.type == cell_type]

    def precalc_distances_to_base(self) -> None:
        base = self.get_by_type(CellType.Base)[0]
        for cell in self.cells:
            cell.distance_to_base = base.dist(cell)

    def hex_to_matrix(self) -> None:
        visited = [False for i in range(self.size)]
        index0 = [0, 0]
        cell0 = self.cells[0]
        self.enumerate_hex_recursive(cell0, visited, index0)
        y_max = -1000
        x_min = 1000
        for cell in self.cells:
            cell.y = -cell.y
            if cell.y > y_max:
                y_max = cell.y
            if cell.x < x_min:
                x_min = cell.x
        for cell in self.cells:
            cell.x -= x_min
            cell.y += y_max

        self.matrix = [
            [None for _ in range(2 * abs(x_min) + 1)] for _ in range(2 * y_max + 1)
        ]
        for cell in self.cells:
            self.matrix[cell.y][cell.x] = cell

    def enumerate_hex_recursive(
        self, cell: Cell, visited: list[bool], index: list[int]
    ) -> None:
        cell.x = index[0]
        cell.y = index[1]

        visited[cell.id] = True
        for i in range(6):
            c = cell.neighbours[i]
            if c and not visited[c.id]:
                next_index = index[:]
                if i == 0:
                    next_index[0] += 2
                if i == 1:
                    next_index[0] += 1
                    next_index[1] += 1
                if i == 2:
                    next_index[0] -= 1
                    next_index[1] += 1
                if i == 3:
                    next_index[0] -= 2
                if i == 4:
                    next_index[0] -= 1
                    next_index[1] -= 1
                if i == 5:
                    next_index[0] += 1
                    next_index[1] -= 1
                visited = self.enumerate_hex_recursive(c, visited, next_index)
        return visited

    def print_map(self):
        for row in self.matrix:
            string = ""
            for cell in row:
                if cell:
                    string += str(cell.to_map())
                else:
                    string += " "
            InputHandler.dp(string)

    def cell(self, x: int, y: int) -> Cell:
        return self.cells[y][x]

    def deepcopy(self):
        return copy.deepcopy(self)


class Strategy(ABC):
    @abstractmethod
    def post_init(self, game_logic: "GameLogic") -> None:
        pass

    @abstractmethod
    def pre_game(self) -> None:
        pass

    @abstractmethod
    def get_lines(self) -> list[str]:
        pass


class Option:
    def __init__(self, cell, map, turns_to_win, crystals_collected):
        self.cell = cell
        self.map = map
        self.turns_to_win = turns_to_win
        self.crystals_collected = crystals_collected

    def __str__(self) -> str:
        return f"Option(id:{self.cell.id:2}, ttw:{self.turns_to_win:2}, crc:{self.crystals_collected:2}, ants:{self.map.my_ants_total:2})"


class StrategyDefault(Strategy):
    def post_init(self, game_logic: "GameLogic") -> None:
        self.game_logic = game_logic

    def pre_game(self) -> None:
        self.game_logic.map.hex_to_matrix()
        self.game_logic.map.precalc_distances_to_base()

    def step_crystal(self, map: Map, cell_id: int):
        map_local = map.deepcopy()
        turns_to_reach = math.ceil(map_local.cells[cell_id].distance_to_base) + 1
        ants_per_cell = map_local.my_ants_total // turns_to_reach
        if ants_per_cell == 0:
            return 1000000, 0, None

        turns_to_deplete = math.ceil(map_local.cells[cell_id].resource / ants_per_cell)
        turns_to_win = turns_to_reach + turns_to_deplete
        # turns_to_win = turns_to_deplete
        crystals_collected = map_local.cells[cell_id].resource
        map_local.cells[cell_id].resource = 0

        return turns_to_win, crystals_collected, map_local

    def step_eggs(self, map: Map, cell_id: int):
        map_local = map.deepcopy()
        turns_to_reach = math.ceil(map_local.cells[cell_id].distance_to_base) + 1
        ants_per_cell = map_local.my_ants_total // turns_to_reach
        if ants_per_cell == 0:
            return 1000000, 0, None

        turns_to_deplete = 0
        while map_local.cells[cell_id].resource > 0:
            mined_eggs = (
                ants_per_cell
                if map_local.cells[cell_id].resource >= ants_per_cell
                else map_local.cells[cell_id].resource
            )
            map_local.my_ants_total += mined_eggs
            map_local.cells[cell_id].resource -= mined_eggs
            ants_per_cell = map_local.my_ants_total // turns_to_reach
            turns_to_deplete += 1
        turns_to_win = turns_to_reach + turns_to_deplete
        # turns_to_win = turns_to_deplete

        return turns_to_win, 0, map_local

    def solve(self) -> int:
        dp = InputHandler.dp
        map = self.game_logic.map
        dp(map.initial_crystals)
        number_of_options = 3
        option = Option(
            cell=None,
            map=map,
            turns_to_win=0,
            crystals_collected=0,
        )
        result = self.solve_step_recursive(dp, number_of_options, option)
        # for option in result:
        #     print(option)
        #     option.map.print_map()
        return result[0].cell.id

    def solve_step_recursive(
        self,
        dp,
        number_of_options: int,
        previous_option: Option,
        depth: int = 0,
        max_depth: int = 3,
    ) -> None:
        map = previous_option.map
        options = self.solve_step(dp, map, number_of_options)

        best_chain = []
        best_option = []
        best_score = -1

        depth += 1

        # print(f"depth: {depth}")
        for option in options:
            option.turns_to_win += previous_option.turns_to_win
            option.crystals_collected += previous_option.crystals_collected
            # print(option)
            result = [option]
            if depth < max_depth:
                result += self.solve_step_recursive(
                    dp, number_of_options, option, depth, max_depth
                )
            score = result[-1].crystals_collected / result[-1].turns_to_win
            # print(score)
            if score > best_score:
                best_option = result
                best_score = score

        best_chain = best_option

        # print(f"depth: {depth}")

        return best_chain

    def solve_step(self, dp, map: Map, number_of_options: int) -> list[Option]:
        options = (
            []
        )  # (cell, map, turns_to_win, crystals_collected, ants_collected) convert to class when ready

        # turns_to_win = 0
        # crystals_collected = 0
        map_local = map.deepcopy()
        added_options = 0
        while added_options < number_of_options:
            best_distance = 1000000
            best_cell = None

            for cell in map_local.cells:
                if (cell.type == CellType.Egg or cell.type == CellType.Crystal) and (
                    cell.resource > 0
                ):
                    distance = cell.distance_to_base
                    if distance < best_distance:
                        best_distance = distance
                        best_cell = cell

            if best_cell:
                if best_cell.type == CellType.Egg:
                    (
                        turns_to_win_step,
                        crystals_collected_step,
                        map_local_step,
                    ) = self.step_eggs(map, best_cell.id)
                elif best_cell.type == CellType.Crystal:
                    (
                        turns_to_win_step,
                        crystals_collected_step,
                        map_local_step,
                    ) = self.step_crystal(map, best_cell.id)

                options.append(
                    Option(
                        best_cell,
                        map_local_step,
                        turns_to_win_step,
                        crystals_collected_step,
                    )
                )
                best_cell.resource = 0
                added_options += 1
            else:
                break

        return options

    def get_lines(self) -> list[str]:
        base: Cell = self.game_logic.map.get_by_type(CellType.Base)[0]
        cell_id = self.solve()
        return [f"LINE {base.id} {cell_id} 1"]

    def get_lines_old(self) -> list[str]:
        base: Cell = self.game_logic.map.get_by_type(CellType.Base)[0]
        eggs: list[Cell] = self.game_logic.map.get_by_type(CellType.Egg)
        res = []
        bestDist = 1000
        bestCell = None
        bestIndex = 0
        for cell in eggs:
            if cell.resource > 0:
                dist = cell.distance_to_base
                if dist < bestDist:
                    bestDist = dist
                    bestCell = cell
                    bestIndex = len(res)
                # res.append(f"LINE {base.id} {cell.id} 1")
        if bestCell:
            # res[bestIndex] = f"LINE {base.id} {bestCell.id} 5"
            res.append(f"LINE {base.id} {bestCell.id} 5")

        bestDist = 1000
        bestCell = None
        bestIndex = 0
        for cell in self.game_logic.map.cells:
            if (cell.type == CellType.Crystal) and (cell.resource > 0):
                dist = cell.distance_to_base
                if dist < bestDist:
                    bestDist = dist
                    bestCell = cell
                    bestIndex = len(res)
                # res.append(f"LINE {base.id} {cell.id} 1")
        if bestCell:
            # res[bestIndex] = f"LINE {base.id} {bestCell.id} 5"
            res.append(f"LINE {base.id} {bestCell.id} 5")

        return [";".join(res)]


class GameLogic:
    def __init__(self, strategy: Strategy):
        self.map: Map = Map()
        self.Strategy = strategy
        self.Strategy.post_init(self)

    def deepcopy(self):
        return copy.deepcopy(self)


class InputHandler:
    __DEBUG = False

    def __init__(self, input=input):
        self.input = input

    @staticmethod
    def __input_debugger__() -> str:
        res = input()
        InputHandler.dp(f'"{res}",')
        return res

    @staticmethod
    def dp(*args, **kwargs):
        print(*args, file=sys.stderr, **kwargs)

    @staticmethod
    def ddp(*args, **kwargs):
        if InputHandler.__DEBUG:
            print(*args, file=sys.stderr, **kwargs)

    def read_initial_input(self, game_logic: GameLogic):
        number_of_cells = int(self.input())  # amount of hexagonal cells in this map
        game_logic.map = Map(number_of_cells)

        def get_cell_or_none(id: int) -> Cell:
            if id == -1:
                return None
            return game_logic.map.cells[id]

        initial_crystals = 0
        for i in range(number_of_cells):
            # _type: 0 for empty, 1 for eggs, 2 for crystal
            # initial_resources: the initial amount of eggs/crystals on this cell
            # neigh_0: the index of the neighbouring cell for each direction
            (
                type,
                initial_resources,
                neigh_0,
                neigh_1,
                neigh_2,
                neigh_3,
                neigh_4,
                neigh_5,
            ) = [int(j) for j in self.input().split()]
            game_logic.map.cells[i].id = i
            game_logic.map.cells[i].resource = initial_resources
            game_logic.map.cells[i].neighbours = [
                get_cell_or_none(neigh_0),
                get_cell_or_none(neigh_1),
                get_cell_or_none(neigh_2),
                get_cell_or_none(neigh_3),
                get_cell_or_none(neigh_4),
                get_cell_or_none(neigh_5),
            ]
            game_logic.map.cells[i].type = CellType(type)
            if game_logic.map.cells[i].type == CellType.Crystal:
                initial_crystals += initial_resources

        game_logic.map.initial_crystals = initial_crystals

        number_of_bases = int(self.input())
        for i in self.input().split():
            my_base_index = int(i)
            game_logic.map.cells[my_base_index].my_base = True
        for i in self.input().split():
            opp_base_index = int(i)
            game_logic.map.cells[opp_base_index].opp_base = True

        return game_logic

    def read_turn_input(self, game_logic: GameLogic):
        my_ants_total = 0
        opp_ants_total = 0

        for i in range(game_logic.map.size):
            # resources: the current amount of eggs/crystals on this cell
            # my_ants: the amount of your ants on this cell
            # opp_ants: the amount of opponent ants on this cell
            resources, my_ants, opp_ants = [int(j) for j in self.input().split()]
            game_logic.map.cells[i].resource = resources
            game_logic.map.cells[i].my_ants = my_ants
            game_logic.map.cells[i].opp_ants = opp_ants
            my_ants_total += my_ants
            opp_ants_total += opp_ants

        game_logic.map.my_ants_total = my_ants_total
        game_logic.map.opp_ants_total = opp_ants_total
        return game_logic


def main():
    random.seed(89819011)
    # ih = InputHandler(input=InputHandler.__input_debugger__)  # type: ignore
    ih = InputHandler()  # type: ignore
    gl = GameLogic(StrategyDefault())
    gl = ih.read_initial_input(gl)
    gl.Strategy.pre_game()
    while True:
        gl = ih.read_turn_input(gl)
        gl.map.print_map()
        lines = gl.Strategy.get_lines()
        if len(lines) == 0:
            print("WAIT")
        else:
            print(";".join(lines))


if __name__ == "__main__":
    main()
