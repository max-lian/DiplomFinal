class FileWR:
    def readQ(filename, featuresLenght, intLenght):
        Qmdict = {}
        with open(filename, 'r') as f:
            for line in f:
                data = line.replace('(', '').replace(')', '')
                data = data.strip().split()
                print(data)
                key1 = data[0:intLenght]
                for i in range(len(key1)):
                    key1[i] = int(key1[i])
                if featuresLenght != intLenght:
                    key2 = data[intLenght:featuresLenght]
                    key = tuple(key1) + tuple(key2[0][1])
                else:
                    key = tuple(key1)
                value = float(data[featuresLenght])
                #print(value)
                Qmdict[key] = value
        return Qmdict

    def writeQ(QModel, filename):
        with open(filename, 'w') as file:
            for st in QModel.state:
                file.write(str(st).replace(',', '') + ' ' + str(QModel.state[st]) + '\n')