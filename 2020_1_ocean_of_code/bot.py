import sys
import math
import random as rnd
import time

rnd.seed(19180891)

def dp(*s):
    print(*s, file=sys.stderr)

def dx(x1,x2):
    return abs(x1[0]-x2[0]) + abs(x1[1]-x2[1])

def dboom(x1,x2):
    d = dx(x1,x2)
    if (d == 0): return 2
    if (d == 1) or ((d == 2) and (x1[0] != x2[0]) and (x1[1] != x2[1])): return 1
    return 0

def getInitialPoint(cells, w, h):
    dp('getInitialPoint')
    
    points = [[0,0], [14,0], [0,14], [14,14]]
    points_ids = [0,1,2,3]
    turns = [-1,-1,-1,-1]
    dists = [0,0,0,0]
    for i in range(4):
        pid = rnd.randint(0,len(points_ids)-1)
        p = points_ids[pid]
        x = points[p][0]
        y = points[p][1]
        state = GameState()
        state.origin = points[p]
        if (not cells[x][y].is_land):
            cells[x][y].is_visited = True
            move, turns[p], dists[p] = getNextMove(cells, state, points[p], None, 10, 10)
            cells[x][y].is_visited = False
        else:
            points_ids.remove(p)
    
    maxI = -1
    maxP = -1
    maxP = max(turns)
    maxI = turns.index(maxP)
    if (maxP != -1):
        return points[maxI]

    while True:
        x = rnd.randint(0,w)
        y = rnd.randint(0,h)
        if (not cells[x][y].is_land):
            return [x,y]

def getNextMove(Cells, State, pos, prevMove, depth, gdepth):
    ix, iy = pos
    thiscell = Cells[ix][iy]
    neibs = thiscell.neib_move.keys()

    dxo = dx(pos, State.origin)
    dxe = 0
    if State.runawaymode and (State.enemySpots < State.enemyLimit):
        dxe = -4*dx(pos, State.enemyPosition)

    for n in neibs:
        thiscell.move_steps[n] = 1
        thiscell.move_dists[n] = dxo +  dxe

    nvalid = 0
    for n in neibs:
        if thiscell.neib_move[n].is_visited:
            thiscell.move_valid[n] = False
        else:
            thiscell.move_valid[n] = True
            nvalid += 1

    if (nvalid > 2) and (prevMove != None): thiscell.move_valid[prevMove] = False
    
    maxS = -1
    maxN = ''
    minD = -1
    if depth > 0:
        for n in neibs:
            if thiscell.move_valid[n]:
                newpos = thiscell.neib_move[n].position[:]
                thiscell.neib_move[n].is_visited = True
                move, kidStep, kidDist = getNextMove(Cells, State, newpos, n, depth-1, gdepth)
                thiscell.move_steps[n] += kidStep
                thiscell.move_dists[n] += kidDist
                thiscell.neib_move[n].is_visited = False

                if (thiscell.move_steps[n] > maxS) or \
                    ((thiscell.move_steps[n] == maxS) and (minD > thiscell.move_dists[n])):
                    maxN = n
                    maxS = thiscell.move_steps[n]
                    minD = thiscell.move_dists[n]
    
    if (maxN != ''): return maxN, maxS, minD
    return None, 0, 0

def Analysis(Cells, State, CMD, is_self=False):
    cmds = CMD.split("|")
    msg = ''

    for cmd in cmds:
        line = cmd.split()

        if (line[0] == 'MOVE'):
            Cells, State = movementAnalysis(Cells, State, line[1], is_self)

        if (line[0] == 'TORPEDO'):
            if not State.runawaymode:
                State.runawaymode = True
                msg = 'You scare me!'
            else:
                msg = 'How rude...'
            Cells, State = torpedoAnalysis(Cells, State, [int(line[1]),int(line[2])], is_self)
        if (line[0] == 'SURFACE'):
            if not is_self:
                State.scannedSector = line[1]
                Cells, State = updateEnemySonar(Cells, State, 'Y')
                msg = 'I know this feeling...'
        if (line[0] == 'SILENCE'):
            msg = 'Where did you go!?'
            Cells, State = silentAnalysis(Cells, State, is_self)

    return Cells, State, msg

def torpedoAnalysis(Cells, State, aim, is_self):
    if not is_self:
        for x in range(15):
            for y in range(15):
                if Cells[x][y].is_enemy \
                    and dx([x,y], aim) > 5:
                    Cells[x][y].is_enemy = False
    else:
        for x in range(15):
            for y in range(15):
                if Cells[x][y].is_self \
                    and dx([x,y], aim) > 5:
                    Cells[x][y].is_self = False
    return Cells, State

def canRepeatPathFromPoint(path, step, point):
    if len(path) == 0: return True      # empty path
    if len(path) == step: return True   # walked all the way down

    if path[step] in point.neib_move:
        return canRepeatPathFromPoint(path, step+1, point.neib_move[path[step]])
    else:
        return False

def movementAnalysis(Cells, State, direction, is_self=False):
    ddx = 0
    ddy = 0
    revDirection = ''
    if (direction == 'N'):
        ddy = -1
        revDirection = 'S'
    if (direction == 'S'):
        ddy =  1
        revDirection = 'N'
    if (direction == 'W'):
        ddx = -1
        revDirection = 'E'
    if (direction == 'E'):
        ddx =  1
        revDirection = 'W'

    if is_self:
        State.selfPath.insert(0,revDirection)
    else:
        State.enemyPath.insert(0,revDirection)

    mypos = State.myPosition
    lim = State.enemyLimit

    if is_self:
        State.selfSpots = 0
    else:
        State.enemySpots = 0
        State.enemyPosition = [0,0]
        State.enemyDist = 9999

    if is_self:
        for x in range(15):
            for y in range(15):
                Cells[x][y].is_self_prev = Cells[x][y].is_self
        for x in range(15):
            for y in range(15):
                Cells[x][y].is_self = False
                if State.selfPath[0] in Cells[x][y].neib_move and \
                    Cells[x][y].neib_move[State.selfPath[0]].is_self_prev and \
                    canRepeatPathFromPoint(State.selfPath, 0, Cells[x][y]):
                    Cells[x][y].is_self = True
                    State.selfSpots += 1

    if not is_self:
        for x in range(15):
            for y in range(15):
                Cells[x][y].is_enemy_prev = Cells[x][y].is_enemy
        for x in range(15):
            for y in range(15):
                Cells[x][y].is_enemy = False
                if State.enemyPath[0] in Cells[x][y].neib_move and \
                    Cells[x][y].neib_move[State.enemyPath[0]].is_enemy_prev and \
                    canRepeatPathFromPoint(State.enemyPath, 0, Cells[x][y]):
                    Cells[x][y].is_enemy = True
                    State.enemySpots += 1
                    if (State.enemySpots < State.enemyLimit):
                        d = dx([x,y], State.myPosition)
                        if (d < State.enemyDist):
                            State.enemyPosition = [x,y]
                            State.enemyDist = d

    if (State.enemySpots == 0):
        Cells, State = resetEnemyPositions(Cells, State)
    
    return Cells, State

def silentAnalysis(Cells, State, is_self=False):
    if not is_self:
        lastTurn = State.enemyPath[0]
        State.enemyPath.clear()

        indexes = []
        for x in range(15):
            for y in range(15):
                if (cells[x][y].is_enemy):
                    indexes.append([x,y])
        for ind in indexes:
            x,y = ind
            # jump to W
            if (lastTurn != 'W'):
                obstacle = False
                for px in range(1,5):
                    nx = x - px
                    if (nx > -1) and (not obstacle):
                        if cells[nx][y].is_land:
                            obstacle = True
                        else:
                            cells[nx][y].is_enemy = True
                            State.enemySpots += 1
            # jump to E
            if (lastTurn != 'E'):
                obstacle = False
                for px in range(1,5):
                    nx = x + px
                    if (nx < 15) and (not obstacle):
                        if cells[nx][y].is_land:
                            obstacle = True
                        else:
                            cells[nx][y].is_enemy = True
                            State.enemySpots += 1
            # jump to N
            if (lastTurn != 'N'):
                obstacle = False
                for py in range(1,5):
                    ny = y - py
                    if (ny > -1) and (not obstacle):
                        if cells[x][ny].is_land:
                            obstacle = True
                        else:
                            cells[x][ny].is_enemy = True
                            State.enemySpots += 1
            # jump to S
            if (lastTurn != 'S'):
                obstacle = False
                for py in range(1,5):
                    ny = y + py
                    if (ny < 15) and (not obstacle):
                        if cells[x][ny].is_land:
                            obstacle = True
                        else:
                            cells[x][ny].is_enemy = True
                            State.enemySpots += 1
    else:
        lastTurn = State.selfPath[0]
        State.selfPath.clear()

        indexes = []
        for x in range(15):
            for y in range(15):
                if (cells[x][y].is_self):
                    indexes.append([x,y])
        for ind in indexes:
            x,y = ind
            if (lastTurn != 'W'):
                obstacle = False
                for px in range(1,5):
                    nx = x - px
                    if (nx > -1) and (not obstacle):
                        if cells[nx][y].is_land:
                            obstacle = True
                        else:
                            cells[nx][y].is_self = True
                            State.selfSpots += 1
            if (lastTurn != 'E'):
                obstacle = False
                for px in range(1,5):
                    nx = x + px
                    if (nx < 15) and (not obstacle):
                        if cells[nx][y].is_land:
                            obstacle = True
                        else:
                            cells[nx][y].is_self = True
                            State.selfSpots += 1
            if (lastTurn != 'N'):
                obstacle = False
                for py in range(1,5):
                    ny = y - py
                    if (ny > -1) and (not obstacle):
                        if cells[x][ny].is_land:
                            obstacle = True
                        else:
                            cells[x][ny].is_self = True
                            State.selfSpots += 1
            if (lastTurn != 'S'):
                obstacle = False
                for py in range(1,5):
                    ny = y + py
                    if (ny < 15) and (not obstacle):
                        if cells[x][ny].is_land:
                            obstacle = True
                        else:
                            cells[x][ny].is_self = True
                            State.selfSpots += 1

    return Cells, State

def silence_calc(cells, state, myPos, move):
    maxJump = rnd.randint(0,4)
    res = ['1', '2', '3', '4']
    pos = [myPos[:] for i in range(maxJump)]
    steps = [-1, -1, -1, -1]
    valid = [True, True, True, True]
    
    is_obstacle = False
    for i in range(maxJump):
        if move == 'N':
            pos[i][1] -= i+1
        elif move == 'S':
            pos[i][1] += i+1
        elif move == 'W':
            pos[i][0] -= i+1
        else:
            pos[i][0] += i+1

        if is_obstacle:
            valid[i] = False
        else:
            x, y = pos[i][:]
            if (x < 0) or (x > 14) or (y < 0) or (y > 14):
                valid[i] = False
            if valid[i]:
                if not cells[x][y].is_valid_turn():
                    is_obstacle = True
                    valid[i] = False

    for i in range(maxJump):
        x, y = pos[i][:]
        if valid[i]:
            cells[x][y].is_visited = True
            movenew, steps[i], dist = getNextMove(cells, state, pos[i], move, 5, 5)
    for i in range(maxJump):
        x, y = pos[i][:]
        if valid[i]: cells[x][y].is_visited = False
    
    maxI = -1
    maxS = max(steps)
    for i in range(maxJump):
        if maxS == steps[i]: maxI = i
    if (maxI != -1):
        return res[maxI], pos[0:maxI]
    else:
        return '0', []

def printMap(cells, pos):
    for y in range(15):
        s = ''
        for x in range(15):
            if (x == pos[0]) and (y == pos[1]):
                s += 'A'
            elif cells[x][y].is_enemy:
                s += 'V'
            # elif cells[x][y].is_self:
            #     s += '?'
            elif cells[x][y].is_mine:
                s+= '@'
            elif cells[x][y].is_visited:
                s += 'x'
            elif cells[x][y].is_land:
                s += '#'
            else:
                s += '~'
        dp(s)

def cleanVisited(cells):
    for i in range(15):
        for j in range(15):
            cells[i][j].is_visited = False
        
def resetEnemyPositions(cells, state):
    state.enemySpots = 0
    for y in range(15):
        for x in range(15):
            if (not cells[x][y].is_land):
                cells[x][y].is_enemy = True
                state.enemySpots += 1
    return cells, state

def torpedoCheck(State, myLife, enemyLife):
    if (State.torpedoCharge == State.torpedoMax) \
        and (State.enemySpots < State.enemyLimit):
        # and ((myLife > enemyLife) or (myLife < State.myHealthBefore)):
        xe = State.enemyPosition[0]
        ye = State.enemyPosition[1]
        xm = State.myPosition[0]
        ym = State.myPosition[1]
        xl = [-1, 0 ,1]
        yl = [-1, 0 ,1]
        if (xe == 14): xl = [-1, 0]
        if (xe == 0):  xl = [0, 1]
        if (ye == 14): yl = [-1, 0]
        if (ye == 0):  yl = [0, 1]
        aims = [[xe + x, ye + y] for x in xl for y in yl]
        
        finalAim = None
        for i in range(len(aims)):
            ax, ay = aims[i]
            if (not cells[ax][ay].is_land) \
                and dx([xm,ym],aims[i]) <= 4 \
                and (dboom(aims[i], State.myPosition) == 0) \
                and (dboom(aims[i], [xe,ye]) == 2):
                return True, aims[i]
    return False, None

def mineCheckPlace(cells, State):
    if (State.mineCharge == State.mineMax):
        x = State.myPosition[0]
        y = State.myPosition[1]
        aims = [[x-1,y],[x+1,y],[x,y-1],[x,y+1]]
        res = ['W', 'E', 'N', 'S']

        for i in range(len(aims)):
            ax, ay = aims[i]
            if (ax > 0) and (ax < 14) and (ay > 0) and (ay < 14) \
                and (not cells[ax][ay].is_land)\
                and (not cells[x][y].is_mine):
                
                return True, res[i], aims[i]

    return False, None, None

def mineCheckTrigger(cells, State):
    aim = None
    if State.enemySpots < State.enemyLimit:
        for x in range(15):
            for y in range(15):
                if cells[x][y].is_mine:
                    boomenemy = dboom(State.enemyPosition,[x,y])
                    boomme = dboom(State.myPosition,[x,y])
                    if (boomenemy == 2) and (boomme == 0): return [x,y]
                    if (boomenemy == 1) and (boomme == 0): aim = [x,y]
    return aim

def sonarCheck(Cells, State):
    if State.sonarCharge == State.sonarMax:
        State.enemySpots = 0
        sectors = [0,0,0, 0,0,0, 0,0,0]
        for x in range(15):
            for y in range(15):
                if cells[x][y].is_enemy:
                    sy = y//5
                    sx = x//5
                    s = 3*sy + (sx + 1)
                    sectors[s-1] += 1
                    State.enemySpots += 1
        maxS = max(sectors)
        if (State.enemySpots/maxS > 2): return True, str(sectors.index(maxS)+1)

    return False, None

def updateEnemySonar(cells, State, sonar_result):
    sector = int(State.scannedSector)
    xmin =  (sector%3 - 1)*5
    if (sector%3 == 0): xmin = 10
    ymin = 0
    if (sector < 4):
        ymin = 0
    elif (sector < 7):
        ymin = 5
    else:
        ymin = 10
    if sonar_result == 'N':
        for px in range(0,5):
            for py in range(0,5):
                if cells[xmin+px][ymin+py].is_enemy:
                    cells[xmin+px][ymin+py].is_enemy = False
    if sonar_result == 'Y':
        for px in range(0,15):
            for py in range(0,15):
                if not ((px >= xmin) and (py >= ymin) and (px <= xmin + 4) and (py <= ymin + 4)) \
                    and cells[px][py].is_enemy:
                    cells[px][py].is_enemy = False
    return cells, State

def updateEnemyPositionAfterShot(cells, State, damage):
    aim2 = State.aimPosition[:]
    a1x = [-1, 0, 1]
    a1y = [-1, 0, 1]
    if (aim2[0] == 14): a1x = [-1, 0]
    if (aim2[0] ==  0): a1x = [ 0, 1]
    if (aim2[1] == 14): a1y = [-1, 0]
    if (aim2[1] ==  0): a1y = [ 0, 1]
    aim1 = [[aim2[0] + x, aim2[1] + y] for x in a1x for y in a1y]
    aim1.remove(aim2)

    if damage == 2:
        for x in range(15):
            for y in range(15):
                cells[x][y].is_enemy = False
        cells[aim2[0]][aim2[1]].is_enemy = True
    elif damage == 1:
        for x in range(15):
            for y in range(15):
                if (cells[x][y].is_enemy) and (not [x,y] in aim1): cells[x][y].is_enemy = False
    elif damage == 0:
        cells[aim2[0]][aim2[1]].is_enemy = False
        for a in aim1:
            cells[a[0]][a[1]].is_enemy = False
    return cells, State

def fillNeibMap(Cells):
    for y in range(15):
              # N     S
        ydl = [-1, 0, 1]
        if (y ==  0): ydl = [ 0, 1]
        if (y == 14): ydl = [-1, 0]
        for x in range(15):

            if not cells[x][y].is_land:

                  # W     E
                xdl = [-1, 0, 1]
                if (x ==  0): xdl = [ 0, 1]
                if (x == 14): xdl = [-1, 0]

                for dydl in ydl:
                    for dxdl in xdl:
                        xnew = x + dxdl
                        ynew = y + dydl
                        
                        if not cells[xnew][ynew].is_land:

                            if (dydl == -1) and (dxdl ==  0):
                                cells[x][y].neib_move['N'] = cells[xnew][ynew]
                                cells[x][y].neib_boom['N'] = cells[xnew][ynew]
                            elif (dydl ==  1) and (dxdl ==  0):
                                cells[x][y].neib_move['S'] = cells[xnew][ynew]
                                cells[x][y].neib_boom['S'] = cells[xnew][ynew]
                            elif (dydl ==  0) and (dxdl == -1):
                                cells[x][y].neib_move['W'] = cells[xnew][ynew]
                                cells[x][y].neib_boom['W'] = cells[xnew][ynew]
                            elif (dydl ==  0) and (dxdl ==  1):
                                cells[x][y].neib_move['E'] = cells[xnew][ynew]
                                cells[x][y].neib_boom['E'] = cells[xnew][ynew]
                            elif (dydl == -1) and (dxdl == -1):
                                cells[x][y].neib_boom['NW'] = cells[xnew][ynew]
                            elif (dydl == -1) and (dxdl ==  1):
                                cells[x][y].neib_boom['NE'] = cells[xnew][ynew]
                            elif (dydl ==  1) and (dxdl == -1):
                                cells[x][y].neib_boom['SW'] = cells[xnew][ynew]
                            elif (dydl ==  1) and (dxdl ==  1):
                                cells[x][y].neib_boom['SE'] = cells[xnew][ynew]

    return Cells

def getCharge(Cells, State):
    silenceReady = State.silenceCharge == State.silenceMax
    torpedoReady = State.torpedoCharge == State.torpedoMax
    sonarReady = State.sonarCharge == State.sonarMax
    mineReady = State.mineCharge == State.mineMax

    charge = ''
    if (State.enemySpots == 1) and (not torpedoReady):
        charge = ' TORPEDO'
        State.torpedoCharge += 1
        return charge, Cells, State
    
    if not silenceReady:
        charge = ' SILENCE'
        State.silenceCharge += 1
    elif not torpedoReady:
        charge = ' TORPEDO'
        State.torpedoCharge += 1
    elif not sonarReady:
        charge = ' SONAR'
        State.sonarCharge += 1
    elif not mineReady:
        charge = ' MINE'
        State.mineCharge += 1

    return charge, Cells, State

def CheckMyHealth(Cells, State, myLife):
    dp(myLife, State.myHealthBefore)
    if (State.myHealthBefore - myLife) == 2:
        for y in range(15):
            for x in range(15):
                Cells[x][y].is_self = False
        Cells[State.myPosition[0]][State.myPosition[1]].is_self = True
        State.selfSpots = 1
    elif (State.myHealthBefore - myLife) == 1:
        State.selfSpots = 0

        for y in range(15):
            for x in range(15):
                Cells[x][y].is_self_prev = Cells[x][y].is_self
                Cells[x][y].is_self = False

        for D in Cells[State.myPosition[0]][State.myPosition[1]].neib_boom:
            if Cells[State.myPosition[0]][State.myPosition[1]].neib_boom[D].is_self_prev:
                Cells[State.myPosition[0]][State.myPosition[1]].neib_boom[D].is_self = True
                State.selfSpots += 1

    return Cells, State

class cell:
    def __init__(self):
        self.position = [0,0]
        self.is_land = False
        self.is_visited = False
        self.is_enemy = False
        self.is_mine = False
        self.neib_move = {}
        self.neib_boom = {}
        self.move_dists = {}
        self.move_valid = {}
        self.move_steps = {}

    def is_valid_turn(self):
            return not (self.is_land or self.is_visited)

class GameState:
    def __init__(self):
        self.silenceCharge = 0
        self.silenceMax = 6

        self.torpedoCharge = 0
        self.torpedoMax = 3

        self.mineCharge = 0
        self.mineMax = 3

        self.sonarCharge = 0
        self.sonarMax = 4
        self.scannedSector = None
        self.checkSonarResults = False

        self.aimPosition = [0,0]
        self.enemyHealthBefore = 0
        self.checkIfEnemyIsHit = False

        self.origin = [0,0]
        self.depthDefault = 5

        self.runawaymode = False
        self.myPosition = [0,0]
        self.myHealthBefore = 0
        self.selfSpots = 15*15
        self.selfPath = []

        self.enemySpots = 15*15
        self.enemyPosition = [0,0]
        self.enemyLimit = 20
        self.enemyDist = 0
        self.enemyPath = []

cells = []

width, height, my_id = [int(i) for i in input().split()]
for i in range(height):
    cells.append([])
    for j in range(width):
        cells[-1].append(cell())

for y in range(height):
    string = list(input())
    for x in range(width):
        cells[x][y].position = [x,y]
        cells[x][y].is_land = False if (string[x] != 'x') else True
        cells[x][y].is_visited = False
        cells[x][y].is_enemy = not cells[x][y].is_land
        cells[x][y].is_self = not cells[x][y].is_land
        cells[x][y].is_enemy_prev = not cells[x][y].is_land
        cells[x][y].is_self_prev = not cells[x][y].is_land
        cells[x][y].is_mine = False

cells = fillNeibMap(cells)

init_pos = getInitialPoint(cells, width, height)
print(str(init_pos[0])+' '+str(init_pos[1]))

State = GameState()
State.origin = init_pos[:]
State.myPosition = init_pos[:]

move = None
depth = State.depthDefault

scaryBit = rnd.randint(0,200)
while True:
    scaryBit -= rnd.randint(-5,10)
    if scaryBit < 1:scaryBit = rnd.randint(0,200)
    
    x, y, myLife, enemyLife, torpedo_cooldown, sonar_cooldown, silence_cooldown, mine_cooldown = [int(i) for i in input().split()]
    sonar_result = input()
    opponent_orders = input()

    start = time.time()

    State.myPosition = [x,y]

    if State.checkIfEnemyIsHit:
        damage = State.enemyHealthBefore - enemyLife
        cells, State = updateEnemyPositionAfterShot(cells, State, damage)
        State.enemyHealthBefore = 0
        State.checkIfEnemyIsHit = False

    if (State.checkSonarResults):
        cells, State = updateEnemySonar(cells, State, sonar_result)
        State.checkSonarResults = False
    
    cells, State, enemyMSG = Analysis(cells, State, opponent_orders)

    t1 = time.time() - start
    dp(t1)

    cells[x][y].is_visited = True
    move, steps, dist = getNextMove(cells, State, [x,y], move, depth, gdepth=depth)

    t2 = time.time() - start
    dp(t2)

    if move != None:
        moveAction = "MOVE "+move
        chargeAction = ''
        otherActions = ''
        silenceAction = ''
        messageAction = ' | MSG '+str(scaryBit)

        if (State.enemySpots == 1):
            messageAction = ' | MSG I see you'

        if (enemyMSG != ''): messageAction = ' | MSG '+ enemyMSG

        fireTorpedo, aimTorpedo = torpedoCheck(State, myLife, enemyLife)

        minePlace, placeDirection, mineAim = mineCheckPlace(cells, State)

        mineTrigger = mineCheckTrigger(cells, State)

        sonarExec, sonarSector = sonarCheck(cells, State)

        t3 = time.time() - start
        dp(t3)

        if mineTrigger != None:
            otherActions = "TRIGGER " + str(mineTrigger[0]) + " "+ str(mineTrigger[1])
            cells[mineTrigger[0]][mineTrigger[1]].is_mine = False
            State.enemyHealthBefore = enemyLife
            State.checkIfEnemyIsHit = True
            State.aimPosition = mineTrigger[:]

        if fireTorpedo:
            if otherActions != '': otherActions += "|"
            otherActions += "TORPEDO " + str(aimTorpedo[0])+" "+str(aimTorpedo[1])
            State.enemyHealthBefore = enemyLife
            State.checkIfEnemyIsHit = True
            State.aimPosition = aimTorpedo[:]

            State.torpedoCharge = 0

        if minePlace:
            if otherActions != '': otherActions += '|'
            otherActions += "MINE " + placeDirection
            cells[mineAim[0]][mineAim[1]].is_mine = True

            State.mineCharge = 0

        if sonarExec:
            if otherActions != '': otherActions += '|'
            otherActions += 'SONAR '+sonarSector
            State.checkSonarResults = True
            State.scannedSector = sonarSector

            State.sonarCharge = 0

        if (State.silenceCharge == State.silenceMax) and ((State.selfSpots < 30) or State.checkIfEnemyIsHit):
            size, path = silence_calc(cells, State, [x,y], move)
            for p in path: cells[p[0]][p[1]].is_visited = True
            silenceAction = "SILENCE "+move+" "+size
            State.silenceCharge = 0

        if otherActions != '': otherActions += '|'
        if silenceAction == '':
            chargeAction, cells, State = getCharge(cells, State)
        else:
            moveAction = silenceAction

        CMD = otherActions + moveAction + chargeAction + messageAction
        print(CMD)
        
        cells, State, msg = Analysis(cells, State, CMD, is_self=True)
    else:
        print("SURFACE")
        cleanVisited(cells)
        State.origin = [x,y]
        depth = State.depthDefault

    cells, State = CheckMyHealth(cells, State, myLife)

    # printMap(cells, [x,y])

    State.myHealthBefore = myLife
    
    end = time.time()
    dt = end - start
    if (dt*2 < 0.025): depth += 1
    if (dt   > 0.025): depth -= 1
    dp("T:", depth, dt, ' E:', State.enemySpots, ' S:', State.selfSpots)