from modules.hazard.data.data_forwarding import determine_forwarding


def ex_stage(shred, log_file):
    instruction = shred.id_ex_latch.decoded_instruction
    decoded_instruction = shred.id_ex_latch.decoded_instruction

    result = None
    opcode = instruction['opcode']
    alu_control_signal = instruction['control_signals']['ALUOp']

    # Data forwarding logic
    forwardA = determine_forwarding(shred, instruction['rs1'])
    forwardB = determine_forwarding(shred, instruction['rs2'])

    # Adjusted execute functions to use forwarded values
    if alu_control_signal == 0:  # R type operations
        result = execute_register_register(decoded_instruction, forwardA, forwardB)
    elif alu_control_signal == 1:  # I type operations
        result = execute_register_immediate(decoded_instruction, forwardA)
    elif alu_control_signal == 2:  # Branch operations
        result = execute_branch(decoded_instruction, forwardA, forwardB)
    elif alu_control_signal == 3:  # Jump operations
        result = execute_jump(decoded_instruction)
    else:
        raise ValueError("Unsupported ALU operation")
    
    # Store the result in the ex_mem_latch
    shred.ex_mem_latch.instruction = instruction
    shred.ex_mem_latch.result = result
    shred.ex_mem_latch.pc = shred.id_ex_latch.pc
    shred.ex_mem_latch.sign_extend_flag = shred.id_ex_latch.sign_extend_flag

    log_entry = f"EX Stage: Instruction {shred.pc - 1} - {shred.raw_instruction_memory[shred.pc - 1]}\n"
    log_file.write(log_entry)

def execute_register_register(data, forwardA, forwardB):
    alu_op = data['funct']

    if alu_op == 32:  # ADD
        return forwardA + forwardB
    elif alu_op == 34:  # SUB
        return forwardA - forwardB
    elif alu_op == 36:  # AND
        return forwardA & forwardB
    elif alu_op == 37:  # OR
        return forwardA | forwardB
    elif alu_op == 38:  # XOR
        return forwardA ^ forwardB
    elif alu_op == 39:  # NOR
        return ~(forwardA | forwardB)
    elif alu_op == 42:  # SLT
        return 1 if forwardA < forwardB else 0
    else:
        raise ValueError("Unsupported R-type instruction")

def execute_register_immediate(instruction, forwardA):
    imm = instruction['imm']

    if instruction['opcode'] == 8:  # ADDI
        return forwardA + imm
    elif instruction['opcode'] == 10:  # SLTI
        return 1 if forwardA < imm else 0
    elif instruction['opcode'] == 12:  # ANDI
        return forwardA & imm
    elif instruction['opcode'] == 13:  # ORI
        return forwardA | imm
    elif instruction['opcode'] == 14:  # XORI
        return forwardA ^ imm
    else:
        raise ValueError("Unsupported I-type instruction")

def execute_branch(instruction, forwardA, forwardB):
    offset = instruction['imm'] << 2  # Shift the offset to the left by 2 bits for branch target

    if forwardA == forwardB:
        return offset
    else:
        return None  # No branch taken

def execute_jump(instruction):
    return instruction['jump_address']
