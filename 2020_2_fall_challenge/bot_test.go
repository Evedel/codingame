package main

import (
	"fmt"
	"testing"
	"time"
)

func Test1(t *testing.T) {
	var state State
	var potion Potion
	state.inv = [4]int{3, 0, 0, 0}
	potion.delta = [4]int{-3, 0, 0, 0}
	dist := get_distance(state, potion)
	if dist != 0 {
		fmt.Println("Failed: test_get_distance: v1: should be zero")
	}
	state.inv = [4]int{3, 0, 0, 0}
	potion.delta = [4]int{-4, 0, 0, 0}
	dist = get_distance(state, potion)
	if dist != 1 {
		fmt.Println("Failed: test_get_distance: v1: should be one")
	}

	state.inv = [4]int{4, 0, 0, 0}
	potion.delta = [4]int{-3, 0, 0, 0}
	dist = get_distance(state, potion)
	if dist != 0 {
		fmt.Println("Failed: test_get_distance: v1: should be zero")
	}

	state.inv = [4]int{4, 0, 0, 0}
	potion.delta = [4]int{-3, -1, 0, 0}
	dist = get_distance(state, potion)
	if dist != 1 {
		fmt.Println("Failed: test_get_distance: v1: should be one")
	}

	state.inv = [4]int{4, 2, 0, 0}
	potion.delta = [4]int{-3, -1, 0, 0}
	dist = get_distance(state, potion)
	if dist != 0 {
		fmt.Println("Failed: test_get_distance: v1: should be zero")
	}

	state.inv = [4]int{4, 0, 0, 0}
	potion.delta = [4]int{-3, 0, -1, 0}
	dist = get_distance(state, potion)
	if dist != 2 {
		fmt.Println("Failed: test_get_distance: v1: should be two")
	}

	state.inv = [4]int{0, 0, 0, 0}
	potion.delta = [4]int{0, -1, 0, 0}
	dist = get_distance(state, potion)
	if dist != 2 {
		fmt.Println("Failed: test_get_distance: v1: should be two")
	}

	state.inv = [4]int{0, 0, 0, 0}
	potion.delta = [4]int{0, 0, -1, 0}
	dist = get_distance(state, potion)
	if dist != 3 {
		fmt.Println("Failed: test_get_distance: v1: should be three")
	}

	state.inv = [4]int{0, 0, 0, 0}
	potion.delta = [4]int{0, -2, -1, -1}
	dist = get_distance(state, potion)
	if dist != 11 {
		fmt.Println("Failed: test_get_distance: v1: should be three")
	}
}

func Test2(t *testing.T) {
	var s1 State
	s1.inv = [4]int{0, 0, 0, 0}
	var p1 Potion
	p1.delta = [4]int{-1, 0, 0, 0}
	r1 := is_enough_ingredients(s1, p1)
	if r1 != false {
		fmt.Println("Failed: test_is_enough_ingredients: v1: should be false")
	}

	var s2 State
	s2.inv = [4]int{1, 0, 0, 0}
	var p2 Potion
	p2.delta = [4]int{-1, 0, 0, 0}
	r2 := is_enough_ingredients(s2, p2)
	if r2 != true {
		fmt.Println("Failed: test_is_enough_ingredients: v1: should be true")
	}
}

func Test3(t *testing.T) {
	var s State
	s.inv = [4]int{0, 0, 0, 0}
	s.spells = append(s.spells, Spell{})
	s.spells[0].delta = [4]int{2, 0, 0, 0}

	s.spells[0].is_ready = false
	_, is_casted := try_cast(s, 0)
	if is_casted != false {
		fmt.Println("Failed: test_try_cast: v1: not ready spell is casted")
	}

	s.spells[0].is_ready = true
	new_state, is_casted := try_cast(s, 0)
	if is_casted == false {
		fmt.Println("Failed: test_try_cast: ready spell is not casted")
	}

	if new_state.spells[0].is_ready == true {
		fmt.Println("Failed: test_try_cast: new spell is ready after cast")
	}
	if s.spells[0].is_ready == false {
		fmt.Println("Failed: test_try_cast: old spell is not ready after cast")
	}
	if new_state.inv != [4]int{2, 0, 0, 0} {
		fmt.Println("Failed: test_try_cast: v1: not ready spell is casted")
	}

	if s.inv != [4]int{0, 0, 0, 0} {
		fmt.Println("Failed: test_try_cast: old inventory is wrong after cast")
	}

	s.spells[0].delta = [4]int{-1, 1, 0, 0}
	new_state, is_casted = try_cast(s, 0)
	if is_casted == true {
		fmt.Println("Failed: test_try_cast: impossible spell is casted")
	}
	if new_state.inv != [4]int{0, 0, 0, 0} {
		fmt.Println("Failed: test_try_cast: new inventory is wrong after not cast")
	}
	if s.inv != [4]int{0, 0, 0, 0} {
		fmt.Println("Failed: test_try_cast: old inventory is wrong after not cast")
	}
	if new_state.spells[0].is_ready == false {
		fmt.Println("Failed: test_try_cast: new spell is not ready after not cast")
	}
	if s.spells[0].is_ready == false {
		fmt.Println("Failed: test_try_cast: old spell is not ready after not cast")
	}

	s.inv = [4]int{3, 3, 3, 0}
	s.spells[0].delta = [4]int{2, 0, 0, 0}
	new_state, is_casted = try_cast(s, 0)
	if is_casted == true {
		fmt.Println("Failed: test_try_cast: impossible spell is casted")
	}
	if new_state.inv != [4]int{3, 3, 3, 0} {
		fmt.Println("Failed: test_try_cast: new inventory is wrong after not cast")
	}
	if s.inv != [4]int{3, 3, 3, 0} {
		fmt.Println("Failed: test_try_cast: old inventory is wrong after not cast")
	}
	if new_state.spells[0].is_ready == false {
		fmt.Println("Failed: test_try_cast: new spell is not ready after not cast")
	}
	if s.spells[0].is_ready == false {
		fmt.Println("Failed: test_try_cast: old spell is not ready after not cast")
	}
}

func Test4(t *testing.T) {
	var s State
	s.inv = [4]int{2, 0, 0, 0}
	var p Potion
	p.delta = [4]int{-1, 0, 0, 0}
	solved := find_solution(s, p)
	if (len(solved.turns) != 1) || (solved.turns[0] != "BREW 0") {
		fmt.Println("Failed: test_find_solution: v1: should be possible")
	}
	if len(s.turns) != 0 {
		fmt.Println("Failed: test_find_solution: v1: should not chabge initial state")
	}

	s.inv = [4]int{1, 0, 0, 0}
	p.delta = [4]int{-2, 0, 0, 0}
	solved = find_solution(s, p)
	if len(solved.turns) != 0 {
		fmt.Println("Failed: test_find_solution: should be impossible")
	}

	s.spells = append(s.spells, Spell{})
	s.spells[0].delta = [4]int{2, 0, 0, 0}
	s.spells[0].is_ready = true
	solved = find_solution(s, p)
	if (len(solved.turns) != 2) || (solved.turns[0] != "CAST 0") || (solved.turns[1] != "BREW 0") {
		fmt.Println("Failed: test_find_solution: v3: should be possible")
	}

	s.spells[0].is_ready = false
	solved = find_solution(s, p)
	// if solved.turns != ['REST', 'CAST 0', 'BREW 0']:
	//   print("Failed: test_find_solution: v4: wrong turns returned")

	p.delta = [4]int{-1, -1, 0, 0}
	s.spells = append(s.spells, Spell{})
	s.spells[1].delta = [4]int{-1, 1, 0, 0}
	s.spells[1].id = 1
	solved = find_solution(s, p)
	// if solved.turns != ['REST', 'CAST 0', 'CAST 1', 'BREW 0']:
	//   print("Failed: test_find_solution: v5: wrong turns returned")

	// s = bot.State()
	// s.inv = [3,0,0,0]

	// s.spells.append(bot.Spell())
	// s.spells[0].delta = [2,0,0,0]
	// s.spells[0].is_ready = True
	// s.spells[0].id = 0

	// s.spells.append(bot.Spell())
	// s.spells[1].delta = [-1,1,0,0]
	// s.spells[1].is_ready = True
	// s.spells[1].id = 1

	// s.spells.append(bot.Spell())
	// s.spells[2].delta = [0,-1,1,0]
	// s.spells[2].is_ready = True
	// s.spells[2].id = 2

	// s.spells.append(bot.Spell())
	// s.spells[3].delta = [0,0,-1,1]
	// s.spells[3].is_ready = True
	// s.spells[3].id = 3

	// p = bot.Potion()
	// p.delta = [0,-4,0,0]
	// print('main test is here ->')
	// solved = bot.find_solution(s, p)
	// print(solved.turns)
	// # s.spells.append(bot.Spell())
	// # s.spells[1].delta = [-1,1,0,0]
	// # s.spells[1].is_ready = True
}

func Test5(t *testing.T) {
	start := time.Now()

	s := State{}

	s.spells = append(s.spells, Spell{})
	s.spells[0].delta = [4]int{2, 0, 0, 0}
	s.spells[0].is_ready = true
	s.spells[0].id = 0

	s.spells = append(s.spells, Spell{})
	s.spells[1].delta = [4]int{-1, 1, 0, 0}
	s.spells[1].is_ready = true
	s.spells[1].id = 1

	s.spells = append(s.spells, Spell{})
	s.spells[2].delta = [4]int{0, -1, 1, 0}
	s.spells[2].is_ready = true
	s.spells[2].id = 2

	s.spells = append(s.spells, Spell{})
	s.spells[3].delta = [4]int{0, 0, -1, 1}
	s.spells[3].is_ready = true
	s.spells[3].id = 3

	s.spells = append(s.spells, Spell{})
	s.spells[4].delta = [4]int{3, 0, 0, 0}
	s.spells[4].is_ready = true
	s.spells[4].id = 4

	s.spells = append(s.spells, Spell{})
	s.spells[5].delta = [4]int{0, 0, 0, 1}
	s.spells[5].is_ready = true
	s.spells[5].id = 5

	s.spells = append(s.spells, Spell{})
	s.spells[6].delta = [4]int{3, -1, 0, 0}
	s.spells[6].is_ready = true
	s.spells[6].id = 6

	s.inv = [4]int{3, 0, 0, 1}

	p := Potion{}
	p.delta = [4]int{0, 0, 0, -5}
	fmt.Println("main test is here ->")
	solved := find_solution(s, p)
	fmt.Println(len(solved.turns), solved.turns)
	elapsed := time.Since(start)

	fmt.Println(elapsed)
	// < 10 ms
}

// 369 -- 15 steps -- my
// 445 -- 14 steps -- sq
