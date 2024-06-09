class Instruction:
    def __init__(self, opcode, dest_reg, src_reg1, src_reg2):
        self.opcode = opcode
        self.dest_reg = dest_reg
        self.src_reg1 = src_reg1
        self.src_reg2 = src_reg2
        self.executing = False

def execute_instruction(inst, cycle_number):
    # Execute the instruction
    print(f"Cycle {cycle_number}: Executing {inst.opcode} {inst.dest_reg}, {inst.src_reg1}, {inst.src_reg2}")
    inst.executing = True

def find_youngest_value(registers):
    youngest_value = None
    for reg in registers:
        if registers[reg] is not None and registers[reg].executing:
            if youngest_value is None or registers[reg].executing < youngest_value.executing:
                youngest_value = registers[reg]
    return youngest_value
    
def main():
    # Define the instructions
    instructions = [
        Instruction("add", "r2", "r3", "r2"),
        Instruction("add", "r2", "r3", "r1"),
        Instruction("add", "r7", "r3", "r4"),
        Instruction("add", "r8", "r3", "r1"),
        Instruction("add", "r2", "r3", "r2")
    ]

    scoreboard = {}
    stall_release = {}

    cycle_number = 1

    # Execute instructions
    for inst in instructions:
        stall_release[inst.dest_reg] = {}
        # Check for output dependency
        youngest_value = find_youngest_value(scoreboard)
        if youngest_value is not None and inst.dest_reg == youngest_value.dest_reg:
            print(f"Cycle {cycle_number}: Output dependency detected, finding youngest value...")
            execute_instruction(youngest_value, cycle_number)
            stall_release[inst.dest_reg][cycle_number] = "Released"
            scoreboard[inst.dest_reg].executing = False
            for reg in (inst.src_reg1, inst.src_reg2):
                if reg in scoreboard:
                    scoreboard[reg].executing = True
        else:
            # Check if source operands are available
            if (inst.src_reg1 in scoreboard and scoreboard[inst.src_reg1].executing) or \
               (inst.src_reg2 in scoreboard and scoreboard[inst.src_reg2].executing):
                # Stall cycle
                print(f"Cycle {cycle_number}: Stalling {inst.opcode} {inst.dest_reg}, {inst.src_reg1}, {inst.src_reg2}")
                stall_release[inst.dest_reg][cycle_number] = "Stalled"
            else:
                # Execute instruction
                execute_instruction(inst, cycle_number)
                # Update scoreboard
                scoreboard[inst.dest_reg] = inst
                for reg in (inst.src_reg1, inst.src_reg2):
                    if reg in scoreboard:
                        scoreboard[reg].executing = True
                stall_release[inst.dest_reg][cycle_number] = "Released"
        cycle_number += 1

    print("\nStall Release Table:")
    print("Register | Stall Release")
    for reg in stall_release:
        print(f"    {reg}    |    {stall_release[reg]}")

if __name__ == "__main__":
    main()