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
	id    int
	price int
	delta [4]int
}

// Spell is a spell =/
type Spell struct {
	id           int
	isRepeatable bool
	delta        [4]int
}

func (s Spell) copy() Spell {
	t := Spell{}
	for i := range s.delta {
		t.delta[i] = s.delta[i]
	}
	t.id = s.id
	t.isRepeatable = s.isRepeatable
	return t
}

// State is a game state =/
type State struct {
	inv          [4]int
	turns        []string
	dist         int
	isSpellReady []bool
}

func (s State) copy() State {
	t := State{}
	for i := range s.isSpellReady {
		t.isSpellReady = append(t.isSpellReady, s.isSpellReady[i])
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

// TODO put is ready check back in here
func tryCast(state State, spell Spell, castsTimes int) (State, bool) {
	newState := state.copy()
	total := 0
	for i := range state.inv {
		newState.inv[i] += castsTimes * spell.delta[i]
		if newState.inv[i] < 0 {
			return state.copy(), false
		}
		total += newState.inv[i]
	}
	if total > 10 {
		return state.copy(), false
	}
	return newState, true
}

func rest(state State) State {
	newState := state.copy()
	for i := range newState.isSpellReady {
		newState.isSpellReady[i] = true
	}
	return newState
}

func getStates(state State, spells []Spell) []State {
	newStates := []State{}
	for i := range spells {
		if state.isSpellReady[i] {
			newState, isOk := tryCast(state, spells[i], 1)
			if isOk {
				newState.addTurn("CAST " + i2s(spells[i].id))
				newStates = append(newStates, newState)
			}
			if spells[i].isRepeatable {
				newState, isOk := tryCast(state, spells[i], 2)
				if isOk {
					newState.addTurn("CAST " + i2s(spells[i].id) + " " + i2s(2))
					newStates = append(newStates, newState)
				}
			}
			newState.isSpellReady[i] = false
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

func (t Timer) getTotalElapsed() time.Duration {
	return time.Since(t.start)
}

func findSolution(state State, spells []Spell, potion Potion) (State, time.Duration) {
	timer := Timer{}
	timer.init(len(spells))

	allStates := []State{}
	allStates = append(allStates, state.copy())

	if isEnoughIngredients(allStates[0], potion) {
		allStates[0].addTurn("BREW " + i2s(potion.id))
		dp(" <> already at solution ")
		return allStates[0], timer.getTotalElapsed()
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
			return state, timer.getTotalElapsed()
		}
		// dp(i, all_states[0].inv, all_states[0].turns, all_states[0].dist, minDist)
		// time.Sleep(time.Millisecond * 100)
		if allStates[0].dist <= minDist {
			newStates := getStates(allStates[0], spells)
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
					return s, timer.getTotalElapsed()
				}
			}
		}
		allStates = allStates[1:]
		i++
	}
	dp(" >> search size : ", i, timer.lastElapsed)
	return state, timer.getTotalElapsed()
}

func readInput() (state State, spells []Spell, learnings []Spell, potions []Potion) {
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
		if actionType == "BREW" {
			potions = append(potions,
				Potion{actionID, price, [4]int{delta0, delta1, delta2, delta3}})
		}
		if actionType == "CAST" {
			spells = append(spells,
				Spell{actionID, repeatable, [4]int{delta0, delta1, delta2, delta3}})
			state.isSpellReady = append(state.isSpellReady, castable)
		}
		if actionType == "LEARN" {
			learnings = append(learnings,
				Spell{actionID, repeatable, [4]int{delta0, delta1, delta2, delta3}})
		}
	}
	for i := 0; i < 2; i++ {
		var inv0, inv1, inv2, inv3, score int
		fmt.Scan(&inv0, &inv1, &inv2, &inv3, &score)
		if i == 0 {
			state.inv = [4]int{inv0, inv1, inv2, inv3}
		}
	}
	return
}

func decideLearning(learnings []Spell, roundNumber int, canLearnAgain int) (forceLearn bool, learnID int) {
	for i := range learnings {
		if (roundNumber < 40) && (!forceLearn) &&
			(learnings[i].delta[0] >= 0) &&
			(learnings[i].delta[1] >= 0) &&
			(learnings[i].delta[2] >= 0) &&
			(learnings[i].delta[3] >= 0) {
			forceLearn = true
			learnID = i
		}
	}
	if (roundNumber == canLearnAgain) && (!forceLearn) {
		forceLearn = true
		learnID = 0
	}
	return
}

func main() {
	learningTimeOut := 20
	canLearnAgain := learningTimeOut
	roundNumber := 0
	deepCheckLearningID := 0
	for {
		learnID := -1
		totalElapsed := time.Duration(0)

		state, spells, learnings, potions := readInput()
		forceLearn, learnID := decideLearning(learnings, roundNumber, canLearnAgain)

		turn := "WAIT"
		d1 := 10000
		c1 := 1
		if forceLearn {
			learnTax := learnID
			if state.inv[0] >= learnTax {
				turn = "LEARN " + i2s(learnings[learnID].id)
				canLearnAgain = roundNumber + learningTimeOut
			} else {
				useSpellID := -1
				for i := range spells {
					if (spells[i].delta[0] > 0) &&
						(state.isSpellReady[i]) &&
						(spells[i].delta[1] == 0) &&
						(spells[i].delta[2] == 0) &&
						(spells[i].delta[3] == 0) {
						if useSpellID == -1 {
							useSpellID = i
						} else {
							if spells[i].delta[0] > spells[useSpellID].delta[0] {
								useSpellID = i
							}
						}
					}
				}
				if useSpellID != -1 {
					turn = "CAST " + i2s(spells[useSpellID].id)
				}
			}
		}

		solvedPotions := []State{}
		if turn == "WAIT" {
			for _, p := range potions {
				solved, elapsed := findSolution(state, spells, p)
				solvedPotions = append(solvedPotions, solved)
				totalElapsed += elapsed
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
					turn = "LEARN " + i2s(learnings[0].id)
					canLearnAgain += learningTimeOut
				} else {
					for i := range spells {
						if state.isSpellReady[i] {
							_, isOk := tryCast(state, spells[i], 1)
							if isOk {
								turn = "CAST " + i2s(spells[i].id)
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

		dp("going to check #", deepCheckLearningID)
		spells = append(spells, learnings[deepCheckLearningID])
		state.isSpellReady = append(state.isSpellReady, false)
		iPotion := 0
		bestSpeedUp := 0
		for (totalElapsed < 50*time.Millisecond) && (iPotion < len(solvedPotions)) {
			if len(solvedPotions[iPotion].turns) > 0 {
				solved, elapsed := findSolution(state, spells, potions[iPotion])
				if len(solved.turns) != 0 {
					speedUp := len(solvedPotions[iPotion].turns) - len(solved.turns)
					if speedUp > bestSpeedUp {
						bestSpeedUp = speedUp
					}
				}
				dp(potions[iPotion].id, len(solvedPotions[iPotion].turns), len(solved.turns))
				totalElapsed += elapsed
				iPotion++
			} else {
				iPotion++
			}
		}
		if bestSpeedUp != 0 {
			if state.inv[0] >= deepCheckLearningID {
				turn = "LEARN " + i2s(learnings[deepCheckLearningID].id)
				deepCheckLearningID = 0
			}
		} else {
			deepCheckLearningID++
			if deepCheckLearningID >= len(learnings) {
				deepCheckLearningID = 0
			}
		}

		dp(totalElapsed)
		fmt.Println(turn)
		roundNumber++
	}
}
