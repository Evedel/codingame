#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from bot import Cell, CellType, Map


class Inputs:
    def generate_I_00_expected_map(self):
        ################# INITIAL INPUT #################

        self.read_indx = -1

        def input():
            self.read_indx += 1
            return self.I_00[self.read_indx]

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

    def generate_I_01_expected_map(self):
        self.I_01_MAP = self.I_00_MAP.deepcopy()
        for cell in self.I_01_MAP.cells:
            cell.resource = 999
            cell.my_ants = 999
            cell.opp_ants = 999

        self.read_indx = -1

        def input():
            self.read_indx += 1
            return self.I_00[self.read_indx]

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

    I_00 = [
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
    I_01 = [
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
