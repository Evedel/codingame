#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from bot import Cell, CellType, Map


class Inputs:
    def generate_I_000_expected_map(self):
        ################# INITIAL INPUT #################

        self.read_indx = -1

        def input():
            self.read_indx += 1
            return self.I_000[self.read_indx]

        number_of_cells = int(input())  # amount of hexagonal cells in this map
        self.I_00_MAP = Map(number_of_cells)

        for i in range(number_of_cells):
            # _type: 0 for empty, 1 for eggs, 2 for crystal
            # initial_resources: the initial amount of eggs/crystals on this cell
            # neigh_0: the index of the neighbouring cell for each direction
            (
                _type,
                initial_resources,
                neigh_0,
                neigh_1,
                neigh_2,
                neigh_3,
                neigh_4,
                neigh_5,
            ) = [int(j) for j in input().split()]
            self.I_00_MAP.cells[i].id = i
            self.I_00_MAP.cells[i].resource = initial_resources

            def get_cell_or_none(id: int) -> Cell:
                if id == -1:
                    return None
                return self.I_00_MAP.cells[id]

            self.I_00_MAP.cells[i].neighbours = [
                get_cell_or_none(neigh_0),
                get_cell_or_none(neigh_1),
                get_cell_or_none(neigh_2),
                get_cell_or_none(neigh_3),
                get_cell_or_none(neigh_4),
                get_cell_or_none(neigh_5),
            ]
            self.I_00_MAP.cells[i].type = CellType(_type)

        number_of_bases = int(input())
        for i in input().split():
            my_base_index = int(i)
            self.I_00_MAP.cells[my_base_index].my_base = True
        for i in input().split():
            opp_base_index = int(i)
            self.I_00_MAP.cells[opp_base_index].opp_base = True

    def generate_I_001_expected_map(self):
        self.generate_I_000_expected_map()
        self.I_01_MAP = self.I_00_MAP.deepcopy()
        for cell in self.I_01_MAP.cells:
            cell.resource = 999
            cell.my_ants = 999
            cell.opp_ants = 999

        self.read_indx = -1

        def input():
            self.read_indx += 1
            return self.I_001[self.read_indx]

        ################# GAME LOOP #################

        for i in range(self.I_00_MAP.size):
            # resources: the current amount of eggs/crystals on this cell
            # my_ants: the amount of your ants on this cell
            # opp_ants: the amount of opponent ants on this cell
            resources, my_ants, opp_ants = [int(j) for j in input().split()]
            self.I_01_MAP.cells[i].resource = resources
            self.I_01_MAP.cells[i].my_ants = my_ants
            self.I_01_MAP.cells[i].opp_ants = opp_ants

        # Write an action using print

    I_000 = [
        "33",
        "2 51 1 -1 3 2 -1 4",
        "0 0 5 7 -1 0 4 14",
        "0 0 0 3 13 6 8 -1",
        "0 0 -1 9 11 13 2 0",
        "0 0 14 1 0 -1 10 12",
        "0 0 15 17 7 1 14 24",
        "0 0 2 13 23 16 18 8",
        "0 0 17 19 -1 -1 1 5",
        "0 0 -1 2 6 18 20 -1",
        "0 0 -1 -1 -1 11 3 -1",
        "0 0 12 4 -1 -1 -1 -1",
        "0 0 9 -1 -1 21 13 3",
        "0 0 22 14 4 10 -1 -1",
        "0 0 3 11 21 23 6 2",
        "0 0 24 5 1 4 12 22",
        "0 0 25 27 17 5 24 -1",
        "0 0 6 23 -1 26 28 18",
        "0 0 27 29 19 7 5 15",
        "0 0 8 6 16 28 30 20",
        "2 41 29 -1 -1 -1 7 17",
        "2 41 -1 8 18 30 -1 -1",
        "0 0 11 -1 -1 31 23 13",
        "0 0 32 24 14 12 -1 -1",
        "0 0 13 21 31 -1 16 6",
        "0 0 -1 15 5 14 22 32",
        "0 0 -1 -1 27 15 -1 -1",
        "0 0 16 -1 -1 -1 -1 28",
        "0 0 -1 -1 29 17 15 25",
        "0 0 18 16 26 -1 -1 30",
        "0 0 -1 -1 -1 19 17 27",
        "0 0 20 18 28 -1 -1 -1",
        "2 5 21 -1 -1 -1 -1 23",
        "2 5 -1 -1 24 22 -1 -1",
        "1",
        "13",
        "14",
    ]
    I_001 = [
        "51 0 0",
        "0 0 0",
        "0 0 0",
        "0 0 0",
        "0 0 0",
        "0 0 0",
        "0 0 0",
        "0 0 0",
        "0 0 0",
        "0 0 0",
        "0 0 0",
        "0 0 0",
        "0 0 0",
        "0 60 0",
        "0 0 60",
        "0 0 0",
        "0 0 0",
        "0 0 0",
        "0 0 0",
        "41 0 0",
        "41 0 0",
        "0 0 0",
        "0 0 0",
        "0 0 0",
        "0 0 0",
        "0 0 0",
        "0 0 0",
        "0 0 0",
        "0 0 0",
        "0 0 0",
        "0 0 0",
        "5 0 0",
        "5 0 0",
    ]

    # seed=3870138661657571000
    I_011 = [
        "37",
        "2 49 1 3 -1 2 4 -1",
        "2 48 -1 5 3 0 -1 14",
        "2 48 0 -1 13 -1 6 4",
        "0 0 5 7 9 -1 0 1",
        "0 0 -1 0 2 6 8 10",
        "2 57 17 -1 7 3 1 -1",
        "2 57 4 2 -1 18 -1 8",
        "1 36 -1 -1 -1 9 3 5",
        "1 36 10 4 6 -1 -1 -1",
        "0 0 7 -1 -1 11 -1 3",
        "0 0 12 -1 4 8 -1 -1",
        "0 0 9 -1 -1 19 13 -1",
        "0 0 20 14 -1 10 -1 -1",
        "0 0 -1 11 19 -1 -1 2",
        "0 0 -1 -1 1 -1 12 20",
        "0 0 21 23 17 -1 -1 30",
        "0 0 -1 -1 29 22 24 18",
        "0 0 23 25 -1 5 -1 15",
        "0 0 6 -1 16 24 26 -1",
        "0 0 11 -1 -1 27 -1 13",
        "0 0 28 -1 14 12 -1 -1",
        "0 0 -1 31 23 15 30 36",
        "0 0 16 29 35 -1 32 24",
        "1 24 31 -1 25 17 15 21",
        "1 24 18 16 22 32 -1 26",
        "2 41 -1 -1 -1 -1 17 23",
        "2 41 -1 18 24 -1 -1 -1",
        "1 26 19 -1 -1 33 29 -1",
        "1 26 34 30 -1 20 -1 -1",
        "0 0 -1 27 33 35 22 16",
        "0 0 36 21 15 -1 28 34",
        "0 0 -1 -1 -1 23 21 -1",
        "0 0 24 22 -1 -1 -1 -1",
        "0 0 27 -1 -1 -1 35 29",
        "0 0 -1 36 30 28 -1 -1",
        "1 16 29 33 -1 -1 -1 22",
        "1 16 -1 -1 21 30 34 -1",
        "1",
        "11",
        "12",
    ]

    I_012 = [
        "49 0 0",
        "48 0 0",
        "48 0 0",
        "0 0 0",
        "0 0 0",
        "57 0 0",
        "57 0 0",
        "36 0 0",
        "36 0 0",
        "0 0 0",
        "0 0 0",
        "0 10 0",
        "0 0 10",
        "0 0 0",
        "0 0 0",
        "0 0 0",
        "0 0 0",
        "0 0 0",
        "0 0 0",
        "0 0 0",
        "0 0 0",
        "0 0 0",
        "0 0 0",
        "24 0 0",
        "24 0 0",
        "41 0 0",
        "41 0 0",
        "26 0 0",
        "26 0 0",
        "0 0 0",
        "0 0 0",
        "0 0 0",
        "0 0 0",
        "0 0 0",
        "0 0 0",
        "16 0 0",
        "16 0 0",
    ]

    # seed=-1829770381140261000
    I_021 = [
        "29",
        "0 0 1 -1 -1 2 -1 -1",
        "1 37 3 5 -1 0 -1 14",
        "1 37 0 -1 13 4 6 -1",
        "0 0 -1 15 5 1 14 20",
        "0 0 2 13 19 -1 16 6",
        "0 0 15 17 7 -1 1 3",
        "0 0 -1 2 4 16 18 8",
        "0 0 17 -1 -1 9 -1 5",
        "0 0 10 -1 6 18 -1 -1",
        "0 0 7 -1 -1 11 -1 -1",
        "0 0 12 -1 -1 8 -1 -1",
        "0 0 9 -1 -1 -1 13 -1",
        "0 0 -1 14 -1 10 -1 -1",
        "0 0 -1 11 -1 19 4 2",
        "0 0 20 3 1 -1 12 -1",
        "0 0 23 25 17 5 3 -1",
        "0 0 6 4 -1 24 26 18",
        "0 0 25 -1 -1 7 5 15",
        "0 0 8 6 16 26 -1 -1",
        "0 0 13 -1 27 -1 -1 4",
        "0 0 -1 -1 3 14 -1 28",
        "2 190 -1 -1 23 -1 -1 -1",
        "2 190 -1 -1 -1 -1 -1 24",
        "0 0 -1 -1 25 15 -1 21",
        "0 0 16 -1 22 -1 -1 26",
        "2 440 -1 -1 -1 17 15 23",
        "2 440 18 16 24 -1 -1 -1",
        "1 15 -1 -1 -1 -1 -1 19",
        "1 15 -1 -1 20 -1 -1 -1",
        "1",
        "18",
        "17",
    ]
    I_022 = [
        "0 0 0",
        "20 0 0",
        "20 2 0",
        "0 0 0",
        "0 0 0",
        "0 0 0",
        "0 0 0",
        "0 0 0",
        "0 0 0",
        "0 0 0",
        "0 0 0",
        "0 0 0",
        "0 0 0",
        "0 0 0",
        "0 0 0",
        "0 0 0",
        "0 0 0",
        "0 0 10",
        "0 10 0",
        "0 0 0",
        "0 0 0",
        "190 0 0",
        "190 0 0",
        "0 0 0",
        "0 0 0",
        "440 0 0",
        "440 0 0",
        "15 0 0",
        "15 0 0",
    ]
