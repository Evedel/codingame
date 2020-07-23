import sys
import math
import random
import datetime
import time

# Deliver more ore to hq (left side of the map) than your opponent. Use radars to find ore but beware of traps!
def disp(i,msg):
    # if (i < 0):
    # print(str(i)+" : "+msg, file=sys.stderr)
    return

width, height = [int(i) for i in input().split()]
scorelog = [[],[],[]]
ix = 0
iy = 1
iowner = 2
iindx = 3
lastchance = []

checkagain = []
lastdig = [[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1]]
target  = [[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1]]
myrobots = [-1,-1,-1,-1,-1]

currentenemypoint = [[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1]]
previousenemypoint = [[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1]]
isenemywithobject = [False,False,False,False,False]
trickwaiting = [False,False,False,False,False]
trickwaited = [True,True,True,True,True]

enemystaysonzero = [0,0,0,0,0]

initialrun = [2,2,2,2,2]
firstbombrunner  = 0
firstradarrunner = 1
maxinitialradars = 2
maxinitialbomber = 2

bombs = []
blacklist = []
cells = []
previouscells = []
curradars = []

thereIsBomber = False
maxradars = 24
lastradarplanted = 0
numcurradars = 0
mytime = 1000
bombsdensity = 32

safetycares = False
gamecycle = 0
feelrisky = False
preferenoholes = True

radarcells = []
for x in [4,8,12,16,20,24,28]:
    for y in [3,7,11]:
        radarcells.append([x,y,-1])

def xy2i(x,y):
    return 30*y + x

def is_deposit_empty(x,y):
    if (x < 30) and (y < 15):
        # disp(-1,str(x)+" " + str(y) + " "+ str(cells[xy2i(x,y)]))
        if (cells[xy2i(x,y)][2] == '0'):
            return True
        else:
            return False
    else:
        return False

def is_in_blacklist(x,y):
    i2 = xy2i(x,y)
    for ebl in blacklist:
        if (ebl[2] == i2):
            return True
    return False

def is_in_bombs(x,y):
    i2 = xy2i(x,y)
    for eb in bombs:
        if (eb[2] == i2):
            return True
    return False

def reset_target(i):
    target[i] = [-1,-1,-1]

def has_target(i):
    if (target[i][0] == -1):
        tar = [-1,-1,-1]
        noTarget = True
    else:
        tar = target[i][:]
        noTarget = False
        disp(i, "Continue move to " + str(tar))
    return tar,noTarget

def get_closest_target(x,y,arr):
    dst = 1000
    tar = [-1,-1,-1]
    for e in arr:
        if ((e[3] != 1) and (e[0] > 3) and e[2] != '0'):
            alreadyTarget = False
            for et in target:
                if (et[0] == e[0]) and (et[1] == e[1]):
                    alreadyTarget = True
            if (not alreadyTarget):
                dstloc = math.hypot(x-e[0],y-e[1])
                if (dstloc < dst):
                    tar = e[:]
                    dst = dstloc
                if (dst <= 1):
                    disp(i,"Got closest " + str(tar))
                    return tar,False
    disp(i,"Got closest " + str(tar))
    return tar,False

def get_random_zero(i):
    noTarget = True
    tar = [-1,-1,-1,-1]
    if (myrobots[i][0] == 0):
        tar = [
            random.randint(4,width/3-1),
            random.randint(1,height-1),
            -1,-1]
        disp(i,"New random position " + str(tar))
        noTarget = False
    return tar, noTarget

def get_same_position(i):
    noTarget = True
    tar = [-1,-1,-1]
    if (i < len(myrobots)):
        for j in range(i+1,len(myrobots)):
            dist = math.hypot(myrobots[i][0]-myrobots[j][0],myrobots[i][1] - myrobots[j][1])
            if (dist < 1):
                disp(i,"To close to " + str(j))
                allGood = False
                while (not allGood):
                    tar = [
                        random.randint(1,width-1),
                        random.randint(1,height-1),
                    -1]
                    if (not is_in_blacklist(tar[0],tar[1])):
                        allGood = True
                tar[2] = xy2i(tar[0],tar[1])
                noTarget = False
    return tar, noTarget

def get_radar_position_random(i):
    global maxinitialradars
    global initialrun

    niter    = 0
    maxdist = 0
    globtar  = [-1,-1]
    borderconditions = [[2,1],[2,13]]
    if (numcurradars <= 3):
        if (numcurradars == 1):
            globtar = [random.randint(6,7),random.randint(6,7),-1]
        elif (numcurradars == 2):
            globtar = [random.randint(13,14),random.randint(6,7),-1]
        elif (numcurradars == 3):
            globtar = [random.randint(20,21),random.randint(6,7),-1]
    else:
        while (niter < 20):
            limx = int(width/4 + width*3/4*min(1,2*numcurradars/maxradars))
            tar = [
                random.randint(4,limx-2),
                random.randint(2,height-2),
            -1]
            tar[2] = xy2i(tar[0],tar[1])
            if (not is_in_blacklist(tar[0],tar[1])):
                mindist = 1000
                for er in curradars:
                    dist = math.hypot(tar[0]-er[0],tar[1]-er[1])
                    if dist < mindist:
                        mindist = dist
                for bc in borderconditions:
                    dist = math.hypot(tar[0]-bc[0],tar[1]-bc[1])
                    if dist < mindist:
                        mindist = dist
                if (mindist > maxdist):
                    globtar  = tar[:]
                    maxdist = mindist
            niter += 1

    disp(i,"Random position for RADAR is "+str(globtar)+" : "+str(maxdist))
    return globtar, False

def get_radar_position_predef(i):
    for ierc in range(len(radarcells)):
        if (radarcells[ierc][2] == -1):
            radarcells[ierc][2] = 1
            disp(i,"Predef position for RADAR is "+str(tar))
            return radarcells[ierc], False
    return [-1,-1], True

def get_closest_LCA(i):
    dst = 1000
    tar = [-1,-1,-1,-1]
    mx = myrobots[i][0]
    my = myrobots[i][1]
    idx = -1

    for ica in range(len(checkagain)):
        notAssigned = checkagain[ica][2] == -1

        if (notAssigned):
            dstloc = math.hypot(mx-checkagain[ica][0],my-checkagain[ica][1])
            mult = 1
            # if (gamecycle < 150):
            #     ixy = xy2i(checkagain[ica][0],checkagain[ica][1])
            #     if (cells[ixy][2] == '3'):
            #         mult = 0.6
            #     if (cells[ixy][2] == '2'):
            #         mult = 0.8
            #     if (cells[ixy][2] == '1'):
            #         mult = 1.0
            #     dstloc = mult*dstloc
            #     if (preferenoholes):
            #         if cells[xy2i(checkagain[ica][0],checkagain[ica][1])][3] == 0:
            #             dstloc = 0.25*dstloc

            if (dstloc < dst):
                tar = checkagain[ica][:]
                dst = dstloc
                idx = ica
            if (dst <= 1):
                checkagain[idx][2] = i
                tar[2] = i
                disp(i,"Got closest from LCA " + str(tar) + " : " + str(dst))
                return tar,False
    if (idx != -1):
        checkagain[idx][2] = i
        tar[2] = i
        disp(i,"Got closest from LCA " + str(tar) + " : " + str(dst))
        return tar,False
    else:
        return tar,True

def delete_from_LCA(i,x,y):
    if (len(checkagain) > 0):
        indx = []
        delind = -1
        for ica in range(len(checkagain)):
            if (checkagain[ica][iowner] == i):
                indx.append(ica)
        if (len(indx) > 0):
            for ind in indx:
                if (checkagain[ind][iindx] == xy2i(x,y)):
                    delind = ind
        if (delind != -1):
            lenca = len(checkagain)
            disp(i,"Deleted from LCA " +
                str(lenca) + " => " + str(len(checkagain)-1)+" "+str(checkagain[delind]))
            del checkagain[delind]

def get_bomb_position_random(i):
    foundPlace = False
    maxiter = 10
    niter = 0
    while (not foundPlace) and (niter < maxiter):
        foundPlace = True
        niter += 1
        limx = int(width/2 + width/2*min(1,2*len(bombs)/bombsdensity))
        tar = [
            random.randint(3,limx-3),
            random.randint(3,height-3),
            -1]
        tar[2] = xy2i(tar[0],tar[1])
        if (is_in_blacklist(tar[0],tar[1])):
            foundPlace = False

    disp(i,"Random position for bomb is "+str(tar))
    return tar

def get_bomb_position_deposit(i):
    foundPlace = False
    maxiter = 10
    niter = 0
    tar = [-1,-1,-1]
    while (not foundPlace) and (niter < maxiter):
        foundPlace = True
        niter += 1
        k = 0
        search = True
        while (k < len(cells)) and search:
            if (cells[k][2] == '2') or (cells[k][2] == '3'):
                tar = [
                    cells[k][0],
                    cells[k][1],
                    xy2i(cells[k][0],cells[k][1])
                ]
                search = False
            if (is_in_blacklist(tar[0],tar[1])):
                search = True
            k += 1
        if (k == len(cells)):
            niter = 10
    if (is_in_blacklist(tar[0],tar[1])):
        tar = [-1,-1,-1]
    if (tar[0] == -1):
        disp(i,"Deposit position for bomb is impossible")
    else:
        disp(i,"Deposit position for bomb is "+str(tar))
    return tar

def get_lastchance(i):
    tar = [-1,-1,-1]
    noTarget = True
    maxiter = 30
    niter = 0
    while (maxiter > niter) and (noTarget):
        niter += 1
        minx = 30
        idx = -1
        for ilc in range(len(lastchance)):
            if (lastchance[ilc][0] < minx):
                alreadyInList = False
                for it in target:
                    if (xy2i(it[0],it[1]) == lastchance[ilc][3]):
                        alreadyInList = True
                if (not alreadyInList) and (not is_in_bombs(lastchance[ilc][0],lastchance[ilc][1])):
                    minx = lastchance[ilc][0]
                    idx = ilc
        if (idx != -1):
            tar = lastchance[idx][:]
            noTarget = False
            disp(i,"Requested to try: "+str(tar))
    return tar,noTarget

def sanitise_LCA():
    delcells  = []
    for ica in range(len(checkagain)):
        icax = checkagain[ica][0]
        icay = checkagain[ica][1]
        if is_deposit_empty(icax,icay) or is_in_blacklist(icax,icay):
            delcells.append([icax,icay])
    for cell in delcells:
        delete_from_LCA(-1,cell[0],cell[1])

def is_holes_new(x,y):
    holebefore = previouscells[xy2i(x,y)][3]
    holenow = cells[xy2i(x,y)][3]
    return holebefore != holenow

def is_hole(x,y):
    return cells[xy2i(x,y)][3] == 1

def analyse_enemy_routs():
    for ienemy in range(5):
        if (currentenemypoint[ienemy][0] != -1) and (previousenemypoint[ienemy][0] != -1):
            if (currentenemypoint[ienemy] == previousenemypoint[ienemy]):
                llbl = len(blacklist)
                digs = []
                if (currentenemypoint[ienemy][0] == 0):
                    dx = currentenemypoint[ienemy][0]+1
                    dy = currentenemypoint[ienemy][1]
                    # if (is_holes_new(dx,dy)):
                    if (is_hole(dx,dy)):
                        if(not is_in_blacklist(dx,dy)):
                            blacklist.append([dx,dy,xy2i(dx,dy)])
                            digs.append([dx,dy])
                    enemystaysonzero[ienemy] = 0
                else:
                    dx = currentenemypoint[ienemy][0]
                    dy = currentenemypoint[ienemy][1]
                    # if (is_holes_new(dx,dy)):
                    if (is_hole(dx,dy)):
                        if(not is_in_blacklist(dx,dy)):
                            blacklist.append([dx,dy,xy2i(dx,dy)])
                            digs.append([dx,dy])
                    if (dx < 29):
                        # if (is_holes_new(dx+1,dy)):
                        if (is_hole(dx+1,dy)):
                            if(not is_in_blacklist(dx+1,dy)):
                                blacklist.append([dx+1,dy,xy2i(dx+1,dy)])
                                digs.append([dx+1,dy])
                    if (dx > 1):
                        # if (is_holes_new(dx-1,dy)):
                        if (is_hole(dx-1,dy)):
                            if(not is_in_blacklist(dx-1,dy)):
                                blacklist.append([dx-1,dy,xy2i(dx-1,dy)])
                                digs.append([dx-1,dy])
                    if (dy > 0):
                        # if (is_holes_new(dx,dy-1)):
                        if (is_hole(dx,dy-1)):
                            if(not is_in_blacklist(dx,dy-1)):
                                blacklist.append([dx,dy-1,xy2i(dx,dy-1)])
                                digs.append([dx,dy-1])
                    if (dy < 14):
                        # if (is_holes_new(dx,dy+1)):
                        if (is_hole(dx,dy+1)):
                            if(not is_in_blacklist(dx,dy+1)):
                                blacklist.append([dx,dy+1,xy2i(dx,dy+1)])
                                digs.append([dx,dy+1])
                if (len(digs) > 0):
                    disp(i,"LBL "+str(llbl)+" => "+str(len(blacklist))+str(digs))
        previousenemypoint[ienemy] = currentenemypoint[ienemy][:]

def print_move(myx,myy,tarx,tary):
    dist = [1000,1000,1000,1000,1000]
    cmd = ["","","","",""]

    dist[0] = math.hypot(myx-tarx,myy-tary)
    cmd[0] = "MOVE "+str(tarx)+" "+str(tary)
    if (tarx <= 28):
        dist[1] = math.hypot(myx-(tarx+1),myy-tary)
        cmd[1] = "MOVE "+str(tarx+1)+" "+str(tary)
    if (tarx >= 1):
        dist[2] = math.hypot(myx-(tarx-1),myy-tary)
        cmd[2] = "MOVE "+str(tarx-1)+" "+str(tary)
    if (tary <= 13):
        dist[3] = math.hypot(myx-tarx,myy-(tary+1))
        cmd[3] = "MOVE "+str(tarx)+" "+str(tary+1)
    if (tary >= 1):
        dist[4] = math.hypot(myx-tarx,myy-(tary-1))
        cmd[4] = "MOVE "+str(tarx)+" "+str(tary-1)
    mind = 1000
    mini = -1
    for di in range(len(dist)):
        if (dist[di] < mind):
            mind = dist[di]
            mini = di
    disp(i, cmd[mini])
    print(cmd[mini])

def handle_initial(i,radar_cooldown):
    global firstbombrunner
    global initialrun
    global maxinitialbomber
    global numcurradars

    if (initialrun[i] > 0):
        disp(i, "Initial handler")
        if (i == firstbombrunner) and (initialrun[i] == maxinitialbomber):
            disp(i,"Initial request for Bomb")
            print("REQUEST TRAP")
            initialrun[i] -= 1
            reset_target(i)
            return True,radar_cooldown
        else:
            if (myrobots[i][0] == 0):
                if (radar_cooldown == 0):
                    disp(i,"Initial request for Radar")
                    print("REQUEST RADAR")
                    numcurradars += 1
                    initialrun[i] -= 1
                    radar_cooldown = -1
                    reset_target(i)
                    return True,radar_cooldown
                else:
                    tar,noTarget = get_closest_LCA(i)
                    if (not noTarget):
                        target[i] = tar[:]
                        handle_moving_digging(i)
                        return True,radar_cooldown
                    else:
                        aimy = handle_safe_return_point(i)
                        if (aimy != myy):
                            disp(i,"Someone is dodgy. Changing position.")
                            print("MOVE 0 "+str(aimy))
                        else:
                            disp(i,"Waiting for my initial turn")
                            print("WAIT")
                        return True,radar_cooldown
            else:
                # imply that myi == -1, cause we are inside of the if
                noTarget = True
                if (noTarget):
                    tar,noTarget = get_initial_target_check(i)
                if (noTarget):
                    tar,noTarget = get_closest_LCA(i)
                if (noTarget):
                    tar = [0,myrobots[i][1],-1]
                target[i] = tar[:]
                handle_moving_digging(i)

                return True,radar_cooldown

    return False,radar_cooldown

def get_initial_target_check(i):
    noTarget = False
    tar = [-1,-1,-1]

    if (target[i][0] == -1):
        noTarget = True
        disp(i,"There is no target yet")
    else:
        is_empty = is_deposit_empty(target[i][0],target[i][1])
        is_banned = is_in_blacklist(target[i][0],target[i][1])
        if (is_empty):
            disp(i, "Already empty at "+str(target[i]))
            delete_from_LCA(i,target[i][ix],target[i][iy])
            noTarget = True
        elif (is_banned) and (not feelrisky) and (gamecycle < 150):
            disp(i, "Cell is in blacklist "+str(target[i]))
            delete_from_LCA(i,target[i][ix],target[i][iy])
            noTarget = True
        else:
            disp(i, "Contimue to move to "+str(target[i]))
            noTarget = False
            tar = target[i][:]

    return tar,noTarget

def handle_moving_digging(i):
    tarx = target[i][0]
    tary = target[i][1]
    myx  = myrobots[i][0]
    myy  = myrobots[i][1]
    disp(i,"Moving to: " + str(target[i]))
    if ((tarx == -1) and (tary == -1)):
        print("WAIT")
    else:
        if (tarx == 0):
            print("MOVE "+str(tarx)+" "+str(tary))
        else:
            dist = math.hypot(myx-tarx,myy-tary)
            if (dist > 1):
                print_move(myx,myy,tarx,tary)
            else:
                disp(i,"Digging ["+str(tarx)+" "+str(tary)+"]")
                disp(i,"DIG " + str(tarx) + " " + str(tary))
                print("DIG " + str(tarx) + " " + str(tary))
                delete_from_LCA(i,tarx,tary)

                lastdig[i][0] = tarx
                lastdig[i][1] = tary
                target[i] = [-1,-1,-1]

def handle_safe_return_point(i):
    dangerpoints = [False]*15
    # all blacklisted
    for ibl in range(len(blacklist)):
        if (blacklist[ibl][0] == 1):
            y = blacklist[ibl][1]
            dangerpoints[y] = True
            if (y > 0):
                dangerpoints[y-1] = True
            if (y < 14):
                dangerpoints[y+1] = True
    # and all with enemies
    for enemy in currentenemypoint:
        if (enemy[0] == 0):
            dangerpoints[enemy[1]] = True

    distmin = 500
    myy = myrobots[i][1]
    aimy = myy
    if (dangerpoints[aimy]):
        distmin = 1000
        for idp in range(len(dangerpoints)):
            if (not dangerpoints[idp]):
                dist = abs(myy - idp)
                if (dist < distmin):
                    aimy = idp
                    distmin = dist
    if (not safetycares):
        disp(i,"Safety entering is disabled  ")
        aimy = myy
    else:
        if (distmin == 500):
            disp(i,"Entrypoint is safe "+str(aimy))
        elif (distmin == 1000):
            disp(i,"I feel risky tooday "+str(aimy)+" (no safe points)")
        else:
            disp(i,"Safe return point is "+str(aimy)+" at "+str(distmin))

    return aimy

def handle_suicide(i):
    for r in myrobots:
        nenemies = 0
        thebomb = []
        thebombid = -1
        for ib in range(len(blacklist)):
            b = blacklist[ib]
            if (math.hypot(r[0]-b[0],r[1]-b[1]) <= 1):
                thebomb = b[:]
                thebombid = ib
        if (thebombid != -1):
            disp(i,"There is a bomb nearby")
            for ie in range(len(currentenemypoint)):
                e1 = currentenemypoint[ie]
                e2 = previousenemypoint[ie]
                if (e1[0]==e2[0])and(e1[1]==e2[1])\
                    and(math.hypot(e1[0]-thebomb[0],e1[1]-thebomb[1]) <= 1):
                    nenemies += 1
            disp(i,"Number of enemies near the bomb is "+str(nenemies))
            if (nenemies > 1):
                nfriends = 0
                for f in myrobots:
                    if (math.hypot(f[0]-thebomb[0],f[1]-thebomb[1]) <= 1):
                        nfriends += 1
                disp(i,"Number of friends near the bomb is "+str(nfriends))
                if (nfriends < 2):
                    disp(i,"It is a time to commit a siucide")
                    disp(i,"DIG " + str(thebomb[0]) + " " + str(thebomb[1]))
                    print("DIG " + str(thebomb[0]) + " " + str(thebomb[1]))
                    del blacklist[thebombid]
                    return True
    return False
# def safe_exit(i):
#     myx = myrobots[i][0]
#     myy = myrobots[i][0]
#     if (myx == 0):
#         aimy = handle_safe_return_point(i)
#         if (aimy != myy):
#

def handle_false_waiting(i):
    global trickwaited

    if (trickwaiting[i]):
        if (myrobots[i][0] == 0):
            if (trickwaited[i]):
                trickwaited[i] = False
                if (random.random() < 0.5):
                    disp(i,"False wait on base")
                    print("WAIT")
                    return True
                else:
                    if (not is_in_blacklist(1,myrobots[i][1])):
                        print("DIG "+str(1)+" "+str(myrobots[i][1]))
        else:
            trickwaited[i] = True
    return False

# game loop
while True:
    timestart = datetime.datetime.now()

    lastradarplanted += 1

    prevcurradars = len(curradars)
    previouscells = cells[:]
    cells = []
    curradars = []
    myrobots = []
    lastchance = []
    # my_score: Amount of ore delivered
    my_score, opponent_score = [int(i) for i in input().split()]
    if (gamecycle == 175) and (my_score <= opponent_score):
        feelrisky = True
        disp(gamecycle, "Feel risky now")

    for i in range(height):
        inputs = input().split()
        for j in range(width):
            x = j
            y = i
            # ore: amount of ore or "?" if unknown
            # hole: 1 if cell has a hole
            ore = inputs[2*j]
            hole = int(inputs[2*j+1])
            cells.append([x,y,ore,hole])
            if (cells[-1][2] != '?') and (cells[-1][2] != '0'):
                if (not is_in_blacklist(cells[-1][0],cells[-1][1])):
                    alreadyInList=False
                    for el in checkagain:
                        if (el[0] == cells[-1][0]) and (el[1] == cells[-1][1]):
                            alreadyInList = True
                            break
                    if (not alreadyInList):
                        checkagain.append([cells[-1][0],cells[-1][1],-1,xy2i(x,y)])
                        # if (cells[-1][2] == '2'):
                        #     checkagain.append([cells[-1][0],cells[-1][1],-1,xy2i(x,y)])
                        # if (cells[-1][2] == '3'):
                        #     checkagain.append([cells[-1][0],cells[-1][1],-1,xy2i(x,y)])

                        disp(i,"New entrances for LCA " + str(checkagain[-1]))
                else:
                    lastchance.append([cells[-1][0],cells[-1][1],-1,xy2i(x,y)])
                    # disp(i,"New entrances for LastChanceList " + str(lastchance[-1]))
    # if (gamecycle > 150) and (my_score <= opponent_score):
    #     nchances = 0
    #     for lc in lastchance:
    #         if (lc[0] <= 15):
    #             nchances += 1
    #     if (nchances > 10):
    #         feelrisky = True
    #         disp(gamecycle, "It look beneficial to be risky now")

    # entity_count: number of entities visible to you
    # radar_cooldown: turns left until a new radar can be requested
    # trap_cooldown: turns left until a new trap can be requested
    entity_count, radar_cooldown, trap_cooldown = [int(i) for i in input().split()]
    for i in range(entity_count):
        # id: unique id of the entity
        # type: 0 for your robot, 1 for other robot, 2 for radar, 3 for trap
        # y: position of the entity
        # item: if this entity is a robot, the item it is carrying (-1 for NONE, 2 for RADAR, 3 for TRAP, 4 for ORE)
        id, type, x, y, item = [int(j) for j in input().split()]
        if (type == 0):
            myrobots.append([x,y,item])
            # I'm dead need to care about safety
            if (myrobots[-1][0] == -1):
                safetycares = True

        if (type == 1):
            nid = id
            if (id > 4):
                nid = nid-5
            currentenemypoint[nid] = [x,y]
        if (type == 2):
            curradars.append([x,y])
        if (type == 3):
            alreadyInList = False
            i2 = xy2i(x,y)
            for eb in bombs:
                if (eb[2] == i2):
                    alreadyInList = True
                    break
            if (not alreadyInList):
                bombs.append([x,y,xy2i(x,y)])

    if (prevcurradars > len(curradars)):
        disp(-1,"Less radars now: "+str(prevcurradars)+" => "+str(len(curradars))+
            " != "+str(numcurradars))
        numcurradars -= (prevcurradars - len(curradars))

    analyse_enemy_routs()
    sanitise_LCA()

    for i in range(len(myrobots)):
        myx = myrobots[i][0]
        myy = myrobots[i][1]
        myi = myrobots[i][2]

        if (myx == -1) and (myy == -1):
            print("WAIT")
        elif (myi == -1):
            handled = False

            if (not handled):
                handled = handle_false_waiting(i)

            if (not handled):
                handled = handle_suicide(i)

            if (not handled):
                handled,radar_cooldown = handle_initial(i,radar_cooldown)

            if (not handled):
                if (lastdig[i][0] != -1):
                    disp(i,"Last dig was bad")
                    lastdig[i] = [-1,-1]

            if (not handled) and (radar_cooldown == 0) \
                and (myx == 0) and (numcurradars <= maxradars) \
                and (len(curradars) < len(radarcells)):

                disp(i,"Requested Radar")
                print("REQUEST RADAR")
                numcurradars += 1
                radar_cooldown = -1
                handled = True

            if (not handled) and (trap_cooldown == 0) \
                and (myx == 0):
                # and (myx == 0) and (random.random() < 0.3):

                disp(i,"Requested Bomb")
                print("REQUEST TRAP")
                trap_cooldown = -1
                thereIsBomber = True

                handled = True

            if (not handled):
                noTarget = True

                if (noTarget):
                    tar,noTarget = get_initial_target_check(i)

                if feelrisky and noTarget:
                    tar, noTarget = get_lastchance(i)

                if (noTarget):
                    # tar, noTarget = get_checkagain(i)
                    tar,noTarget = get_closest_LCA(i)
                if (noTarget):
                    tar, noTarget = get_random_zero(i)
                # if (noTarget):
                #     tar, noTarget = get_same_position(i)

                if (noTarget):
                    tar, noTarget = get_closest_target(myx,myy,cells)
                if (noTarget):
                    tar, noTarget = get_lastchance(i)
                # if (tar[0] == -1):
                #     tar, noTarget = get_closest_target(myx,myy,cells)

                target[i] = tar[:]
                tarx = tar[0]
                tary = tar[1]

                handle_moving_digging(i)

        elif (myi == 2):
            tar,noTarget = has_target(i)

            if (is_in_blacklist(tar[0],tar[1])):
                noTarget = True

            if (noTarget):
                tar,noTarget = get_radar_position_random(i)
                # tar,noTarget = get_radar_position_predef(i)
                # if (noTarget):
                #     tar,noTarget = get_radar_position_random(i)

            target[i] = tar[:]
            tarx = tar[0]
            tary = tar[1]

            dist = math.hypot(myx-tarx,myy-tary)
            if ((tarx == -1) and (tary == -1)):
                print("WAIT")
            else:
                if (dist > 1):
                    print_move(myx,myy,tarx,tary)
                else:
                    disp(i,"Radar has been planted ["+str(tarx)+" "+str(tary)+"]")
                    reset_target(i)
                    disp(i,"DIG " + str(tarx) + " " + str(tary))
                    print("DIG " + str(tarx) + " " + str(tary))

        elif (myi == 3):
            tar,noTarget = has_target(i)

            if (is_in_blacklist(tar[0],tar[1])):
                noTarget = True

            if (noTarget):
                if (random.random() < 0.2):
                    tar = get_bomb_position_deposit(i)
                if (tar[0] == -1):
                    tar = get_bomb_position_random(i)


            target[i] = [tar[0],tar[1]]
            tarx = tar[0]
            tary = tar[1]

            dist = math.hypot(myx-tarx,myy-tary)
            if ((tarx == -1) and (tary == -1)):
                print("WAIT")
            else:
                if (dist > 1):
                    print_move(myx,myy,tarx,tary)
                else:
                    disp(i,"Bomb has been planted " + str(target[i]))
                    blacklist.append([tarx,tary,xy2i(tarx,tary)])
                    reset_target(i)
                    thereIsBomber = False
                    disp(i,"DIG " + str(tarx) + " " + str(tary))
                    print("DIG " + str(tarx) + " " + str(tary))

        elif (myi == 4):
            if (lastdig[i][0] != -1):
                ldx = lastdig[i][0]
                ldy = lastdig[i][1]

                lenca = len(checkagain)
                alreadyInList = False
                for ca in checkagain:
                    if (ca[0] == ldx) and (ca[1] == ldy):
                        alreadyInList = True
                if (not alreadyInList) and (not is_deposit_empty(ldx,ldy)):
                    checkagain.append([ldx,ldy,-1,xy2i(ldx,ldy)])
                lastdig[i] = [-1,-1]
                dbgstr = ""
                if (len(checkagain) > 0):
                    dbgstr = str(checkagain[-1])

                disp(i,"Last dig was good LCA "+
                    str(lenca)+" => "+str(len(checkagain))+" "+dbgstr)

            disp(i,"Moving back to base")
            aimy = handle_safe_return_point(i)
            if (aimy != myy):
                disp(i,"MOVE "+str(3)+" "+str(aimy))
                print("MOVE "+str(3)+" "+str(aimy))
            else:
                print("MOVE 0 " + str(myy))

    # disp(-1, "LCA: " + str(checkagain))
    # disp(-1, "LLD: " + str(lastdig))
    # disp(-1, "LTG: " + str(target))
    # disp(-1, "LBL: " + str(blacklist))
    # disp(-1, "LER: " + str(enemyrouts))
    timeend = datetime.datetime.now()
    mytime += 50
    disp(gamecycle,"Time: "+str(mytime - int((timeend-timestart).total_seconds()*1000)))
    gamecycle += 1

    scorelog[0].append(gamecycle)
    scorelog[1].append(my_score)
    scorelog[2].append(opponent_score)
    nalive = 0
    for r in myrobots:
        if (r[0] != -1):
            nalive += 1
    if (gamecycle == 199)or(nalive == 1):
        disp(-1,str(scorelog[0]))
        disp(-1,str(scorelog[1]))
        disp(-1,str(scorelog[2]))
