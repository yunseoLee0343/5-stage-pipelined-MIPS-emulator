from collections import deque

class Instruction:
    def __init__(self, name, index):
        self.name = name
        self.index = index  # Instruction index
        self.stage = 0  # Current stage of the instruction

    def __repr__(self):
        return f"{self.name} (Stage {self.stage})"

class PipelineDeque:
    def __init__(self):
        self.stages = ["IF", "ID", "EX", "MEM", "WB"]
        self.pipeline = deque([None] * 5)  # Initialize pipeline with 5 stages, all empty
        self.clock = 0  # Initialize clock cycle counter

    def if_stage(self, instruction):
        print(f"IF Stage: Instruction {instruction.index} - {instruction.name}")
        instruction.stage += 1

    def id_stage(self, instruction):
        print(f"ID Stage: Instruction {instruction.index} - {instruction.name}")
        instruction.stage += 1

    def ex_stage(self, instruction):
        print(f"EX Stage: Instruction {instruction.index} - {instruction.name}")
        instruction.stage += 1

    def mem_stage(self, instruction):
        print(f"MEM Stage: Instruction {instruction.index} - {instruction.name}")
        instruction.stage += 1

    def wb_stage(self, instruction):
        print(f"WB Stage: Instruction {instruction.index} - {instruction.name}")
        instruction.stage += 1

    def process_stage(self, index):
        if index == 0:
            self.if_stage(self.pipeline[index])
        elif index == 1:
            self.id_stage(self.pipeline[index])
        elif index == 2:
            self.ex_stage(self.pipeline[index])
        elif index == 3:
            self.mem_stage(self.pipeline[index])
        elif index == 4:
            self.wb_stage(self.pipeline[index])

    def run(self, instructions):
        while instructions or any(self.pipeline):
            self.clock += 1
            print(f"\nClock Cycle {self.clock}: {list(self.pipeline)}")

            # Process pipeline stages in reverse order to prevent overwriting
            for i in range(len(self.stages) - 1, -1, -1):
                if self.pipeline[i]:
                    if self.pipeline[i].stage == len(self.stages):
                        self.pipeline[i] = None  # Instruction is done
                    else:
                        self.process_stage(i)

            # Move instructions to the next stage
            for i in range(len(self.stages) - 1, 0, -1):
                if not self.pipeline[i]:
                    self.pipeline[i] = self.pipeline[i - 1]
                    self.pipeline[i - 1] = None

            # Fetch new instruction
            if instructions and not self.pipeline[0]:
                self.pipeline[0] = instructions.pop(0)

        print(f"\nFinal State at Clock Cycle {self.clock}: {list(self.pipeline)}")

# Example instructions
instructions = [Instruction("ADD", 0), Instruction("SUB", 1), Instruction("MUL", 2), Instruction("DIV", 3)]

# Simulate the pipeline
pipeline_deque = PipelineDeque()
pipeline_deque.run(instructions)
