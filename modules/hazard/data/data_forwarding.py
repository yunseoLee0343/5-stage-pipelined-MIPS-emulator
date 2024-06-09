def determine_forwarding(shred, reg):
    if reg == shred.ex_mem_latch.rd and shred.ex_mem_latch.regWrite:
        return shred.ex_mem_latch.result
    elif reg == shred.mem_wb_latch.rd and shred.mem_wb_latch.regWrite:
        return shred.mem_wb_latch.result
    else:
        return shred.registers[reg]