# 5 Staged Pipelined MIPS Emulator

### Abstract

This project involves the development of a five-stage pipelined MIPS emulator using Python, drawing insights and references from QEMU. The emulator implements core features of a pipelined architecture, addressing challenges such as maintaining stage independence, handling data and control hazards, and optimizing performance through techniques like scoreboarding and data forwarding. By comparing specific implementations with reference code, this project demonstrates the nuances of pipeline execution and hazard management, providing a detailed examination of each stage's functionality and the strategies employed to enhance the emulator's efficiency and accuracy.

- Test Codes: <[https://github.com/yunseoLee0343/5-stage-pipelined-MIPS-emulator.git/tests](https://github.com/yunseoLee0343/5-stage-pipelined-MIPS-emulator/tree/7b7359778913838d83b205742c17a6b25cb8aad7/tests)>

# Table of contents

- [5 Staged Pipelined MIPS Emulator](#5-staged-pipelined-mips-emulator)
    - [Abstract](#abstract)
    - [Topic 1: Pipelining](#topic-1-pipelining)
        - [1. Maintaining Stage Sequence](#1-maintaining-stage-sequence)
          - [Part 1. My Implementation](#part-1-my-implementation)
          - [Part 2. QEMU Implementation](#part-2-qemu-implementation)
          - [Part 3. My code improved by referring to QEMU](#part-3-my-code-improved-by-referring-to-qemu)
        - [2. Independence Between Stages](#2-independence-between-stages)
          - [Part 1. My Implementation](#part-1-my-implementation)
          - [Part 2. QEMU Implementation**](#part-2-qemu-implementation)
        - [3. Instruction Overlapping](#3-instruction-overlapping)
          - [Part 1. My Implementation](#part-1-my-implementation)
    - [Topic 2: Hazard](#topic-2-hazard)
      - [1. Control Hazard](#1-control-hazard)
      - [2. Data Hazard](#2-data-hazard)
    - [Topic 3: Detecting Hazard](#topic-3-detecting-hazard)
      - [1. Control Hazard: isBranch, isTaken](#1-control-hazard-isbranch-istaken)
      - [2. Data Hazard: (Rs or Rt) and RegWrite](#2-data-hazard-rs-or-rt-and-regwrite)
      - [1. Data Hazard](#1-data-hazard)
    - [Topic 4: Data Hazard in Detail, how can minimize?](#topic-4-data-hazard-in-detail-how-can-minimize)
      - [1. Stall using scoreboarding.](#1-stall-using-scoreboarding)
      - [2. Data Forwarding (Bypassing)](#2-data-forwarding-bypassing)
      - [1. Stall using scoreboarding.](#1-stall-using-scoreboarding)
    - [Topic 4: Control Hazard in Detail, how can minimize?](#topic-4-control-hazard-in-detail-how-can-minimize)
      - [1. Simply Stalling](#1-simply-stalling)
      - [2. Stalling makes more execution time.](#2-stalling-makes-more-execution-time)
    - [Sol1. Minimize control-related instructions](#sol1-minimize-control-related-instructions)
      - [1. Just guessing nextPC = PC + 4](#1-just-guessing-nextpc--pc--4)
      - [2. Predicate Combining](#2-predicate-combining)
      - [3. Predicated Execution](#3-predicated-execution)
      - [2. Predicate Combining](#2-predicate-combining)
    - [Sol2. Delayed Branching](#sol2-delayed-branching)
      - [1. Inserting nop.](#1-inserting-nop)
      - [2. Reordering, filling branch delay slot.](#2-reordering-filling-branch-delay-slot)
    - [Misprediction Penalty](#misprediction-penalty)
    - [Sol3. Static Branch Prediction](#sol3-static-branch-prediction)
    - [Sol4. Dynamic Branch Prediction](#sol4-dynamic-branch-prediction)
  - [Conclusion](#conclusion)


### Topic 1: Pipelining

![](docs/assets/Aspose.Words.db74fd64-4fc5-4662-9ad1-efd722149e28.001.png)

1. Maintaining Stage Sequence
   - IF, ID, EX, MEM, WB. (But to prevent overwritting issue, we should execute reversely)
2. Independence Between Stages
   - Each stage can operate concurrently without interference.
   - Each stage writes its output to a latch, and the next stage reads from that.
3. Instruction overlapping
   - Instruction 1’s ID and next instruction’s IF are executed in same cycle.**

##### 1. Maintaining Stage Sequence

###### Part 1. My Implementation

In the development of the five-stage pipelined MIPS emulator, the primary focus was to maintain the integrity of the stage sequence, namely: Instruction Fetch (IF), Instruction Decode (ID), Execute (EX), Memory Access (MEM), and Write Back (WB).

```Python
for i in range(len(self.stages) - 1, -1, -1):
```

To address the issue of overwriting and ensure smooth transitions between stages, the emulator was designed to process stages in reverse order. This approach ensures that data dependencies and stage outputs are properly managed, preventing conflicts and data corruption.

###### Part 2. QEMU Implementation

QEMU's implementation of instruction execution involves a multi-stage process analogous to a CPU pipeline, though it is not structured in exactly the same way as a physical pipeline.
Instead, QEMU focuses on translating guest instructions into host instructions that can be executed directly by the host CPU.

> Q1. How QEMU divided stages?\
> A. IF+ID to TB (Translation Block) Execution, EX+MEM to Instruction Translation.

> Q2. What is TB?\
> A. QEMU groups a sequence of guest instructions into a Translation Block (TB).**

Each TB is a unit of execution containing several instructions that are translated together. The core execution loop in QEMU fetches and executes these TBs, akin to the IF (Instruction Fetch) and ID (Instruction Decode) stages in a classic CPU pipeline.

```C
tb = tb_lookup(cpu, pc, cs_base, flags, cflags);
if (tb == NULL) {
  mmap_lock();
  tb = tb_gen_code(cpu, pc, cs_base, flags, cflags);
  mmap_unlock();
 }
```

‘tb\_lookup’ searches for an existing TB in the cache based on the current PC, cs\_base, flags, and cflags. If no cached TB is found, ‘tb\_gen\_code’ generates a new TB. This involves translating a block of guest instructions into host instructions.

```C
/*
We add the TB in the virtual pc hash table for the fast lookup
*/
h = tb_jmp_cache_hash_func(pc);
jc = cpu->tb_jmp_cache;
jc->array[h].pc = pc;
qatomic_set(&jc->array[h].tb, tb);
```
https://github.com/qemu/qemu/blob/dec9742cbc59415a8b83e382e7ae36395394e4bd/accel/tcg/cpu-exec.c
(from cpu\_exec\_loop(CPUState \*cpu, SyncCloks \*sc)

The newly generated TB is added to a jump cache (cpu->tb\_jmp\_cache). This cache uses a hash function (tb\_jmp\_cache\_hash\_func) to map PCs to their corresponding TBs for fast lookup in future executions.

> Q3. Why QEMU used TB?\
> A. For performance optimization. More specifically, dynamic binary translation and caching.
> - QEMU Converts guest machine instructions into host machine instructions, in other words, provides dynamic binary translation. Also, instead of translating instructions one at a time, QEMU translates blocks of instructions. By caching the TBs, QEMU can bypass this translation step on subsequent executions of the same code block, thereby speeding up execution.
> - QEMU uses the TCG(Tiny Code Generator) to translate guest instructions into intermediate code, which is then translated into host machine code. This process involves stages similar to the EX (Execute) and MEM (Memory Access) stages. TCG performs the translation in stages, starting from the guest instruction set to intermediate representation and finally to host instructions.
> - Finally, QEMU uses block chaining to link multiple TB. Block chaining involves linking together multiple stages or tasks in the pipeline so that the output of one stage is directly connected to the input of the next stage, forming a chain. This allows data to flow seamlessly from one stage to the next without the need for intermediate storage or context switching.
> - The main idea behind block chaining is to reduce the latency introduced by switching between stages. Instead of completing one task in a stage, storing the result temporarily, and then transferring it to the next stage, block chaining enables the result to be transferred directly from one stage to the next as soon as it is available. This eliminates unnecessary delays and improves overall throughput.

###### Part 3. My code improved by referring to QEMU

I think adopting TB concept is not appropriate for my codework.

If MIPS is the host, then there may not be a need to introduce the concept of Translation Blocks (TBs). TBs are typically used in virtualization or emulation software to efficiently manage the translation of instructions between the host and guest architectures. If the host system directly supports the MIPS architecture, such translation processes may not be necessary.

Therefore, without introducing the concept of TBs, it is possible to directly execute MIPS instructions and return results. However, using the TB concept can optimize performance in certain situations, so it may be worth considering for performance improvement if needed.

But using block chaining may helpful. So, I decided to add code below.

- inserted code
```Python
# Pre-load next instruction (block chaining logic)
next_index = shred.pc + self.pipeline_depth - 1
```

- full code
```python
# Move instructions to the next stage
for i in range(len(self.stages) - 1, 0, -1):
    if not self.pipeline[i]:
    self.pipeline[i] = self.pipeline[i - 1]
    self.pipeline[i - 1] = None

    # Fetch new instruction
    if shred.pc < len(instruction_memory) and not self.pipeline[0]:
    self.pipeline[0] = self.if_stage(shred, log)

    # Pre-load next instruction (block chaining logic)
    next_index = shred.pc + self.pipeline_depth - 1
    if next_index < len(instruction_memory):
    self.pipeline[-1] = instruction_memory[next_index]
```

In the context of the provided code, block chaining can be implemented by loading the next instruction into the pipeline's last stage immediately after loading the current instruction into the first stage. This ensures that the next instruction is ready to be executed as soon as the current instruction completes, without waiting for additional cycles or context switches.

By leveraging block chaining, the pipeline can maintain a continuous flow of instructions, maximizing throughput and minimizing idle time. This ultimately leads to improved performance and efficiency in executing a sequence of instructions.

##### 2. Independence Between Stages

###### Part 1. My Implementation

```python
class Latch:
    def __init__(self):
        self.pc = None
        self.instruction = Instruction()
    def flush(self):
        self.pc = None
        self.instruction = None
```

To achieve concurrent operation of all pipeline stages without interference, each stage's output written to a latch, which the subsequent stage reads from. This decoupling allows each stage to operate independently, ensuring that the execution of one stage does not affect the others.

###### Part 2. QEMU Implementation**

In QEMU, the Transfer Block (TB) mechanism is used.

When a TB is generated, it encapsulates a sequence of translated instructions along with metadata such as the source program counter (PC) and flags. During execution, the TB is traversed through various stages, each representing a step in the emulation process. Data is transferred between these stages primarily through the TB structure itself, which carries the necessary information for each stage to perform its tasks. This allows for seamless coordination and execution of translated code within QEMU's emulation pipeline.

```C
TranslationBlock *tb_gen_code(CPUState *cpu,
                              vaddr pc, uint64_t cs_base,
                              uint32_t flags, int cflags)
{
    CPUArchState *env = cpu_env(cpu);
    TranslationBlock *tb, *existing_tb;
    ...
    phys_pc = get_page_addr_code_hostp(env, pc, &host_pc);
    ...
    tb = tb_alloc(pc, cs_base, flags, cflags);
    ...
    tb->cs_base = cs_base;
    tb->flags = flags;
    tb->cflags = cflags;
```

##### 3. Instruction Overlapping

###### Part 1. My Implementation

```python
class Pipeline:
    def __init__(self):
        self.stages = ["IF", "ID", "EX", "MEM", "WB"]
        self.pipeline = deque([None] * 5)  # Initialize pipeline with 5 stages, all empty
        self.clock = 0  # Initialize clock cycle counter
```

Deque is utilized in the code to manage the pipeline stages efficiently. By representing each stage as an element in the deque, it allows for easy insertion and removal of instructions at different pipeline stages. This data structure facilitates overlapping execution by enabling the movement of instructions through the pipeline in a streamlined manner. With deque, instructions can be added to the front of the pipeline while older instructions progress through subsequent stages, maintaining the overlap of instruction execution. Overall, deque enhances the management and processing of instructions within the pipeline, contributing to improved performance and efficiency.

```python
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
```
(Reverse order for preventing overwriting. I already explained in Topic1)

```python
for i in range(len(self.stages) - 1, -1, -1):
    if shred.pc >= len(instruction_memory):
        return
    if self.pipeline[i]:
        if self.pipeline[i].stage == len(self.stages):
            self.pipeline[i] = None  # Instruction is done
        else:
            self.process_stage(i, shred, log)
```
This segment of the code advances instructions to the next pipeline stage by shifting them down the pipeline. It ensures instruction overlapping by allowing new instructions to enter the pipeline when the first stage is vacant. This mechanism enables efficient pipelining, where multiple instructions can be processed simultaneously at different stages, enhancing overall throughput. The "if not self.pipeline[0]" condition checks if the first stage is empty, indicating space for a new instruction, facilitating overlapping execution.



### Topic 2: Hazard

![](docs/assets/Aspose.Words.db74fd64-4fc5-4662-9ad1-efd722149e28.016.png)

![](docs/assets/Aspose.Words.db74fd64-4fc5-4662-9ad1-efd722149e28.017.png)

#### 1. Control Hazard
   - Current instruction's IF stage is dependent on previous instruction's WB stage.
#### 2. Data Hazard
   - (RAW) Current instruction's EX stage is dependent on previous instructions’ EX, MM, WB.
   - (WAR, WAW) Occur due to non-uniform execution time of each stages. 
   - If current instruction's EX is dependent to previous instruction's EX, is WAR. 
   - If dependent to WB, is WAW.**

I think WAW, WAR Hazard's aspect is different from RAW. Output dependency is caused by execution time, unlike input dependency, which is a problem caused by the overlap of pipelines itself.

Control Hazards occur when the pipeline makes incorrect assumptions about control flow, especially with branch instructions. In MIPS pipelines, branch decisions typically occur during the execution (EX) stage, which can lead to delays if the branch outcome isn't determined early enough. To mitigate this issue, Pipeline Stalling, Branch Prediction, Delayed Branching can employed.

Data Hazards arise when instructions with data dependencies are executed in a manner that disrupts the pipeline sequence. There are three main types: RAW, WAR, WAW.

To mitigate these hazards, MIPS processors employ techniques like data forwarding (bypassing), where data is transferred directly between pipeline stages to resolve dependencies without stalling the pipeline unnecessarily. Additionally, pipeline stalling is used to ensure instructions are executed in the correct sequence when dependencies cannot be resolved immediately. Compiler optimizations such as code reordering also play a role in minimizing these hazards during program compilation, contributing to improved pipeline efficiency and performance.



### Topic 3: Detecting Hazard

![](docs/assets/Aspose.Words.db74fd64-4fc5-4662-9ad1-efd722149e28.018.png)

#### 1. Control Hazard: isBranch, isTaken
   - isBranch is determined in ID, and isTaken is determined in EX.
#### 2. Data Hazard: (Rs or Rt) and RegWrite
   - Current instruction's ID stage detects. 
   - If Rs or Rt and other instruction's RegWrite's register is same.

#### 1. Data Hazard

- Conceptual
```python
def stall(instruction, IRID):
    if (rs(IRID) == instruction.destEX) and use_rs(IRID) and instruction.RegWriteEX:
        return True
    elif (rs(IRID) == instruction.destMEM) and use_rs(IRID) and instruction.RegWriteMEM:
        return True
    elif (rs(IRID) == instruction.destWB) and use_rs(IRID) and instruction.RegWriteWB:
        return True
    elif (instruction.rt == IRID.destEX) and use_rt(IRID) and instruction.RegWriteEX:
        return True
    elif (instruction.rt == IRID.destMEM) and use_rt(IRID) and instruction.RegWriteMEM:
        return True
    elif (instruction.rt == IRID.destWB) and use_rt(IRID) and instruction.RegWriteWB:
        return True
    return False
```

- In Pipeline
```python
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
```
The `detect_data_hazard` function checks for data hazards in a pipelined processor by examining the `ex_mem_latch` and `mem_wb_latch` stages. It first verifies if the current instruction's source registers (`rs` or `rt`) match the destination register (`rd`) of instructions in these pipeline stages that are performing register writes (`RegWrite`).

If either the `ex_mem_latch` or `mem_wb_latch` contains an instruction performing a register write to a register that the current instruction depends on (`rs` or `rt`), the function returns `True`, indicating a data hazard. Otherwise, it returns `False`, indicating no hazard is detected.

***2. Control Hazard***

- In ID_Stage
```python
def isBranch(opcode):
    return opcode in [2, 3, 4, 5]  # j, jal, beq, bne
```

- In Pipeline
```python
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
```

The control hazard detection logic in the pipeline ensures the proper handling of branch instructions and their potential to alter the program flow. This is achieved by checking the isBranch and isTaken flags in the EX/MEM latch. If a branch instruction is detected (isBranch is true) and the branch is taken (isTaken is true), the pipeline is stalled, the program counter (PC) is updated to the branch target address (shred.pc = self.ex\_mem\_latch.result), and the initial stages of the pipeline (IF, ID, EX) are cleared to prevent any incorrect instructions from being fetched or executed.


### Topic 4: Data Hazard in Detail, how can minimize?
![](docs/assets/Aspose.Words.db74fd64-4fc5-4662-9ad1-efd722149e28.023.png)

#### 1. Stall using scoreboarding.
   - Utilizes valid bits to track RAW dependency.**
#### 2. Data Forwarding (Bypassing)
   - Forwarding results from EX/MEM and MEM/WB stages to earlier pipeline stages.**

#### 1. Stall using scoreboarding.

```python
# Execute instructions
for inst in instructions:
   stall_release[inst.dest_reg] = {}
   # Check if source operands are available
   if (inst.src_reg1 in scoreboard and not scoreboard[inst.src_reg1]) or
           (inst.src_reg2 in scoreboard and not scoreboard[inst.src_reg2]):
      # Stall cycle
      print(f"Cycle {cycle_number}: Stalling {inst.opcode} {inst.dest_reg}, {inst.src_reg1}, {inst.src_reg2}")
      stall_release[inst.dest_reg][cycle_number] = "Stalled"
   else:
      # Execute instruction
      execute_instruction(inst, cycle_number)
      # Update scoreboard
      scoreboard[inst.dest_reg] = False
      for reg in (inst.src_reg1, inst.src_reg2):
         if reg in scoreboard:
            scoreboard[reg] = True
      stall_release[inst.dest_reg][cycle_number] = "Released"
   cycle_number += 1
```

The implemented scoreboarding system uses a dictionary, scoreboard, to track register states with Boolean values indicating availability. Another dictionary, stall\_release, records whether each register was executed or stalled per cycle. It checks and stalls instructions if their source registers are in use, otherwise executes them and updates scoreboard and stall\_release. This approach efficiently manages data dependencies, minimizes stalls, and enhances overall execution performance.

In the given code, the first instruction `Instruction("add", "r2", "r3", "r2")` writes to register `r2`, and immediately after, the second instruction `Instruction("sub", "r2", "r5", "r4")` also attempts to write to `r2`. This creates a Write After Write (WAW) dependency.

However, the simple scoreboarding implementation does not detect such WAW dependencies. It only checks if the destination register (`dest\_reg`) of each instruction is currently being written to by another instruction in the scoreboard. It does not verify if another instruction has already written to the same register before the current instruction attempts to write to it. Therefore, after the first instruction writes to `r2`, the second instruction may proceed without stalling, potentially leading to unexpected behavior.


![](docs/assets/Aspose.Words.db74fd64-4fc5-4662-9ad1-efd722149e28.025.png)
  Simple Scoreboarding, Limitations

```python
def main():
    # Define the instructions
    instructions = [
        Instruction("add", "r2", "r3", "r2"),   # WAW hazard with the next instruction
        Instruction("sub", "r2", "r5", "r4")    # Should be stalled due to WAW hazard
    ]
```

- Output
```
Cycle 1: Executing add r2, r3, r2
Cycle 2: Executing sub r2, r5, r4

Stall Release Table:
Register | Stall Release
    r2    |    {2: 'Released'}
```
For output dependency, register renaming and out-of-order execution may helpful.

So, advanced scoreboarding required.

```python
def find_youngest_value(registers):
    youngest_value = None
    for reg in registers:
        if registers[reg] is not None and registers[reg].executing:
            if youngest_value is None or registers[reg].executing < youngest_value.executing:
                youngest_value = registers[reg]
    return youngest_value
```
The function `find_youngest_value` is responsible for detecting the most recently executed instruction in the 'scoreboard' dictionary. The function checks the status of each register stored in the 'scoreboard' to find the most recently executed instruction in the running instruction. It manages the data dependencies between commands and detects output dependencies to determine whether it is necessary to perform stall processing.


### Topic 4: Control Hazard in Detail, how can minimize?

![](docs/assets/Aspose.Words.db74fd64-4fc5-4662-9ad1-efd722149e28.029.png)

#### 1. Simply Stalling
   - Wait until previous instruction's WB ends, and insert nop.
#### 2. Stalling makes more execution time.

When a branch instruction is encountered in a pipeline, such as a conditional branch like `beq` or `bne`, the processor faces a control hazard. To minimize this, the pipeline typically stalls, inserting no-operation (nop) instructions until the branch condition is resolved. However, stalling prolongs execution time because it delays subsequent instructions that could proceed independently.

### Sol1. Minimize control-related instructions

![](docs/assets/Aspose.Words.db74fd64-4fc5-4662-9ad1-efd722149e28.030.png)

#### 1. Just guessing nextPC = PC + 4
#### 2. Predicate Combining
   - Get rid of unnecessary control flow instructions.
#### 3. Predicated Execution
   - Convert control dependences into data dependences.

With Predicate Combining, we aim to combine multiple predicates to minimize branching. With Predicated Execution, we convert control dependences into data dependences using conditional operations.

#### 2. Predicate Combining

- Before
```
sub $t8, $t0, $t1       # $t8 = a - b
bgtz $t8, true_block1   # if a > b, go to true_block1
# false_block1
sub $t9, $t2, $t3       # $t9 = d - e
bgtz $t9, true_block2   # if d > e, go to true_block2
# false_block2
add $t7, $t5, $t6       # f = g + h
j end                   # jump to end
true_block2:
sub $t7, $t5, $t6       # f = g - h
j end                   # jump to end
true_block1:
add $t4, $t2, $t3       # c = d + e
j end                   # jump to end
end:
```

Branch misprediction penalties arise from the `bgtz` instructions in the control flow, which modern processors handle using branch predictors. Incorrect predictions result in pipeline flushes, discarding partially executed instructions and reloading with the correct path's instructions, leading to pipeline stalls and performance degradation. The original code contains two branches (`bgtz` for `true\_block1` and `true\_block2`), each potentially mispredicted, doubling the chance of pipeline stalls. This increases pipeline flushes and control flow complexity, heightening the prediction difficulty and likelihood of mispredictions. Predicate combining simplifies control flow by merging multiple conditions and reducing the number of branches, thereby optimizing performance.

- After
```
sub $t8, $t0, $t1       # $t8 = a - b
slt $t9, $t0, $t1       # $t9 = 1 if a < b, 0 otherwise

sub $t10, $t2, $t3      # $t10 = d - e
slt $t11, $t2, $t3      # $t11 = 1 if d < e, 0 otherwise

# Calculate all possible outcomes
add $t4, $t2, $t3       # temp_c = d + e
sub $t7, $t5, $t6       # temp_f1 = g - h
add $t12, $t5, $t6      # temp_f2 = g + h

# Use the predicates to select the correct outcomes
movz $t7, $t12, $t11    # if $t11 == 0 (d >= e), $t7 = temp_f2
movn $t7, $t7, $t9      # if $t9 != 0 (a > b), $t7 = temp_f1

movn $t4, $t4, $t9      # if $t9 != 0 (a > b), $t4 = temp_c

end:
```

**3. Predicated Execution**

Using `bgtz` with a temporary register like `$t9` to minimize control dependency is a strategy aimed at reducing the impact of branch mispredictions in the pipeline. By employing a conditionally executed instruction (`bgtz`) rather than a branch, the processor can potentially avoid the penalties associated with branch prediction failures. This approach allows the processor to continue executing subsequent instructions without stalling while waiting for the branch outcome. However, it's important to note that this technique introduces dependencies on the evaluation of the condition (`$t9 > 0`), which must be accurately predicted to avoid performance degradation. Therefore, while it can improve pipeline efficiency by reducing stalls due to mispredictions, careful consideration is needed to balance the benefits with the potential risks of relying on accurate condition evaluation in hardware execution.

- Before
```
# Assuming registers $t0 = a, $t1 = b, $t2 = d, $t3 = e, $t4 = c, $t5 = g, $t6 = h, $t7 = f

# Original MIPS Code
sub $t8, $t0, $t1       # $t8 = a - b
bgtz $t8, true_block    # if a > b, go to true_block
# false_block
add $t7, $t5, $t6       # f = g + h
j end                   # jump to end
true_block:
add $t4, $t2, $t3       # c = d + e
end:
```

- After
```
# Predicated Execution
sub $t8, $t0, $t1       # $t8 = a - b
slt $t9, $t8, $zero     # $t9 = (a <= b) ? 1 : 0
add $t4, $t2, $t3       # c = d + e
mul $t7, $t9, $t5       # t7 = (a <= b) ? g : 0
mul $t10, $t9, $t6      # t10 = (a <= b) ? h : 0
add $t7, $t7, $t10      # f = g + h if a <= b
```

### Sol2. Delayed Branching

![](docs/assets/Aspose.Words.db74fd64-4fc5-4662-9ad1-efd722149e28.036.png)

#### 1. Inserting nop.
#### 2. Reordering, filling branch delay slot.

Both methods aim to reduce pipeline stalls caused by branch instructions. Inserting NOPs is straightforward but adds idle cycles in the pipeline. Reordering instructions to fill the delay slot can potentially improve performance by keeping the pipeline busy with useful instructions. The choice between these methods often depends on the specific pipeline design and the characteristics of the branch instructions.


### Misprediction Penalty

![](docs/assets/Aspose.Words.db74fd64-4fc5-4662-9ad1-efd722149e28.037.png)

![](docs/assets/Aspose.Words.db74fd64-4fc5-4662-9ad1-efd722149e28.038.png)

Misprediction penalty refers to the additional delay incurred by a CPU when a branch prediction fails. When a branch instruction (e.g., conditional jump, branch command) is encountered, the CPU predicts the next instruction's address to optimize performance. If this prediction turns out to be incorrect, the CPU must discard the current execution path and redirect to the correct instruction, resulting in a penalty of typically 3 cycles, known as "3 bubbles." During this time, the CPU prepares to jump to the correct address and fetches the correct instruction, effectively introducing idle cycles into the execution pipeline. Efficient branch prediction algorithms are crucial in minimizing misprediction penalties and optimizing CPU performance.

### Sol3. Static Branch Prediction

Branch prediction strategies play a crucial role in optimizing the performance of modern processors by predicting the outcome of conditional branches before their actual execution. Here are some key strategies:

- Always taken
  - This strategy predicts that all branches will be taken, meaning control flow will always follow the branch instructions. This approach is beneficial when branches are predominantly taken, reducing the risk of mispredictions but potentially causing inefficiencies when branches are not taken.
- Always not taken**
  - In contrast, this strategy assumes that all branches will not be taken, meaning control flow proceeds to the next sequential instruction after a branch instruction unless explicitly redirected by the branch condition. This strategy is effective when branches are rarely taken, minimizing misprediction penalties but possibly failing to exploit opportunities for optimization in branches that are frequently taken.
- BTFN (Backward Taken, Forward Not Taken)**
  - BTFN predicts that backward branches (branches to lower memory addresses) are taken and forward branches (branches to higher memory addresses) are not taken. This strategy leverages typical program control flow patterns where loops tend to have backward branches and conditional checks tend to have forward branches.
- Compiler-based and program-based**
  - Compiler-based strategies use static analysis performed by the compiler to predict branch outcomes based on heuristics and profiling data gathered during compilation. Program-based strategies rely on dynamic execution characteristics observed at runtime to adaptively predict branch outcomes.

Each strategy has trade-offs in terms of prediction accuracy and performance impact. Effective branch prediction improves processor throughput by minimizing stalls due to branch delays and reducing the penalties associated with mispredicted branches, thereby enhancing overall system efficiency.

- Implementation
```python
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
```

### Sol4. Dynamic Branch Prediction

My code simulates a simple pipelined processor with a focus on branch prediction. It includes the `Instruction` class to model instructions and their attributes, such as opcode, destination register, source registers, program counter, and branch prediction details. The `BranchTargetBuffer` (BTB) class manages branch target entries and updates, while the `LastTimePredictor` (LTP) class handles branch prediction states. The pipeline stages (IF, ID, EX, MEM, WB) are implemented in separate functions, each processing instructions and updating the pipeline state. The `Shred` class initializes the pipeline with instructions and manages pipeline latches. The `simulate\_pipeline` function runs the simulation cycle-by-cycle, and the `test\_pipeline` function tests the pipeline, printing the final states of BTB and LTP.

In this code, a 2-bit counter is used within the Last Time Predictor (LTP) to improve branch prediction accuracy by tracking the state of branch instructions. The counter has four states: 0 (Strongly Not Taken), 1 (Weakly Not Taken), 2 (Weakly Taken), and 3 (Strongly Taken). When a branch is encountered, the LTP checks the counter state to predict the outcome. If the state is 2 or 3, the branch is predicted as taken; if the state is 0 or 1, it is predicted as not taken. After the branch outcome is known, the counter is updated: it increments if the branch was taken and decrements if it was not, ensuring that the predictor gradually adjusts to the actual behavior of branches.

- in Instruction class
```python
self.target_address = 0  # Target address for branch instructions
self.branch_prediction = None  # Predicted outcome of the branch
self.branch_taken = None  # Actual outcome of the branch
self.predicted_target_address = None  # Predicted target address for branch instructions
self.predictor_state = 0  # Initial predictor state (Strongly not taken)
self.btb_valid = False  # Valid bit for BTB
self.btb_tag = None  # Tag to identify branch in BTB
self.ltp_history = 0  # History bits for LTP
```
These attributes are added to the `Instruction` class to facilitate branch prediction and tracking within the pipeline. `self.branch\_prediction` stores the predicted outcome of a branch instruction, while `self.branch\_taken` records the actual outcome after execution. `self.predicted\_target\_address` holds the predicted target address for branch instructions. `self.predictor\_state` represents the current state of the 2-bit counter used in the Last Time Predictor (LTP). `self.btb\_valid` indicates if the Branch Target Buffer (BTB) entry is valid, and `self.btb\_tag` helps identify branches in the BTB. Finally, `self.ltp\_history` keeps track of the branch history bits for the LTP. These attributes collectively enable accurate branch prediction and update mechanisms within the pipeline stages.

- in BranchTargetBuffer class
```python
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
```
This `BranchTargetBuffer` class provides a mechanism to store and manage target addresses for branch instructions in a processor. It initializes with a specified size and uses an array (`entries`) to store tuples of (PC, target address). Methods include `get\_entry` to retrieve entries based on PC, `update\_entry` to store PC and target address pairs, and `update\_tag` to update tags in existing entries based on PC. This class supports efficient branch prediction by storing and retrieving target addresses quickly using modulo indexing.

- in LastTimePredictor class
```python
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
```
This `LastTimePredictor` class implements a 2-bit counter-based branch prediction mechanism. It maintains a `predictor\_table` to store the prediction states for different program counters (PCs). The `predict\_branch` method predicts the outcome of a branch instruction based on the stored state in `predictor\_table`. If the PC exists in `predictor\_table` and the state is 2 or higher, it predicts the branch as taken; otherwise, it predicts it as not taken. The `update\_branch\_prediction` method updates the predictor state based on the actual outcome (`branch\_taken`) of the branch instruction. It adjusts the state upwards for taken branches and downwards for not taken branches, ensuring the predictor adapts to changing branch behavior over time. This class effectively enhances branch prediction accuracy by dynamically adjusting predictions using historical behavior stored in the 2-bit counters.

## Conclusion

The development of the five-stage pipelined MIPS emulator highlighted the complexity and intricacies of pipeline architecture in modern processors. Through careful implementation and comparison with QEMU's codebase, the emulator successfully demonstrated the key features of pipelining, including stage independence, instruction overlapping, and effective hazard management.

1. Pipelining Efficiency
   - By maintaining stage sequence and ensuring independence between stages, the emulator was able to simulate concurrent execution without interference, closely mimicking real-world pipeline behavior.

2. Hazard Management
   - Addressing data and control hazards was a significant aspect of the project. Techniques such as scoreboarding and data forwarding effectively minimized the impact of hazards, ensuring smooth instruction flow and accurate execution. Control hazards were managed through various strategies, including static and dynamic branch prediction, which helped in maintaining pipeline efficiency.

3. Performance Optimization
   - The project explored several methods to enhance pipeline performance, such as minimizing control-related instructions and employing advanced hazard detection mechanisms. These optimizations were crucial in improving the emulator's overall efficiency and reducing execution stalls.

4. Comparative Insights 
   - By comparing the emulator's implementation with QEMU and Nucleusrv’s code, the project provided valuable insights into different approaches to handling pipeline execution and hazards. This comparative analysis highlighted the strengths and limitations of various techniques, contributing to a deeper understanding of pipeline architecture.

