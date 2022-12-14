from enum import Enum
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


class GameLogic:
    def __init__(self):
        self.my_id: int = 0
        self.en_id: int = 0
        self.width: int = 0
        self.height: int = 0
        self.my_matter: int = 0
        self.en_matter: int = 0
        self.map: Map = Map()


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
                game_logic.map.cells[i][j] = cell

        return game_logic


def main():
    # ih = InputHandler(input=InputHandler.__input_debugger__)  # type: ignore
    ih = InputHandler()  # type: ignore
    gl = GameLogic()

    gl = ih.read_initial_input(gl)
    while True:
        gl = ih.read_turn_input(gl)
        gl.map.print_map()
        print("WAIT")


if __name__ == "__main__":
    main()
