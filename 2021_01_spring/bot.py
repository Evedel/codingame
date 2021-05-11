import sys
import math
import random

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
    self.is_tree = False
    self.tree_size = 0
    self.is_mine = False
    self.is_dormant = False
  
  def copy(self):
    cell = Cell()
    self.neigh_cells = []
    cell.neigh_index = self.neigh_index[:]
    cell.neigh_dir = self.neigh_dir[:]
    cell.index = self.index
    cell.richness = self.richness
    cell.is_tree = self.is_tree
    cell.tree_size = self.tree_size
    cell.is_mine = self.is_mine
    cell.is_dormant = self.is_dormant
    return cell

  def clean(self):
    self.is_tree = False
    self.tree_size = 0
    self.is_mine = False
    self.is_dormant = False

def clean(arena):
  for c in arena:
    c.clean()

def copy_arena(indexed_cells):
  indexed_cells_copy = []
  for c in indexed_cells:
    indexed_cells_copy.append(c.copy())
  indexed_cells_copy = make_links(indexed_cells_copy)
  return indexed_cells_copy

def read_input_setup():
  indexed_cells = []

  number_of_cells = int(input())
  for i in range(number_of_cells):
    index, richness, neigh_0, neigh_1, neigh_2, neigh_3, neigh_4, neigh_5 = [int(j) for j in input().split()]
    cell = Cell()
    cell.index = index
    cell.richness = richness
    cell.neigh_index = [neigh_0, neigh_1, neigh_2, neigh_3, neigh_4, neigh_5]
    indexed_cells.append(cell)

  return indexed_cells

def make_links(indexed_cells):
  for ic in range(len(indexed_cells)):
    cell = indexed_cells[ic]
    cell.neigh_cells = []
    for i in range(len(cell.neigh_index)):
      n = cell.neigh_index[i]
      if n != -1:
        cell.neigh_cells.append(indexed_cells[n])
        cell.neigh_dir.append(i)

  return indexed_cells

def print_arena(indexed_cells):
  arena = indexed_cells[0]
  line = ["." for i in range(13)]
  matrix = [line[:] for i in range(7)]
  visited = [False for i in range(37)]
  startindex = [3,6]
  matrix,visited = hex_to_matrix(arena,matrix,visited,startindex)
  print_matrix(matrix)

def read_input_turn(indexed_cells):
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
  for i in range(number_of_trees):
    inputs = input().split()
    cell_index = int(inputs[0])  # location of this tree
    size = int(inputs[1])  # size of this tree: 0-3
    is_mine = inputs[2] != "0"  # 1 if this is your tree
    is_dormant = inputs[3] != "0"  # 1 if this tree is dormant
    c = indexed_cells[cell_index]
    c.is_tree = True
    c.tree_size = size
    c.is_mine = is_mine
    c.is_dormant = is_dormant
  number_of_possible_actions = int(input())  # all legal actions
  for i in range(number_of_possible_actions):
    possible_action = input()  # try printing something from here to start with
  return sun,indexed_cells

def get_all_steps(arena,sun):
  size_0_trees = 0
  size_1_trees = 0
  size_2_trees = 0
  size_3_trees = 0

  for c in arena:
    if c.is_tree and c.is_mine:
      if c.tree_size == 0:
        size_0_trees += 1
      if c.tree_size == 1:
        size_1_trees += 1
      if c.tree_size == 2:
        size_2_trees += 1
      if c.tree_size == 3:
        size_3_trees += 1

  steps = []
  for c in arena:
    if c.is_tree and c.is_mine:
      if (c.tree_size == 1) and (sun >= 3 + size_2_trees):
        steps.append("GROW "+str(c.index))
      elif (c.tree_size == 2) and (sun >= 7 + size_3_trees):
        steps.append("GROW "+str(c.index))
      elif (c.tree_size == 3) and (sun >= 4):
        steps.append("COMPLETE "+str(c.index))

  steps.append("WAIT")
  return steps

# def apply_step():

def get_best_step(arena,sun,depth):
  if depth > 5:
    return -1, {}

  steps = get_all_steps(arena,sun)
  dp(steps)
  best_points = -1
  best_step = random.choice(steps)
  # for s in steps:
  #   new_arena = apply_step(arena,s)
  #   local_best_points,tmp = get_best_step(new_arena,sun,depth+1)
  #   if local_best_points > best_points:
  #     best_points = local_best_points
  #     best_step = s[:]
  return best_points,best_step

def get_next_step(indexed_cells,sun):
  points,step = get_best_step(indexed_cells,sun,0)

  return step

def main():
  indexed_cells = read_input_setup()
  indexed_cells = make_links(indexed_cells)
  print_arena(indexed_cells)

  # game loop
  while True:
    clean(indexed_cells)
    sun,indexed_cells = read_input_turn(indexed_cells)
    res = get_next_step(indexed_cells, sun)
    print(res)

if __name__ == "__main__":
  main()