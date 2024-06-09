from models.instruction import Instruction
from models.latch import EX_MEM_Latch, ID_EX_Latch, IF_ID_Latch, Latch, MEM_WB_Latch

class GlobalVariables:
    pc = 0
    cycle = 0

    raw_instruction_memory = []
    n = len(raw_instruction_memory)
    instruction_memory = [Instruction() for i in range(100)]
    data_memory = [0] * 1000
    registers = [0] * 32
    
    if_id_latch = IF_ID_Latch()
    id_ex_latch = ID_EX_Latch()
    ex_mem_latch = EX_MEM_Latch()
    mem_wb_latch = MEM_WB_Latch()