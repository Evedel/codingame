import sys
import math

debug = True
def dp(s):
  if debug: print(s, file=sys.stderr, flush=True)

number_of_cells = int(input())  # 37
for i in range(number_of_cells):
    # index: 0 is the center cell, the next cells spiral outwards
    # richness: 0 if the cell is unusable, 1-3 for usable cells
    # neigh_0: the index of the neighbouring cell for each direction
    index, richness, neigh_0, neigh_1, neigh_2, neigh_3, neigh_4, neigh_5 = [int(j) for j in input().split()]
    # dp(str(index)+" "+str(richness) + " "+str(neigh_0)+" "+str(neigh_1)+" "+str(neigh_2)+" "+str(neigh_3)+" "+str(neigh_4)+" "+str(neigh_5))

# game loop
while True:
    day = int(input())  # the game lasts 24 days: 0-23
    nutrients = int(input())  # the base score you gain from the next COMPLETE action
    # sun: your sun points
    # score: your current score
    sun, score = [int(i) for i in input().split()]
    inputs = input().split()
    opp_sun = int(inputs[0])  # opponent's sun points
    opp_score = int(inputs[1])  # opponent's score
    opp_is_waiting = inputs[2] != "0"  # whether your opponent is asleep until the next day
    number_of_trees = int(input())  # the current amount of trees
    max_index = 0
    max_size = 0
    size_2_trees = 0
    size_3_trees = 0
    for i in range(number_of_trees):
        inputs = input().split()
        cell_index = int(inputs[0])  # location of this tree
        size = int(inputs[1])  # size of this tree: 0-3
        is_mine = inputs[2] != "0"  # 1 if this is your tree
        is_dormant = inputs[3] != "0"  # 1 if this tree is dormant
        if is_mine:
            if size == 2:
                size_2_trees += 1
            if size == 3:
                size_3_trees += 1

            if size > max_size:
                max_size = size
                max_index = cell_index
    number_of_possible_actions = int(input())  # all legal actions
    for i in range(number_of_possible_actions):
        possible_action = input()  # try printing something from here to start with

    # GROW cellIdx | SEED sourceIdx targetIdx | COMPLETE cellIdx | WAIT <message>
    if (max_size == 1) and (sun >= 3 + size_2_trees):
        print("GROW "+str(max_index))
    elif (max_size == 2) and (sun >= 7 + size_3_trees):
        print("GROW "+str(max_index))
    elif (max_size == 3) and (sun >= 4):
        print("COMPLETE "+str(max_index))
    else:
        print("WAIT")