class Accumulator:

    def __init__(self):
        self.value = 0

    def tick(self):
        self.value += 1

    def reset(self):
        self.value = 0

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return 'value: ' + self.__str__()

