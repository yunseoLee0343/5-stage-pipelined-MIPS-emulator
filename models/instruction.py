class Instruction:
    def __init__(self):
        self.stage = 0  # Current stage of the instruction

    def __repr__(self):
        return f"({self.index}, {self.stage})"
    
    def setProperties(self, value, index, stage):
        self.value = value
        self.index = index
        self.stage = stage