import random
import FileWR
import plot_animation
import PlotModule

#Параметры
leftSensorLenght = 5
leftMiddleSensorLenght = 8
middleSensorLenght = 12
rightMiddleSensorLenght = 8
rightSensorLenght = 5
backSensorLenght = 0
n = 40
m = 40

class Q:
    def __init__(self, state = {}):
        self.gamma = 0.4
        self.alpha = 0.1
        self.state = state

    def get_wp(self, plr):
        self.plr = plr

    def run_model(self, silent=1):
        self.plr.curr_state = tuple(self.plr.get_features())
        r = self.plr.reward
        if self.plr.prev_state not in self.state:
            self.state[self.plr.prev_state] = 0
        if r == -100:
            nvec = 0
        else:
            nvec = []
            for i in self.plr.actions:
                cstate = self.plr.curr_state  + tuple(self.plr.actions[i])
                if cstate not in self.state:
                    self.state[cstate] = 0
                nvec.append(self.state[cstate])
            #print(self.plr.prev_state, r, nvec)
            nvec = min(nvec)
        self.state[self.plr.prev_state] = self.state[self.plr.prev_state] + self.alpha * (-self.state[self.plr.prev_state]
                + r + self.gamma * nvec)


class W:
    def __init__(self, map, QModel, eps, x = 1, y = 1, randomDest = False):
        self.P=P(self,x,y, eps)
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
            #print(self.P.x, self.P.y)

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
            self.P.reward = 10
        if end_bool == 1:
            self.P.reward = -100

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
                    namea = name1 + tuple(self.P.actions[i])
                    if namea not in self.QM.state:
                        self.QM.state[namea] = 0
                    ANIM[iter].append(self.QM.state[namea])
                ANIM[iter].append(name1)
            #exception
            if iter > 1000:
                #print("iterations:", iter, end_bool, "sensors:", self.P.get_features(), "dx,dy", self.P.dx, self.P.dy,
                #      "coords:", self.P.getxy())
                #time.sleep(1)
                break
            #main proces
            self.step()
            end_bool = self.is_finished()
            self.get_reward(end_bool, iter)
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
            self.x = a
            self.y = b
            #try:
            self.sensorController.collectData(self)

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
    def generateMap(self,map1, eps):
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
    def printMap(self, map1):
        for i in range(0, n):
            for j in range(0, m):
                print(map1[i][j], end=' '),
            print()

if __name__=="__main__":
    mapgen = MapGenerator()
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
    plot_epoh = []
    try:
        QmodelStates = FileWR.FileWR.readQ('Qmodel.txt', 6, 5)
        for i in QmodelStates:
            print(i, QmodelStates[i])
    except FileNotFoundError:
        print("file not found")
    QModel = Q(QmodelStates)
    giter = 200000
    for i in range(giter):
        '''''
        if i < giter/4:
            wr = W(map, QModel, 0.9, 1, 1, 0, True)
        if i >= giter/4 and i <= giter * 3 / 4:
            wr = W(map, QModel, 0.4, 1, 1, 0, True)
        if i > giter * 3 / 4:
        '''
        wr = W(map, QModel, 0.1, 1, 1, True)
        iter = wr.play()
        plot_epoh.append(iter)
        if i % 100 == 99:
            print(i, iter)
            #print( i * 0.8/(giter+1))
            #mapgen.generateMap(map, 0.3 + i * 0.6/(giter+1))
            randomnum = (random.random() - 0.5) * 0.5
            #randomnum = 0
            mapgen.generateMap(map, 0.7 + randomnum)


    for i in QModel.state:
        print(i, QModel.state[i])

    plotBuilder = PlotModule.plotBilder()
    plotBuilder.buildPlot(plot_epoh)
    FileWR.FileWR.writeQ(QModel, 'Qmodel.txt')
    animation = plot_animation.moveAnimation()
    #mapgen.generateMap(map, 0.85)
    wr = W(map, QModel, 0, 1, 11)
    anim = wr.play(True)
    animation.animate(map, anim, 'randMap')
