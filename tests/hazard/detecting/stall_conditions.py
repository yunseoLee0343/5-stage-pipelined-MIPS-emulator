class Instruction:
    def __init__(self, name, index, rs, rt, destEX, destMEM, destWB, RegWriteEX, RegWriteMEM, RegWriteWB):
        self.name = name
        self.index = index
        self.rs = rs
        self.rt = rt
        self.destEX = destEX
        self.destMEM = destMEM
        self.destWB = destWB
        self.RegWriteEX = RegWriteEX
        self.RegWriteMEM = RegWriteMEM
        self.RegWriteWB = RegWriteWB

def rs(I):
    return I.rs

def use_rs(I):
    return I.rs != 'r0'

def use_rt(I):
    return I.rt != 'r0'

def stall(instruction, IRID):
    if (rs(IRID) == instruction.destEX) and use_rs(IRID) and instruction.RegWriteEX:
        return True
    elif (rs(IRID) == instruction.destMEM) and use_rs(IRID) and instruction.RegWriteMEM:
        return True
    elif (rs(IRID) == instruction.destWB) and use_rs(IRID) and instruction.RegWriteWB:
        return True
    elif (instruction.rt == IRID.destEX) and use_rt(IRID) and instruction.RegWriteEX:
        return True
    elif (instruction.rt == IRID.destMEM) and use_rt(IRID) and instruction.RegWriteMEM:
        return True
    elif (instruction.rt == IRID.destWB) and use_rt(IRID) and instruction.RegWriteWB:
        return True
    return False

# Example instructions
instruction1 = Instruction("ADD", 1, 'r1', 'r2', 'r3', 'r4', 'r5', True, False, True)
instruction2 = Instruction("SUB", 2, 'r2', 'r3', 'r6', 'r7', 'r8', False, True, False)
instruction3 = Instruction("MUL", 3, 'r3', 'r4', 'r9', 'r10', 'r11', True, True, False)

# Test stall function
print(stall(instruction1, instruction2))  # Should return True if there's a stall
print(stall(instruction2, instruction3))  # Should return False as there's no stall
