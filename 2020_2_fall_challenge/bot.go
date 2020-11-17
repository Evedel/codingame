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

func i2s(n int) string {
	return strconv.Itoa(n)
}

// Potion is a potion =/
type Potion struct {
	dist  int
	id    int
	price int
	delta [4]int
}

// Spell is a spell =/
type Spell struct {
	delta        [4]int
	id           int
	isReady      bool
	isRepeatable bool
}

func (s Spell) copy() Spell {
	t := Spell{}
	for i := range s.delta {
		t.delta[i] = s.delta[i]
	}
	t.id = s.id
	t.isReady = s.isReady
	t.isRepeatable = s.isRepeatable
	return t
}

// State is a game state =/
type State struct {
	inv    [4]int
	spells []Spell
	turns  []string
	dist   int
}

func (s State) copy() State {
	t := State{}
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

func (s *State) addTurn(t string) {
	s.turns = append(s.turns, t)
}

func isEnoughIngredients(state State, potion Potion) bool {
	for i := 0; i < 4; i++ {
		if state.inv[i]+potion.delta[i] < 0 {
			return false
		}
	}
	return true
}

func tryCast(state State, spellID int, castsNumber int) (State, bool) {
	newState := state.copy()
	total := 0
	for i := range state.inv {
		newState.inv[i] += castsNumber * newState.spells[spellID].delta[i]
		if newState.inv[i] < 0 {
			return state.copy(), false
		}
		total += newState.inv[i]
	}
	if total > 10 {
		return state.copy(), false
	}
	newState.spells[spellID].isReady = false
	return newState, true
}

func rest(state State) State {
	newState := state.copy()
	for i := range newState.spells {
		newState.spells[i].isReady = true
	}
	return newState
}

func getStates(state State) []State {
	newStates := []State{}
	for i := range state.spells {
		if state.spells[i].isReady {
			newState, isOk := tryCast(state, i, 1)
			if isOk {
				newState.addTurn("CAST " + i2s(newState.spells[i].id))
				newStates = append(newStates, newState)
			}
			if state.spells[i].isRepeatable {
				newState, isOk := tryCast(state, i, 2)
				if isOk {
					newState.addTurn("CAST " + i2s(newState.spells[i].id) + " " + i2s(2))
					newStates = append(newStates, newState)
				}
			}
		} else {
			newState := rest(state)
			newState.addTurn("REST")
			newStates = append(newStates, newState)
		}
	}
	return newStates
}

func getDistance(state State, potion Potion) int {
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
		} else {
			dist[i] = -dist[i]
		}
		total += dist[i]
	}
	return total
}

// Timer is a timer struct
type Timer struct {
	start         time.Time
	lastElapsed   time.Duration
	sumElapsed    time.Duration
	timeMeasures  int64
	checkEachIter int
	avgElapsedMUS int64
}

func (t *Timer) init(nspells int) {
	t.start = time.Now()
	t.lastElapsed = time.Since(t.start)
	t.sumElapsed = time.Since(t.start)
	t.timeMeasures = 1
	n := nspells
	if nspells == 0 {
		n = 1
	}
	t.checkEachIter = int(50.0 * (4.0 / float64(n)))
}

func (t Timer) isDueToCheck(iter int) bool {
	return iter%t.checkEachIter == 0
}

func (t *Timer) check() {
	t.sumElapsed += (time.Since(t.start) - t.lastElapsed)
	t.timeMeasures++
	t.avgElapsedMUS = t.sumElapsed.Microseconds() / int64(t.timeMeasures)
	t.lastElapsed = time.Since(t.start)
}

func (t Timer) isNextCheckAfter(dt time.Duration) bool {
	return t.lastElapsed.Microseconds()+t.avgElapsedMUS > dt.Microseconds()
}

func findSolution(state State, potion Potion) State {
	timer := Timer{}
	timer.init(len(state.spells))

	allStates := []State{}
	allStates = append(allStates, state.copy())

	if isEnoughIngredients(allStates[0], potion) {
		allStates[0].addTurn("BREW " + i2s(potion.id))
		dp(" <> already at solution ")
		return allStates[0]
	}
	allStates[0].dist = getDistance(allStates[0], potion)
	minDist := allStates[0].dist

	i := 0
	for {
		if timer.isDueToCheck(i) {
			timer.check()
			if timer.isNextCheckAfter(time.Millisecond * 10) {
				break
			}
			// dp(elapsed, elapsed.Microseconds(), avgElapsed, elapsed.Microseconds()+avgElapsed)
		}
		if len(allStates) == 0 {
			return state
		}
		// dp(i, all_states[0].inv, all_states[0].turns, all_states[0].dist, minDist)
		// time.Sleep(time.Millisecond * 100)
		// if allStates[0].dist <= minDist {
		newStates := getStates(allStates[0])
		for _, s := range newStates {
			s.dist = getDistance(s, potion)
			if s.dist <= minDist {
				allStates = append(allStates, s)
				minDist = s.dist
			}
			// dp(i, s.inv, s.turns, s.dist, minDist)
			if isEnoughIngredients(s, potion) {
				s.addTurn("BREW " + i2s(potion.id))
				// dp(i, s.inv, s.turns, s.dist, minDist)
				dp(" >> found solution in : " + i2s(i) + " steps")
				return s
			}
		}
		// }
		allStates = allStates[1:]
		i++
	}
	dp(" >> search size : ", i, timer.lastElapsed)
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
			var actionID int
			var actionType string
			var delta0, delta1, delta2, delta3, price, tomeIndex, taxCount int
			var castable, repeatable bool
			var _castable, _repeatable int
			fmt.Scan(&actionID, &actionType, &delta0, &delta1, &delta2, &delta3, &price, &tomeIndex, &taxCount, &_castable, &_repeatable)
			castable = _castable != 0
			repeatable = _repeatable != 0
			// dp(" ?? ", actionId, actionType, delta0, delta1, delta2, delta3, price, tomeIndex, taxCount, _castable, _repeatable)
			if actionType == "BREW" {
				var p Potion
				p.delta = [4]int{delta0, delta1, delta2, delta3}
				p.price = price
				p.id = actionID
				potions = append(potions, p)
			}
			if actionType == "CAST" {
				var s Spell
				s.delta = [4]int{delta0, delta1, delta2, delta3}
				s.id = actionID
				s.isReady = castable
				s.isRepeatable = repeatable
				state.spells = append(state.spells, s)
			}
			if actionType == "LEARN" {
				spellsToLearn = append(spellsToLearn,
					Spell{[4]int{delta0, delta1, delta2, delta3}, actionID, castable, repeatable})
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
		if (roundNumber < 6) && (!forceLearn) {
			forceLearn = true
			learnID = 0
		}
		if forceLearn {
			learnTax := learnID
			if state.inv[0] >= learnTax {
				turn = "LEARN " + i2s(spellsToLearn[learnID].id)
				canLearnAgain = roundNumber + learningTimeOut
			} else {
				useSpellID := -1
				for i := range state.spells {
					if (state.spells[i].delta[0] > 0) &&
						(state.spells[i].isReady) &&
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
					turn = "CAST " + i2s(state.spells[useSpellID].id)
				} else {
					turn = "REST"
				}
			}
		} else {
			// prices := [5]int{}
			// for i, p := range potions {
			// 	prices[i] = p.price
			// }
			// sort.Ints(prices[:])
			// meanPrice := prices[2]
			for _, p := range potions {
				// if p.price < meanPrice {
				// 	continue
				// }
				solved := findSolution(state, p)
				if len(solved.turns) != 0 {
					d2 := len(solved.turns)
					c2 := p.price

					if math.Abs(float64(d1-d2)) > 2.0 {
						dd := float64(d1) / float64(d2)
						dc := float64(c1) / float64(c2)
						if dc < 2*dd {
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
					turn = "LEARN " + i2s(spellsToLearn[0].id)
					canLearnAgain += learningTimeOut
				} else {
					for i := range state.spells {
						if state.spells[i].isReady {
							_, isOk := tryCast(state, i, 1)
							if isOk {
								turn = "CAST " + i2s(state.spells[i].id)
								break
							}
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
