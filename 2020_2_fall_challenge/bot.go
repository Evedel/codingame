package main

import (
	"fmt"
	"os"
	"strconv"
)

var debug = true

func dp(s ...interface{}) {
	if debug {
		fmt.Fprintln(os.Stderr, s...)
	}
}

type Potion struct {
	dist  int
	id    int
	price int
	delta [4]int
}

type Spell struct {
	delta    [4]int
	id       int
	is_ready bool
}

func (s Spell) copy() Spell {
	var t Spell
	for i := range s.delta {
		t.delta[i] = s.delta[i]
	}
	t.id = s.id
	t.is_ready = s.is_ready
	return t
}

type State struct {
	inv    [4]int
	spells []Spell
	turns  []string
	dist   int
}

func (s State) copy() State {
	var t State
	for _, sp := range s.spells {
		t.spells = append(t.spells, sp.copy())
	}
	for i := range s.inv {
		t.inv[i] = s.inv[i]
	}
	for i := range s.turns {
		t.turns = append(t.turns, s.turns[i])
	}
	t.dist = s.dist
	return t
}

func is_enough_ingredients(state State, potion Potion) bool {
	for i := 0; i < 4; i++ {
		if state.inv[i]+potion.delta[i] < 0 {
			return false
		}
	}
	return true
}

func try_cast(state State, spell_id int) (State, bool) {
	new_state := state.copy()
	if new_state.spells[spell_id].is_ready {
		total := 0
		for i := range state.inv {
			new_state.inv[i] += new_state.spells[spell_id].delta[i]
			if new_state.inv[i] < 0 {
				return state.copy(), false
			}
			total += new_state.inv[i]
		}
		if total > 10 {
			return state.copy(), false
		}
		new_state.spells[spell_id].is_ready = false
		return new_state, true
	}
	return state.copy(), false
}

func rest(state State) State {
	new_state := state.copy()
	for i := range new_state.spells {
		new_state.spells[i].is_ready = true
	}
	return new_state
}

func get_states(state State) []State {
	new_states := []State{}
	for i := range state.spells {
		if state.spells[i].is_ready {
			new_state, is_possible := try_cast(state, i)
			if is_possible {
				new_state.turns = append(new_state.turns, "CAST "+strconv.Itoa(new_state.spells[i].id))
				new_states = append(new_states, new_state)
			}
		} else {
			new_state := rest(state)
			new_state.turns = append(new_state.turns, "REST")
			new_states = append(new_states, new_state)
		}
	}
	return new_states
}

func get_distance(state State, potion Potion) int {
	dist := [4]int{0, 0, 0, 0}
	for i := range potion.delta {
		if potion.delta[i] < 0 {
			dist[i] += state.inv[i] + potion.delta[i]
			if dist[i] < 0 {
				jfirst := -1
				for j := i; j > -1; j-- {
					if dist[j] > 0 {
						jfirst = j
						break
					}
				}
				dist[i] *= i - jfirst
			}
		}
	}
	total := 0
	for i := 0; i < 4; i++ {
		if dist[i] > 0 {
			dist[i] = 0
		}
		if dist[i] < 0 {
			dist[i] = -dist[i]
		}
		total += dist[i]
	}
	return total
}

func find_solution(state State, potion Potion) State {
	all_states := []State{}
	all_states = append(all_states, state.copy())

	if is_enough_ingredients(all_states[0], potion) {
		all_states[0].turns = append(all_states[0].turns, "BREW "+strconv.Itoa(potion.id))
		// # print(i, all_states[0].inv, potion.delta, all_states[0].turns)
		dp("found solution in 0 steps")
		return all_states[0]
	}
	all_states[0].dist = get_distance(all_states[0], potion)
	max_int := 1300
	for i := 0; i < max_int; i++ {
		if len(all_states) == 0 {
			return state
		}
		new_states := get_states(all_states[0])
		for _, s := range new_states {
			// s.dist = get_distance(s, potion)
			// if s.dist <= all_states[0].dist {
			all_states = append(all_states, s)
			// }
			if is_enough_ingredients(s, potion) {
				s.turns = append(s.turns, "BREW "+strconv.Itoa(potion.id))
				dp("found solution in " + strconv.Itoa(i) + " steps")
				return s
			}
		}
		all_states = all_states[1:]
	}
	return state
}

func main() {
	for {
		var state State
		potions := []Potion{}

		var actionCount int
		fmt.Scan(&actionCount)
		for i := 0; i < actionCount; i++ {
			var actionId int
			var actionType string
			var delta0, delta1, delta2, delta3, price, tomeIndex, taxCount int
			// var castable, repeatable bool
			var castable bool
			var _castable, _repeatable int
			fmt.Scan(&actionId, &actionType, &delta0, &delta1, &delta2, &delta3, &price, &tomeIndex, &taxCount, &_castable, &_repeatable)
			castable = _castable != 0
			// repeatable = _repeatable != 0
			if actionType == "BREW" {
				var p Potion
				p.delta = [4]int{delta0, delta1, delta2, delta3}
				p.price = price
				p.id = actionId
				potions = append(potions, p)
			}
			if actionType == "CAST" {
				var s Spell
				s.delta = [4]int{delta0, delta1, delta2, delta3}
				s.id = actionId
				s.is_ready = castable
				state.spells = append(state.spells, s)
			}
		}
		for i := 0; i < 2; i++ {
			var inv0, inv1, inv2, inv3, score int
			fmt.Scan(&inv0, &inv1, &inv2, &inv3, &score)
			if i == 0 {
				state.inv = [4]int{inv0, inv1, inv2, inv3}
			}
		}

		turn := "WAIT"
		d1 := 10000
		c1 := 1
		for _, p := range potions {
			solved := find_solution(state, p)
			if len(solved.turns) != 0 {
				d2 := len(solved.turns)
				c2 := p.price

				dd := float64(d1) / float64(d2)
				dc := float64(c1) / float64(c2)
				if dc < dd {
					turn = solved.turns[0]
					d1 = d2
					c1 = c2
				}
				dp(p.id, dc, dd)
			}
			dp(p.id, p.price, len(solved.turns), solved.turns)
		}
		if turn == "WAIT" {
			for i := 0; i < 4; i++ {
				_, is_ok := try_cast(state, i)
				if is_ok {
					turn = "CAST " + strconv.Itoa(state.spells[i].id)
					break
				}
			}
			if turn == "WAIT" {
				turn = "REST"
			}
		}
		fmt.Println(turn)
	}
}
