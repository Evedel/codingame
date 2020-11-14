import sys
import math
import time
import random

debug = True
def dp(s):
  if debug: print(s, file=sys.stderr, flush=True)

class Potion:
  def __init__(self):
    self.id = 0
    self.price = 0

class Spell:
  def __init__(self):
    self.delta = [0,0,0,0]
    self.id = 0
    self.is_ready = False

  def copy(self):
    t = Spell()
    t.delta = self.delta[:]
    t.id = self.id
    t.is_ready = self.is_ready
    return t

class State:
  def __init__(self):
    self.inv = []
    self.spells = []
    self.turns = []
    self.dist = 0

  def copy(self):
    t = State()
    t.spells = []
    for s in self.spells:
      t.spells.append(s.copy())
    t.inv = self.inv[:]
    t.turns = self.turns[:]
    t.dist = self.dist
    return t

def is_enough_ingredients(state, potion):
  for i in range(4):
    if state.inv[i]+potion.delta[i] < 0:
      return False
  return True

def try_cast(state,spell_id):
  new_state = state.copy()
  if new_state.spells[spell_id].is_ready:
    for i in range(4):
      new_state.inv[i] += new_state.spells[spell_id].delta[i]
    if min(new_state.inv) < 0:
      return state.copy(), False
    if sum(new_state.inv) > 10:
      return state.copy(), False
    new_state.spells[spell_id].is_ready = False
    return new_state, True
  return state.copy(), False

def rest(state):
  new_state = state.copy()
  for s in new_state.spells:
    s.is_ready = True
  return new_state

def get_states(state):
  new_states = []
  for i in range(len(state.spells)):
    if state.spells[i].is_ready:
      new_state, is_possible = try_cast(state, i)
      if is_possible:
        new_state.turns.append('CAST '+str(new_state.spells[i].id))
        new_states.append(new_state)
    else:
      new_state = rest(state)
      new_state.turns.append('REST')
      new_states.append(new_state)
  return new_states

def get_distance(state, potion):
  dist = [0,0,0,0]
  for i in range(4):
    if (potion.delta[i] < 0):
      dist[i] += state.inv[i] + potion.delta[i]
      if dist[i] < 0:
        jfirst = -1
        for j in reversed(range(i)):
          if dist[j] > 0:
            jfirst = j
            break
        dist[i] *= i-jfirst
  for i in range(4):
    dist[i] = abs(min(0,dist[i]))
  return sum(dist)

def find_solution(state, potion):
  all_states = [state.copy()]

  if (is_enough_ingredients(all_states[0], potion)):
    all_states[0].turns.append('BREW '+str(potion.id))
    # print(i, all_states[0].inv, potion.delta, all_states[0].turns)
    # dp('found solution in '+str(i)+' steps')
    return all_states[0]

  all_states[0].dist = get_distance(all_states[0], potion)
  max_int = 170
  for i in range(max_int):
    # print('Q',len(all_states),all_states[0].turns)
    if len(all_states) == 0:
      return state
    new_states = get_states(all_states[0])
    for s in new_states:
      s.dist = get_distance(s, potion)
      if (s.dist <= all_states[0].dist):
        all_states.append(s)
      if (is_enough_ingredients(s, potion)):
        s.turns.append('BREW '+str(potion.id))
        # print(i, s.inv, potion.delta, s.turns)
        dp('found solution in '+str(i)+' steps')
        return s
    del all_states[0]
  # dp('found solution in '+str(i)+' steps')
  return state

def main():
  while True:
    state = State()
    potions = []

    action_count = int(input())
    for i in range(action_count):
      action_id, action_type, delta_0, delta_1, delta_2, delta_3, price, tome_index, tax_count, castable, repeatable = input().split()
      action_id = int(action_id)
      delta_0 = int(delta_0)
      delta_1 = int(delta_1)
      delta_2 = int(delta_2)
      delta_3 = int(delta_3)
      price = int(price)
      tome_index = int(tome_index)
      tax_count = int(tax_count)
      castable = castable != "0"
      repeatable = repeatable != "0"
      if action_type == 'BREW':
        p = Potion()
        p.delta = [delta_0, delta_1, delta_2, delta_3]
        p.price = price
        p.id = action_id
        potions.append(p)
      if action_type == 'CAST':
        s = Spell()
        s.delta = [delta_0, delta_1, delta_2, delta_3]
        s.id = action_id
        s.is_ready = castable
        state.spells.append(s)
      # dp((action_id, action_type, delta_0, delta_1, delta_2, delta_3, price, tome_index, tax_count, castable, repeatable))

    for i in range(2):
      inv_0, inv_1, inv_2, inv_3, score = [int(j) for j in input().split()]
      if i == 0:
        state.inv = [inv_0, inv_1, inv_2, inv_3]

    turn = 'WAIT'
    d1 = 10000
    c1 = 1
    for p in potions:
      solved = find_solution(state, p)
      if (len(solved.turns) != 0):
        d2 = len(solved.turns)
        c2 = p.price

        dd = float(d1)/d2
        dc = float(c1)/c2
        if (dc < dd):
          turn = solved.turns[0]
          d1 = d2
          c1 = c2
      dp((p.id,p.price,len(solved.turns), solved.turns))
    if (turn == 'WAIT'):
      for i in range(4):
        new_state, is_ok = try_cast(state,i)
        if is_ok:
          turn = 'CAST '+str(state.spells[i].id)
          break
      if turn == 'WAIT':
        turn = 'REST'

    # in the first league: BREW <id> | WAIT; later: BREW <id> | CAST <id> [<times>] | LEARN <id> | REST | WAIT
    print(turn)

if (__name__ == "__main__"):
  random.seed(19081991)
  main()