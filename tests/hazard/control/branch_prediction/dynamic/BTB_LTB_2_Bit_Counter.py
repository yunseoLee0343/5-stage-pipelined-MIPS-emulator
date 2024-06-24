class Instruction:
    def __init__(self, opcode="", dest_reg="", src_reg1="", src_reg2="", pc=0):
        self.opcode = opcode
        self.dest_reg = dest_reg
        self.src_reg1 = src_reg1
        self.src_reg2 = src_reg2
        self.stage = 0  # Initialize stage as 0
        self.pc = pc  # Program Counter for branch instructions
        self.target_address = 0  # Target address for branch instructions
        self.branch_prediction = None  # Predicted outcome of the branch
        self.branch_taken = None  # Actual outcome of the branch
        self.predicted_target_address = None  # Predicted target address for branch instructions
        self.predictor_state = 0  # Initial predictor state (Strongly not taken)
        self.btb_valid = False  # Valid bit for BTB
        self.btb_tag = None  # Tag to identify branch in BTB
        self.ltp_history = 0  # History bits for LTP
        
    def set_pc(self, pc):
        self.pc = pc

    def get_target_address(self):
        # Placeholder for getting target address based on branch type
        return self.target_address

    def is_branch(self):
        # Placeholder for branch instruction detection
        return self.opcode in ["b", "beq", "bne", "bgtz", "blez"]  # Add more branch opcodes as needed

class BranchTargetBuffer:
    def __init__(self, size):
        self.size = size
        self.entries = [None] * size  # Initialize BTB entries with None

    def get_entry(self, pc):
        index = pc % self.size
        return self.entries[index]

    def update_entry(self, pc, target_address):
        index = pc % self.size
        self.entries[index] = (pc, target_address)  # Store both PC and target address

    def update_tag(self, pc, tag):
        index = pc % self.size
        if self.entries[index] is not None:
            self.entries[index] = (tag, self.entries[index][1])  # Update tag only


class LastTimePredictor:
    def __init__(self):
        self.predictor_table = {}

    def predict_branch(self, instruction):
        if instruction.pc in self.predictor_table:
            state = self.predictor_table[instruction.pc].predictor_state
            if state >= 2:
                return True
            else:
                return False
        else:
            return False  # Default not taken for new branches

    def update_branch_prediction(self, instruction):
        if instruction.pc not in self.predictor_table:
            self.predictor_table[instruction.pc] = instruction
        else:
            state = self.predictor_table[instruction.pc].predictor_state
            if instruction.branch_taken:
                state = min(state + 1, 3)  # Strongly taken (3), Weakly taken (2)
            else:
                state = max(state - 1, 0)  # Weakly not taken (1), Strongly not taken (0)
            self.predictor_table[instruction.pc].predictor_state = state


def if_stage(shred, btb, ltp):
    if shred.pc < len(shred.raw_instruction_memory):
        raw_instruction = shred.raw_instruction_memory[shred.pc]
        opcode = raw_instruction.split()[0]  # Extract opcode
        instruction = Instruction(opcode=opcode, pc=shred.pc)

        # Check if the instruction is a branch
        if instruction.is_branch():
            # First, try to predict using BTB
            btb_entry = btb.get_entry(instruction.pc)
            if btb_entry is not None and btb_entry[0] == instruction.pc:
                instruction.predicted_target_address = btb_entry[1]
                instruction.btb_valid = True
                instruction.btb_tag = btb_entry[0]
            else:
                instruction.btb_valid = False

            # Next, predict using Last Time Predictor (LTP)
            prediction = ltp.predict_branch(instruction)
            instruction.branch_prediction = prediction

            # Determine final prediction and update PC and BTB/LTP
            if instruction.btb_valid and not instruction.branch_prediction:
                shred.pc = instruction.predicted_target_address
            elif not instruction.btb_valid and instruction.branch_prediction:
                shred.pc = instruction.get_target_address()
            else:
                shred.pc += 1

            # Update instruction with actual branch outcome after execution
            instruction.branch_taken = instruction.branch_prediction
            btb.update_entry(instruction.pc, instruction.get_target_address())
            ltp.update_branch_prediction(instruction)
            btb.update_tag(instruction.pc, instruction.pc)

        # Move instruction to next stage
        instruction.stage += 1
        shred.if_id_latch.instruction = instruction
        shred.if_id_latch.pc = shred.pc
        shred.pc += 1
        shred.cycle += 1
        print(f"IF Stage: Instruction {shred.pc} - {raw_instruction}\n")

        return instruction

    shred.cycle += 1
    return None

# Similar adjustments should be made for id_stage, ex_stage, mem_stage, and wb_stage functions

    
    
def id_stage(shred, btb, ltp):
    instruction = shred.if_id_latch.instruction

    if instruction:
        # Simulate ID stage processing
        instruction.stage += 1
        shred.id_ex_latch.instruction = instruction
        shred.id_ex_latch.pc = shred.if_id_latch.pc
        shred.cycle += 1
        # print(f"ID Stage: Instruction {shred.pc} - {instruction.value}\n")
        return instruction

    shred.cycle += 1
    return None

def ex_stage(shred, btb, ltp):
    instruction = shred.id_ex_latch.instruction

    if instruction:
        # Simulate EX stage processing
        instruction.stage += 1
        shred.ex_mem_latch.instruction = instruction
        shred.ex_mem_latch.pc = shred.id_ex_latch.pc
        shred.cycle += 1
        # print(f"EX Stage: Instruction {shred.pc} - {instruction.value}\n")
        return instruction

    shred.cycle += 1
    return None

def mem_stage(shred, btb, ltp):
    instruction = shred.ex_mem_latch.instruction

    if instruction:
        # Simulate MEM stage processing
        instruction.stage += 1
        shred.mem_wb_latch.instruction = instruction
        shred.mem_wb_latch.pc = shred.ex_mem_latch.pc
        shred.cycle += 1
        # print(f"MEM Stage: Instruction {shred.pc} - {instruction.value}\n")
        return instruction

    shred.cycle += 1
    return None

def wb_stage(shred, btb, ltp):
    instruction = shred.mem_wb_latch.instruction

    if instruction:
        # Simulate WB stage processing
        instruction.stage += 1
        shred.cycle += 1
        # print(f"WB Stage: Instruction {shred.pc} - {instruction.value}\n")
        return instruction

    shred.cycle += 1
    return None


class Shred:
    def __init__(self):
        self.pc = 0
        self.cycle = 0
        self.raw_instruction_memory = [
            "bgtz $t0, true_block",
            "add $t1, $t2, $t3",
            "j end",
            "true_block:",
            "sub $t4, $t5, $t6",
            "end:"
        ]
        self.instruction_memory = [Instruction() for _ in range(len(self.raw_instruction_memory))]
        self.if_id_latch = Instruction()
        self.id_ex_latch = Instruction()
        self.ex_mem_latch = Instruction()
        self.mem_wb_latch = Instruction()


def simulate_pipeline(shred, btb, ltp):
    stages = [if_stage, id_stage, ex_stage, mem_stage, wb_stage]
    stage_names = ["IF", "ID", "EX", "MEM", "WB"]

    while True:
        print(f"Cycle: {shred.cycle}")
        stage_output = []
        for stage, stage_name in zip(stages, stage_names):
            output = stage(shred, btb, ltp)
            stage_output.append((stage_name, output))
        print("\n")
        if all(output is None for _, output in stage_output):
            break


def test_pipeline():
    shred = Shred()
    btb = BranchTargetBuffer(size=16)  # Size of BTB
    ltp = LastTimePredictor()

    simulate_pipeline(shred, btb, ltp)

    # Print final BTB and LTP states
    print("\nFinal BTB Entries:")
    for entry in btb.entries:
        if entry:
            print(f"PC: {entry[0]}, Target Address: {entry[1]}")

    print("\nFinal Last Time Predictor Table:")
    for pc, instruction in ltp.predictor_table.items():
        print(f"PC: {pc}, Predictor State: {instruction.predictor_state}")


if __name__ == "__main__":
    test_pipeline()
