
def isBranch(opcode):
    return opcode in [2, 3, 4, 5]  # j, jal, beq, bne

def detect_data_hazard(rs, rt, shred):
    # Check EX stage
    if shred.ex_mem_latch.instruction is not None:
        ex_decoded_instruction = shred.ex_mem_latch.decoded_instruction
        if ex_decoded_instruction['control_signals']['RegWrite']:
            ex_rd = ex_decoded_instruction['rd']
            if rs == ex_rd or rt == ex_rd:
                return True

    # Check MEM stage
    if shred.mem_wb_latch.instruction is not None:
        mem_decoded_instruction = shred.mem_wb_latch.decoded_instruction
        if mem_decoded_instruction['control_signals']['RegWrite']:
            mem_rd = mem_decoded_instruction['rd']
            if rs == mem_rd or rt == mem_rd:
                return True

    return False

def id_stage(shred, log):
    # Get the instruction from the IF/ID latch
    instruction = shred.if_id_latch.instruction
    if instruction is not None:
        instruction.stage += 1

        # Decode the instruction
        sign_extend_flag = 0
        decoded_instruction, sign_extend_flag = decode_instruction(instruction.value, shred, log)

        # Check for control hazards
        if isBranch(decoded_instruction['opcode']):
            log.write(f"ID Stage: Detected control hazard for instruction {instruction.value}\n")
            shred.stall = True  # Set stall signal
        else:
            shred.stall = False

        # Check for data hazards
        rs = decoded_instruction['rs']
        rt = decoded_instruction['rt']

        if detect_data_hazard(rs, rt, shred):
            log.write(f"ID Stage: Detected data hazard for instruction {instruction.value}\n")
            shred.stall = True  # Set stall signal
        else:
            shred.stall = False

        # Write data to ID/EX latch
        shred.id_ex_latch.instruction = instruction
        shred.id_ex_latch.decoded_instruction = decoded_instruction
        shred.id_ex_latch.pc = shred.if_id_latch.pc
        shred.id_ex_latch.sign_extend_flag = sign_extend_flag

        entry = f"ID Stage: Instruction {shred.pc - 1} - {shred.raw_instruction_memory[shred.pc - 1]}\n"
        log.write(entry)
    else:
        shred.id_ex_latch.flush()
    shred.cycle += 1

def is_negative(number, identifier):
    return (number >> identifier) & 1 == 1

def determine_control_signals(opcode, funct):
    control_signals = {
        'ALUSrc': 0,
        'ALUOp': 0,
        'RegDst': 0,
        'MemWrite': 0,
        'MemRead': 0,
        'MemToReg': 0,
        'RegWrite': 0,
        'Jump': 0,
        'Branch': 0,
    }
    sign_extend_flag = 0

    if opcode == 0:  # R-type
        control_signals['ALUSrc'] = 0
        control_signals['ALUOp'] = funct
        control_signals['RegDst'] = 1
        control_signals['MemWrite'] = 0
        control_signals['MemRead'] = 0
        control_signals['MemToReg'] = 0
        control_signals['RegWrite'] = 1
        control_signals['Jump'] = 0
        control_signals['Branch'] = 0
    if opcode == 0 & funct in [0, 2]:  # sll, srl
        control_signals['ALUSrc'] = 1
        control_signals['ALUOp'] = funct
        control_signals['RegDst'] = 1
        control_signals['MemWrite'] = 0
        control_signals['MemRead'] = 0
        control_signals['MemToReg'] = 0
        control_signals['RegWrite'] = 1
        control_signals['Jump'] = 0
        control_signals['Branch'] = 0
    elif opcode == 2: # j
        control_signals['ALUSrc'] = 0
        control_signals['ALUOp'] = 0
        control_signals['RegDst'] = 0
        control_signals['MemWrite'] = 0
        control_signals['MemRead'] = 0
        control_signals['MemToReg'] = 0
        control_signals['RegWrite'] = 0
        control_signals['Jump'] = 1
        control_signals['Branch'] = 0
    elif opcode == 3: # jal
        control_signals['ALUSrc'] = 0
        control_signals['ALUOp'] = 0
        control_signals['RegDst'] = 0
        control_signals['MemWrite'] = 0
        control_signals['MemRead'] = 0
        control_signals['MemToReg'] = 0
        control_signals['RegWrite'] = 1
        control_signals['Jump'] = 1
        control_signals['Branch'] = 0
    elif opcode in [4, 5]:  # beq
        control_signals['ALUSrc'] = 0
        control_signals['ALUOp'] = opcode * 100
        control_signals['RegDst'] = 0
        control_signals['MemWrite'] = 0
        control_signals['MemRead'] = 0
        control_signals['MemToReg'] = 0 
        control_signals['RegWrite'] = 0
        control_signals['Jump'] = 1
        control_signals['Branch'] = 0
        sign_extend_flag = 1
    elif opcode in [8, 9, 10, 11, 12, 13, 14, 15]:  # I-type instructions
        control_signals['ALUSrc'] = 1
        control_signals['ALUOp'] = opcode * 100
        control_signals['RegDst'] = 0
        control_signals['MemWrite'] = 0
        control_signals['MemRead'] = 0
        control_signals['MemToReg'] = 0
        control_signals['RegWrite'] = 1
        control_signals['Jump'] = 1
        control_signals['Branch'] = 0
    elif opcode == 35:  # lw
        control_signals['ALUSrc'] = 1
        control_signals['ALUOp'] = opcode * 100
        control_signals['RegDst'] = 0
        control_signals['MemWrite'] = 0
        control_signals['MemRead'] = 1
        control_signals['MemToReg'] = 1
        control_signals['RegWrite'] = 1
        control_signals['Jump'] = 1
        control_signals['Branch'] = 0
        sign_extend_flag = 1
    elif opcode == 43:  # sw
        control_signals['ALUSrc'] = 1
        control_signals['ALUOp'] = opcode * 100
        control_signals['RegDst'] = 0
        control_signals['MemWrite'] = 1
        control_signals['MemRead'] = 0
        control_signals['MemToReg'] = 0 
        control_signals['RegWrite'] = 0
        control_signals['Jump'] = 1
        control_signals['Branch'] = 0
        sign_extend_flag = 1
    else:
        print(f"Error: Unknown opcode {opcode}")

    return control_signals, sign_extend_flag

def decode_instruction(raw_instruction, shred, log_file):
    if raw_instruction is None:
        return None, None, sign_extend_flag
    
    instruction = raw_instruction
    # Extract opcode and other fields
    opcode = (instruction >> 26) & 0b111111
    rs = (instruction >> 21) & 0b11111
    rt = (instruction >> 16) & 0b11111
    rd = (instruction >> 11) & 0b11111
    funct = instruction & 0b111111
    imm = instruction & 0xFFFF
    jump_address = instruction & 0x3FFFFFF
    
    # Control signals
    control_signals, sign_extend_flag = determine_control_signals(opcode, funct)
    # 
    log_entry = f"ID Stage: Instruction {shred.pc - 1} - {shred.instruction_memory[shred.pc - 1]}\n"
    log_entry += f"~ Opcode: {hex(opcode)}, rs: {hex(rs)}, rt: {hex(rt)}, rd: {hex(rd)}, funct: {hex(funct)}, imm: {hex(imm)}, jump_address: {hex(jump_address)}, Control Signals: {control_signals}\n"
    log_file.write(log_entry)
    
    # Return decoded instruction and control signals
    return {
        'opcode': opcode,
        'rs': rs,
        'rt': rt,
        'rd': rd,
        'funct': funct,
        'control_signals': control_signals
    }, sign_extend_flag