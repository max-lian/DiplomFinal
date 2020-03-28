import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import copy
import CarSensorsModel
Writer = animation.writers['ffmpeg']
writer = Writer(fps=2, metadata=dict(artist='M.Yakovlev'), bitrate=1800)
class moveAnimation:
    def makeMoveAnimation(self, map, QM, animName):
        wr = CarSensorsModel.W(map, QM, 0)
        anim = wr.play(True)
        self.animate(map, anim)

    def animate(self, map, ANIM, animName : str):
        print("anim begin")
        range1 = min(300, len(ANIM))
        FORWARD = []
        RIGHT = []
        LEFT = []
        SENSORS = []
        for i in range (range1):
            x = ANIM[i][0]
            y = ANIM[i][1]
            FORWARD.append(ANIM[i][2])
            LEFT.append(ANIM[i][3])
            RIGHT.append(ANIM[i][4])
            SENSORS.append(ANIM[i][5])
            ANIM[i] = copy.deepcopy(map)
            ANIM[i][x][y] = 3
#        print(down[0])

        def update(i):
            matrice.set_array(ANIM[i])
            forward.set_text('FORWARD = %f' % FORWARD[i])
            right.set_text('RIGHT = %f' % RIGHT[i])
            left.set_text('LEFT = %f' % LEFT[i])
            sensors.set_text(SENSORS[i])
        fig, ax = plt.subplots()
        forward = ax.text(0.4, 1.1, '', transform=ax.transAxes)
        right = ax.text(1.02, 0.5, '', transform=ax.transAxes)
        left = ax.text(-0.4, 0.5, '', transform=ax.transAxes)
        sensors = ax.text(0.9, 1.1, '', transform=ax.transAxes)
        matrice = ax.matshow(ANIM[0])
        ani = animation.FuncAnimation(fig, update, frames=range1, interval=1000)
        ani.save(animName + '.mp4', writer=writer)
        plt.show()
        plt.show(block=True)