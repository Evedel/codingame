package main

import (
	"fmt"
	"math"
	"os"
	"strconv"
	"time"
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
	// total := 0
	// for i := range potion.delta {
	// 	diff := state.inv[i] + potion.delta[i]
	// 	if diff > 0 {
	// 		diff = 0
	// 	} else {
	// 		diff = -diff * (i + 1) * (i + 1)
	// 	}
	// 	total += diff
	// }
	return total
}

func find_solution(state State, potion Potion) State {
	start := time.Now()

	all_states := []State{}
	all_states = append(all_states, state.copy())

	if is_enough_ingredients(all_states[0], potion) {
		all_states[0].turns = append(all_states[0].turns, "BREW "+strconv.Itoa(potion.id))
		// # print(i, all_states[0].inv, potion.delta, all_states[0].turns)
		dp(" <> already at solution ")
		return all_states[0]
	}
	all_states[0].dist = get_distance(all_states[0], potion)
	minDist := all_states[0].dist
	i := 0
	elapsed := time.Since(start)
	lastElapsed := elapsed
	sumElapsed := elapsed
	timeMeasures := 1
	checkTime := int(50.0 * (4.0 / float64(len(state.spells))))
	for {
		elapsed = time.Since(start)
		if i%checkTime == 0 {
			sumElapsed += (elapsed - lastElapsed)
			lastElapsed = elapsed
			timeMeasures++
			avgElapsed := sumElapsed.Microseconds() / int64(timeMeasures)
			if elapsed.Microseconds()+avgElapsed > (time.Millisecond * 10).Microseconds() {
				break
			}
			// dp(elapsed, elapsed.Microseconds(), avgElapsed, elapsed.Microseconds()+avgElapsed)
		}
		if len(all_states) == 0 {
			return state
		}
		// dp(i, all_states[0].inv, all_states[0].turns, all_states[0].dist, minDist)
		// time.Sleep(time.Millisecond * 100)
		new_states := get_states(all_states[0])
		for _, s := range new_states {
			s.dist = get_distance(s, potion)
			if s.dist <= minDist {
				all_states = append(all_states, s)
				minDist = s.dist
			}
			if is_enough_ingredients(s, potion) {
				s.turns = append(s.turns, "BREW "+strconv.Itoa(potion.id))
				// dp(i, s.inv, s.turns, s.dist, minDist)
				dp(" >> found solution in : " + strconv.Itoa(i) + " steps")
				return s
			}
		}
		all_states = all_states[1:]
		i++
	}
	// dp(" >> search size : ", i, elapsed)
	return state
}

func main() {
	learningTimeOut := 20
	canLearnAgain := learningTimeOut
	roundNumber := 0
	for {
		forceLearn := false
		learnID := -1

		var state State
		potions := []Potion{}
		spellsToLearn := []Spell{}

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
			// dp(" ?? ", actionId, actionType, delta0, delta1, delta2, delta3, price, tomeIndex, taxCount, _castable, _repeatable)
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
			if actionType == "LEARN" {
				spellsToLearn = append(spellsToLearn,
					Spell{[4]int{delta0, delta1, delta2, delta3}, actionId, true})
				if (!forceLearn) &&
					(roundNumber < 50) &&
					(delta0 >= 0) &&
					(delta1 >= 0) &&
					(delta2 >= 0) &&
					(delta3 >= 0) {
					forceLearn = true
					learnID = len(spellsToLearn) - 1
				}
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
		if (roundNumber < 10) && (!forceLearn) {
			forceLearn = true
			learnID = 0
		}
		if forceLearn {
			learnTax := learnID
			if state.inv[0] >= learnTax {
				turn = "LEARN " + strconv.Itoa(spellsToLearn[learnID].id)
				canLearnAgain = roundNumber + learningTimeOut
			} else {
				useSpellID := -1
				for i := range state.spells {
					if (state.spells[i].delta[0] > 0) &&
						(state.spells[i].is_ready) &&
						(state.spells[i].delta[1] == 0) &&
						(state.spells[i].delta[2] == 0) &&
						(state.spells[i].delta[3] == 0) {
						if useSpellID == -1 {
							useSpellID = i
						} else {
							if state.spells[i].delta[0] > state.spells[useSpellID].delta[0] {
								useSpellID = i
							}
						}
					}
				}
				if useSpellID != -1 {
					turn = "CAST " + strconv.Itoa(state.spells[useSpellID].id)
				} else {
					turn = "REST"
				}
			}
		} else {
			for _, p := range potions {
				solved := find_solution(state, p)
				if len(solved.turns) != 0 {
					d2 := len(solved.turns)
					c2 := p.price

					if math.Abs(float64(d1-d2)) > 2.0 {
						dd := float64(d1) / float64(d2)
						dc := float64(c1) / float64(c2)
						if dc < dd {
							turn = solved.turns[0]
							d1 = d2
							c1 = c2
						}
						dp(" >> ", p.id, dc, dd)
					} else {
						if c1 < c2 {
							turn = solved.turns[0]
							d1 = d2
							c1 = c2
						}
					}
				}
				dp(" >> ", p.id, p.price, len(solved.turns), solved.turns)
			}
			if turn == "WAIT" {
				if roundNumber > canLearnAgain {
					turn = "LEARN " + strconv.Itoa(spellsToLearn[0].id)
					canLearnAgain += learningTimeOut
				} else {
					for i := range state.spells {
						_, isOk := try_cast(state, i)
						if isOk {
							turn = "CAST " + strconv.Itoa(state.spells[i].id)
							break
						}
					}
					if turn == "WAIT" {
						turn = "REST"
					}
				}
			}
		}
		fmt.Println(turn)
		roundNumber++
	}
}
