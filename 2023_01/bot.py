#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from abc import ABC, abstractmethod
import copy
from enum import Enum
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
        self.x: int = 0
        self.y: int = 0

    def dist(self, cell):
        if abs(self.y - cell.y) < 2:
            return abs(self.x - cell.x)
        return (abs(self.x - cell.x) + abs(self.y - cell.y)) / 2

    def to_map(self):
        return str(self.resource)

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

    def get_by_type(self, cell_type: CellType) -> list[Cell]:
        if cell_type == CellType.Base:
            return [cell for cell in self.cells if cell.my_base]
        return [cell for cell in self.cells if cell.type == cell_type]

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


class StrategyDefault(Strategy):
    def post_init(self, game_logic: "GameLogic") -> None:
        self.game_logic = game_logic

    def pre_game(self) -> None:
        self.game_logic.map.hex_to_matrix()

    def get_lines(self) -> list[str]:
        base: Cell = self.game_logic.map.get_by_type(CellType.Base)[0]
        eggs: list[Cell] = self.game_logic.map.get_by_type(CellType.Egg)
        res = []
        bestDist = 1000
        bestCell = None
        bestIndex = 0
        for cell in eggs:
            if cell.resource > 0:
                dist = self.game_logic.dist(base, cell)
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
                dist = self.game_logic.dist(base, cell)
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

    def dist(self, cell1: Cell, cell2: Cell):
        if abs(cell1.x - cell2.x) < 2:
            return abs(cell1.y - cell2.y)
        return (abs(cell1.x - cell2.x) + abs(cell1.y - cell2.y)) / 2


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

        number_of_bases = int(self.input())
        for i in self.input().split():
            my_base_index = int(i)
            game_logic.map.cells[my_base_index].my_base = True
        for i in self.input().split():
            opp_base_index = int(i)
            game_logic.map.cells[opp_base_index].opp_base = True

        return game_logic

    def read_turn_input(self, game_logic: GameLogic):
        for i in range(game_logic.map.size):
            # resources: the current amount of eggs/crystals on this cell
            # my_ants: the amount of your ants on this cell
            # opp_ants: the amount of opponent ants on this cell
            resources, my_ants, opp_ants = [int(j) for j in self.input().split()]
            game_logic.map.cells[i].resource = resources
            game_logic.map.cells[i].my_ants = my_ants
            game_logic.map.cells[i].opp_ants = opp_ants

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
