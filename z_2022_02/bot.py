from abc import ABC, abstractmethod
import copy
from enum import Enum
import math
import random
import sys
from typing import Tuple


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
        self.scrap_amount: int = 0
        self.Owner: OwnerType = OwnerType.No
        self.Units: int = 0
        self.Recycler: bool = False
        self.CanBuild: bool = False
        self.CanSpawn: bool = False
        self.InRangeOfRecycler: bool = False
        self.x: int = 0
        self.y: int = 0
        self.zone_checked: bool = False
        self.n_u: Cell = None  # type: ignore
        self.n_d: Cell = None  # type: ignore
        self.n_l: Cell = None  # type: ignore
        self.n_r: Cell = None  # type: ignore

    def destroy(self):
        self.scrap_amount = 0
        self.Owner = OwnerType.No
        self.Units = 0
        self.Recycler = False
        self.CanBuild = False
        self.CanSpawn = False
        self.InRangeOfRecycler = False

    def is_alomost_destroyed(self):
        return self.InRangeOfRecycler and self.scrap_amount == 1

    def is_contact_with_enemy(self):
        if self.n_u and (self.n_u.Owner == OwnerType.En) and (self.scrap_amount > 0):
            return True
        if self.n_d and (self.n_d.Owner == OwnerType.En) and (self.scrap_amount > 0):
            return True
        if self.n_l and (self.n_l.Owner == OwnerType.En) and (self.scrap_amount > 0):
            return True
        if self.n_r and (self.n_r.Owner == OwnerType.En) and (self.scrap_amount > 0):
            return True
        return False

    def is_contact_with_empty(self):
        if (
            self.n_u
            and (self.n_u.Owner == OwnerType.No)
            and (self.scrap_amount > 0)
            and (self.n_u.scrap_amount > 0)
        ):
            return True
        if (
            self.n_d
            and (self.n_d.Owner == OwnerType.No)
            and (self.scrap_amount > 0)
            and (self.n_d.scrap_amount > 0)
        ):
            return True
        if (
            self.n_l
            and (self.n_l.Owner == OwnerType.No)
            and (self.scrap_amount > 0)
            and (self.n_l.scrap_amount > 0)
        ):
            return True
        if (
            self.n_r
            and (self.n_r.Owner == OwnerType.No)
            and (self.scrap_amount > 0)
            and (self.n_r.scrap_amount > 0)
        ):
            return True
        return False

    def is_contact(self):
        return self.is_contact_with_enemy() or self.is_contact_with_empty()

    def to_map(self):
        print_char = self.scrap_amount
        if self.Owner == OwnerType.My:
            print_char = "M"
        elif self.Owner == OwnerType.En:
            print_char = "E"
        return print_char

    def same(self, other: "Cell"):
        if (
            self.scrap_amount == other.scrap_amount
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
        self.cutline: list[Cell] = []


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


class Strategy(ABC):
    @abstractmethod
    def post_init(self, game_logic: "GameLogic") -> None:
        pass

    @abstractmethod
    def get_moves(self) -> list[str]:
        pass

    @abstractmethod
    def get_builds(self) -> list[str]:
        pass

    @abstractmethod
    def get_spawns(self) -> list[str]:
        pass


class Move:
    def __init__(self, cell: Cell, target: Cell, zone: Zone, distance: float):
        self.cell = cell
        self.target = target
        self.zone = zone
        self.distance = distance


class GameLogic:
    def __init__(self, strategy: Strategy):
        self.my_id: int = 0
        self.en_id: int = 0
        self.width: int = 0
        self.height: int = 0
        self.my_matter: int = 0
        self.en_matter: int = 0
        self.map: Map = Map()
        self.zones: list[Zone] = []
        self.recycler_my = 0
        self.recycler_en = 0
        self.Strategy = strategy
        self.Strategy.post_init(self)

    def deepcopy(self):
        return copy.deepcopy(self)

    def dist(self, x1: int, y1: int, x2: int, y2: int) -> float:
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def is_walkable(self, cell: Cell) -> bool:
        if (cell.scrap_amount > 0) and (not cell.Recycler):
            return True
        return False

    def preprocess(self) -> None:
        self.link_cells()
        self.zones_init()

    def link_cells(self):
        for y in range(self.height):
            for x in range(self.width):
                cell = self.map.cell(x, y)
                if x > 0:
                    cell.n_l = self.map.cell(x - 1, y)
                if x < self.width - 1:
                    cell.n_r = self.map.cell(x + 1, y)
                if y > 0:
                    cell.n_u = self.map.cell(x, y - 1)
                if y < self.height - 1:
                    cell.n_d = self.map.cell(x, y + 1)

    def zones_init(self):
        self.zones.clear()
        for cl in self.map.cells:
            for cell in cl:
                cell.zone_checked = False
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

    def get_closest_empty(self, cell_from: Cell, zone: Zone):
        dist = 10000
        cell_to = None
        for cell in zone.cells:
            if cell.Owner == OwnerType.No and cell.scrap_amount > 0:
                current_dist = self.dist(cell_from.x, cell_from.y, cell.x, cell.y)
                if current_dist < dist:
                    dist = current_dist
                    cell_to = cell
        return cell_to, dist  # type: ignore

    def get_closest_enemy(self, cell_from: Cell, zone: Zone):
        dist = 10000
        cell_to = None
        for cell in zone.cells:
            if cell.Owner == OwnerType.En:
                current_dist = self.dist(cell_from.x, cell_from.y, cell.x, cell.y)
                if current_dist < dist:
                    dist = current_dist
                    cell_to = cell
        return cell_to, dist  # type: ignore

    def get_addjusted_cells(self, this_cell: Cell) -> list[Cell]:
        cells: list[Cell] = []
        if this_cell.n_u:
            cells.append(this_cell.n_u)
        if this_cell.n_d:
            cells.append(this_cell.n_d)
        if this_cell.n_l:
            cells.append(this_cell.n_l)
        if this_cell.n_r:
            cells.append(this_cell.n_r)
        return cells

    def check_zones_if_built(self, cell: Cell) -> list[Zone]:
        game_state_copy = self.deepcopy()

        cell_copy = game_state_copy.map.cell(cell.x, cell.y)
        adj_cells = game_state_copy.get_addjusted_cells(cell_copy)
        for adj_cell in adj_cells:
            adj_cell.scrap_amount -= 1
            if adj_cell.scrap_amount <= 0:
                adj_cell.destroy()
        cell_copy.scrap_amount -= 1
        if cell_copy.scrap_amount <= 0:
            cell_copy.destroy()
        else:
            cell_copy.Recycler = True

        game_state_copy.zones_init()
        return game_state_copy.zones

    def check_zones_if_built_long(self, cell: Cell) -> list[Zone]:
        game_state_copy = self.deepcopy()
        recycler_lifetime = cell.scrap_amount

        cell_copy = game_state_copy.map.cell(cell.x, cell.y)
        adj_cells = game_state_copy.get_addjusted_cells(cell_copy)
        for adj_cell in adj_cells:
            adj_cell.scrap_amount -= recycler_lifetime
            if adj_cell.scrap_amount <= 0:
                adj_cell.destroy()
        cell_copy.destroy()

        game_state_copy.zones_init()
        return game_state_copy.zones

    def check_recycler_output(self, cell: Cell) -> int:
        scrap = cell.scrap_amount
        adj_cells = self.get_addjusted_cells(cell)
        for adj_cell in adj_cells:
            scrap += min(adj_cell.scrap_amount, cell.scrap_amount)
        return scrap

    def check_balance(self, zones: list[Zone]) -> Tuple[int, int, int, int, int, int]:
        zones_unreachable = 0
        zones_my = 0
        zones_en = 0
        cells_unreachable = 0
        cells_my = 0
        cells_en = 0

        for zone in zones:
            if zone.type == ZoneType.Unreachable:
                zones_unreachable += 1
                cells_unreachable += len(zone.cells)
            elif zone.type == ZoneType.GuaranteedMy:
                zones_my += 1
                cells_my += len(zone.cells)
            elif zone.type == ZoneType.GuaranteedEn:
                zones_en += 1
                cells_en += len(zone.cells)
            elif zone.type == ZoneType.CapturedMy:
                zones_my += 1
                cells_my += len(zone.cells)
            elif zone.type == ZoneType.CapturedEn:
                zones_en += 1
                cells_en += len(zone.cells)
            # elif zone.type == ZoneType.FightInProgress:
            #     cells_my += int(
            #         zone.cell_owners[OwnerType.My] + zone.cell_owners[OwnerType.No] / 2
            #     )
            #     cells_en += int(
            #         zone.cell_owners[OwnerType.En] + zone.cell_owners[OwnerType.No] / 2
            #     )

        return (
            zones_unreachable,
            zones_my,
            zones_en,
            cells_unreachable,
            cells_my,
            cells_en,
        )

    def get_moves(self) -> list[str]:
        return self.Strategy.get_moves()

    def get_builds(self) -> list[str]:
        return self.Strategy.get_builds()

    def get_spawns(self) -> list[str]:
        return self.Strategy.get_spawns()


class StrategyDefault(Strategy):
    def post_init(self, game_logic: "GameLogic") -> None:
        self.game_logic = game_logic

    def get_spawn_point_in_guaranteed_zone(self, zone: Zone, amount: int) -> str:
        shuffled_cells = zone.cells[:]
        random.shuffle(shuffled_cells)
        for cell in shuffled_cells:
            if cell.CanSpawn and (not cell.is_alomost_destroyed()):
                if cell.is_contact_with_empty():
                    self.game_logic.my_matter -= 10 * amount
                    return f"SPAWN {amount} {cell.x} {cell.y}"
        return None  # type: ignore

    def get_spawn_point_in_fighting_zone(self, zone: Zone, amount: int) -> str:
        are_there_contact_cells = False
        for cells in zone.cells:
            if cells.CanSpawn and (not cells.is_alomost_destroyed()):
                if cells.is_contact_with_enemy():
                    are_there_contact_cells = True
                    break
        if are_there_contact_cells:
            shuffled_cells = zone.cells[:]
            random.shuffle(shuffled_cells)
            for cell in shuffled_cells:
                if cell.CanSpawn and (not cell.is_alomost_destroyed()):
                    if cell.is_contact_with_enemy():
                        self.game_logic.my_matter -= 10 * amount
                        return f"SPAWN {amount} {cell.x} {cell.y}"
        else:
            return self.get_spawn_point_in_guaranteed_zone(zone, amount)
        return None  # type: ignore

    def get_spawns(self) -> list[str]:
        spawn_cmds = []
        max_spawns = self.game_logic.my_matter // 10

        if max_spawns == 0:
            return spawn_cmds

        max_spawns_guaranteed = 0
        for zone in self.game_logic.zones:
            if (zone.type == ZoneType.GuaranteedMy) and (zone.units[OwnerType.My] == 0):
                max_spawns_guaranteed = 1

        max_spawns_fighting = max_spawns - max_spawns_guaranteed

        if max_spawns_guaranteed != 0:
            emptiest_zone = None
            emptiest_fraction = 100000.0
            for zone in self.game_logic.zones:
                if zone.type == ZoneType.GuaranteedMy:
                    fraction = zone.units[OwnerType.My] / zone.cell_owners[OwnerType.My]
                    if fraction < emptiest_fraction:
                        emptiest_fraction = fraction
                        emptiest_zone = zone

            if emptiest_zone is not None:
                spawn_cmd = self.get_spawn_point_in_guaranteed_zone(
                    emptiest_zone, max_spawns_guaranteed
                )
                if spawn_cmd is not None:
                    spawn_cmds.append(spawn_cmd)

        if max_spawns_fighting != 0:
            emptiest_zone = None
            emptiest_fraction = 100000.0
            for zone in self.game_logic.zones:
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
                spawn_cmd = self.get_spawn_point_in_fighting_zone(
                    emptiest_zone, max_spawns_fighting
                )
                if spawn_cmd is not None:
                    spawn_cmds.append(spawn_cmd)

        return spawn_cmds

    def get_builds(self) -> list[str]:
        (
            zones_unreachable_before,
            zones_my_before,
            zones_en_before,
            cells_unreachable_before,
            cells_my_before,
            cells_en_before,
        ) = self.game_logic.check_balance(self.game_logic.zones)
        cells_balance_before = cells_my_before - cells_en_before

        best_balance = cells_balance_before
        best_cell = None

        build_cmds = []
        if self.game_logic.recycler_my > self.game_logic.recycler_en:
            return build_cmds

        for zone in self.game_logic.zones:
            if zone.type == ZoneType.FightInProgress:
                max_tries = 5
                num_tries = 0
                iter_cells = zone.cells[:]
                random.shuffle(iter_cells)
                for cell in iter_cells:
                    if (
                        num_tries <= max_tries
                        and self.game_logic.my_matter >= 10
                        and cell.CanBuild
                        # and self.game_logic.check_recycler_output(cell) >= 10
                    ):
                        num_tries += 1
                        new_zones = self.game_logic.check_zones_if_built_long(cell)
                        (
                            zones_unreachable_after,
                            zones_my_after,
                            zones_en_after,
                            cells_unreachable_after,
                            cells_my_after,
                            cells_en_after,
                        ) = self.game_logic.check_balance(new_zones)
                        cells_balance_after = cells_my_after - cells_en_after

                        if cells_balance_after > best_balance:
                            best_balance = cells_balance_after
                            best_cell = cell

        if best_cell:
            best_cell.CanBuild = False
            best_cell.Recycler = True
            self.game_logic.my_matter -= 10
            self.game_logic.recycler_my += 1
            build_cmds.append(f"BUILD {best_cell.x} {best_cell.y}")

        return build_cmds

    def get_move_target(self, zone: Zone, cell: Cell) -> Move:
        if cell.Owner == OwnerType.My and cell.Units > 0:
            if zone.type == ZoneType.FightInProgress:
                target_en, distance_en = self.game_logic.get_closest_enemy(cell, zone)
                target_no, distance_no = self.game_logic.get_closest_empty(cell, zone)
                if target_no and (distance_no == 1):
                    return Move(cell, target_no, zone, distance_no)
                elif target_en:
                    return Move(cell, target_en, zone, distance_en)
            elif zone.type == ZoneType.GuaranteedMy:
                target, distance = self.game_logic.get_closest_empty(cell, zone)
                if target:
                    return Move(cell, target, zone, distance)
        return None  # type: ignore

    def get_moves(self) -> list[str]:
        moves: list[Move] = []
        for zone in self.game_logic.zones:
            for cell in zone.cells:
                move = self.get_move_target(zone, cell)
                if move:
                    moves.append(move)

        # repeat = True
        # while repeat:
        #     for i in range(len(moves)):
        #         if moves[i].target is None:
        #             moves[i] = self.get_move_target(moves[i].zone, moves[i].cell)

        #     repeat = False
        #     for i in range(len(moves)):
        #         if moves[i].target is not None:
        #             if moves[i].target.Owner == OwnerType.No:
        #                 moves[i].target.Owner = OwnerType.My
        #             for j in range(len(moves)):
        #                 if (
        #                     (i != j)
        #                     and (moves[i].target == moves[j].target)
        #                     and moves[i].target.Owner != OwnerType.En
        #                 ):
        #                     repeat = True
        #                     if distances[i] < distances[j]:
        #                         targets[j] = None
        #                         distances[j] = 10000
        #                     else:
        #                         targets[i] = None
        #                         distances[i] = 10000
        #                         break

        move_cmds = []
        for move in moves:
            if move.cell.Units > 2:
                move.cell.Units = 2
            move_cmds.append(
                f"MOVE {move.cell.Units} {move.cell.x} {move.cell.y} {move.target.x} {move.target.y}"
            )
        return move_cmds


class StrategySplits(Strategy):
    def post_init(self, game_logic: "GameLogic") -> None:
        self.game_logic = game_logic

    def get_spawns(self) -> list[str]:
        sd = StrategyDefault()
        sd.post_init(self.game_logic)
        return sd.get_spawns()

    def get_builds(self) -> list[str]:
        sd = StrategyDefault()
        sd.post_init(self.game_logic)
        return sd.get_builds()

    def get_moves(self) -> list[str]:
        sd = StrategyDefault()
        sd.post_init(self.game_logic)
        return sd.get_moves()


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
        game_logic.recycler_my = 0
        game_logic.recycler_en = 0
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
                cell.scrap_amount = scrap_amount
                cell.Owner = OwnerType(owner)
                cell.Units = units
                cell.Recycler = True if recycler == 1 else False
                cell.CanBuild = True if can_build == 1 else False
                cell.CanSpawn = True if can_spawn == 1 else False
                cell.InRangeOfRecycler = True if in_range_of_recycler == 1 else False
                cell.x = j
                cell.y = i
                if cell.Recycler and cell.Owner == OwnerType.My:
                    game_logic.recycler_my += 1
                if cell.Recycler and cell.Owner == OwnerType.En:
                    game_logic.recycler_en += 1
                game_logic.map.cells[i][j] = cell

        return game_logic


def main():
    random.seed(18081991)
    # ih = InputHandler(input=InputHandler.__input_debugger__)  # type: ignore
    ih = InputHandler()  # type: ignore
    gl = GameLogic(StrategyDefault())

    gl = ih.read_initial_input(gl)
    while True:
        gl = ih.read_turn_input(gl)
        gl.preprocess()
        moves = gl.get_moves()
        builds = gl.get_builds()
        spawns = gl.get_spawns()
        if (len(moves) == 0) and (len(builds) == 0) and (len(spawns) == 0):
            print("WAIT")
        else:
            print(";".join(builds + spawns + moves))


if __name__ == "__main__":
    main()
