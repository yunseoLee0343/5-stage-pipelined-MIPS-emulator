from models.instruction import Instruction

def if_stage(shred, log):
    if shred.pc < len(shred.instruction_memory):
        # Write data to instruction memory
        instruction = Instruction()
        instruction.setProperties(shred.raw_instruction_memory[shred.pc], shred.pc, 0)
        shred.instruction_memory[shred.pc] = instruction

        # Move instruction to next stage
        instruction.stage += 1
        shred.if_id_latch.instruction = instruction
        shred.if_id_latch.pc = shred.pc
        shred.pc += 1
        shred.cycle += 1
        #
        print("IF Stage: Instruction ", shred.pc, " - ", instruction.value, "\n")
        entry = f"IF Stage: Instruction {shred.pc} - {instruction.value}\n"
        log.write(entry)

        # Return the instruction to be processed in the next stage
        return instruction
    shred.cycle += 1
    return None