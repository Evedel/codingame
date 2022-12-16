from enum import Enum
import math
import random
import sys


class OwnerType(Enum):
    My = 1
    En = 0
    No = -1


class Cell:
    ScrapAmount: int
    Owner: OwnerType
    Units: int
    Recycler: bool
    CanBuild: bool
    CanSpawn: bool
    InRangeOfRecycler: bool
    x: int
    y: int

    def to_map(self):
        print_char = self.ScrapAmount
        if self.Owner == OwnerType.My:
            print_char = "M"
        elif self.Owner == OwnerType.En:
            print_char = "E"
        return print_char


class Map:
    cells: list[list[Cell]]

    def print_map(self):
        for row in self.cells:
            string = ""
            for cell in row:
                string += str(cell.to_map())
            InputHandler.dp(string)

    def cell(self, x: int, y: int) -> Cell:
        return self.cells[y][x]


class GameLogic:
    def __init__(self):
        self.my_id: int = 0
        self.en_id: int = 0
        self.width: int = 0
        self.height: int = 0
        self.my_matter: int = 0
        self.en_matter: int = 0
        self.map: Map = Map()

    class Path:
        def __init__(self):
            path: list[Cell] | None = None
            cost: int | None = None
            dist: float | None = None

    @staticmethod
    def dist(x1: int, y1: int, x2: int, y2: int) -> float:
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def get_robot_moves(self) -> list[str]:
        move_cmds = []
        for cl in self.map.cells:
            for cell in cl:
                if (cell.Owner == OwnerType.My) and (cell.Units > 0):
                    if random.random() < 0.5:
                        target = self.get_closest_unoccupied(cell)
                    else:
                        target = self.get_closest_enemy(cell)
                    if target is not None:
                        move_cmds.append(
                            f"MOVE 1 {cell.x} {cell.y} {target.x} {target.y}"
                        )
                        target.Owner = OwnerType.My
        return move_cmds

    def get_closest_unoccupied(self, cell_from: Cell) -> Cell:
        dist = 10000
        cell_to = None
        for cl in self.map.cells:
            for cell in cl:
                if cell.Owner == OwnerType.No and cell.ScrapAmount > 0:
                    current_dist = self.dist(cell_from.x, cell_from.y, cell.x, cell.y)
                    if current_dist < dist:
                        dist = current_dist
                        cell_to = cell
        return cell_to

    def get_closest_enemy(self, cell_from: Cell) -> Cell:
        dist = 10000
        cell_to = None
        for cl in self.map.cells:
            for cell in cl:
                if cell.Owner == OwnerType.En:
                    current_dist = self.dist(cell_from.x, cell_from.y, cell.x, cell.y)
                    if current_dist < dist:
                        dist = current_dist
                        cell_to = cell
        return cell_to

    def get_addjusted_cells(self, this_cell: Cell) -> list[Cell]:
        cells: list[Cell] = []
        x = this_cell.x
        y = this_cell.y
        if x > 0:
            cells.append(self.map.cell(x - 1, y))
        if x < self.width - 1:
            cells.append(self.map.cell(x + 1, y))
        if y > 0:
            cells.append(self.map.cell(x, y - 1))
        if y < self.height - 1:
            cells.append(self.map.cell(x, y + 1))
        return cells

    def get_builds(self) -> list[str]:
        build_cmds = []
        max_builds_per_turn = 1
        for cl in self.map.cells:
            for cell in cl:
                if max_builds_per_turn > 0 and self.my_matter >= 10 and cell.CanBuild:
                    should_build = True
                    adjusted_cells = self.get_addjusted_cells(cell)
                    for adj_cell in adjusted_cells:
                        if adj_cell.Recycler:
                            should_build = False
                        else:
                            adjusted_of_adjusted_cells = self.get_addjusted_cells(
                                adj_cell
                            )
                            for adj_adj_cell in adjusted_of_adjusted_cells:
                                if adj_adj_cell.Recycler:
                                    should_build = False
                    if should_build:
                        cell.CanBuild = False
                        cell.Recycler = True
                        self.my_matter -= 10
                        max_builds_per_turn -= 1
                        build_cmds.append(f"BUILD {cell.x} {cell.y}")
        return build_cmds

    def get_spawns(self) -> list[str]:
        spawn_cmds = []
        xs = list(range(0, self.width - 1))
        random.shuffle(xs)
        for x in xs:
            ys = list(range(0, self.height - 1))
            random.shuffle(ys)
            for y in ys:
                cell = self.map.cell(x, y)
                if self.my_matter >= 10 and cell.CanSpawn:
                    self.my_matter -= 10
                    spawn_cmds.append(f"SPAWN 1 {cell.x} {cell.y}")
        return spawn_cmds


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
        my_id = 1
        en_id = 1 - my_id

        game_logic.my_id = my_id
        game_logic.en_id = en_id

        game_logic.width, game_logic.height = [int(i) for i in self.input().split()]
        game_logic.map.cells = [
            [Cell() for _ in range(game_logic.width)] for _ in range(game_logic.height)
        ]
        return game_logic

    def read_turn_input(self, game_logic: GameLogic):
        game_logic.my_matter, game_logic.en_matter = [
            int(i) for i in self.input().split()
        ]
        for i in range(game_logic.height):
            for j in range(game_logic.width):
                (
                    scrap_amount,
                    owner,
                    units,
                    recycler,
                    can_build,
                    can_spawn,
                    in_range_of_recycler,
                ) = [int(k) for k in self.input().split()]
                cell = Cell()
                cell.ScrapAmount = scrap_amount
                cell.Owner = OwnerType(owner)
                cell.Units = units
                cell.Recycler = True if recycler == 1 else False
                cell.CanBuild = True if can_build == 1 else False
                cell.CanSpawn = True if can_spawn == 1 else False
                cell.InRangeOfRecycler = True if in_range_of_recycler == 1 else False
                cell.x = j
                cell.y = i
                game_logic.map.cells[i][j] = cell

        return game_logic


def main():
    random.seed(18081991)
    # ih = InputHandler(input=InputHandler.__input_debugger__)  # type: ignore
    ih = InputHandler()  # type: ignore
    gl = GameLogic()

    gl = ih.read_initial_input(gl)
    while True:
        gl = ih.read_turn_input(gl)
        moves = gl.get_robot_moves()
        builds = gl.get_builds()
        spawns = gl.get_spawns()
        print(";".join(builds + spawns + moves))


if __name__ == "__main__":
    main()
