class Instruction:
    def __init__(self):
        self.opcode = ""
        self.dest_reg = ""
        self.src_reg1 = ""
        self.src_reg2 = ""
        self.stage = 0  # Initialize stage as 0
        self.value = ""  # String representation of the instruction
        self.pc = 0  # Program Counter for branch instructions
        self.target_address = 0  # Target address for branch instructions

    def set_properties(self, value, pc, target_address):
        self.value = value
        self.pc = pc
        self.target_address = target_address

    def is_branch(self):
        return self.opcode in ["b", "beq", "bne", "bgtz", "blez"]  # Add more branch opcodes as needed

    def get_target_address(self):
        return self.target_address

def if_stage(shred, prediction_mode="always_taken"):
    if shred.pc < len(shred.instruction_memory):
        # Write data to instruction memory
        raw_instruction = shred.raw_instruction_memory[shred.pc]
        instruction = Instruction()
        instruction.set_properties(raw_instruction, shred.pc, 0)
        shred.instruction_memory[shred.pc] = instruction

        # Determine if the instruction is a branch
        if instruction.is_branch():
            # Apply static branch prediction based on prediction_mode
            if prediction_mode == "always_taken":
                taken = True
            elif prediction_mode == "always_not_taken":
                taken = False
            elif prediction_mode == "btfnt":
                # Backward Taken, Forward Not Taken
                if shred.pc > shred.if_id_latch.pc:  # Forward branch
                    taken = False
                else:  # Backward branch
                    taken = True
            else:
                # Default behavior, could be compiler-based or program-based prediction
                # Not explicitly implemented here
                taken = True  # Assume always taken as default

            # Check if prediction matches actual outcome
            if taken == (instruction.get_target_address() != shred.pc + 1):
                penalty = 3  # Misprediction penalty
            else:
                penalty = 0

            # Update PC based on prediction
            if taken:
                shred.pc = instruction.get_target_address()

            # Record cycle count with penalty
            shred.cycle += penalty

        # Move instruction to next stage
        instruction.stage += 1
        shred.if_id_latch.instruction = instruction
        shred.if_id_latch.pc = shred.pc
        shred.pc += 1
        shred.cycle += 1
        print(f"IF Stage: Instruction {shred.pc} - {instruction.value}")

        # Return the instruction to be processed in the next stage
        return instruction

    shred.cycle += 1
    return None
    

class Shred:
    def __init__(self):
        self.pc = 0
        self.cycle = 0
        self.raw_instruction_memory = [
            "bgtz $t0, true_block",     # Branch if $t0 > 0 (often taken)
            "add $t1, $t2, $t3",        # Non-branch instruction
            "j end",                    # Unconditional jump to end (always taken)
            "true_block:",              # Label for branch target
            "sub $t4, $t5, $t6",        # Non-branch instruction after true_block
            "end:"                      # End label (always taken)
        ]
        self.instruction_memory = [Instruction() for _ in range(len(self.raw_instruction_memory))]
        self.if_id_latch = Instruction()


def test_branch_prediction_modes():
    shred = Shred()
    prediction_modes = ["always_taken", "always_not_taken", "btfnt"]

    for mode in prediction_modes:
        print(f"Testing with prediction mode: {mode}")
        shred.pc = 0
        shred.cycle = 0
        misprediction_count = 0
        while if_stage(shred, mode):
            if shred.cycle > 1:  # Only count mispredictions after warm-up period
                misprediction_count += 1

        total_cycles = shred.cycle
        print(f"Total cycles with {mode}: {total_cycles}")
        print(f"Misprediction count with {mode}: {misprediction_count}")
        if total_cycles > 0:
            misprediction_rate = (misprediction_count / total_cycles) * 100
            print(f"Misprediction rate with {mode}: {misprediction_rate:.2f}%")
        print()

if __name__ == "__main__":
    test_branch_prediction_modes()
