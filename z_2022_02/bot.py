from ast import Tuple
from enum import Enum
import math
import random
import sys


class OwnerType(Enum):
    My = 1
    En = 0
    No = -1


class ZoneType(Enum):
    # no enemy or my cells
    Unreachable = 0
    # only my cells
    CapturedMy = 1
    # only enemy cells
    CapturedEn = 2
    # my and enemy cells
    FightInProgress = 3
    # my and empty cells
    GuaranteedMy = 4
    # enemy and empty cells
    GuaranteedEn = 5


class Cell:
    def __init__(self):
        self.ScrapAmount: int = 0
        self.Owner: OwnerType = OwnerType.No
        self.Units: int = 0
        self.Recycler: bool = False
        self.CanBuild: bool = False
        self.CanSpawn: bool = False
        self.InRangeOfRecycler: bool = False
        self.x: int = 0
        self.y: int = 0
        self.zone_checked: bool = False

    def to_map(self):
        print_char = self.ScrapAmount
        if self.Owner == OwnerType.My:
            print_char = "M"
        elif self.Owner == OwnerType.En:
            print_char = "E"
        return print_char

    def same(self, other: "Cell"):
        if (
            self.ScrapAmount == other.ScrapAmount
            and self.Owner == other.Owner
            and self.Units == other.Units
            and self.Recycler == other.Recycler
            and self.CanBuild == other.CanBuild
            and self.CanSpawn == other.CanSpawn
            and self.InRangeOfRecycler == other.InRangeOfRecycler
            and self.x == other.x
            and self.y == other.y
            and self.zone_checked == other.zone_checked
        ):
            return True
        return False


class Zone:
    def __init__(self):
        self.cells: list[Cell] = []
        self.type: ZoneType = None  # type: ignore
        self.cell_owners: dict[OwnerType, int]
        self.units: dict[OwnerType, int]


class Map:
    cells: list[list[Cell]] = []

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
        self.zones: list[Zone] = []
        self.RecyclerMy = 0
        self.RecyclerEn = 0

    @staticmethod
    def dist(x1: int, y1: int, x2: int, y2: int) -> float:
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def is_walkable(self, cell: Cell) -> bool:
        if (cell.ScrapAmount > 0) and (not cell.Recycler):
            return True
        return False

    def detect_zones(self) -> None:
        self.zones.clear()
        for cl in self.map.cells:
            for cell in cl:
                if self.is_walkable(cell) and (not cell.zone_checked):
                    zone = self.walk_zone(cell)
                    self.zones.append(zone)
                cell.zone_checked = True

        self.mark_zones()

    def walk_zone(self, cell: Cell) -> Zone:
        cells_to_check: list[Cell] = []
        zone = Zone()
        zone.cells.append(cell)
        cell.zone_checked = True
        cells_to_check += self.get_addjusted_cells(cell)
        while len(cells_to_check) > 0:
            cell_to_check = cells_to_check.pop(0)
            if self.is_walkable(cell_to_check) and (not cell_to_check.zone_checked):
                zone.cells.append(cell_to_check)
                cells_to_check += self.get_addjusted_cells(cell_to_check)
            cell_to_check.zone_checked = True
        return zone

    def mark_zones(self):
        for zone in self.zones:
            cell_owners = {OwnerType.My: 0, OwnerType.En: 0, OwnerType.No: 0}
            units = {OwnerType.My: 0, OwnerType.En: 0, OwnerType.No: 0}
            for cell in zone.cells:
                cell_owners[cell.Owner] += 1
                units[cell.Owner] += cell.Units

            zone.cell_owners = cell_owners
            zone.units = units

            if cell_owners[OwnerType.No] == len(zone.cells):
                zone.type = ZoneType.Unreachable

            if cell_owners[OwnerType.En] == len(zone.cells):
                zone.type = ZoneType.CapturedEn

            if cell_owners[OwnerType.My] == len(zone.cells):
                zone.type = ZoneType.CapturedMy

            if (
                zone.type == None
                and (cell_owners[OwnerType.No] != 0)
                and (cell_owners[OwnerType.En] != 0)
                and (cell_owners[OwnerType.My] != 0)
            ):
                zone.type = ZoneType.FightInProgress

            if (
                zone.type == None
                and (cell_owners[OwnerType.En] != 0)
                and (cell_owners[OwnerType.My] != 0)
            ):
                zone.type = ZoneType.FightInProgress

            if (
                zone.type == None
                and (cell_owners[OwnerType.No] != 0)
                and (cell_owners[OwnerType.En] != 0)
            ):
                zone.type = ZoneType.GuaranteedEn

            if (
                zone.type == None
                and (cell_owners[OwnerType.No] != 0)
                and (cell_owners[OwnerType.My] != 0)
            ):
                zone.type = ZoneType.GuaranteedMy

    def get_robot_moves(self) -> list[str]:
        move_cmds = []
        for cl in self.map.cells:
            for cell in cl:
                if (cell.Owner == OwnerType.My) and (cell.Units > 0):
                    target_empy, dist_empty = self.get_closest_unoccupied(cell)
                    target_enemy, dist_enemy = self.get_closest_enemy(cell)

                    target = None
                    if dist_empty < dist_enemy:
                        target = target_empy
                    else:
                        target = target_enemy

                    if target is not None:
                        move_cmds.append(
                            f"MOVE {cell.Units} {cell.x} {cell.y} {target.x} {target.y}"
                        )
                        target.Owner = OwnerType.My
        return move_cmds

    def get_closest_unoccupied(self, cell_from: Cell):
        dist = 10000
        cell_to = None
        for cl in self.map.cells:
            for cell in cl:
                if cell.Owner == OwnerType.No and cell.ScrapAmount > 0:
                    current_dist = self.dist(cell_from.x, cell_from.y, cell.x, cell.y)
                    if current_dist < dist:
                        dist = current_dist
                        cell_to = cell
        return cell_to, dist  # type: ignore

    def get_closest_enemy(self, cell_from: Cell):
        dist = 10000
        cell_to = None
        for cl in self.map.cells:
            for cell in cl:
                if cell.Owner == OwnerType.En:
                    current_dist = self.dist(cell_from.x, cell_from.y, cell.x, cell.y)
                    if current_dist < dist:
                        dist = current_dist
                        cell_to = cell
        return cell_to, dist  # type: ignore

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
        if self.RecyclerMy > self.RecyclerEn:
            return build_cmds
        for zone in self.zones:
            if zone.type == ZoneType.FightInProgress:
                for cell in zone.cells:
                    if self.my_matter >= 10 and cell.CanBuild:
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
                            self.RecyclerMy += 1
                            build_cmds.append(f"BUILD {cell.x} {cell.y}")
                            if self.RecyclerMy > self.RecyclerEn:
                                return build_cmds
        return build_cmds

    def get_spawns(self) -> list[str]:
        spawn_cmds = []
        max_spawns = self.my_matter // 10
        max_spawns_guaranteed = int(max_spawns * 0.2)
        max_spawns_fighting = max_spawns - max_spawns_guaranteed

        if max_spawns == 0:
            return spawn_cmds

        need_guaranteed_spawns = False
        for zone in self.zones:
            if (zone.type == ZoneType.GuaranteedMy) and (zone.units[OwnerType.My] == 0):
                need_guaranteed_spawns = True

        if need_guaranteed_spawns:
            max_spawns_guaranteed = min(2, max_spawns)
            max_spawns_fighting = max_spawns - max_spawns_guaranteed

        if max_spawns_guaranteed != 0:
            emptiest_zone = None
            emptiest_fraction = 100000.0
            for zone in self.zones:
                if zone.type == ZoneType.GuaranteedMy:
                    fraction = zone.units[OwnerType.My] / zone.cell_owners[OwnerType.My]
                    if fraction < emptiest_fraction:
                        emptiest_fraction = fraction
                        emptiest_zone = zone

            if emptiest_zone is not None:
                cells = emptiest_zone.cells[:]
                random.shuffle(cells)
                for cell in cells:
                    if cell.CanSpawn:
                        self.my_matter -= 10 * max_spawns_guaranteed
                        spawn_cmds.append(
                            f"SPAWN {max_spawns_guaranteed} {cell.x} {cell.y}"
                        )
                        break

        if max_spawns_fighting != 0:
            emptiest_zone = None
            emptiest_fraction = 100000.0
            for zone in self.zones:
                if zone.type == ZoneType.FightInProgress:
                    if zone.units[OwnerType.En] == 0:
                        if emptiest_zone == None:
                            emptiest_zone = zone
                        continue
                    fraction = zone.units[OwnerType.My] / zone.units[OwnerType.En]
                    if fraction < emptiest_fraction:
                        emptiest_fraction = fraction
                        emptiest_zone = zone

            if emptiest_zone is not None:
                cells = emptiest_zone.cells[:]
                random.shuffle(cells)
                for cell in cells:
                    if cell.CanSpawn:
                        self.my_matter -= 10 * max_spawns_fighting
                        spawn_cmds.append(
                            f"SPAWN {max_spawns_fighting} {cell.x} {cell.y}"
                        )
                        break

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
        game_logic.RecyclerMy = 0
        game_logic.RecyclerEn = 0
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
                if cell.Recycler and cell.Owner == OwnerType.My:
                    game_logic.RecyclerMy += 1
                if cell.Recycler and cell.Owner == OwnerType.En:
                    game_logic.RecyclerEn += 1
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
        gl.detect_zones()
        moves = gl.get_robot_moves()
        builds = gl.get_builds()
        spawns = gl.get_spawns()
        if (len(moves) == 0) and (len(builds) == 0) and (len(spawns) == 0):
            print("WAIT")
        else:
            print(";".join(builds + spawns + moves))


if __name__ == "__main__":
    main()
