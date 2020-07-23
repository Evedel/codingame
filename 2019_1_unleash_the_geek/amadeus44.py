import sys
import math
import random
import datetime
import time

class Cell:
    def __init__(self):
        self._x = -1
        self._y = -1
        self._ore = "x"
        self._hole = False
        self._myhole = False
        self._enemyhole = False
        self._mybomb = False
        self._enemybomb = False
        self._blacklist = False
        self._lastupdated = -1

    def copy(self,cell):
        self._x = cell.x
        self._y = cell.y
        self._ore = cell.ore
        self._hole = cell.hole
        self._myhole = cell.myhole
        self._enemyhole = cell.enemyhole
        self._mybomb = cell.mybomb
        self._enemybomb = cell.enemybomb
        self._blacklist = cell.blacklist
        self._lastupdated = gamecycle

    @property
    def x(self):
        return self._x
    @x.setter
    def x(self, value):
        self._x = value
        self._lastupdated = gamecycle

    @property
    def y(self):
        return self._y
    @y.setter
    def y(self, value):
        self._y = value
        self._lastupdated = gamecycle

    @property
    def hole(self):
        return self._hole
    @hole.setter
    def hole(self, value):
        self._hole = value
        self._lastupdated = gamecycle

    @property
    def myhole(self):
        return self._myhole
    @myhole.setter
    def myhole(self, value):
        self._myhole = value
        self._lastupdated = gamecycle

    @property
    def enemyhole(self):
        return self._enemyhole
    @enemyhole.setter
    def enemyhole(self, value):
        self._enemyhole = value
        self._lastupdated = gamecycle

    @property
    def ore(self):
        return self._ore
    @ore.setter
    def ore(self, value):
        self._ore = value
        self._lastupdated = gamecycle

    @property
    def mybomb(self):
        return self._mybomb
    @mybomb.setter
    def mybomb(self, value):
        self._mybomb = value
        self._lastupdated = gamecycle

    @property
    def enemybomb(self):
        return self._enemybomb
    @enemybomb.setter
    def enemybomb(self, value):
        self._enemybomb = value
        self._lastupdated = gamecycle

    @property
    def blacklist(self):
        return self._blacklist
    @blacklist.setter
    def blacklist(self, value):
        self._blacklist = value
        self._lastupdated = gamecycle

    @property
    def lastupdated(self):
        return self._lastupdated

    @property
    def p(self):
        return ""
        # return "[ "+str(self._x)+" "+str(self._y)+" | o="+self._ore+\
        #     " h="+str(self._hole)[0]+" mb="+str(self._mybomb)[0]+" eb="+\
        #     str(self._enemybomb)[0]+" bl="+str(self._blacklist)[0]+\
        #     " mh="+str(self._myhole)[0]+" eh="+str(self._enemyhole)[0]+\
        #     " ud="+str(self._lastupdated)+"]"

def disp(i,msg):
    # if (i < 0):
    # print(str(i)+" : "+msg, file=sys.stderr)
    return

def disp_timer(i,msg):
    print(str(i)+" : "+msg, file=sys.stderr)

width, height = [int(i) for i in input().split()]
scorelog = [[],[],[]]
ix = 0
iy = 1
iowner = 2
iindx = 3
lastchance = []

checkagain = []
lastdig = [[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1]]
target  = [-1,-1,-1,-1,-1]
myrobots = [-1,-1,-1,-1,-1]

currentenemypoint = [[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1]]
previousenemypoint = [[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1]]

isenemywithobject = [False,False,False,False,False]
trickwaitingbomb = [True,True,True,True,True]

trickwaiting = [True,True,True,True,True]
cantrickwait = [True,True,True,True,True]

radarcarrierfollowers = [[-1,-2],[-1,2],[2,1],[2,-1]]
enemystaysonzero = [0,0,0,0,0]

initialrun = [2,2,2,2,2]
firstbombrunner  = 0
firstradarrunner = 1
maxinitialradars = 2
maxinitialbomber = 2

bombs = []
prevbombs = []

curradars = []

maxradars = 16
lastradarplanted = 0
numcurradars = 0
mytime = 1000
bombsdensity = 64

safetycares = False
gamecycle = 0
feelrisky = False

preferenoholes   = [False,False,True,True,True]
prefermore       = [False,False,True,True,True]
preferenemyholes = [False,False,True,True,True]

agressivekiller = True
killerid = -1

sabbotage = True

cells = []
prevcells = []
for i in range(height):
    for j in range(width):
        x = j
        y = i
        cells.append(Cell())
        prevcells.append(Cell())
        cells[-1].x = x
        cells[-1].y = y

def norm1(x,y):
    return abs(x)+abs(y)

def xy2i(x,y):
    return 30*y + x

def is_blacklist(x,y):
    return cells[xy2i(x,y)].blacklist

def is_checkagain(x,y):
    for el in checkagain:
        if (el[0] == x) and (el[1] == y):
            return True
    return False

def is_mybomb(x,y):
    return cells[xy2i(x,y)].mybomb

def get_radar_carier():
    for ir in range(len(myrobots)):
        if (myrobots[ir][2] == 2):
            return ir
    return -1

def has_target(i):
    if (target[i] == None):
        tar = None
        noTarget = True
    else:
        tar = target[i]
        noTarget = False
        disp(i, "Continue move to " + str(cells[tar].p))
    return tar,noTarget

def get_closest_target(i):
    x = myrobots[i][0]
    y = myrobots[i][1]
    dst = 1000
    tar = None
    noTarget = True
    for ic in range(width*height):
        if ((not cells[ic].hole) and (cells[ic].x > 3) and (cells[ic].ore != '0')):
            alreadyTarget = False
            for et in target:
                if (et == ic):
                    alreadyTarget = True
            if (not alreadyTarget):
                dstloc = norm1(x - cells[ic].x,y - cells[ic].y)
                if (dstloc < dst):
                    tar = ic
                    dst = dstloc
                    noTarget = False
                if (dst <= 1):
                    disp(i,"Got closest "+cells[tar].p)
                    return tar,noTarget
    if (not noTarget):
        disp(i,"Got closest "+cells[tar].p)
    return tar,noTarget

def get_random_zero(i):
    noTarget = True
    tar = None
    if (myrobots[i][0] == 0):
        tar = xy2i(random.randint(4,width/3-1),random.randint(1,height-1))
        disp(i,"New random position "+cells[tar].p)
        noTarget = False
    return tar, noTarget

def get_same_position(i):
    noTarget = True
    tar = None
    if (i < len(myrobots)):
        for j in range(i+1,len(myrobots)):
            dist = norm1(myrobots[i][0]-myrobots[j][0],myrobots[i][1] - myrobots[j][1])
            if (dist < 1):
                disp(i,"To close to " + str(j))
                allGood = False
                while (not allGood):
                    tar = xy2i(random.randint(1,width-1),random.randint(1,height-1))
                    if (not is_blacklist(tar[0],tar[1])):
                        allGood = True
                noTarget = False
    return tar, noTarget

def get_radar_position_random(i):
    global maxinitialradars
    global initialrun

    niter    = 0
    maxdist = 0
    globtar  = -1
    borderconditions = [[2,1],[2,13]]
    if (numcurradars <= 3):
        if (numcurradars == 1):
            globtar = xy2i(random.randint(6,7),random.randint(6,7))
        elif (numcurradars == 2):
            globtar = xy2i(random.randint(13,14),random.randint(6,7))
        elif (numcurradars == 3):
            globtar = xy2i(random.randint(20,21),random.randint(6,7))
    else:
        while (niter < 20):
            limx = int(width/4 + width*3/4*min(1,2*numcurradars/maxradars))
            tarx = random.randint(4,limx-2)
            tary = random.randint(2,height-2)
            if (not is_blacklist(tarx,tary)):
                mindist = 1000
                for er in curradars:
                    dist = norm1(tarx-er[0],tary-er[1])
                    if dist < mindist:
                        mindist = dist
                for bc in borderconditions:
                    dist = norm1(tarx-bc[0],tary-bc[1])
                    if dist < mindist:
                        mindist = dist
                if (mindist > maxdist):
                    globtar  = xy2i(tarx,tary)
                    maxdist = mindist
            niter += 1

    disp(i,"Random position for RADAR is "+cells[globtar].p+" : "+str(maxdist))
    return globtar, False

def get_closest_LCA(i):
    dst = 1000
    tar = None
    mx = myrobots[i][0]
    my = myrobots[i][1]
    idx = -1

    for ica in range(len(checkagain)):
        notAssigned = checkagain[ica][2] == -1

        if (notAssigned):
            dstloc = norm1(mx-checkagain[ica][0],my-checkagain[ica][1])
            ixy = xy2i(checkagain[ica][0],checkagain[ica][1])
            mult = 1
            if (gamecycle < 100):
                if (prefermore[i]):
                    if (cells[ixy].ore == '3'):
                        mult = 0.7
                    if (cells[ixy].ore == '2'):
                        mult = 0.9
                    if (cells[ixy].ore == '1'):
                        mult = 1.0
                    dstloc = mult*dstloc
                if (preferenoholes[i]):
                    if (not cells[ixy].hole):
                        dstloc = 0.5*dstloc
                if (preferenemyholes[i]):
                    if (not cells[ixy].myhole):
                        dstloc = 0.5*dstloc

            if (dstloc < dst):
                tar = ixy
                dst = dstloc
                idx = ica
            if (dst <= 1):
                checkagain[idx][2] = i
                disp(i,"Got closest from LCA " +cells[tar].p+" : " + str(dst))
                return tar,False
    if (idx != -1):
        checkagain[idx][2] = i
        disp(i,"Got closest from LCA "+cells[tar].p+ " : " + str(dst))
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
    noTarget = True
    maxiter = 10
    niter = 0
    tar = None
    tarx = -1
    tary = -1
    while (noTarget) and (niter < maxiter):
        niter += 1
        limx = int(width/4 + width*3/4*min(1,2*len(bombs)/bombsdensity))
        tarx = random.randint(1,limx-3)
        tary = random.randint(3,height-3)
        if (not is_blacklist(tarx,tary)):
            noTarget = False

    tar = xy2i(tarx,tary)
    disp(i,"Random position for bomb is "+cells[tar].p)
    return tar,noTarget

def get_bomb_position_deposit(i):
    noTarget = True
    tar = None
    k = 0
    gdist = 1000
    mx = myrobots[i][0]
    my = myrobots[i][0]
    for k in range(height*width):
        if ((cells[k].ore == '2') or (cells[k].ore == '3')) \
            and (cells[k].hole) and (not cells[k].myhole) \
            and (not cells[k].blacklist):
                dist = norm1(mx-cells[k].x,my-cells[k].y)
                if (dist < gdist):
                    gdist = dist
                    noTarget = False
                    tar = k
    if (noTarget == True):
        disp(i,"Deposit position for bomb is impossible")
    else:
        disp(i,"Deposit position for bomb is "+cells[tar].p)
    return tar,noTarget

def get_bomb_position_deposit_trick(i):
    noTarget = True
    tar = None
    k = 0
    mx = myrobots[i][0]
    my = myrobots[i][1]
    gdist = 1000
    for k in range(height*width):
        if (cells[k].ore != '0') and (cells[k].ore != '?') and (cells[k].hole):
                dist = norm1(mx-cells[k].x,my-cells[k].y)
                if (dist < gdist):
                    tar = k
                    gdist = dist
                    noTarget = False
    if (noTarget == True):
        disp(i,"Deposit position for bomb is impossible")
    else:
        disp(i,"Deposit position for bomb is "+cells[tar].p)
    return tar,noTarget

def get_lastchance(i):
    tar = None
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
                    if (it == lastchance[ilc][3]):
                        alreadyInList = True
                if (not alreadyInList) and (not is_mybomb(lastchance[ilc][0],lastchance[ilc][1])):
                    minx = lastchance[ilc][0]
                    idx = ilc
        if (idx != -1):
            tar = xy2i(lastchance[idx][0],lastchance[idx][1])
            noTarget = False
            disp(i,"Requested to try: "+cells[tar].p)
    return tar,noTarget

def sanitise_LCA():
    delcells  = []
    for ica in range(len(checkagain)):
        icax = checkagain[ica][0]
        icay = checkagain[ica][1]
        if (cells[xy2i(icax,icay)].ore == '0') or (is_blacklist(icax,icay)):
            delcells.append([icax,icay])
    for c in delcells:
        delete_from_LCA(-1,c[0],c[1])

def is_hole_new(x,y):
    xy = xy2i(x,y)
    return cells[xy].hole and (not prevcells[xy].hole)

def is_hole(x,y):
    return cells[xy2i(x,y)].hole

def analyse_enemy_routs():
    disp(-1,str(currentenemypoint))
    disp(-1,str(previousenemypoint))
    for ienemy in range(5):
        if (currentenemypoint[ienemy][0] != -1) and (previousenemypoint[ienemy][0] != -1):
            disp(ienemy,"valid")
            p1x = currentenemypoint[ienemy][0]
            p1y = currentenemypoint[ienemy][1]
            p0x = previousenemypoint[ienemy][0]
            p0y = previousenemypoint[ienemy][1]
            if (p1x == p0x) and (p1y == p0y):
                disp(ienemy,"waited")
                digs = []
                llbl = 0
                if (p1x == 0):
                    disp(ienemy,"zero")
                    ixy = xy2i(p1x+1,p1y)
                    if (cells[ixy].hole):
                        disp(ienemy,"close to hole")
                        # there is a hole
                        # and it is not my hole
                        if (prevcells[ixy].hole):
                            disp(ienemy,"old hole")
                            # it was there before
                            # he may burried somethig inside
                            if(not cells[ixy].blacklist):
                                cells[ixy].blacklist = True
                                digs.append([p1x+1,p1y])
                                llbl += 1
                            # or took an object
                            isenemywithobject[ienemy] = True
                        else:
                            disp(ienemy,"new holes")
                            # it is a new hole
                            # did he have an object for this?
                            if(not cells[xy2i(p1x+1,p1y)].blacklist):
                                cells[xy2i(p1x+1,p1y)].blacklist = True
                                digs.append([p1x+1,p1y])
                                llbl += 1
                    else:
                        disp(ienemy,"took object/waited")
                        # there is no hole so
                        # he should have taken an object
                        isenemywithobject[ienemy] = True
                else:
                    disp(ienemy,"in the field")
                    # enemy is not on zero, but stopped
                    # x1 = x2 in the middle of the field
                    if (isenemywithobject[ienemy]):
                        disp(ienemy,"with objetc")
                        # he may have burried an object
                        points = [[p1x,p1y]]
                        if (p1x < 29):
                            points.append([p1x+1,p1y])
                        if (p1x > 1):
                            points.append([p1x-1,p1y])
                        if (p1y > 0):
                            points.append([p1x,p1y-1])
                        if (p1y < 14):
                            points.append([p1x,p1y+1])

                        nnewpoints = 0
                        for p in points:
                            if (is_hole_new(p[0],p[1])):
                                disp(ienemy,"new hole" + str(p))
                                if(not is_blacklist(p[0],p[1])):
                                    cells[xy2i(p[0],p[1])].blacklist = True
                                    llbl += 1
                                    digs.append([p[0],p[1]])
                                nnewpoints += 1
                        disp(ienemy,str(nnewpoints))
                        if (nnewpoints == 0):
                            disp(ienemy,"no new holes")
                            for p in points:
                                if (is_hole(p[0],p[1])):
                                    disp(ienemy,"agree to any hole")
                                    if(not is_blacklist(p[0],p[1])):
                                        cells[xy2i(p[0],p[1])].blacklist = True
                                        llbl += 1
                                        digs.append([p[0],p[1]])
                    else:
                        # he is without object so all is good
                        disp(ienemy,"empty")
                        pass
                if (len(digs) > 0):
                    disp(i,"LBL "+str(llbl)+" => "+str(digs))
            # p1x != p0x or p1y != p0y
            if (p1x != p0x) and (p0x > 0) and (p1x == 0):
                # suppose enemy has returned to base
                # so he is without an object already
                isenemywithobject[ienemy] = False
        previousenemypoint[ienemy] = currentenemypoint[ienemy][:]
    disp(-1,str(isenemywithobject))

def print_move(myx,myy,tarx,tary):
    dist = [1000,1000,1000,1000,1000]
    cmd = ["","","","",""]

    dist[0] = norm1(myx-tarx,myy-tary)
    cmd[0] = "MOVE "+str(tarx)+" "+str(tary)
    if (tarx <= 28):
        dist[1] = norm1(myx-(tarx+1),myy-tary)
        cmd[1] = "MOVE "+str(tarx+1)+" "+str(tary)
    if (tarx >= 1):
        dist[2] = norm1(myx-(tarx-1),myy-tary)
        cmd[2] = "MOVE "+str(tarx-1)+" "+str(tary)
    if (tary <= 13):
        dist[3] = norm1(myx-tarx,myy-(tary+1))
        cmd[3] = "MOVE "+str(tarx)+" "+str(tary+1)
    if (tary >= 1):
        dist[4] = norm1(myx-tarx,myy-(tary-1))
        cmd[4] = "MOVE "+str(tarx)+" "+str(tary-1)
    mind = 1000
    mini = -1
    for di in range(len(dist)):
        if (dist[di] < mind):
            mind = dist[di]
            mini = di
    disp(i, cmd[mini])
    print(cmd[mini])

def get_radar_follower(i,irc):
    tar = None
    noTarget = True
    if (irc != -1):
        if (target[irc] != None):
            tarx = cells[target[irc]].x
            tary = cells[target[irc]].y
            if (i > irc):
                tarx += radarcarrierfollowers[i-1][0]
                tary += radarcarrierfollowers[i-1][1]
            else:
                tarx += radarcarrierfollowers[i][0]
                tary += radarcarrierfollowers[i][1]
            tar = xy2i(tarx,tary)
            disp(i,"Following a radar carrier to "+cells[tar].p)
            noTarget = False
    return tar,noTarget

def handle_bots_too_close(i):
    # mx = myrobots[i][0]
    # my = myrobots[i][1]
    # corners = [[-1,-1],[1,14],[29,0],[29,14]]
    # for ir in range(len(myrobots)):
    #     if (ir != i) and (norm1(myrobots[ir][0]-mx,myrobots[ir][1]-my) < 2):
    #         p = corners[random.randint(1,4)]
    #         print("MOVE " + p[0] + " " + p[1])
    #         return True
    return False

def handle_initial(i,radar_cooldown):
    global firstbombrunner
    global initialrun
    global maxinitialbomber
    global numcurradars

    if (initialrun[i] > 0):
        disp(i, "Initial handler")
        # if (i == firstbombrunner) and (initialrun[i] == maxinitialbomber):
        #     disp(i,"Initial request for Bomb")
        #     print("REQUEST TRAP")
        #     initialrun[i] -= 1
        #     target[i] = None
        #     return True,radar_cooldown
        # else:
        if (myrobots[i][0] == 0):
            if (radar_cooldown == 0):
                if (gamecycle < 5):
                    if (firstradarrunner == i):
                        disp(i,"Initial request for RADAR")
                        print("REQUEST RADAR")
                        numcurradars += 1
                        initialrun[i] -= 1
                        radar_cooldown = -1
                        target[i] = None
                    else:
                        disp(i,"Waiting for my initial turn")
                        print("WAIT")
                else:
                    disp(i,"Initial request for Radar")
                    print("REQUEST RADAR")
                    numcurradars += 1
                    initialrun[i] -= 1
                    radar_cooldown = -1
                    target[i] = None
            else:
                tar,noTarget = get_closest_LCA(i)
                if (not noTarget):
                    target[i] = tar
                    handle_moving_digging(i)
                else:
                    irc = get_radar_carier()
                    tar,noTarget = get_radar_follower(i,irc)
                    if (noTarget):
                        aimy = handle_safe_return_point(i)
                        if (aimy != myy):
                            disp(i,"Someone is dodgy. Changing position.")
                            print("MOVE 0 "+str(aimy))
                        else:
                            disp(i,"Waiting for my initial turn")
                            print("WAIT")
                    else:
                        target[i] = tar
                        handle_moving_digging(i)
        else:
            # imply that myi == -1, cause we are inside of the if
            noTarget = True
            if (noTarget):
                tar,noTarget = get_initial_target_check(i)
            if (noTarget):
                tar,noTarget = get_closest_LCA(i)
            if (noTarget):
                irc = get_radar_carier()
                tar,noTarget = get_radar_follower(i,irc)
            if (noTarget):
                tar = xy2i(0,myrobots[i][1])
            target[i] = tar
            handle_moving_digging(i)

        return True,radar_cooldown
    else:
        return False,radar_cooldown

def get_initial_target_check(i):
    noTarget = False
    tar = None

    if (target[i] == None):
        noTarget = True
        disp(i,"There is no target yet")
    else:
        tx = cells[target[i]].x
        ty = cells[target[i]].y
        is_empty = cells[target[i]].ore == '0'
        is_banned = is_blacklist(tx,ty)
        if (is_empty):
            disp(i, "Already empty at "+cells[target[i]].p)
            delete_from_LCA(i,tx,ty)
            noTarget = True
        elif (is_banned) and (not feelrisky) and (gamecycle < 150):
            disp(i, "Cell is in blacklist "+cells[target[i]].p)
            delete_from_LCA(i,tx,ty)
            noTarget = True
        elif (cells[target[i]].mybomb):
            disp(i, "Clearly there is my own bomb on "+cells[target[i]].p)
            delete_from_LCA(i,tx,ty)
            noTarget = True
        else:
            disp(i, "Contimue to move to "+cells[target[i]].p)
            noTarget = False
            tar = target[i]

    return tar,noTarget

def handle_moving_digging(i):
    if (target[i] == None):
        disp(i,"After all the efforts I haven't found the solution")
        print("WAIT")
    else:
        tarx = cells[target[i]].x
        tary = cells[target[i]].y
        myx  = myrobots[i][0]
        myy  = myrobots[i][1]
        disp(i,"Moving to: "+cells[target[i]].p)
        if (tarx == 0):
            print("MOVE "+str(tarx)+" "+str(tary))
        else:
            dist = norm1(myx-tarx,myy-tary)
            if (dist > 1):
                print_move(myx,myy,tarx,tary)
            else:
                disp(i,"Digging "+cells[target[i]].p)
                cells[target[i]].myhole = True
                cells[target[i]].hole = True
                disp(i,"DIG " + str(tarx) + " " + str(tary))
                print("DIG " + str(tarx) + " " + str(tary))
                delete_from_LCA(i,tarx,tary)
                lastdig[i][0] = tarx
                lastdig[i][1] = tary
                target[i] = None

def handle_safe_return_point(i):
    if (not safetycares) or (gamecycle >= 150):
        disp(i,"Safety entering is disabled  ")
        aimy = myrobots[i][1]
    else:
        dangerpoints = [False]*15
        # all blacklisted
        for ibl in range(height):
            if (cells[xy2i(1,ibl)].blacklist):
                dangerpoints[ibl] = True
                if (y > 0):
                    dangerpoints[ibl-1] = True
                if (y < 14):
                    dangerpoints[ibl+1] = True
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
        if (distmin == 500):
            disp(i,"Entrypoint is safe "+str(aimy))
        elif (distmin == 1000):
            disp(i,"I feel risky tooday "+str(aimy)+" (no safe points)")
        else:
            disp(i,"Safe return point is "+str(aimy)+" at "+str(distmin))

    return aimy

def handle_suicide(i):
    # for r in myrobots:
    r = myrobots[i][:]
    nenemies = 0
    thebomb = []
    thebombid = None
    for ib in range(width*height):
        if (cells[ib].blacklist):
            if (norm1(r[0]-cells[ib].x,r[1]-cells[ib].y) <= 1):
                thebomb = [cells[ib].x,cells[ib].y]
                thebombid = ib
    if (thebombid != None):
        disp(i,"There is a bomb nearby "+cells[ib].p)
        falive = 0
        ealive = 0
        for ie in range(len(currentenemypoint)):
            e1 = currentenemypoint[ie]
            e2 = previousenemypoint[ie]
            if (myrobots[ie][0] != -1):
                falive += 1
            if (e1[0] != -1):
                ealive += 1
            if (e1[0]==e2[0])and(e1[1]==e2[1])\
                and(norm1(e1[0]-thebomb[0],e1[1]-thebomb[1]) <= 1):
                nenemies += 1
        disp(i,"Number of enemies near the bomb is "+str(nenemies))
        if (nenemies > 1) or\
            ((falive > ealive)and(nenemies > 0))\
            and (ealive > 0):
            nfriends = 0
            for f in myrobots:
                if (norm1(f[0]-thebomb[0],f[1]-thebomb[1]) <= 1):
                    nfriends += 1
            disp(i,"Number of friends near the bomb is "+str(nfriends))
            if (nfriends < 2):
                disp(i,"It is a time to commit a siucide")
                disp(i,"DIG " + str(thebomb[0]) + " " + str(thebomb[1]))
                print("DIG " + str(thebomb[0]) + " " + str(thebomb[1]))
                cells[thebombid].myhole = False
                cells[thebombid].hole = False
                cells[thebombid].blacklist = False
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
    global cantrickwait

    if (trickwaiting[i]):
        if (myrobots[i][0] == 0):
            if (cantrickwait[i]):
                cantrickwait[i] = False
                # if (random.random() < 0.5):
                disp(i,"False wait on base")
                print("WAIT")
                return True
            else:
                cantrickwait[i] = True
    return False

# def extrapolate_next_step(i):
#     disp(i,"I'm on " + str(myrobots[i]))
#     if (target[i] != None):
#         mx = myrobots[i][0]
#         my = myrobots[i][1]
#         tx = cells[target[i]].x
#         ty = cells[target[i]].y
#
#         disp(i,"My aim is "+cells[target[i]].p)
#         answer = [0,0]
#         if (norm1(mx-tx,my-ty) <= 4):
#             answer = [tx,ty]
#         else:
#
#         disp(i,"Next stop "+str(answer))

def update_mybombs():
    if (len(prevbombs) > len(bombs)):
        for pb in prevbombs:
            if (not (pb in bombs)):
                cells[pb].mybomb = False
                cells[pb].blacklist = False
# game loop
while True:
    lastradarplanted += 1

    prevcurradars = len(curradars)
    for k in range(height*width):
        # if (prevcells[k].lastupdated != cells[k].lastupdated):
        prevcells[k].copy(cells[k])

    prevbombs = bombs[:]
    bombs = []
    curradars = []
    myrobots = []
    lastchance = []

    # my_score: Amount of ore delivered
    my_score, opponent_score = [int(i) for i in input().split()]
    timestart = datetime.datetime.now()
    # if (gamecycle == 175) and (my_score-10 <= opponent_score):
    #     feelrisky = True
    #     disp(gamecycle, "Feel risky now")

    for i in range(height):
        inputs = input().split()
        for j in range(width):
            x = j
            y = i
            # ore: amount of ore or "?" if unknown
            # hole: 1 if cell has a hole
            ore = inputs[2*j]
            hole = int(inputs[2*j+1])

            ixy = xy2i(x,y)
            if (ore != cells[ixy].ore): cells[ixy].ore = ore
            if (cells[ixy].hole != hole): cells[ixy].hole = (hole == 1)

            if (ore != '?') and (ore != '0'):
                if (not is_blacklist(x,y)) and (not is_checkagain(x,y)):
                    checkagain.append([x,y,-1,xy2i(x,y)])
                    # if (cells[-1][2] == '2'):
                    #     checkagain.append([cells[-1][0],cells[-1][1],-1,xy2i(x,y)])
                    # if (cells[-1][2] == '3'):
                    #     checkagain.append([cells[-1][0],cells[-1][1],-1,xy2i(x,y)])
                    disp(i,"New entrances for LCA " + str(checkagain[-1]))
                else:
                    if (not cells[xy2i(x,y)].mybomb):
                        lastchance.append([x,y,-1,xy2i(x,y)])
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
            # if (myrobots[-1][0] == -1):
            #     safetycares = True

        if (type == 1):
            nid = id
            if (id > 4):
                nid = nid-5
            currentenemypoint[nid] = [x,y]
        if (type == 2):
            curradars.append([x,y])
        if (type == 3):
            bombs.append(xy2i(x,y))

    if (prevcurradars > len(curradars)):
        disp(-1,"Less radars now: "+str(prevcurradars)+" => "+str(len(curradars))+
            " != "+str(numcurradars))
        numcurradars -= (prevcurradars - len(curradars))

    if (gamecycle == 0):
        dist = 1000
        firstradarrunner = 0
        for ir in range(5):
            if abs(myrobots[ir][1] - 7) < dist:
                dist = abs(myrobots[ir][1] - 7)
                firstradarrunner = ir
        disp(firstradarrunner, "I'am the first radar runner")

    update_mybombs()
    analyse_enemy_routs()
    sanitise_LCA()

    for i in range(len(myrobots)):
        myx = myrobots[i][0]
        myy = myrobots[i][1]
        myi = myrobots[i][2]

        # if (i == killerid):
        #     handled = handle_killer_searsh(i)
        handled = handle_bots_too_close(i)

        if (myx == -1) and (myy == -1):
            if (not handled): print("WAIT")
        elif (myi == -1):
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
                and (gamecycle < 175):

                disp(i,"Requested Radar")
                print("REQUEST RADAR")
                numcurradars += 1
                radar_cooldown = -1
                handled = True
                target[i] = None

            if (not handled) and (trap_cooldown == 0) \
                and (myx == 0) and (gamecycle < 150):
                if (random.random() < 0.5) and (cantrickwait[i]):
                    disp(i,"Requested Bomb")
                    print("REQUEST TRAP")
                    trap_cooldown = -1
                    handled = True
                    target[i] = None
                else:
                    handled = handle_false_waiting(i)
            # if (not handled) and (gamecycle < 150):
            #     handled = handle_false_waiting(i)

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
                    irc = get_radar_carier()
                    tar,noTarget = get_radar_follower(i,irc)

                if (noTarget):
                    tar, noTarget = get_random_zero(i)
                # if (noTarget):
                #     tar, noTarget = get_same_position(i)

                if (noTarget):
                    tar, noTarget = get_closest_target(i)
                if (noTarget):
                    tar, noTarget = get_lastchance(i)
                # if (tar[0] == -1):
                #     tar, noTarget = get_closest_target(myx,myy,cells)
                target[i] = tar
                handle_moving_digging(i)

        elif (myi == 2):
            if (not handled):
                tar,noTarget = has_target(i)

                if (not noTarget):
                    if (is_blacklist(cells[tar].x,cells[tar].y)):
                        noTarget = True

                if (noTarget):
                    tar,noTarget = get_radar_position_random(i)

                target[i] = tar
                tarx = cells[target[i]].x
                tary = cells[target[i]].y

            # handled = handle_suicide(i)
            # handled = False
            if (not handled):
                dist = norm1(myx-tarx,myy-tary)
                if ((tarx == -1) and (tary == -1)):
                    print("WAIT")
                else:
                    if (dist > 1):
                        print_move(myx,myy,tarx,tary)
                    else:
                        disp(i,"Radar has been planted ["+str(tarx)+" "+str(tary)+"]")
                        cells[target[i]].myhole = True
                        cells[target[i]].hole = False
                        disp(i,"DIG " + str(tarx) + " " + str(tary))
                        print("DIG " + str(tarx) + " " + str(tary))
                        target[i] = None

        elif (myi == 3):
            if (not handled):
                tar,noTarget = has_target(i)

                if (not noTarget) and (not trickwaitingbomb[i]):
                    if (is_blacklist(cells[tar].x,cells[tar].y)):
                        noTarget = True

                if (noTarget):
                    if (trickwaitingbomb[i]):
                        tar,noTarget = get_bomb_position_deposit_trick(i)
                    else:
                        tar,noTarget = get_bomb_position_deposit(i)

                if (noTarget):
                    tar, noTarget = get_bomb_position_random(i)

                target[i] = tar
                tarx = cells[target[i]].x
                tary = cells[target[i]].y

            if (not handled):
                handled = handle_suicide(i)

            if (not handled):
                dist = norm1(myx-tarx,myy-tary)
                if ((tarx == -1) and (tary == -1)):
                    print("WAIT")
                else:
                    if (dist > 1):
                        print_move(myx,myy,tarx,tary)
                    else:
                        if (trickwaitingbomb[i]):
                            trickwaitingbomb[i] = False
                            disp(i,"Trick planting the bomb")
                            print("WAIT")
                            target[i] = None
                        else:
                            trickwaitingbomb[i] = True
                            cells[target[i]].blacklist = True
                            cells[target[i]].mybomb = True
                            cells[target[i]].myhole = True
                            cells[target[i]].hole = True
                            disp(i,"Bomb has been planted " +cells[target[i]].p)
                            disp(i,"DIG " + str(tarx) + " " + str(tary))
                            print("DIG " + str(tarx) + " " + str(tary))
                            target[i] = None

        elif (myi == 4):
            if (not handled):
                if (lastdig[i][0] != -1):
                    ldx = lastdig[i][0]
                    ldy = lastdig[i][1]

                    lenca = len(checkagain)
                    alreadyInList = False
                    for ca in checkagain:
                        if (ca[0] == ldx) and (ca[1] == ldy):
                            alreadyInList = True

                    dbgstr = ""
                    if (not alreadyInList) and (not cells[xy2i(ldx,ldy)].ore == '0'):
                        checkagain.append([ldx,ldy,-1,xy2i(ldx,ldy)])
                        dbgstr = str(checkagain[-1])
                    lastdig[i] = [-1,-1]

                    disp(i,"Last dig was good LCA "+
                        str(lenca)+" => "+str(len(checkagain))+" "+dbgstr)

            if (not handled):
                handled = handle_suicide(i)

            if (not handled):
                disp(i,"Moving back to base")
                aimy = handle_safe_return_point(i)
                if (aimy != myy):
                    disp(i,"MOVE "+str(3)+" "+str(aimy))
                    print("MOVE "+str(3)+" "+str(aimy))
                else:
                    disp(i,"MOVE 0 "+str(myy))
                    print("MOVE 0 " + str(myy))

    # disp(-1, "LCA: " + str(checkagain))
    # disp(-1, "LLD: " + str(lastdig))
    # disp(-1, "LTG: " + str(target))
    # disp(-1, "LBL: " + str(blacklist))
    # disp(-1, "LER: " + str(enemyrouts))
    timeend = datetime.datetime.now()
    mytime += 50
    delta = int((timeend-timestart).total_seconds()*1000)
    disp_timer(gamecycle,"time: "+str(mytime - delta)+" delta: "+str(delta))
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
