class Latch:
    def __init__(self):
        self.pc = None
    def flush(self):
        self.pc = None

class IF_ID_Latch(Latch):
    def __init__(self):
        super().__init__()
        self.instruction = None
    
    def flush(self):
        super().flush()
        self.instruction = None

class ID_EX_Latch(Latch):
    def __init__(self):
        super().__init__()
        self.instruction = None
        self.decoded_instruction = None
        self.sign_extend_flag = 0
    
    def flush(self):
        super().flush()
        self.instruction = None
        self.decoded_instruction = None
        self.sign_extend_flag = 0

class EX_MEM_Latch(Latch):
    def __init__(self):
        super().__init__()
        self.instruction = None
        self.result = None
        self.pc = None
        self.sign_extend_flag = None
    
    def flush(self):
        super().flush()
        self.instruction = None
        self.result = None
        self.pc = None
        self.sign_extend_flag = None

class MEM_WB_Latch(Latch):
    def __init__(self):
        super().__init__()
        self.instruction = None
        self.result = None
    
    def flush(self):
        super().flush()
        self.instruction = None
        self.result = None
