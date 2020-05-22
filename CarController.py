import FileWR
if __name__=="__main__":
    n = 24
    m = 24
    map = []
    with open('road1.txt') as file:
        file = file.read()
        q = file.replace(' ', '')
        q = q.replace('\n', '')
        for i in range(0, n):
            map.append([])
            for j in range(0, m):
                map[i].append(int(q[j + i * n]))
                # print(j + i * 10, q[j + i * 10])
    for i in range(0, n):
        print(' ')
        for j in range(0, m):
            print(map[i][j], end=''),
    QmodelXY = {}
    try:
        QmodelXY = FileWR.FileWR.readQ('QmodelXY.txt', 4, 4)
    except FileNotFoundError:
        print("file not found")
    QmodelStates = {}
    try:
        QmodelStates = FileWR.FileWR.readQ('Qmodel.txt', 6, 5)
        for i in QmodelStates:
            print(i, QmodelStates[i])
    except FileNotFoundError:
        print("file not found")
    QModel = Q(QmodelStates)