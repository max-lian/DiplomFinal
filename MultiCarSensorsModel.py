import enum
import random
import time
from abc import abstractmethod
import plot_animation
import json
import FileWR
import copy
#Параметры
leftSensorLenght = 4
leftMiddleSensorLenght = 8
middleSensorLenght = 10
rightMiddleSensorLenght = 8
rightSensorLenght = 4
backSensorLenght = 0
n = 24
m = 24

class Q:
    def __init__(self, state = {}):
        self.gamma = 0.4
        self.alpha = 0.1
        self.state = state

    def get_wp(self, plr):
        self.plr = plr

    def run_model(self, silent=1):
        for i in self.plr:
            i.curr_state = tuple(self.plr.get_features())
            r = i.reward
            if i.prev_state not in self.state:
                self.state[self.plr.prev_state] = 0
            if r == -100:
                nvec = 0
            else:
                nvec = []
                for i in i.actions:
                    cstate = i.curr_state  + tuple(i.actions[i])
                    if cstate not in self.state:
                        self.state[cstate] = 0
                    nvec.append(self.state[cstate])
                #print(self.plr.prev_state, r, nvec)
                nvec = min(nvec)
            self.state[i.prev_state] = self.state[i.prev_state] + self.alpha * (-self.state[i.prev_state]
                    + r + self.gamma * nvec)


class W:
    def __init__(self, map, QModel, eps, coords, randomDest = False):
        self.ens = []
        self.eps = eps
        self.PList = []
        self.map = copy.deepcopy(map)
        self.n = 0
        self.m = 0
        self.fillSize()
        if randomDest:
            for i in coords:
                self.doRandomDest()
        else:
            for i in range (0, len(coords)):
                self.PList.append(P(self,coords[i][0],coords[i][1], eps))

        self.QM = QModel
        self.QM.get_wp(self.PList)

    def fillSize(self):
        self.n = len(map)
        self.m = len(map[0])

    def doRandomDest(self):
        flag = True
        while flag:
            x = random.randint(0, self.n - 1)
            y = random.randint(0, self.m - 1)
            if map[x][y] == 0:
                self.PList.append(P(self, x, y, self.eps))
                flag = False
                self.map[x][y] = 1
            #print(self.P.x, self.P.y)

    def step(self):
        for i in self.PList:
            i.move()
        for i in self.ens:
            if i.active:
                i.move()

    def is_finished(self):
        end_bool = []
        for i in self.PList:
            end_bool_temp = 0
            px, py = i.getxy()
            if map[px][py] == 1:
                end_bool_temp = 1
            end_bool.append([i, end_bool_temp])
        return end_bool

    def get_reward(self, end_bool):
        for i in range (0, len(self.PList)):
            if end_bool[i][1] == 0:
                end_bool[i][0].reward = 10
            if end_bool[i][1] == 1:
                end_bool[i][0].reward = -100

    def play(self, anim = False):
        end_bool = self.is_finished()
        iter = 0
        ANIM = []
        for i in self.PList:
            try:
                i.sensorController.collectData(i)
            except IndexError:
                print("ERROR: ", i.getxy())
        while end_bool == 0:
            # block for animation
            ''''
            if anim:
                ANIM.append([self.P.x, self.P.y])
                name1 = tuple(self.P.get_features())
                for i in self.P.actions:
                    namea = name1 + tuple(self.P.actions[i])
                    if namea not in self.QM.state:
                        self.QM.state[namea] = 0
                    ANIM[iter].append(self.QM.state[namea])
                ANIM[iter].append(name1)
            '''''
            #exception
            if iter > 1000:
                #print("iterations:", iter, end_bool, "sensors:", self.P.get_features(), "dx,dy", self.P.dx, self.P.dy,
                #      "coords:", self.P.getxy())
                #time.sleep(1)
                break
            #main proces
            self.step()
            end_bool = self.is_finished()
            self.get_reward(end_bool)
            self.QM.run_model()
            iter = iter + 1
        if anim:
            return ANIM
        return iter

class un:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.actions = {"forward": 'f',
                        "left": 'l',
                        "right": 'r'}
    def getxy(self):
        return self.x, self.y

class P(un):
    def __init__(self,W, x, y, eps):
        self.sensorController = sensorsController()
        self.W = W
        self.dx = -1
        self.dy = 0
        self.eps = eps
        self.movmnt = 'f'
        un.__init__(self, x, y)
        self.prev_state = tuple(self.get_features()) + (self.dx, self.dy)
        self.curr_state = tuple(self.get_features()) + (self.dx, self.dy)

    def setTarget(self):
        for i in range(0, self.W.n):
            for j in range(0, self.W.m):
                if self.W.map[i][j] == 2:
                    self.targetX = i
                    self.targetY = j


    def get_dxdy(self):
        return self.dx, self.dy
    def get_features(self):
        features = []
        features.append(self.sensorController.leftSensor.distance)
        features.append(self.sensorController.leftMiddleSensor.distance)
        features.append(self.sensorController.middleSensor.distance)
        features.append(self.sensorController.rightMiddleSensor.distance)
        features.append(self.sensorController.rightSensor.distance)
        return features
    def strtg(self):
        randomnum = random.random()
        if  randomnum < self.eps:
            a = []
            for i in self.actions:
                a.append(self.actions[i])
            act = random.choice(a)
        else:
            name1 = tuple(self.get_features())
            best = ['f', float('-inf')]
            for i in self.actions:
                #print(self.actions[i], type(self.actions[i]))
                namea = name1 + tuple(self.actions[i])
                #if self.eps == 0:
                #    print("namea: ",namea, self.QM.state[namea])
                if namea not in self.W.QM.state:
                    self.W.QM.state[namea] = 0
                if best[1] < self.W.QM.state[namea]:
                    best = [self.actions[i], self.W.QM.state[namea]]
            act = best[0]
            #if self.eps == 0:
            #    print("namea act: ", act)
        return act
    def getXYFromMovmnt(self):
        if self.movmnt == 'l':
            tempdx = -self.dy
            self.dy = self.dx
            self.dx = tempdx
        if self.movmnt == 'r':
            tempdx = self.dy
            self.dy = -self.dx
            self.dx = tempdx
    def move(self):
        self.movmnt = self.strtg()
        self.getXYFromMovmnt()
        self.prev_state = tuple(self.get_features()) + tuple(self.movmnt)
        a = self.x + self.dx
        b = self.y + self.dy
        expr = ((0 <= a < self.W.n) and (0 <= b < self.W.m))
        if expr:
            self.W.map[self.x][self.y] = 0
            self.W.map[a][b] = 1
            self.x = a
            self.y = b
            #try:
            self.sensorController.collectData(self)

class EN(un):
    def __init__(self, W, x, y, active = False):
        un.__init__(self, x, y)
        self.W = W
        self.active = active

    def move(self):
        expr = False
        while not expr:
            act = random.choice(self.actions)
            a = self.x + act[0]
            b = self.y + act[1]
            expr = ((0 <= a < self.W.n) and (0 <= b < self.W.n))
            if expr:
                self.x = a
                self.y = b

class sensor():
    def __init__(self, lenght):
        self.lenght = lenght
        #self.data = [0 for i in range(lenght)]
        self.distance = 1
    '''
    def getDistance(self):
        dist = 1
        while dist  <= self.lenght and self.data[dist - 1] == 0:
            dist += 1
        return dist
    '''
class sensorsController():
    def __init__(self):
        self.leftSensor = sensor(leftSensorLenght)
        self.leftMiddleSensor = sensor(leftMiddleSensorLenght)
        self.middleSensor = sensor(middleSensorLenght)
        self.rightMiddleSensor = sensor(rightMiddleSensorLenght)
        self.rightSensor = sensor(rightSensorLenght)
        #self.backSensor = sensor(backSensorLenght)
    def collectData(self, player : P):
        self.leftSensor.distance = 1
        self.leftMiddleSensor.distance = 1
        self.middleSensor.distance = 1
        self.rightMiddleSensor.distance = 1
        self.rightSensor.distance = 1
        #self.backSensor.distance = 1
        x, y = player.getxy()
        dx, dy = player.get_dxdy()
        #print("collectData: ", x, y, dx, dy)

        if x == 0 or x == player.W.n - 1 or y == 0 or y == player.W.m - 1:
            self.leftSensor.distance = 0
            self.leftMiddleSensor.distance = 0
            self.middleSensor.distance = 0
            self.rightMiddleSensor.distance = 0
            self.rightSensor.distance = 0
            #self.backSensorLenght = 0
            return 0
        i = 1
        while i <= leftSensorLenght and map[x - dy*i][y + dx*i] != 1:
            self.leftSensor.distance += 1
            i += 1
        i = 1
        while i <= leftMiddleSensorLenght and map[x + (dx - dy) * i][y + (dx + dy) * i] != 1:
            self.leftMiddleSensor.distance += 1
            i += 1
        i = 1
        while i <= middleSensorLenght and map[x + dx * i][y + dy * i] != 1:
            self.middleSensor.distance += 1
            i += 1
        i = 1
        while i <= rightMiddleSensorLenght and map[x + (dx + dy) * i][y + (-dx + dy) * i] != 1:
            self.rightMiddleSensor.distance += 1
            i += 1
        i = 1
        while i <= rightSensorLenght and map[x + dy * i][y - dx * i] != 1:
            self.rightSensor.distance += 1
            i += 1
        i = 1
        '''''
        while i <= backSensorLenght and map[x - dx * i][y - dy * i] != 1:
            self.backSensor.distance += 1
            i += 1
        '''
class MapGenerator:
    def generateMap(map1, eps):
        n = len(map1)
        m = len(map1[0])
        for i in range(1, n-1):
            for j in range(1, m-1):
                randomnum = random.random()
                if randomnum < eps:
                    map1[i][j] = 0
                else:
                    map1[i][j] = 1
        #MapGenerator.printMap(map1)
    def printMap(map1):
        for i in range(0, n):
            for j in range(0, m):
                print(map1[i][j], end=' '),
            print()

if __name__=="__main__":
    mapgen = MapGenerator
    map = [[1 for i in range(n)] for j in range(m)]
    mapgen.generateMap(map, 0.5)
    '''
    with open('map2.txt') as file:
        file = file.read()
        q = file.replace(' ', '')
        q = q.replace('\n', '')
        for i in range(0, N):
            map.append([])
            for j in range(0, N):
                map[i].append(int(q[j + i * N]))
                #print(j + i * 10, q[j + i * 10])
    '''
    QmodelStates = {}
    try:
        QmodelStates = FileWR.FileWR.readQ('QmodelMult.txt', 6, 5)
        for i in QmodelStates:
            print(i, QmodelStates[i])
    except FileNotFoundError:
        print("file not found")
    QModel = Q(QmodelStates)
    giter = 10000
    coords = [[2, 2], [5, 5]]
    for i in range(giter):
        if i % 2 == 0:
            wr = W(map, QModel, 0.7, coords, True)
        else:
            wr = W(map, QModel, 0.95, coords, True)
        iter = wr.play()
        if i % 1000 == 999:
            print(i, iter)
            #print( i * 0.8/(giter+1))
            mapgen.generateMap(map, 0.3 + i * 0.6/(giter+1))


    for i in QModel.state:
        print(i, QModel.state[i])

    with open('road1.txt') as file:
        file = file.read()
        q = file.replace(' ', '')
        q = q.replace('\n', '')
        for i in range(0, n):
            for j in range(0, m):
                map[i][j] = (int(q[j + i * n]))
                # print(j + i * 10, q[j + i * 10])
    FileWR.FileWR.writeQ(QModel, 'QmodelMult.txt')
    animation = plot_animation.moveAnimation()
    #mapgen.generateMap(map, 0.85)
    wr = W(map, QModel, coords, True)
    anim = wr.play(True)
    animation.animate(map, anim, 'randMap')