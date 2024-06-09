
def wb_stage(shred, log_file):
    # Get instruction and result from mem_wb_latch
    instruction = shred.mem_wb_latch.instruction
    result = shred.mem_wb_latch.result

    # If no instruction, do nothing
    if instruction is None:
        return

    # Write data back to registers
    opcode = instruction['opcode']
    if opcode == 35:  # LW (Load Word)
        self.write_back(instruction, result, shred)
    #
    log_entry = f"WB Stage: Instruction {shred.pc - 1} - {shred.raw_instruction_memory[shred.pc - 1]}\n"
    log_file.write(log_entry)

def write_back(self, instruction, data, shred):
    # Write data to destination register
    rd = instruction['rd']
    shred.registers[rd] = data
