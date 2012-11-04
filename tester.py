import numpy as np
class Tester():
    def __init__(self, data, strategyClass):
        self.strategy = strategyClass(self)
        self.data = data
    def start(self):
        d = np.array([])
        for instrument in self.data:
            names = [instrument.name for i in range(len(instrument.data[:, 0]))]
            if not d.size:
                d = np.column_stack((instrument.data, np.array(names)))
            else:
                a = np.column_stack((instrument.data, np.array(names)))
                d = np.vstack((d,a))
        d = d[d[:,0].argsort()]
        for bar in d:
            self.strategy.onBar(bar)