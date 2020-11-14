#!/usr/bin/env python

import bot
import time

def test_is_enough_ingredients():
  s1 = bot.State()
  s1.inv = [0,0,0,0]
  p1 = bot.Potion()
  p1.delta = [-1,0,0,0]
  r1 = bot.is_enough_ingredients(s1,p1)
  if r1 == True:
    print('Failed')

  s2 = bot.State()
  s2.inv = [1,0,0,0]
  p2 = bot.Potion()
  p2.delta = [-1,0,0,0]
  r2 = bot.is_enough_ingredients(s2,p2)
  if r2 == False:
    print('Failed')

def test_try_cast():
  s = bot.State()
  s.inv = [0,0,0,0]
  s.spells = []
  s.spells.append(bot.Spell())
  s.spells[0].delta = [2,0,0,0]

  s.spells[0].is_ready = False
  new_state, is_casted = bot.try_cast(s,0)
  if is_casted == True:
    print('Failed: test_try_cast: not ready spell is casted')

  s.spells[0].is_ready = True
  new_state, is_casted = bot.try_cast(s,0)
  if is_casted == False:
    print('Failed: test_try_cast: ready spell is not casted')
  if new_state.spells[0].is_ready == True:
    print('Failed: test_try_cast: new spell is ready after cast')
  if s.spells[0].is_ready == False:
    print('Failed: test_try_cast: old spell is not ready after cast')
  if new_state.inv != [2,0,0,0]:
    print('Failed: test_try_cast: new inventory is wrong after cast')
  if s.inv != [0,0,0,0]:
    print('Failed: test_try_cast: old inventory is wrong after cast')

  s.spells[0].delta = [-1,1,0,0]
  new_state, is_casted = bot.try_cast(s,0)
  if is_casted == True:
    print('Failed: test_try_cast: impossible spell is casted')
  if new_state.inv != [0,0,0,0]:
    print('Failed: test_try_cast: new inventory is wrong after not cast')
  if s.inv != [0,0,0,0]:
    print('Failed: test_try_cast: old inventory is wrong after not cast')
  if new_state.spells[0].is_ready == False:
    print('Failed: test_try_cast: new spell is not ready after not cast')
  if s.spells[0].is_ready == False:
    print('Failed: test_try_cast: old spell is not ready after not cast')

  s.inv = [3,3,3,0]
  s.spells[0].delta = [2,0,0,0]
  new_state, is_casted = bot.try_cast(s,0)
  if is_casted == True:
    print('Failed: test_try_cast: impossible spell is casted')
  if new_state.inv != [3,3,3,0]:
    print('Failed: test_try_cast: new inventory is wrong after not cast')
  if s.inv != [3,3,3,0]:
    print('Failed: test_try_cast: old inventory is wrong after not cast')
  if new_state.spells[0].is_ready == False:
    print('Failed: test_try_cast: new spell is not ready after not cast')
  if s.spells[0].is_ready == False:
    print('Failed: test_try_cast: old spell is not ready after not cast')

def test_rest():
  s = bot.State()
  s.inv = [0,0,0,0]
  s.spells = []
  s.spells.append(bot.Spell())
  s.spells.append(bot.Spell())
  s.spells[0].delta = [2,0,0,0]
  s.spells[1].delta = [0,2,0,0]
  s.spells[0].is_ready = True
  s.spells[1].is_ready = True
  new_state = bot.rest(s)
  if new_state.spells[0].is_ready == False:
    print('Failed: test_try_cast: not ready spell after rest')
  if new_state.spells[1].is_ready == False:
    print('Failed: test_try_cast: not ready spell after rest')

  s.spells[0].is_ready = False
  s.spells[1].is_ready = True
  new_state = bot.rest(s)
  if new_state.spells[0].is_ready == False:
    print('Failed: test_try_cast: not ready spell after rest')
  if new_state.spells[1].is_ready == False:
    print('Failed: test_try_cast: not ready spell after rest')

def test_find_solution():
  s = bot.State()
  s.inv = [2,0,0,0]
  p = bot.Potion()
  p.delta = [-1,0,0,0]
  solved = bot.find_solution(s, p)
  if solved.turns != ['BREW 0']:
    print("Failed: test_find_solution: v1: should be possible")
  if s.turns != []:
    print("Failed: test_find_solution: v1: should not chabge initial state")

  s.inv = [1,0,0,0]
  p.delta = [-2,0,0,0]
  solved = bot.find_solution(s, p)
  if solved.turns != []:
    print("Failed: test_find_solution: should be impossible")

  s.spells.append(bot.Spell())
  s.spells[0].delta = [2,0,0,0]
  s.spells[0].is_ready = True
  solved = bot.find_solution(s, p)
  if solved.turns != ['CAST 0', 'BREW 0']:
    print("Failed: test_find_solution: v3: should be possible")

  s.spells[0].is_ready = False
  solved = bot.find_solution(s, p)
  if solved.turns != ['REST', 'CAST 0', 'BREW 0']:
    print("Failed: test_find_solution: v4: wrong turns returned")

  p.delta = [-1,-1,0,0]
  s.spells.append(bot.Spell())
  s.spells[1].delta = [-1,1,0,0]
  s.spells[1].id = 1
  solved = bot.find_solution(s, p)
  if solved.turns != ['REST', 'CAST 0', 'CAST 1', 'BREW 0']:
    print("Failed: test_find_solution: v5: wrong turns returned")

  s = bot.State()
  s.inv = [3,0,0,0]

  s.spells.append(bot.Spell())
  s.spells[0].delta = [2,0,0,0]
  s.spells[0].is_ready = True
  s.spells[0].id = 0

  s.spells.append(bot.Spell())
  s.spells[1].delta = [-1,1,0,0]
  s.spells[1].is_ready = True
  s.spells[1].id = 1

  s.spells.append(bot.Spell())
  s.spells[2].delta = [0,-1,1,0]
  s.spells[2].is_ready = True
  s.spells[2].id = 2

  s.spells.append(bot.Spell())
  s.spells[3].delta = [0,0,-1,1]
  s.spells[3].is_ready = True
  s.spells[3].id = 3

  p = bot.Potion()
  p.delta = [0,-4,0,0]
  print('main test is here ->')
  solved = bot.find_solution(s, p)
  print(solved.turns)
  # s.spells.append(bot.Spell())
  # s.spells[1].delta = [-1,1,0,0]
  # s.spells[1].is_ready = True

def test_real_life():
  t1 = time.time()

  s = bot.State()
  s.inv = [3,0,0,0]

  s.spells.append(bot.Spell())
  s.spells[0].delta = [2,0,0,0]
  s.spells[0].is_ready = True
  s.spells[0].id = 0

  s.spells.append(bot.Spell())
  s.spells[1].delta = [-1,1,0,0]
  s.spells[1].is_ready = True
  s.spells[1].id = 1

  s.spells.append(bot.Spell())
  s.spells[2].delta = [0,-1,1,0]
  s.spells[2].is_ready = True
  s.spells[2].id = 2

  s.spells.append(bot.Spell())
  s.spells[3].delta = [0,0,-1,1]
  s.spells[3].is_ready = True
  s.spells[3].id = 3

  p = bot.Potion()
  p.delta = [0,-4,0,0]
  print('main test is here ->')
  solved = bot.find_solution(s, p)
  print(solved.turns)
  t2 = time.time()
  print(t2-t1)
  # < 0.015

def test_get_distance():
  state = bot.State()
  potion = bot.Potion()
  state.inv = [3,0,0,0]
  potion.delta = [-3,0,0,0]
  dist = bot.get_distance(state, potion)
  if dist != 0:
    print("Failed: test_get_distance: v1: should be zero")

  state.inv = [3,0,0,0]
  potion.delta = [-4,0,0,0]
  dist = bot.get_distance(state, potion)
  if dist != 1:
    print("Failed: test_get_distance: v1: should be one")

  state.inv = [4,0,0,0]
  potion.delta = [-3,0,0,0]
  dist = bot.get_distance(state, potion)
  if dist != 0:
    print("Failed: test_get_distance: v1: should be zero")


  state.inv = [4,0,0,0]
  potion.delta = [-3,-1,0,0]
  dist = bot.get_distance(state, potion)
  if dist != 1:
    print("Failed: test_get_distance: v1: should be one")

  state.inv = [4,2,0,0]
  potion.delta = [-3,-1,0,0]
  dist = bot.get_distance(state, potion)
  if dist != 0:
    print("Failed: test_get_distance: v1: should be zero")

  state.inv = [4,0,0,0]
  potion.delta = [-3,0,-1,0]
  dist = bot.get_distance(state, potion)
  if dist != 2:
    print("Failed: test_get_distance: v1: should be two")

  state.inv = [0,0,0,0]
  potion.delta = [0,-1,0,0]
  dist = bot.get_distance(state, potion)
  if dist != 2:
    print("Failed: test_get_distance: v1: should be two")

  state.inv = [0,0,0,0]
  potion.delta = [0,0,-1,0]
  dist = bot.get_distance(state, potion)
  if dist != 3:
    print("Failed: test_get_distance: v1: should be three")

  state.inv = [0,0,0,0]
  potion.delta = [0,-2,-1,-1]
  dist = bot.get_distance(state, potion)
  if dist != 11:
    print("Failed: test_get_distance: v1: should be three")

def test_priority():
  d1 = 10000
  p1 = 1
  d2 = 6
  p2 = 11

  dd = d1/d2
  dp = p1/p2
  if (dp < dd):
    print('choose 2',dd,dp)
  else:
    print('choose 1',dd,dp)
  
# test_is_enough_ingredients()
# test_try_cast()
# test_rest()
# test_find_solution()

test_real_life()
# test_priority()

# test_get_distance()