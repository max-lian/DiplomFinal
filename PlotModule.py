import matplotlib.pyplot as plt

class plotBilder:

    def buildPlot(self, yData):
        newYData = self.separator(yData, 50)
        xData = [i for i in range(len(newYData))]
        print(newYData)
        print(xData)
        plt.bar(xData, newYData)
        plt.grid()
        plt.show()

    def separator(self, dataForSeparate, sizeOfSeparated):
        newData = []
        for i in range (sizeOfSeparated):
            avg = 0
            for j in range(i * len(dataForSeparate)//sizeOfSeparated, (i + 1) * len(dataForSeparate)//sizeOfSeparated):
                avg += dataForSeparate[j]
            avg = avg / (len(dataForSeparate)//sizeOfSeparated)
            newData.append(avg)
        return newData