from dataclasses import dataclass
from mimetypes import common_types
import sys
import math
import copy
from enum import Enum


class EntityType(Enum):
    Wall = -2
    Empty = -1
    MyLeader = 0
    MyWarior = 1
    EnLeader = 2
    EnWarior = 3
    Neutral = 4


@dataclass
class Cell:
    entity: EntityType

    def to_map(self):
        if self.entity == EntityType.Wall:
            return "x"
        elif self.entity == EntityType.Empty:
            return "."
        elif self.entity == EntityType.MyLeader:
            return "M"
        elif self.entity == EntityType.MyWarior:
            return "i"
        elif self.entity == EntityType.EnLeader:
            return "m"
        elif self.entity == EntityType.EnWarior:
            return "l"
        elif self.entity == EntityType.Neutral:
            return "o"
        else:
            return "?"


@dataclass
class Unit:
    id: int
    type: EntityType = None
    pos_x: int = None
    pos_y: int = None


class PathSearcher:
    @dataclass
    class Path:
        path: list = None
        cost: int = None
        dist: float = None

    def get_possible_moves(self, x: int, y: int, map: list[list[Cell]]):
        moves = []
        if x > 0 and map[y][x - 1].entity == EntityType.Empty:
            moves.append((x - 1, y))
        if x < 12 and map[y][x + 1].entity == EntityType.Empty:
            moves.append((x + 1, y))
        if y > 0 and map[y - 1][x].entity == EntityType.Empty:
            moves.append((x, y - 1))
        if y < 6 and map[y + 1][x].entity == EntityType.Empty:
            moves.append((x, y + 1))
        return moves

    def get_occupied_by(
        self, x: int, y: int, unit_type: EntityType, map: list[list[Cell]]
    ):
        moves = []
        if x > 0 and map[y][x - 1].entity == unit_type:
            moves.append((x - 1, y))
        if x < 12 and map[y][x + 1].entity == unit_type:
            moves.append((x + 1, y))
        if y > 0 and map[y - 1][x].entity == unit_type:
            moves.append((x, y - 1))
        if y < 6 and map[y + 1][x].entity == unit_type:
            moves.append((x, y + 1))
        return moves

    @staticmethod
    def dist(x1: int, y1: int, x2: int, y2: int) -> float:
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    @staticmethod
    def walls_collision(x0: int, y0: int, x1: int, y1: int, map: list[list[Cell]]):
        # always draw a line from smallest y
        if y0 < y1:
            p0 = (x0, y0)
            p1 = (x1, y1)
        else:
            p1 = (x0, y0)
            p0 = (x1, y1)

        # chose where there are more steps
        line = lambda x: x
        is_wall = lambda x: x
        if abs(p1[0] - p0[0]) > abs(p1[1] - p0[1]):
            # if dx > dy => more x cells, use y=f(x) from p0 to p1
            i_start = p0[0]
            i_end = p1[0]
            i_step = 1 if i_start < i_end else -1
            line = lambda x: (p1[1] - p0[1]) / (p1[0] - p0[0]) * (x - p0[0]) + p0[1]

            def local_is_wall(i: int):
                xi = i
                yi = line(xi)
                if yi % 1 == 0.5:
                    yi0 = math.floor(yi)
                    yi1 = math.ceil(yi)
                    return (
                        map[yi0][xi].entity == EntityType.Wall
                        or map[yi1][xi].entity == EntityType.Wall
                        or map[yi0][xi].entity == EntityType.Neutral
                        or map[yi1][xi].entity == EntityType.Neutral
                    )
                else:
                    return (
                        map[round(yi)][xi].entity == EntityType.Wall
                        or map[round(yi)][xi].entity == EntityType.Neutral
                    )

            is_wall = local_is_wall
        else:
            # if dy > dx => more y cells, use x=f(y) from p0 to p1
            i_start = p0[1]
            i_end = p1[1]
            i_step = 1 if i_start < i_end else -1
            line = lambda y: (p1[0] - p0[0]) / (p1[1] - p0[1]) * (y - p0[1]) + p0[0]

            def local_is_wall(i: int):
                yi = i
                xi = line(yi)
                if xi % 1 == 0.5:
                    xi0 = math.floor(xi)
                    xi1 = math.ceil(xi)
                    return (
                        map[yi][xi0].entity == EntityType.Wall
                        or map[yi][xi1].entity == EntityType.Wall
                        or map[yi][xi0].entity == EntityType.Neutral
                        or map[yi][xi1].entity == EntityType.Neutral
                    )
                else:
                    return (
                        map[yi][round(xi)].entity == EntityType.Wall
                        or map[yi][round(xi)].entity == EntityType.Neutral
                    )

            is_wall = local_is_wall

        # check if there is a wall on the line
        for i in range(i_start, i_end, i_step):
            if is_wall(i):
                return True

        return False

    def path_search(
        self,
        from_x: int,
        from_y: int,
        to_x: int,
        to_y: int,
        map: list[list[Cell]],
        unit_type: EntityType = EntityType.Empty,
    ):
        path_queue = [
            self.Path(
                path=[(from_x, from_y)],
                cost=0,
                dist=PathSearcher.dist(from_x, from_y, to_x, to_y),
            )
        ]

        InputHandler.ddp("Searching path from", from_x, from_y, "to", to_x, to_y)
        iter = 0
        while True:
            # print(path_queue[0])
            iter += 1
            if iter > 100:
                return None
            if len(path_queue) == 0:
                return None
            current_path = path_queue.pop(0)
            moves = self.get_occupied_by(
                current_path.path[-1][0],
                current_path.path[-1][1],
                EntityType.Empty,
                map,
            )
            if unit_type != EntityType.Empty:
                units = self.get_occupied_by(
                    current_path.path[-1][0], current_path.path[-1][1], unit_type, map
                )
                for unit in units:
                    if unit[0] == to_x and unit[1] == to_y:
                        new_path = copy.deepcopy(current_path)
                        new_path.path.append(unit)
                        new_path.cost += 1
                        new_path.dist = 0
                        return new_path
            for move in moves:
                if move[0] == to_x and move[1] == to_y:
                    new_path = copy.deepcopy(current_path)
                    new_path.path.append(move)
                    new_path.cost += 1
                    new_path.dist = 0
                    return new_path
                else:
                    if move not in current_path.path:
                        new_path = copy.deepcopy(current_path)
                        new_path.path.append(move)
                        new_path.cost += 1
                        new_path.dist = self.dist(move[0], move[1], to_x, to_y)
                        # insert before the next path with a bigger dist
                        path_queue.insert(
                            next(
                                (
                                    i
                                    for i, path in enumerate(path_queue)
                                    if path.dist > new_path.dist
                                ),
                                len(path_queue),
                            ),
                            new_path,
                        )
            # sleep(2)


class GameLogic:
    __MY_ID__: int
    __EN_ID__: int

    def find_units_by_type(self, units: list[Unit], type: EntityType):
        return [unit for unit in units if unit.type == type]

    def find_nearest_neutral(self, leader, units: list[Unit]):
        nearest_neutral = None
        nearest_dist = 1000
        for u in units:
            if u.type == EntityType.Neutral:
                dist = PathSearcher.dist(leader.pos_x, leader.pos_y, u.pos_x, u.pos_y)
                if dist < nearest_dist:
                    nearest_dist = dist
                    nearest_neutral = u

        return nearest_neutral

    def convert_nuetral(self, units: list[Unit], map: list[list[Cell]]):
        ps = PathSearcher()

        my_leader = self.find_units_by_type(units, EntityType.MyLeader)[0]
        neutrals = self.find_units_by_type(units, EntityType.Neutral)

        command = "WAIT"
        best_path = None
        best_cost = 1000
        best_neutral = None
        for neutral in neutrals:
            path = ps.path_search(
                my_leader.pos_x,
                my_leader.pos_y,
                neutral.pos_x,
                neutral.pos_y,
                map,
                EntityType.Neutral,
            )
            if path is not None and path.cost <= best_cost:
                best_path = path
                best_cost = path.cost
                best_neutral = neutral

        if best_path is not None:
            if len(best_path.path) == 2:
                command = f"{my_leader.id} CONVERT {best_neutral.id}"
            else:
                command = (
                    f"{my_leader.id} MOVE {best_path.path[1][0]} {best_path.path[1][1]}"
                )
        return command

    def make_turn(self, units: list[Unit], map: list[list[Cell]]):
        command = "WAIT"

        my_wariors = self.find_units_by_type(units, EntityType.MyWarior)
        my_leader = self.find_units_by_type(units, EntityType.MyLeader)[0]
        neutrals = self.find_units_by_type(units, EntityType.Neutral)

        command = self.check_convenient_convert(my_leader, neutrals)

        command = self.check_convenient_shoot(units, map)

        if command == "WAIT":
            command = self.convert_nuetral(units, map)

        InputHandler.ddp(command)

        # cannot reach any units to convert
        if command == "WAIT":
            neutrals = self.find_units_by_type(units, EntityType.Neutral)
            # but still there are some other neutrals
            # then lets try to shuffle my furthest warrior closser to enemy leader
            if len(neutrals) > 0:
                command = self.fight_shuffle_closer_to_leader(units, map)

        return command

    def fight_general(self, units: list[Unit], map: list[list[Cell]]):
        ps = PathSearcher()
        my_wariors = self.find_units_by_type(units, EntityType.MyWarior)
        en_leader = self.find_units_by_type(units, EntityType.EnLeader)[0]
        en_wariors = self.find_units_by_type(units, EntityType.EnWarior)

        closest_enemy = None
        closest_waroir = None
        closest_path = None
        closest_dist = 1000
        for w in my_wariors:
            for e in en_wariors:
                path = ps.path_search(
                    w.pos_x, w.pos_y, e.pos_x, e.pos_y, map, EntityType.EnWarior
                )
                if path is not None and path.cost < closest_dist:
                    closest_dist = path.cost
                    closest_enemy = e
                    closest_waroir = w
                    closest_path = path
        for w in my_wariors:
            path = ps.path_search(
                w.pos_x,
                w.pos_y,
                en_leader.pos_x,
                en_leader.pos_y,
                map,
                EntityType.EnLeader,
            )
            if path is not None and path.cost <= closest_dist:
                closest_dist = path.cost
                closest_enemy = en_leader
                closest_waroir = w
                closest_path = path

        command = "WAIT"
        if closest_path is not None:
            p0 = (closest_waroir.pos_x, closest_waroir.pos_y)
            p1 = (closest_enemy.pos_x, closest_enemy.pos_y)
            dist = ps.dist(p0[0], p0[1], p1[0], p1[1])
            are_there_walls = ps.walls_collision(p0[0], p0[1], p1[0], p1[1], map)
            if (dist < 6) and (not are_there_walls):
                command = f"{closest_waroir.id} SHOOT {closest_enemy.id}"
            else:
                command = f"{closest_waroir.id} MOVE {closest_path.path[1][0]} {closest_path.path[1][1]}"

        return command

    def check_convenient_convert(self, my_leader: list[Unit], neutral: list[Unit]):
        ps = PathSearcher()
        for n in neutral:
            InputHandler.ddp(
                "check_convenient_convert",
                ps.dist(my_leader.pos_x, my_leader.pos_y, n.pos_x, n.pos_y),
            )
            if ps.dist(my_leader.pos_x, my_leader.pos_y, n.pos_x, n.pos_y) == 1.0:
                InputHandler.ddp(
                    f"check_convenient_convert return {n.id}",
                )
                return f"{my_leader.id} CONVERT {n.id}"
        return "WAIT"

    def check_convenient_shoot(self, units: list[Unit], map: list[Unit]):
        ps = PathSearcher()
        my_wariors = self.find_units_by_type(units, EntityType.MyWarior)
        en_leaders = self.find_units_by_type(units, EntityType.EnLeader)
        en_wariors = self.find_units_by_type(units, EntityType.EnWarior)

        closest_enemy = None
        closest_waroir = None
        closest_dist = 1000
        command = "WAIT"
        for w in my_wariors:
            for e in en_wariors + en_leaders:
                dist = ps.dist(w.pos_x, w.pos_y, e.pos_x, e.pos_y)
                are_there_walls = ps.walls_collision(
                    w.pos_x, w.pos_y, e.pos_x, e.pos_y, map
                )
                if (dist < 7) and (dist <= closest_dist) and (not are_there_walls):
                    closest_enemy = e
                    closest_waroir = w
                    closest_dist = dist
                    command = f"{closest_waroir.id} SHOOT {closest_enemy.id}"
        return command

    def fight_shuffle_closer_to_leader(self, units: list[Unit], map: list[list[Cell]]):
        ps = PathSearcher()
        my_wariors = self.find_units_by_type(units, EntityType.MyWarior)
        en_leader = self.find_units_by_type(units, EntityType.EnLeader)[0]

        best_warior = None
        best_dist = 0
        for w in my_wariors:
            dist = ps.dist(
                w.pos_x,
                w.pos_y,
                en_leader.pos_x,
                en_leader.pos_y,
            )
            if dist > best_dist:
                best_dist = dist
                best_warior = w

        moves = ps.get_possible_moves(best_warior.pos_x, best_warior.pos_y, map)
        best_move = None
        best_dist = 1000
        for m in moves:
            dist = ps.dist(
                m[0],
                m[1],
                en_leader.pos_x,
                en_leader.pos_y,
            )
            if dist < best_dist:
                best_dist = dist
                best_move = m

        command = "WAIT"
        if best_warior is not None:
            command = f"{best_warior.id} MOVE {best_move[0]} {best_move[1]}"

        return command


class InputHandler:
    __DEBUG__ = False

    def __init__(self, input=input):
        self.input = input

    @staticmethod
    def __input_debugger__():
        res = input()
        InputHandler.dp(f'"{res}",')
        return res

    @staticmethod
    def dp(*args, **kwargs):
        print(*args, file=sys.stderr, **kwargs)

    @staticmethod
    def ddp(*args, **kwargs):
        if InputHandler.__DEBUG__:
            print(*args, file=sys.stderr, **kwargs)

    @staticmethod
    def print_map(map: list[list[Cell]]):
        print(file=sys.stderr)
        for row in map:
            for cell in row:
                print(cell.to_map(), end=" ", file=sys.stderr)
            print(file=sys.stderr)

    @staticmethod
    def print_path(map: list[list[Cell]], path):
        print(file=sys.stderr)
        for y, row in enumerate(map):
            for x, cell in enumerate(row):
                if ((x, y) in path) and cell.entity == EntityType.Empty:
                    print("+", end=" ", file=sys.stderr)
                else:
                    print(cell.to_map(), end=" ", file=sys.stderr)
            print(file=sys.stderr)

    def read_initial_input(self, map):
        my_id = int(self.input())
        en_id = 1 - my_id

        GameLogic.__MY_ID__ = my_id
        GameLogic.__EN_ID__ = en_id

        width, height = [int(i) for i in self.input().split()]
        map = []
        for i in range(height):
            map.append([])
            line = self.input()
            for j, c in enumerate(line):
                unit_type = EntityType.Empty
                if c == ".":
                    unit_type = EntityType.Empty
                elif c == "x":
                    unit_type = EntityType.Wall
                map[i].append(Cell(entity=unit_type))
        return map

    def read_turn_input(
        self, map: list[list[Cell]], units: list[Unit], map0: list[list[Cell]]
    ):
        units.clear()
        map = copy.deepcopy(map0)
        num_of_units = int(self.input())
        for i in range(num_of_units):
            unit_id, unit_type, hp, x, y, owner = [int(j) for j in self.input().split()]
            entity_type = None
            if (unit_type == 0) and (owner == GameLogic.__EN_ID__):
                entity_type = EntityType.EnWarior
            if (unit_type == 1) and (owner == GameLogic.__EN_ID__):
                entity_type = EntityType.EnLeader
            if (unit_type == 0) and (owner == GameLogic.__MY_ID__):
                entity_type = EntityType.MyWarior
            if (unit_type == 1) and (owner == GameLogic.__MY_ID__):
                entity_type = EntityType.MyLeader
            if owner == 2:
                entity_type = EntityType.Neutral

            map[y][x].entity = entity_type
            units.append(Unit(unit_id, entity_type, x, y))

        return map, units


def main():
    dp = InputHandler.dp
    print_map = InputHandler.print_map
    print_path = InputHandler.print_path

    def move_leader_to_neutral():
        pass

    map0: list[list[Cell]] = []

    map: list[list[Cell]] = []
    units: list[Unit] = []

    ih = InputHandler(input=InputHandler.__input_debugger__)
    gl = GameLogic()

    map0 = ih.read_initial_input(map0)

    while True:
        map, units = ih.read_turn_input(map, units, map0)
        command = gl.make_turn(units, map)
        # WAIT | unitId MOVE x y | unitId SHOOT target| unitId CONVERT target
        print(command)


if __name__ == "__main__":
    main()
