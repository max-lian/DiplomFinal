class FileWR:
    def readQ(filename, featuresLenght):
        Qmdict = {}
        with open(filename, 'r') as f:
            for line in f:
                data = line.replace('(', '').replace(')', '')
                data = data.strip().split()
                #print(data)
                key = data[0:featuresLenght]
                for i in range(len(key)):
                    key[i] = int(key[i])

                key = tuple(key)
                #print(key)
                value = float(data[featuresLenght])
                #print(value)
                Qmdict[key] = value
        return Qmdict

    def writeQ(QModel, filename):
        with open(filename, 'w') as file:
            for st in QModel.state:
                file.write(str(st).replace(',', '') + ' ' + str(QModel.state[st]) + '\n')