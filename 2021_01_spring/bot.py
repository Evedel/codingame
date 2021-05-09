import sys
import math

debug = True
def dp(s):
  if debug: print(s, file=sys.stderr, flush=True)

# will convert the hex tree into gorgeous matrux that can be printed into console
# depth first recursive search
# output example
#
# ...1.1.1.1...
# ..1.0.2.2.1..
# .1.2.3.3.2.1.
# 1.2.3.3.3.2.1
# .1.2.3.3.2.1.
# ..1.2.2.0.1..
# ...1.1.1.1...
#
def hex_to_matrix(cell,matrix,visited,index):
  matrix[index[0]][index[1]] = str(cell.richness)
  visited[cell.index] = True
  for i in range(len(cell.neigh_cells)):
    c = cell.neigh_cells[i]
    d = cell.neigh_dir[i]
    if not visited[c.index]:
      next_index = index[:]
      if d == 0:
        next_index[1] += 2
      if d == 1:
        next_index[0] -= 1
        next_index[1] += 1
      if d == 2:
        next_index[0] -= 1
        next_index[1] -= 1
      if d == 3:
        next_index[1] -= 2
      if d == 4:
        next_index[0] += 1
        next_index[1] -= 1
      if d == 5:
        next_index[0] += 1
        next_index[1] += 1
      matrix,visited = hex_to_matrix(c,matrix,visited,next_index)
  return matrix,visited

def print_matrix(matrix):
  s = ""
  for r in matrix:
    for c in r:
      s += c
    s += '\n'
  dp(s)

class Cell:
  def __init__(self):
    self.neigh_cells = []
    self.neigh_index = []
    self.neigh_dir = []
    self.index = 0
    self.richness = 0

indexed_cells = []

number_of_cells = int(input())
for i in range(number_of_cells):
  index, richness, neigh_0, neigh_1, neigh_2, neigh_3, neigh_4, neigh_5 = [int(j) for j in input().split()]
  cell = Cell()
  cell.index = index
  cell.richness = richness
  cell.neigh_index = [neigh_0, neigh_1, neigh_2, neigh_3, neigh_4, neigh_5]
  indexed_cells.append(cell)

for ic in range(len(indexed_cells)):
  cell = indexed_cells[ic]
  cell.neigh_cells = []
  for i in range(len(cell.neigh_index)):
    n = cell.neigh_index[i]
    if n != -1:
      cell.neigh_cells.append(indexed_cells[n])
      cell.neigh_dir.append(i)

arena = indexed_cells[0]

line = ["." for i in range(13)]
matrix = [line[:] for i in range(7)]
visited = [False for i in range(37)]
startindex = [3,6]
matrix,visited = hex_to_matrix(arena,matrix,visited,startindex)
print_matrix(matrix)

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