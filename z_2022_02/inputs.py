from z_2022_02.bot import Cell, Map, OwnerType


class Inputs:
    def __init__(self):
        w = self.I1[0].split(" ")[0]
        h = self.I1[0].split(" ")[1]

        for i in range(int(h)):
            self.I1_MAP.cells.append([])
            for j in range(int(w)):
                l = i * int(w) + j + 2
                (
                    scrap_amount,
                    owner,
                    units,
                    recycler,
                    can_build,
                    can_spawn,
                    in_range_of_recycler,
                ) = [int(k) for k in self.I1[l].split()]
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
                self.I1_MAP.cells[i].append(cell)

    I1 = [
        "20 10",  # 0
        "10 10",  # 1
        "0 -1 0 0 0 0 0",  # 2
        "0 -1 0 0 0 0 0",  # 3
        "0 -1 0 0 0 0 0",  # 4
        "0 -1 0 0 0 0 0",  # 5
        "0 -1 0 0 0 0 0",  # 6
        "8 -1 0 0 0 0 0",  # 7
        "10 -1 0 0 0 0 0",  # 8
        "6 -1 0 0 0 0 0",  # 9
        "8 -1 0 0 0 0 0",  # 10
        "9 -1 0 0 0 0 0",  # 11
        "9 -1 0 0 0 0 0",  # 12
        "8 -1 0 0 0 0 0",  # 13
        "6 -1 0 0 0 0 0",  # 14
        "10 -1 0 0 0 0 0",  # 15
        "8 -1 0 0 0 0 0",  # 16
        "0 -1 0 0 0 0 0",  # 17
        "0 -1 0 0 0 0 0",  # 18
        "0 -1 0 0 0 0 0",  # 19
        "0 -1 0 0 0 0 0",  # 20
        "0 -1 0 0 0 0 0",  # 21
        "8 -1 0 0 0 0 0",  # 22
        "0 -1 0 0 0 0 0",  # 23
        "0 -1 0 0 0 0 0",  # 24
        "0 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "10 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "10 -1 0 0 0 0 0",
        "6 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "6 -1 0 0 0 0 0",
        "10 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "10 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "6 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "6 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "6 -1 0 0 0 0 0",
        "9 -1 0 0 0 0 0",
        "9 -1 0 0 0 0 0",
        "6 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "6 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "6 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "6 -1 0 0 0 0 0",
        "1 1 1 0 0 1 0",
        "8 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "10 -1 0 0 0 0 0",
        "10 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "9 -1 0 0 0 0 0",
        "9 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "10 -1 0 0 0 0 0",
        "10 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "1 0 1 0 0 0 0",
        "6 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "10 -1 0 0 0 0 0",
        "1 1 1 0 0 1 0",
        "10 1 0 0 1 1 0",
        "8 1 1 0 0 1 0",
        "8 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "10 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "10 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "8 0 1 0 0 0 0",
        "10 0 0 0 0 0 0",
        "1 0 1 0 0 0 0",
        "10 -1 0 0 0 0 0",
        "6 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "1 1 1 0 0 1 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "6 -1 0 0 0 0 0",
        "9 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "9 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "9 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "9 -1 0 0 0 0 0",
        "6 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "1 0 1 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "6 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "9 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "9 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "6 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "6 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "9 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "9 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "6 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "10 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "10 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "6 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "6 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "6 -1 0 0 0 0 0",
        "10 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "10 -1 0 0 0 0 0",
        "6 -1 0 0 0 0 0",
        "6 -1 0 0 0 0 0",
        "10 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "10 -1 0 0 0 0 0",
        "6 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "6 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "9 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "10 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "10 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "10 -1 0 0 0 0 0",
        "10 -1 0 0 0 0 0",
        "8 -1 0 0 0 0 0",
        "10 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "10 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "9 -1 0 0 0 0 0",
    ]
    I1_MAP = Map()

    zone_i1 = [
        "3 3",
        "10 10",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "1 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
    ]
    zone_i2 = [
        "3 3",
        "10 10",
        "1 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
    ]
    zone_i3 = [
        "3 3",
        "10 10",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "1 -1 0 0 0 0 0",
    ]
    # 0 0 0
    # 0 0 0
    # 1 1 1
    zone_i4 = [
        "3 3",
        "10 10",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "1 -1 0 0 0 0 0",
        "1 -1 0 0 0 0 0",
        "1 -1 0 0 0 0 0",
    ]
    # 1 0 0
    # 1 0 0
    # 1 0 0
    zone_i5 = [
        "3 3",
        "10 10",
        "1 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "1 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "1 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
    ]
    # 1 0 0
    # 0 1 0
    # 0 0 1
    zone_i6 = [
        "3 3",
        "10 10",
        "1 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "1 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "1 -1 0 0 0 0 0",
    ]
    # 0 1 0
    # 0 R 0
    # 0 1 0
    zone_i7 = [
        "3 3",
        "10 10",
        "0 -1 0 0 0 0 0",
        "1 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "1 -1 0 1 0 0 0",
        "0 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
        "1 -1 0 0 0 0 0",
        "0 -1 0 0 0 0 0",
    ]