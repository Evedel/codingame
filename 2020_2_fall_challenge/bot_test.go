package main

import (
	"fmt"
	"testing"
	"time"
)

func TestGetDistance(t *testing.T) {
	var state State
	var potion Potion
	state.inv = [4]int{3, 0, 0, 0}
	potion.delta = [4]int{-3, 0, 0, 0}
	dist := getDistance(state, potion)
	if dist != 0 {
		fmt.Println("Failed: TestGetDistance: v1: should be zero")
	}
	state.inv = [4]int{3, 0, 0, 0}
	potion.delta = [4]int{-4, 0, 0, 0}
	dist = getDistance(state, potion)
	if dist != 1 {
		fmt.Println("Failed: TestGetDistance: v1: should be one")
	}

	state.inv = [4]int{4, 0, 0, 0}
	potion.delta = [4]int{-3, 0, 0, 0}
	dist = getDistance(state, potion)
	if dist != 0 {
		fmt.Println("Failed: TestGetDistance: v1: should be zero")
	}

	state.inv = [4]int{4, 0, 0, 0}
	potion.delta = [4]int{-3, -1, 0, 0}
	dist = getDistance(state, potion)
	if dist != 1 {
		fmt.Println("Failed: TestGetDistance: v1: should be one")
	}

	state.inv = [4]int{4, 2, 0, 0}
	potion.delta = [4]int{-3, -1, 0, 0}
	dist = getDistance(state, potion)
	if dist != 0 {
		fmt.Println("Failed: TestGetDistance: v1: should be zero")
	}

	state.inv = [4]int{4, 0, 0, 0}
	potion.delta = [4]int{-3, 0, -1, 0}
	dist = getDistance(state, potion)
	if dist != 2 {
		fmt.Println("Failed: TestGetDistance: v1: should be two")
	}

	state.inv = [4]int{0, 0, 0, 0}
	potion.delta = [4]int{0, -1, 0, 0}
	dist = getDistance(state, potion)
	if dist != 2 {
		fmt.Println("Failed: TestGetDistance: v1: should be two")
	}

	state.inv = [4]int{0, 0, 0, 0}
	potion.delta = [4]int{0, 0, -1, 0}
	dist = getDistance(state, potion)
	if dist != 3 {
		fmt.Println("Failed: TestGetDistance: v1: should be three")
	}

	state.inv = [4]int{0, 0, 0, 0}
	potion.delta = [4]int{0, -2, -1, -1}
	dist = getDistance(state, potion)
	if dist != 11 {
		fmt.Println("Failed: TestGetDistance: v1: should be three")
	}
}

func TestIsEnoughIngredients(t *testing.T) {
	var s1 State
	s1.inv = [4]int{0, 0, 0, 0}
	var p1 Potion
	p1.delta = [4]int{-1, 0, 0, 0}
	r1 := isEnoughIngredients(s1, p1)
	if r1 != false {
		fmt.Println("Failed: TestIsEnoughIngredients: v1: should be false")
	}

	var s2 State
	s2.inv = [4]int{1, 0, 0, 0}
	var p2 Potion
	p2.delta = [4]int{-1, 0, 0, 0}
	r2 := isEnoughIngredients(s2, p2)
	if r2 != true {
		fmt.Println("Failed: TestIsEnoughIngredients: v1: should be true")
	}
}

func TestTryCast(t *testing.T) {
	var st State
	var sps []Spell
	st.inv = [4]int{0, 0, 0, 0}
	sps = append(sps, Spell{})
	sps[0].delta = [4]int{2, 0, 0, 0}

	st.isSpellReady = append(st.isSpellReady, true)
	newState, isCasted := tryCast(st, sps[0], 1)
	if isCasted == false {
		fmt.Println("Failed: TestTryCast: ready spell is not casted")
	}

	if newState.inv != [4]int{2, 0, 0, 0} {
		fmt.Println("Failed: TestTryCast: v1: not ready spell is casted")
	}

	if st.inv != [4]int{0, 0, 0, 0} {
		fmt.Println("Failed: TestTryCast: old inventory is wrong after cast")
	}

	sps[0].delta = [4]int{-1, 1, 0, 0}
	newState, isCasted = tryCast(st, sps[0], 1)
	if isCasted == true {
		fmt.Println("Failed: TestTryCast: impossible spell is casted")
	}
	if newState.inv != [4]int{0, 0, 0, 0} {
		fmt.Println("Failed: TestTryCast: new inventory is wrong after not cast")
	}
	if st.inv != [4]int{0, 0, 0, 0} {
		fmt.Println("Failed: TestTryCast: old inventory is wrong after not cast")
	}
	if newState.isSpellReady[0] == false {
		fmt.Println("Failed: TestTryCast: new spell is not ready after not cast")
	}
	if st.isSpellReady[0] == false {
		fmt.Println("Failed: TestTryCast: old spell is not ready after not cast")
	}

	st.inv = [4]int{3, 3, 3, 0}
	sps[0].delta = [4]int{2, 0, 0, 0}
	newState, isCasted = tryCast(st, sps[0], 1)
	if isCasted == true {
		fmt.Println("Failed: TestTryCast: impossible spell is casted")
	}
	if newState.inv != [4]int{3, 3, 3, 0} {
		fmt.Println("Failed: TestTryCast: new inventory is wrong after not cast")
	}
	if st.inv != [4]int{3, 3, 3, 0} {
		fmt.Println("Failed: TestTryCast: old inventory is wrong after not cast")
	}
	if newState.isSpellReady[0] == false {
		fmt.Println("Failed: TestTryCast: new spell is not ready after not cast")
	}
	if st.isSpellReady[0] == false {
		fmt.Println("Failed: TestTryCast: old spell is not ready after not cast")
	}
}

func TestFindSolution(t *testing.T) {
	var s State
	s.inv = [4]int{2, 0, 0, 0}
	var p Potion
	testName := "TestFindSolution"
	p.delta = [4]int{-1, 0, 0, 0}

	sps := []Spell{}

	solved, _ := findSolution(s, sps, p)
	if (len(solved.turns) != 1) || (solved.turns[0] != "BREW 0") {
		fmt.Println("Failed: " + testName + ": v1: should be possible")
	}
	if len(s.turns) != 0 {
		fmt.Println("Failed: " + testName + ": v1: should not chabge initial state")
	}

	s.inv = [4]int{1, 0, 0, 0}
	p.delta = [4]int{-2, 0, 0, 0}
	solved, _ = findSolution(s, sps, p)
	if len(solved.turns) != 0 {
		fmt.Println("Failed: " + testName + ": should be impossible")
	}

	sps = append(sps, Spell{})
	sps[0].delta = [4]int{2, 0, 0, 0}
	s.isSpellReady = append(s.isSpellReady, true)
	solved, _ = findSolution(s, sps, p)
	if (len(solved.turns) != 2) || (solved.turns[0] != "CAST 0") || (solved.turns[1] != "BREW 0") {
		fmt.Println("Failed: " + testName + ": v3: should be possible")
	}

	s.isSpellReady[0] = false
	solved, _ = findSolution(s, sps, p)
	// if solved.turns != ['REST', 'CAST 0', 'BREW 0']:
	// print("Failed: "+testName+": v4: wrong turns returned")

	p.delta = [4]int{-1, -1, 0, 0}
	sps = append(sps, Spell{})
	sps[1].delta = [4]int{-1, 1, 0, 0}
	sps[1].id = 1
	s.isSpellReady = append(s.isSpellReady, true)
	solved, _ = findSolution(s, sps, p)
	// if solved.turns != ['REST', 'CAST 0', 'CAST 1', 'BREW 0']:
	// print("Failed: "+testName+": v5: wrong turns returned")

	// s = bot.State()
	// s.inv = [3,0,0,0]

	// sps.append(bot.Spell())
	// sps[0].delta = [2,0,0,0]
	// sps[0].isReady = True
	// sps[0].id = 0

	// sps.append(bot.Spell())
	// sps[1].delta = [-1,1,0,0]
	// sps[1].isReady = True
	// sps[1].id = 1

	// sps.append(bot.Spell())
	// sps[2].delta = [0,-1,1,0]
	// sps[2].isReady = True
	// sps[2].id = 2

	// sps.append(bot.Spell())
	// sps[3].delta = [0,0,-1,1]
	// sps[3].isReady = True
	// sps[3].id = 3

	// p = bot.Potion()
	// p.delta = [0,-4,0,0]
	// print('main test is here ->')
	// solved = bot.findSolution(s, p)
	// print(solved.turns)
	// # sps.append(bot.Spell())
	// # sps[1].delta = [-1,1,0,0]
	// # sps[1].isReady = True
}

func TestRealLifeSearch(t *testing.T) {
	// start := time.Now()
	s := State{}
	sps := []Spell{}

	sps = append(sps, Spell{})
	sps[0].delta = [4]int{2, 0, 0, 0}
	s.isSpellReady = append(s.isSpellReady, true)
	sps[0].id = 0

	sps = append(sps, Spell{})
	sps[1].delta = [4]int{-1, 1, 0, 0}
	s.isSpellReady = append(s.isSpellReady, true)
	sps[1].id = 1

	sps = append(sps, Spell{})
	sps[2].delta = [4]int{0, -1, 1, 0}
	s.isSpellReady = append(s.isSpellReady, true)
	sps[2].id = 2

	sps = append(sps, Spell{})
	sps[3].delta = [4]int{0, 0, -1, 1}
	s.isSpellReady = append(s.isSpellReady, true)
	sps[3].id = 3

	// sps = append(sps, Spell{})
	// sps[4].delta = [4]int{-5, 0, 0, 2}
	// s.isSpellReady = append(s.isSpellReady, true)
	// sps[4].isRepeatable = true
	// sps[4].id = 4

	// sps = append(sps, Spell{})
	// sps[5].delta = [4]int{0, 0, 0, 1}
	// s.isSpellReady = append(s.isSpellReady, true)
	// sps[5].id = 5

	// sps = append(sps, Spell{})
	// sps[6].delta = [4]int{3, -1, 0, 0}
	// s.isSpellReady = append(s.isSpellReady, true)
	// sps[6].id = 6

	s.inv = [4]int{3, 0, 0, 0}

	p := Potion{}
	p.delta = [4]int{0, -2, -2, -2}
	// fmt.Println("main test is here ->")
	// solved, _ := findSolution(s, sps, p)
	// fmt.Println(len(solved.turns), solved.turns)
	// elapsed := time.Since(start)

	// fmt.Println(elapsed)
	// < 10 ms
}

func TestGetStatesV2(t *testing.T) {
	state := State{}
	spells := []Spell{}
	potions := []Potion{}
	states := getStatesV2(state, spells, potions)
	if len(states) != 0 {
		t.Error("should be empty")
	}

	state.inv = [4]int{1, 0, 0, 0}
	potions = append(potions, Potion{0, 0, [4]int{-1, 0, 0, 0}, 0})
	state.isPotionBrewed = append(state.isPotionBrewed, true)
	states = getStatesV2(state, spells, potions)
	if len(states) != 0 {
		t.Error("should be empty")
	}
	state.isPotionBrewed[0] = false
	states = getStatesV2(state, spells, potions)
	if (len(states) != 1) && (len(states[0].turns) != 1) && (states[0].turns[0] != "BREW 0") {
		t.Error("something went wrong", states)
	}
}

func TestFindSolutionV2(t *testing.T) {
	state := State{}
	potions := []Potion{}
	spells := []Spell{}
	timeLimit := time.Millisecond * 25

	state.inv = [4]int{3, 0, 0, 0}

	potions = append(potions, Potion{1, 11, [4]int{-3, 0, -2, 0}, 0})
	potions = append(potions, Potion{2, 16, [4]int{-2, -2, 0, -2}, 0})
	potions = append(potions, Potion{3, 12, [4]int{0, -2, -1, -1}, 0})
	potions = append(potions, Potion{4, 12, [4]int{-1, -1, -1, -1}, 0})
	potions = append(potions, Potion{5, 14, [4]int{0, 0, -2, -2}, 0})
	state.isPotionBrewed = append(state.isPotionBrewed, false)
	state.isPotionBrewed = append(state.isPotionBrewed, false)
	state.isPotionBrewed = append(state.isPotionBrewed, false)
	state.isPotionBrewed = append(state.isPotionBrewed, false)
	state.isPotionBrewed = append(state.isPotionBrewed, false)

	spells = append(spells, Spell{1, false, [4]int{2, 0, 0, 0}})
	spells = append(spells, Spell{2, false, [4]int{-1, 1, 0, 0}})
	spells = append(spells, Spell{3, false, [4]int{0, -1, 1, 0}})
	spells = append(spells, Spell{4, false, [4]int{0, 0, -1, 1}})
	// spells = append(spells, Spell{5, false, [4]int{0, 0, 0, 1}})
	state.isSpellReady = append(state.isSpellReady, true)
	state.isSpellReady = append(state.isSpellReady, true)
	state.isSpellReady = append(state.isSpellReady, true)
	state.isSpellReady = append(state.isSpellReady, true)
	// state.isSpellReady = append(state.isSpellReady, true)

	state, elapsed := findSolutionV2(state, potions, spells, timeLimit)
	fmt.Println(state)
	fmt.Println(elapsed)
}
