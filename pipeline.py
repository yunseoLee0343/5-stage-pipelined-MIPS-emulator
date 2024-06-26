from collections import deque
from models.latch import EX_MEM_Latch, ID_EX_Latch, IF_ID_Latch, Latch, MEM_WB_Latch
from modules.stages.EX import ex_stage
from modules.stages.ID import id_stage
from modules.stages.IF import if_stage
from modules.stages.MEM import mem_stage
from modules.stages.WB import wb_stage

class Pipeline:
    def __init__(self):
        self.stages = ["IF", "ID", "EX", "MEM", "WB"]
        self.pipeline = deque([None] * 5)  # Initialize pipeline with 5 stages, all empty
        self.clock = 0  # Initialize clock cycle counter

        self.if_id_latch = IF_ID_Latch()
        self.id_ex_latch = ID_EX_Latch()
        self.ex_mem_latch = EX_MEM_Latch()
        self.mem_wb_latch = MEM_WB_Latch()

    def process_stage(self, index, shred, log):
        if index == 0:
            instruction = if_stage(shred, log)
            if instruction:
                self.pipeline[index] = instruction
        elif index == 1:
            id_stage(shred, log)
        elif index == 2:
            ex_stage(shred, log)
        elif index == 3:
            mem_stage(shred, log)
        elif index == 4:
            wb_stage(shred, log)
        # print("Instruction: ", shred.instruction_memory[index].value, "Stage: ", shred.instruction_memory[index].stage)
        shred.instruction_memory[index].stage += 1

    def run(self, shred):
        instruction_memory = shred.instruction_memory

        with open("logs/pipelined.txt", "w") as log:
            log.write(f"\nClock Cycle {self.clock}: (idx, stage)\n")
            while shred.pc <= len(instruction_memory) or any(self.pipeline):
                self.clock += 1
                log.write(f"\nClock Cycle {self.clock}: {list(self.pipeline)}\n")

                # Process pipeline stages in reverse order to prevent overwriting
                for i in range(len(self.stages) - 1, -1, -1):
                    if shred.pc >= len(instruction_memory):
                        return
                    if self.pipeline[i]:
                        if self.pipeline[i].stage == len(self.stages):
                            self.pipeline[i] = None  # Instruction is done
                        else:
                            self.process_stage(i, shred, log)

                # Check for control hazards
                if self.ex_mem_latch.isBranch and self.ex_mem_latch.isTaken:
                    log.write(f"Pipeline stalled due to control hazard at clock cycle {self.clock}\n")
                    shred.pc = self.ex_mem_latch.result  # Update PC to the branch target
                    shred.stall = True
                    # Clear the pipeline stages
                    self.pipeline[0] = None
                    self.pipeline[1] = None
                    self.pipeline[2] = None
                else:
                    shred.stall = False

                # Move instructions to the next stage if no stall
                if not shred.stall:
                    for i in range(len(self.stages) - 1, 0, -1):
                        if not self.pipeline[i]:
                            self.pipeline[i] = self.pipeline[i - 1]
                            self.pipeline[i - 1] = None

                    # Fetch new instruction if IF stage is empty
                    if self.pipeline[0] is None and shred.pc < len(shred.instruction_memory):
                        self.pipeline[0] = if_stage(shred, log)

                shred.cycle += 1

            log.write(f"\nFinal State at Clock Cycle {self.clock}: {list(self.pipeline)}\n")