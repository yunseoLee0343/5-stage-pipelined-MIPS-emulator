def ex_stage(shred, log_file):
    instruction = shred.id_ex_latch.instruction
    decoded_instruction = shred.id_ex_latch.decoded_instruction

    print("instuction: ", instruction.value, "\n decoded_instruction: ", decoded_instruction)

    result = None
    opcode = decoded_instruction['opcode']
    alu_control_signal = decoded_instruction['control_signals']
    isTaken = False  # Initialize isTaken flag for branch instructions

    if alu_control_signal == 0:  # R type operations
        execute_register_register(decoded_instruction, shred.registers)
    elif alu_control_signal == 1:  # I type operations
        execute_register_immediate(decoded_instruction, shred.registers)
    elif alu_control_signal == 2:  # Branch operations
        execute_branch(decoded_instruction, shred.registers)
    elif alu_control_signal == 3:  # Jump operations
        execute_jump(decoded_instruction, shred.registers)
    else:
        raise ValueError("Unsupported ALU operation")
    
    # Store the result in the ex_mem_latch
    shred.ex_mem_latch.instruction = instruction
    shred.ex_mem_latch.result = result
    shred.ex_mem_latch.pc = shred.id_ex_latch.pc
    shred.ex_mem_latch.sign_extend_flag = shred.id_ex_latch.sign_extend_flag
    shred.ex_mem_latch.isTaken = isTaken  # Store isTaken flag in the latch
    #
    log_entry = f"EX Stage: Instruction {shred.pc - 1} - {shred.raw_instruction_memory[shred.pc - 1]}\n"
    log_file.write(log_entry)

def execute_register_register(data, registers):
    rs_value = registers[data['rs']]
    rt_value = registers[data['rt']]
    alu_op = data['funct']

    if alu_op == 32:  # ADD
        return rs_value + rt_value
    elif alu_op == 34:  # SUB
        return rs_value - rt_value
    elif alu_op == 36:  # AND
        return rs_value & rt_value
    elif alu_op == 37:  # OR
        return rs_value | rt_value
    elif alu_op == 38:  # XOR
        return rs_value ^ rt_value
    elif alu_op == 39:  # NOR
        return ~(rs_value | rt_value)
    elif alu_op == 42:  # SLT
        return 1 if rs_value < rt_value else 0
    else:
        raise ValueError("Unsupported R-type instruction")

def execute_register_immediate(instruction, registers):
    rs_value = registers[instruction['rs']]
    imm = instruction['imm']

    if instruction['opcode'] == 8:  # ADDI
        return rs_value + imm
    elif instruction['opcode'] == 9:  # ADDIU
        return rs_value + imm
    elif instruction['opcode'] == 10:  # SLTI
        return 1 if rs_value < imm else 0
    elif instruction['opcode'] == 12:  # ANDI
        return rs_value & imm
    elif instruction['opcode'] == 13:  # ORI
        return rs_value | imm
    elif instruction['opcode'] == 14:  # XORI
        return rs_value ^ imm
    else:
        raise ValueError("Unsupported I-type instruction")

def execute_branch(instruction, registers):
    rs_value = registers[instruction['rs']]
    rt_value = registers[instruction['rt']]
    offset = instruction['imm'] << 2  # Shift the offset to the left by 2 bits for branch target

    isTaken = False
    if instruction['opcode'] == 4:  # beq
        isTaken = rs_value == rt_value
    elif instruction['opcode'] == 5:  # bne
        isTaken = rs_value != rt_value

    if isTaken:
        return offset, True
    else:
        return None, False  # No branch taken

def execute_jump(instruction):
    return instruction['jump_address']
