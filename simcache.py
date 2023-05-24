#!/usr/bin/python3

"""
CS-UY 2214
Joel Harawa
E20 cache simulator
simcache.py
"""

import argparse

OPCODES = {"0000" : "add", "0001": "sub", "0010": "or", "0011": "and", "0100" : "slt", "1000" : "jr", "001" : "addi", "001" : "addi", "110" : "jeq", "101" : "sw", "100" : "lw", "111" : "slti", "010": "j"}

PC = 0
R0 = 0
R1 = 0
R2 = 0
R3 = 0
R4 = 0
R5 = 0
R6 = 0
R7 = 0

REGISTERS = {"000" : R0, "001" : R1, "010" : R2, "011" : R3, "100" : R4, "101" : R5, "110" : R6, "111" : R7}

#takes opcode and other arguments in instruction as well as program
#counter and applies appropriate function and updates and returns
#program counter
def format_opcode(opcode, second_arg, third_arg, fourth_arg, PC):
    if opcode not in OPCODES:
        return PC + 1
    if OPCODES[opcode] == "add":
        add(fourth_arg, second_arg, third_arg)
        PC += 1
    if OPCODES[opcode] == "sub":
        sub(fourth_arg, second_arg, third_arg)
        PC += 1
    if OPCODES[opcode] == "or":
        Or(fourth_arg, second_arg, third_arg)
        PC += 1
    if OPCODES[opcode] == "and":
        And(fourth_arg, second_arg, third_arg)
        PC += 1
    if OPCODES[opcode] == "jr":
        PC = REGISTERS[second_arg]
    if OPCODES[opcode] == "slt":
        slt(fourth_arg, second_arg, third_arg)
        PC += 1
    return PC

#takes strings from .bin file removes unwanted texted, outputs machine code representations
def format_bin(instructions):
    machine_code = []
    for i in range(len(instructions)):
        machine_code.append(instructions[i].split('b')[1].strip(';'))  
    for i in range(8192-len(instructions)):
        machine_code.append("0000000000000000")
    return machine_code 

 #takes value in source register and immediate value, performs addition,
 #and then stores the value in the destination register
def addi(src, dst, imm):
    result = 0
    if dst == "000":
        return None
    if imm >= 64:
        result = REGISTERS[src] + imm - 128
    else:
        result = REGISTERS[src] + imm
    if result >= 0 and result <= 65535:
        REGISTERS[dst] = result
    if result > 65535:
        REGISTERS[dst] = result - 65535          
    if result < 0 and result >= -65535:
        REGISTERS[dst] = 65535 + result + 1
    if result < -65535:
        REGISTERS[dst] = - (65535 + result + 1) 

 #takes values of registers, immediate value, memory  and applies function of store word instruction        
def lw(addr, dst, imm, instructions):
    if dst == "000":
        return None
    REGISTERS[dst] = int(instructions[REGISTERS[addr] + imm], 2)

#takes values of registers, immediate value, memory  and applies function of store word instruction
def sw(addr, src, imm, instructions):
    instructions[REGISTERS[addr] + imm] = '{:016b}'.format(REGISTERS[src])        

#takes values of registers A and B, compares them and updates program counter based on comparison
def jeq(reg_A, reg_B, imm, PC):
    if (REGISTERS[reg_A] == REGISTERS[reg_B]):
        if imm >= 64:
            PC = 128 - imm
        else:
            PC += imm + 1
    else:
        PC += 1
    return PC
 #takes value in source register and compares it to immediate, updates destination register
def slti(src, dst, imm):
    if dst == "000":
        return None
    if REGISTERS[src] < imm:
        REGISTERS[dst] = 1
    else: 
        REGISTERS[dst] = 0 

#takes value in register A and B, and applies addition operation                 
def add(dst, reg_A, reg_B):

    if dst == "000":
        return None
    result = REGISTERS[reg_A] + REGISTERS[reg_B]
    if result >= 0 and result < 65535:
        REGISTERS[dst] = result
    if result > 65535:
        REGISTERS[dst] = result - 65535
    if result < 0 and result >= -65535:
        REGISTERS[dst] = 65535 + result + 1
    if result < -65535:
        REGISTERS[dst] = - (65535 + result)

#takes value in register A and B, and applies subtraction operation
def sub(dst, reg_A, reg_B):
     if dst == "000":
         return None
     result = REGISTERS[reg_A] - REGISTERS[reg_B]
     if result >= 0 and result < 65535:
        REGISTERS[dst] = result
     if result > 65535:
         REGISTERS[dst] = result - 65535
     if result < 0 and result >= -65535:
         REGISTERS[dst] = 65536 + result
     if result < -65535:
         REGISTERS[dst] = - (65535 + result)
  
#takes value in register A and B, and applies or operation
def Or(dst, reg_A, reg_B):
    if dst == "000":
        return None
    result = REGISTERS[reg_A] | REGISTERS[reg_B]
    if result >= 0 and result < 65535:
        REGISTERS[dst] = result
    if result > 65535:
        REGISTERS[dst] = result - 65535
    if result < 0 and result >= -65535:
        REGISTERS[dst] = 65536 + result
    if result < -65535:
        REGISTERS[dst] = - (65535 + result)

#takes value in register A and B, and applies and operation
def And(dst, reg_A, reg_B):
    if dst == "000":
        return None
    result  = REGISTERS[reg_A] & REGISTERS[reg_B]
    if result >= 0 and result < 65535:
        REGISTERS[dst] = result
    if result > 65535:
        REGISTERS[dst] = result - 65535
    if result < 0 and result >= -65535:
        REGISTERS[dst] = 65536 + result
    if result < -65535:
         REGISTERS[dst] = - (65535 + result)

#compares value in register A and register B and sets destination
#register to 1 or 0 based on comparison
def slt(dst, reg_A, reg_B):
    if dst == "000":
        return None
    if (REGISTERS[reg_A] < REGISTERS[reg_B]):
        REGISTERS[dst] = 1
    else:
        REGISTERS[dst] = 0

#takes machine code representations, loops through instructions
#detects which instruction is happening, calls function to execute instruction
def simulate_e20(instructions, parts, cache_table, L1, L2):
    PC = 0
    while PC < len(instructions):
        first_arg = instructions[PC][:3]
        second_arg = instructions[PC][3:6]
        third_arg = instructions[PC][6:9]
        fourth_arg = instructions[PC][9:12]
        imm_7 = int(instructions[PC][9:], 2)
        imm_13 = int(instructions[PC][3:], 2)
     
        if first_arg == "000":
            opcode = instructions[PC][-4:]
            PC = format_opcode(opcode, second_arg, third_arg, fourth_arg, PC)
        if first_arg == "001":
            addi(second_arg, third_arg, imm_7)
            PC += 1
        if first_arg == "010":
            if imm_13 == PC:
                break
            PC = imm_13
        if first_arg == "011":
            REGISTERS["111"] = PC + 1
            if imm_13 == PC:
                break
            PC = imm_13
        if first_arg == "100":
            lw(second_arg, third_arg, imm_7, instructions)
            addr = imm_7 +  REGISTERS[second_arg]
            cache(parts, cache_table, PC, addr, L1, L2, "lw")  
            PC += 1
        if first_arg == "101":
            sw(second_arg, third_arg, imm_7, instructions)
            addr = imm_7 + REGISTERS[second_arg]
            cache(parts, cache_table, PC, addr, L1, L2, "sw")
            PC += 1
        if first_arg == "110":
            PC = jeq(second_arg, third_arg, imm_7, PC)
        if first_arg == "111":
            slti(second_arg, third_arg, imm_7)
            PC += 1

def print_cache_config(cache_name, size, assoc, blocksize, num_rows):
    """
    Prints out the correctly-formatted configuration of a cache.

    cache_name -- The name of the cache. "L1" or "L2"

    size -- The total size of the cache, measured in memory cells.
        Excludes metadata

    assoc -- The associativity of the cache. One of [1,2,4,8,16]

    blocksize -- The blocksize of the cache. One of [1,2,4,8,16,32,64])

    num_rows -- The number of rows in the given cache.

    sig: str, int, int, int, int -> NoneType
    """

    summary = "Cache %s has size %s, associativity %s, " \
        "blocksize %s, rows %s" % (cache_name,
        size, assoc, blocksize, num_rows)
    print(summary)

def print_log_entry(cache_name, status, pc, addr, row):
    """
    Prints out a correctly-formatted log entry.

    cache_name -- The name of the cache where the event
        occurred. "L1" or "L2"

    status -- The kind of cache event. "SW", "HIT", or
        "MISS"

    pc -- The program counter of the memory
        access instruction

    addr -- The memory address being accessed.

    row -- The cache row or set number where the data
        is stored.

    sig: str, str, int, int, int -> NoneType
    """
    log_entry = "{event:8s} pc:{pc:5d}\taddr:{addr:5d}\t" \
        "row:{row:4d}".format(row=row, pc=pc, addr=addr,
            event = cache_name + " " + status)
    print(log_entry)

#takes input of entry and cache, adds entry to cache based on contents of cache
#and type of instruction
def add_entry(entry, associativity, curr_cache, instr_type):
    for j in range(len(curr_cache)): 
        if j == entry[0]:
            if len(curr_cache[j]) == 0:
                curr_cache[j].append(entry)
                return True  
            if len(curr_cache[j]) <= associativity:
                for i in range(len(curr_cache[j])):
                    if curr_cache[j][i][1] == entry[1] and instr_type == "lw":
                        curr_cache[j].pop(i)
                        curr_cache[j].append(entry)
                        return False
                if len(curr_cache[j]) == associativity:
                    curr_cache[j].pop(0)
                curr_cache[j].append(entry)
                return True
 
#takes input of information about L1 and L2, the cache structures L1 and L2, and informaion
#about the current instruction
#updates the L1, L2, and cache_table               
def  cache(parts, cache_table, pc, addr, L1, L2, instr_type):
    miss = True 
    name = "" 
    entries = len(parts) // 4
    print(parts)
    num_rows = 0
    block_id = 0
    tag = 0
    status = "MISS"
    for i in range(entries):
        if i % 2 == 0:
            
            name = "L1"
            num_rows = int(parts[3]) if entries == 1 else int(parts[6])
            block_id = addr // int(parts[2]) 
            row = block_id % num_rows
            tag = block_id // num_rows
            entry = [row, tag]
            miss = add_entry(entry, int(parts[1]), L1, instr_type)
            if not miss:
                status = "HIT"
            if instr_type == "sw":
                status = "SW"
                miss = True              
            cache_table.append([name, status, pc, addr, row])                     
        elif miss:
            name = "L2"
            num_rows = int(parts[7])
            block_id = addr // int(parts[5]) 
            row = block_id % num_rows
            tag = block_id // num_rows
            entry = [row, tag]
            miss = add_entry(entry, int(parts[4]), L2, instr_type)
            if not miss:
                status = "HIT"
            if instr_type == "sw":
                status = "SW"
            cache_table.append([name, status, pc, addr, row])
    
def main():
    parser = argparse.ArgumentParser(description='Simulate E20 cache')
    parser.add_argument('filename', help=
        'The file containing machine code, typically with .bin suffix')
    parser.add_argument('--cache', help=
        'Cache configuration: size,associativity,blocksize (for one cache) '
        'or size,associativity,blocksize,size,associativity,blocksize (for two caches)')
    cmdline = parser.parse_args()
    instructions = []
    with open(cmdline.filename) as file:
        for line in file:
            line = line.split("//", 1)[0].strip()
            instructions.append(line)
    machine_code = format_bin(instructions)
    
    cache_table = []
    L1 = [] 
    L2 = []
    if cmdline.cache is not None:
        parts = cmdline.cache.split(",")
        if len(parts) == 3:
            [L1size, L1assoc, L1blocksize] = [int(x) for x in parts]
            # TODO: execute E20 program and simulate one cache here
            num_rows = L1size // (L1assoc * L1blocksize)
            L1 = [[] for i in range(num_rows)]
            parts.append(num_rows)
            simulate_e20(machine_code, parts, cache_table, L1, L2)
            print_cache_config("L1", L1size, L1assoc, L1blocksize, num_rows)
            for i in range(len(cache_table)):
                print_log_entry(cache_table[i][0], cache_table[i][1], cache_table[i][2], cache_table[i][3], cache_table[i][4])
        elif len(parts) == 6:
            [L1size, L1assoc, L1blocksize, L2size, L2assoc, L2blocksize] = \
                [int(x) for x in parts]
            # TODO: execute E20 program and simulate two caches here
            num_rows1 = L1size // (L1assoc * L1blocksize)
            num_rows2 = L2size // (L2assoc * L2blocksize)
            L1 = [[] for i in range(num_rows1)]
            L2 = [[] for i in range(num_rows2)]
            parts.append(num_rows1)
            parts.append(num_rows2)
            simulate_e20(machine_code, parts, cache_table, L1, L2)
            print_cache_config("L1", L1size, L1assoc, L1blocksize, num_rows1)
            print_cache_config("L2", L2size, L2assoc, L2blocksize, num_rows2)
            for i in range(len(cache_table)):
                print_log_entry(cache_table[i][0], cache_table[i][1], cache_table[i][2], cache_table[i][3], cache_table[i][4])
        else:
            raise Exception("Invalid cache config")


if __name__ == "__main__":
    main()
#ra0Eequ6ucie6Jei0koh6phishohm9
