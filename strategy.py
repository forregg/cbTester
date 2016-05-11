class Strategy:
    def __init__(self, engine):
        self.engine = engine
        self.name = ''

    def onBar(self):
        raise NotImplementedError

    def onOrderExecution(self, order):
        pass