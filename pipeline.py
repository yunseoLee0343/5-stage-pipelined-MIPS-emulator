from collections import deque
from models.latch import ID_EX_Latch, IF_ID_Latch, Latch
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
        self.ex_mem_latch = Latch()
        self.mem_wb_latch = Latch()

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

                # Move instructions to the next stage
                for i in range(len(self.stages) - 1, 0, -1):
                    if not self.pipeline[i]:
                        self.pipeline[i] = self.pipeline[i - 1]
                        self.pipeline[i - 1] = None

                # Fetch new instruction
                if shred.pc < len(instruction_memory) and not self.pipeline[0]:
                    self.pipeline[0] = self.if_stage(shred, log)
                
                shred.cycle += 1

            log.write(f"\nFinal State at Clock Cycle {self.clock}: {list(self.pipeline)}\n")