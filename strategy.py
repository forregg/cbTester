class Strategy:
    def __init__(self, engine, name =''):
        self.engine = engine
        self.name = ''

    def onBar(self):
        raise NotImplementedError

    def onOrderExecution(self, order):
        pass