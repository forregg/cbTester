class Instrument:
    currentBar = 0
    def __init__(self, name, data):
        self.name, self.data = name, data