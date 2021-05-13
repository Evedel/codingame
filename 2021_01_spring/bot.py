import sys
import math
import random
from typing import List, Set, Tuple, Dict

debug = True
def dp(s):
  if debug: print(s, file=sys.stderr, flush=True)

class Cell:
  def __init__(self):
    self.neigh_cells: List[Cell] = []
    self.neigh_index: List[int] = []
    self.neigh_dir: List[int] = []
    self.index = 0
    self.index_x = 0
    self.index_y = 0
    self.richness = 0
    self.is_tree = False
    self.tree_size = 0
    self.is_mine = False
    self.is_dormant = False
    self.is_shadowed = False
  
  def clone(self):
    cell = Cell()
    self.neigh_cells = None
    cell.neigh_index = self.neigh_index[:]
    cell.neigh_dir = self.neigh_dir[:]
    cell.index = self.index
    cell.index_x = self.index_x
    cell.index_y = self.index_y
    cell.richness = self.richness
    cell.is_tree = self.is_tree
    cell.tree_size = self.tree_size
    cell.is_mine = self.is_mine
    cell.is_dormant = self.is_dormant
    cell.is_shadowed = self.is_shadowed
    return cell

  def clean(self):
    self.tree_size = 0
    self.is_tree = False
    self.is_mine = False
    self.is_dormant = False
    self.is_shadowed = False
  
  def dist(self,cell):
    if abs(self.index_y - cell.index_y) < 2:
      return abs(self.index_x - cell.index_x)
    return (abs(self.index_x - cell.index_x) + abs(self.index_y - cell.index_y))/2

class GameState:
  # self.is_mine == True  => me is self.xxx[1]
  # self.is_mine == False => op is self.xxx[0]
  def __init__(self):
    self.sun        : List[int]  = [-1, -1]
    self.score      : List[int]  = [-1, -1]
    self.is_waiting : List[bool] = [False, False]
    self.nutrients  : int = -1
    self.day        : int = -1

  def clone(self):
    gs = GameState()
    gs.sun = self.sun[:]
    gs.score = self.score[:]
    gs.is_waiting = self.is_waiting[:]
    gs.nutrients = self.nutrients
    gs.day = self.day
    return gs

class Snapshot:
  def __init__(self):
    self.price : float      = None
    self.path  : List[str]  = None
    self.arena : List[Cell] = None
    self.state : GameState  = None
  
  def clone(self):
    new_snapshot = Snapshot()
    new_snapshot.price = self.price
    new_snapshot.path = self.path[:]
    new_snapshot.arena = clone_arena(self.arena)
    new_snapshot.state = self.state.clone()
    return new_snapshot
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
def convert_hex_to_matrix(cell:Cell,visited:List[bool],index:List[int]) -> List[List[str]]:
  cell.index_x = index[0]
  cell.index_y = index[1]

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
      visited = convert_hex_to_matrix(c,visited,next_index)
  return visited

def enumerate_hex_to_matrix(arena:List[Cell]):
  visited = [False for i in range(37)]
  starting_index = [3,6]
  starting_cell = arena[0]
  convert_hex_to_matrix(starting_cell,visited,starting_index)

def print_matrix(matrix):
  s = ""
  for r in matrix:
    for c in r:
      s += c
    s += '\n'
  dp(s)

def print_arena(arena:List[Cell]):
  line = ["." for i in range(13)]
  matrix = [line[:] for i in range(7)]

  trees_shadowed = ["f", "t", "F", "T"]
  trees_opened = ["n", "m", "N", "M"]
  for a in arena:
    dx = a.index_x
    dy = a.index_y
    matrix[dx][dy] = str(a.richness)
    if a.is_tree:
      if a.is_shadowed:
        matrix[dx][dy] = trees_shadowed[a.tree_size]
      else:
        matrix[dx][dy] = trees_opened[a.tree_size]

  print_matrix(matrix)

def clean(arena):
  for c in arena:
    c.clean()

def clone_arena(arena:List[Cell]) -> List[Cell]:
  arena_copy = []
  for a in arena:
    arena_copy.append(a.clone())
  return arena_copy

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

def get_all_seed_actions(arena,cell):
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
      res.append("SEED "+str(c1.index)+" "+str(c2.index))
  return res

def get_trees_numbers(arena:List[Cell]) -> Tuple[int,int,int,int]:
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

  return size_0_trees,size_1_trees,size_2_trees,size_3_trees

def get_all_actions(arena:List[Cell],game_state:GameState) -> List[str]:
  size_0_trees,size_1_trees,size_2_trees,size_3_trees = get_trees_numbers(arena)

  actions = []
  for c in arena:
    if c.is_tree and c.is_mine and (not c.is_dormant):
      if (c.tree_size != 0) and (size_0_trees <= game_state.sun[1]):
        actions += get_all_seed_actions(arena,c)
      if (c.tree_size == 0) and (game_state.sun[1] >= 1 + size_1_trees):
        actions.append("GROW "+str(c.index))
      elif (c.tree_size == 1) and (game_state.sun[1] >= 3 + size_2_trees):
        actions.append("GROW "+str(c.index))
      elif (c.tree_size == 2) and (game_state.sun[1] >= 7 + size_3_trees):
        actions.append("GROW "+str(c.index))
      elif (c.tree_size == 3) and (game_state.sun[1] >= 4):
        actions.append("COMPLETE "+str(c.index))

  actions.append("WAIT")
  return actions

def calculate_shadowed_trees(arena:List[Cell],day:int) -> List[Cell]:
  direction_reversal = {0:3, 1:4, 2:5, 3:0, 4:1, 5:2}

  shadow_to = day % 6
  shadow_from = direction_reversal[shadow_to]
  
  def cell_has_no_neighbour_at_direction(c: Cell, d:int) -> bool:
    return (c.neigh_index[d] == -1)

  shadow_casters: List[Cell] = []
  for a in arena:
    if cell_has_no_neighbour_at_direction(a,shadow_from):
      shadow_casters.append(a)
  
  while len(shadow_casters) > 0:
    sc = shadow_casters.pop(0)
    if sc.is_tree:
      neigh_last = sc
      for i in range(sc.tree_size):
        neigh_index = neigh_last.neigh_index[shadow_to]
        if neigh_index == -1:
          break
        else:
          neigh = arena[neigh_index]
          if neigh.is_tree and (neigh.tree_size <= sc.tree_size):
            neigh.is_shadowed = True
          neigh_last = neigh

    neigh_index = sc.neigh_index[shadow_to]
    if neigh_index != -1:
      neigh = arena[neigh_index]
      shadow_casters.append(neigh)

  return arena

def clean_shadows(arena:List[Cell]):
  for a in arena:
    a.is_shadowed = False

def apply_wait(snapshot:Snapshot):
  whoami = True
  myid = int(whoami)
  snapshot.state.day += 1
  for a in snapshot.arena:
    if a.is_tree:
      a.is_dormant = False
      a.is_shadowed = False
  calculate_shadowed_trees(snapshot.arena,snapshot.state.day)
  for a in snapshot.arena:
    if a.is_tree and (whoami == a.is_mine) and (not a.is_shadowed):
      snapshot.state.sun[myid] += a.tree_size

def apply_grow(snapshot:Snapshot,index:int):
  whoami = True
  myid = int(whoami)
  trees_cost = [0,1,3,7]
  trees_numbers = get_trees_numbers(snapshot.arena)
  snapshot.arena[index].is_dormant = True
  snapshot.arena[index].tree_size += 1
  new_size = snapshot.arena[index].tree_size
  snapshot.state.sun[myid] -= trees_cost[new_size] + trees_numbers[new_size]

def apply_complete(snapshot:Snapshot,index:int):
  whoami = True
  myid = int(whoami)
  richness_bonus = [0,0,2,4]
  richness = snapshot.arena[index].richness
  snapshot.state.score[myid] += snapshot.state.nutrients + richness_bonus[richness]
  snapshot.state.nutrients -= 1
  snapshot.arena[index].is_tree     = False
  snapshot.arena[index].is_dormant  = False
  snapshot.arena[index].is_mine     = False
  snapshot.arena[index].is_shadowed = False
  snapshot.arena[index].tree_size   = -1

def apply_seed(snapshot:Snapshot,index_parent:int,index_kid:int):
  whoami = True
  myid = int(whoami)
  trees_numbers = get_trees_numbers(snapshot.arena)
  snapshot.arena[index_parent].is_dormant = True
  snapshot.arena[index_kid].is_dormant = True
  snapshot.arena[index_kid].is_tree = True
  snapshot.arena[index_kid].is_mine = whoami
  snapshot.arena[index_kid].tree_size = 0
  snapshot.state.sun[myid] -= trees_numbers[0]

def apply_step(snapshot:Snapshot,action:str) -> Snapshot:
  new_snapshot : Snapshot = snapshot.clone()
  
  new_snapshot.path.append(action)
  action_parts = action.split()
  if action_parts[0] == "WAIT":
    apply_wait(new_snapshot)
  if action_parts[0] == "GROW":
    apply_grow(new_snapshot,int(action_parts[1]))
  if action_parts[0] == "COMPLETE":
    apply_complete(new_snapshot,int(action_parts[1]))
  if action_parts[0] == "SEED":
    apply_seed(new_snapshot,int(action_parts[1]),int(action_parts[2]))
  
  clean_shadows(new_snapshot.arena)
  new_snapshot.state.day += 1
  calculate_shadowed_trees(new_snapshot.arena,new_snapshot.state.day)
  new_snapshot.price = calculate_price(new_snapshot.arena,new_snapshot.state)
  new_snapshot.state.day -= 1
  return new_snapshot

def choose_best_actions(states_now:List[Snapshot],states_next:List[Snapshot],number:int) -> Tuple[List[Snapshot],List[Snapshot]]:
  states_next.sort(key=lambda x: x.price, reverse=True)
  states_now = states_next[:number]
  states_next = []
  return states_now,states_next

def get_best_step(states_now:List[Snapshot],states_next:List[Snapshot],depth:int) -> Tuple[int,str]:
  if depth > 1:
    best_action = ''
    best_price = -1
    for s in states_now:
      if s.price > best_price:
        best_price = s.price
        best_action = s.path[0]
    return best_price,best_action

  while len(states_now) != 0:
    snapshot = states_now.pop(0)
    # dp(str(depth)+" : "+str(snapshot.price) + " : "+str(snapshot.path))

    actions = get_all_actions(snapshot.arena,snapshot.state)

    for a in actions:
      new_snapshot = apply_step(snapshot,a)
      states_next.append(new_snapshot)
      # if new_snapshot.price > best_price:
      #   best_price = new_snapshot.price
      #   best_action = new_snapshot.path[0]
      # dp(str(new_snapshot.price) + " : "+str(new_snapshot.path))
      # print_arena(new_snapshot.arena)
      # states_next.append(new_snapshot)  
      # local_best_points,tmp = get_best_step(new_arena,sun,depth+1)
  
  states_now,states_next = choose_best_actions(states_now,states_next,10)
  return get_best_step(states_now,states_next,depth+1)

def calculate_price(arena:List[Cell],state:GameState) -> float:
  whoami = True
  myid = int(whoami)
  price = 0
  max_days = 24
  day_muliplier = (max_days - state.day)/max_days
  new_suns = 0
  for a in arena:
    if a.is_tree and (a.is_mine == whoami) and (not a.is_shadowed):
      # new_suns += a.tree_size
      price += a.richness*a.tree_size*day_muliplier

  # price += (state.sun[myid] + new_suns)*day_muliplier
  price += new_suns*day_muliplier
  price += state.score[myid]*(1 - day_muliplier)*0.125
  return price

def get_next_step(arena:List[Cell], state:GameState) -> str:
  states_now  : List[Snapshot] = []
  states_next : List[Snapshot] = []

  next_day_state = state.clone()
  next_day_state.day += 1
  next_day_arena = clone_arena(arena)
  calculate_shadowed_trees(next_day_arena,next_day_state.day)

  origin = Snapshot()
  origin.arena = clone_arena(arena)
  origin.path  = []
  origin.price = calculate_price(next_day_arena,next_day_state)
  origin.state = state.clone()

  states_now = [origin]
  points,action = get_best_step(states_now,states_next,0)
  dp("best price:" + str(points))
  return action

def main():
  random.seed(18081991)

  arena = read_input_setup()

  make_links(arena)
  enumerate_hex_to_matrix(arena)
  game_state = GameState()
  # game loop
  while True:
    # print_arena(arena)
    clean(arena)
    arena,game_state = read_input_turn(arena,game_state)
    action = get_next_step(arena,game_state)
    print(action)

if __name__ == "__main__":
  main()