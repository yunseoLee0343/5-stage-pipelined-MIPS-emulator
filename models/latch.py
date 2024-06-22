from models.instruction import Instruction

class Latch:
    def __init__(self):
        self.pc = None
        self.instruction = Instruction()
    def flush(self):
        self.pc = None
        self.instruction = None

class IF_ID_Latch(Latch):
    def __init__(self):
        super().__init__()
    
    def flush(self):
        super().flush()

class ID_EX_Latch(Latch):
    def __init__(self):
        super().__init__()
        self.decoded_instruction = None
        self.sign_extend_flag = 0
    
    def flush(self):
        super().flush()
        self.decoded_instruction = None
        self.sign_extend_flag = 0

class EX_MEM_Latch(Latch):
    def __init__(self):
        super().__init__()
        self.result = None
        self.pc = None
        self.sign_extend_flag = None
    
    def flush(self):
        super().flush()
        self.result = None
        self.pc = None
        self.sign_extend_flag = None

class MEM_WB_Latch(Latch):
    def __init__(self):
        super().__init__()
        self.result = None
    
    def flush(self):
        super().flush()
        self.result = None
