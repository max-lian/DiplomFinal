import enum
import random
import time
from abc import abstractmethod
import plot_animation

#Параметры
leftSensorLenght = 1
leftMiddleSensorLenght = 3
middleSensorLenght = 4
rightMiddleSensorLenght = 3
rightSensorLenght = 1
backSensorLenght = 1
n = 24
m = 24

class Q:
    def __init__(self):
        self.gamma = 0.9
        self.alpha = 0.1
        self.state = {}

    def get_wp(self, plr):
        self.plr = plr

    def run_model(self, silent=1):
        self.plr.curr_state = tuple(self.plr.get_features()) + (self.plr.dx, self.plr.dy)

        r = self.plr.reward
        #print(r)
        if self.plr.prev_state not in self.state:
            self.state[self.plr.prev_state] = 0

        nvec = []
        #if self.plr.eps == 0:
        #   print(self.plr.curr_state[:-2])
        #    print("X, Y: ",self.plr.x, self.plr.y, " prev state: ", self.plr.prev_state, self.state[self.plr.prev_state], " stete: ",self.plr.curr_state, self.state[self.plr.curr_state])
        for i in self.plr.actions:
            cstate = self.plr.curr_state[:-2] + (i[0], i[1])
            if cstate not in self.state:
                self.state[cstate] = 0
            nvec.append(self.state[cstate])

        #if self.plr.eps == 0:
        #    print(nvec)
        nvec = max(nvec)
        self.state[self.plr.prev_state] = self.state[self.plr.prev_state] + self.alpha * (-self.state[self.plr.prev_state]
                + r + self.gamma * nvec)


class W:
    def __init__(self, map, QModel, eps, x=1, y=1, enem=0, randomDest=False):
        self.ens = []
        for i in range(enem):
            self.ens.append(EN(self, x, y))
        self.P = P(self, x, y, eps)
        self.map = map
        self.n = 0
        self.m = 0
        self.fillSize()
        if randomDest:
            self.doRandomDest()
        self.QM = QModel
        self.QM.get_wp(self.P)

    def fillSize(self):
        self.n = len(map)
        self.m = len(map[0])

    def doRandomDest(self):
        flag = True
        while flag:
            x = random.randint(0, self.n - 1)
            y = random.randint(0, self.m - 1)
            if map[x][y] == 0:
                flag = False
                self.P.x = x
                self.P.y = y

    def step(self):
        self.P.move()

    def is_finished(self):
        px, py = self.P.getxy()
        end_bool = 0
        if map[px][py] == 1:
            end_bool = 1
        if map[px][py] == 2:
            end_bool = 2
        return end_bool

    def get_reward(self, end_bool, iteration):
        if end_bool == 0:
            self.P.reward = -0.1 #+ 1/(100 * ((self.P.x - self.P.targetX) ** 2 + (self.P.y - self.P.targetY) ** 2))
        if end_bool == 1:
            self.P.reward = -100
        if end_bool == 2:
            self.P.reward = 1000

    def play(self, anim = False):
        end_bool = self.is_finished()
        iter = 0
        ANIM = []
        try:
            self.P.sensorController.collectData(self.P)
        except IndexError:
            print("ERROR: ", self.P.getxy())
        while end_bool == 0:
            # block for animation
            if anim:
                ANIM.append([self.P.x, self.P.y])
                name1 = tuple(self.P.get_features())
                for i in self.P.actions:
                    namea = name1 + (i[0], i[1])
                    if namea not in self.QM.state:
                        self.QM.state[namea] = 0
                    ANIM[iter].append(self.QM.state[namea])
            #exception
            if iter > 10000:
                print("iterations:", iter, end_bool, "sensors:", self.P.get_features(), "dx,dy", self.P.dx, self.P.dy,
                      "coords:", self.P.getxy())
                #time.sleep(1)
                break
            #main proces
            self.step()
            end_bool = self.is_finished()
            self.get_reward(end_bool, iter)
            self.QM.run_model()
            iter = iter + 1
            #if(iter % 100 == 0):
        #if(self.P.eps == 0):
        #    print("end coords:", self.P.getxy())
        if anim:
            return ANIM
        return iter

class un:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.actions = [(1, 0), (-1, 0),
                        (0, 1), (0, -1)]
    def getxy(self):
        return self.x, self.y

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

class P(un):
    def __init__(self,W, x, y, eps):
        self.sensorController = sensorsController()
        self.W = W
        self.dx = -1
        self.dy = 0
        self.eps = eps
        un.__init__(self, x, y)
        self.prev_state = tuple(self.get_features()) + (self.dx, self.dy)
        self.curr_state = tuple(self.get_features()) + (self.dx, self.dy)

    def setTarget(self):
        for i in range(0, self.W.n):
            for j in range(0, self.W.m):
                if self.map[i][j] == 2:
                    self.targetX = i
                    self.targetY = j


    def get_dxdy(self):
        return self.dx, self.dy
    def get_features(self):
        features = []
        features.append(self.x)
        features.append(self.y)
        return features

    def strtg(self):
        randomnum = random.random()
        if  randomnum < self.eps:
            act = random.choice(self.actions)
        else:
            name1 = tuple(self.get_features())
            best = [(0, 0), float('-inf')]
            for i in self.actions:
                namea = name1 + (i[0], i[1])
                #if self.eps == 0:
                #    print("namea: ",namea, self.QM.state[namea])
                if namea not in self.W.QM.state:
                    self.W.QM.state[namea] = 0
                if best[1] < self.W.QM.state[namea]:
                    best = [i, self.W.QM.state[namea]]
            act = best[0]
            #if self.eps == 0:
            #    print("namea act: ", act)
        return act

    def move(self):
        self.dx, self.dy = self.strtg()
        self.prev_state = tuple(self.get_features()) + (self.dx, self.dy)
        a = self.x + self.dx
        b = self.y + self.dy
        expr = ((0 <= a < self.W.n) and (0 <= b < self.W.m))
        if expr:
            self.x = a
            self.y = b
            #try:
            self.sensorController.collectData(self)
            #except IndexError:
            #    print("ERROR: ", self.getxy())
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
        '''
        while i <= backSensorLenght and map[x - dx * i][y - dy * i] != 1:
            self.backSensor.distance += 1
            i += 1
        '''

if __name__=="__main__":
    map = []
    with open('road1.txt') as file:
        file = file.read()
        q = file.replace(' ', '')
        q = q.replace('\n', '')
        for i in range(0, n):
            map.append([])
            for j in range(0, m):
                map[i].append(int(q[j + i * n]))
                #print(j + i * 10, q[j + i * 10])
    for i in range(0, n):
        print(' ')
        for j in range(0, m):
            print(map[i][j], end=''),
    QModel = Q()


    for i in range(50000):
        if i % 2 == 0:
            wr = W(map, QModel, 0.2, 1, 1, 0, True)
        else:
            wr = W(map, QModel, 0.9, 1, 1, 0, True)
        iter = wr.play()
        if i % 100 == 0:
            print(i, iter)

    for i in QModel.state:
        print(i, QModel.state[i])
    animation = plot_animation.moveAnimation()
    wr = W(map, QModel, 0, 1, 1, 0)
    anim = wr.play(True)
    animation.animate(map, anim, 'testvideo')