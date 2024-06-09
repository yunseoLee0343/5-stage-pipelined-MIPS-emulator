
def mem_stage(shred, log_file):
    # Get instruction and data from ex_mem_latch
    instruction = shred.ex_mem_latch.instruction
    result = shred.ex_mem_latch.result

    # If no instruction, do nothing
    if instruction is None:
        return

    # Perform memory operation based on opcode
    opcode = instruction['opcode']
    if opcode == 35:  # LW (Load Word)
        load_word(instruction, result, shred)
    elif opcode == 43:  # SW (Store Word)
        store_word(instruction, result, shred)
    else:
        raise ValueError("Unsupported memory operation")
    #
    log_entry = f"MEM Stage: Instruction {shred.pc - 1} - {shred.raw_instruction_memory[shred.pc - 1]}\n"
    log_file.write(log_entry)

def load_word(self, instruction, address, shred):
    # Perform LW operation: Read data from memory and write to mem_wb_latch
    data = shred.memory[address]
    shred.mem_wb_latch.instruction = instruction
    shred.mem_wb_latch.result = data

def store_word(self, instruction, address, shred):
    # Perform SW operation: Write data from ex_mem_latch to memory
    data = shred.registers[instruction['rt']]
    shred.memory[address] = data
