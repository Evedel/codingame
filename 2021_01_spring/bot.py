import sys
import math
import random
from typing import List, Set, Tuple, Dict

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
  cell.index_x = index[0]
  cell.index_y = index[1]

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
    self.index_x = 0
    self.index_y = 0
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
  
  def dist(self,cell):
    if abs(self.index_y - cell.index_y) < 2:
      return abs(self.index_x - cell.index_x)
    return (abs(self.index_x - cell.index_x) + abs(self.index_y - cell.index_y))/2

class GameState:
  # self.is_mine == True  => me is self.xxx[1]
  # self.is_mine == False => op is self.xxx[0]
  def __init__(self):
    self.sun = [-1, -1]
    self.score = [-1, -1]
    self.is_waiting = [False, False]
    self.nutrients = -1
    self.day = -1
  def clone(self):
    gs = GameState()
    gs.sun = self.sun[:]
    gs.score = self.score[:]
    gs.is_waiting = self.is_waiting[:]
    gs.nutrients = self.nutrients
    gs.day = self.day
    return gs

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

def read_input_turn(arena: List[Cell], game_state: GameState) -> Tuple[List[Cell],GameState]:
  game_state.day = int(input())  # the game lasts 24 days: 0-23
  game_state.nutrients = int(input())  # the base score you gain from the next COMPLETE action
  game_state.sun[1], game_state.score[1] = [int(i) for i in input().split()] # sun: your sun points # score: your current score
  inputs = input().split()
  game_state.sun[0] = int(inputs[0])  # opponent's sun points
  game_state.score[0] = int(inputs[1])  # opponent's score
  game_state.is_waiting[0] = inputs[2] != "0"  # whether your opponent is asleep until the next day
  number_of_trees = int(input())  # the current amount of trees
  for i in range(number_of_trees):
    inputs = input().split()
    cell_index = int(inputs[0])  # location of this tree
    size = int(inputs[1])  # size of this tree: 0-3
    is_mine = inputs[2] != "0"  # 1 if this is your tree
    is_dormant = inputs[3] != "0"  # 1 if this tree is dormant
    c = arena[cell_index]
    c.is_tree = True
    c.tree_size = size
    c.is_mine = is_mine
    c.is_dormant = is_dormant
  number_of_possible_actions = int(input())  # all legal actions
  for i in range(number_of_possible_actions):
    possible_action = input()  # try printing something from here to start with
  return arena,game_state

def get_all_seed_actions(arena,day_miltiplier,cell):
  res = []
  c1 = cell
  for c2 in arena:
    if (not c2.is_tree) and (c2.richness > 0) and (c1.dist(c2) <= c1.tree_size):
      min_dist = c1.tree_size
      for c3 in arena:
        if c3.is_tree:
          dist = c2.dist(c3)
          if dist < min_dist:
            min_dist = dist
      res.append(["SEED "+str(c1.index)+" "+str(c2.index), min_dist*c2.richness*(1-day_miltiplier)])
  return res

def get_all_actions(arena:List[Cell],game_state:GameState) -> List[str]:
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

  day_miltiplier = 0.05 if game_state.day < 20 else 1

  actions = []
  for c in arena:
    if c.is_tree and c.is_mine:
      if (size_0_trees <= game_state.sun[1]) and (not c.is_dormant) and (c.tree_size != 0):
        actions += get_all_seed_actions(arena,day_miltiplier,c)
      if (c.tree_size == 0) and (game_state.sun[1] >= 1 + size_1_trees):
        actions.append(["GROW "+str(c.index), 3*c.richness])
      elif (c.tree_size == 1) and (game_state.sun[1] >= 3 + size_2_trees):
        actions.append(["GROW "+str(c.index), 6*c.richness])
      elif (c.tree_size == 2) and (game_state.sun[1] >= 7 + size_3_trees):
        actions.append(["GROW "+str(c.index), 10*c.richness])
      elif (c.tree_size == 3) and (game_state.sun[1] >= 4):
        actions.append(["COMPLETE "+str(c.index), 20*c.richness*day_miltiplier])

  actions.append(["WAIT", 0])
  return actions

# def apply_step():
# day change when both players stop taking actions
# best outcome => max my suns and points => min same for enemy
def get_best_step(arena:List[Cell],game_state:GameState,depth:int) -> Tuple[int,str]:
  if depth > 5:
    return -1, {}

  actions = get_all_actions(arena,game_state)
  dp(actions)

  best_points = -1
  best_action = []
  for a in actions:
    if a[1] > best_points:
      best_action = a[0]
      best_points = a[1]
  # for a in actions:
  #   new_arena = apply_step(arena,a)
  #   local_best_points,tmp = get_best_step(new_arena,sun,depth+1)
  #   if local_best_points > best_points:
  #     best_points = local_best_points
  #     best_step = a[:]
  return best_points,best_action

def get_next_step(arena:List[Cell], game_state:GameState) -> str:
  points,action = get_best_step(arena,game_state,0)
  return action

def main():
  random.seed(18081991)

  arena = read_input_setup()
  arena = make_links(arena)
  print_arena(arena)
  game_state = GameState()
  # game loop
  while True:
    clean(arena)
    arena,game_state = read_input_turn(arena,game_state)
    action = get_next_step(arena,game_state)
    print(action)

if __name__ == "__main__":
  main()