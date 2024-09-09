import struct
import sys

# TODO:
# - Add PUSH SPM and special registers shortcut "PUSH SP => PUSH.R 0, PUSH SPM3 => PUSH.S 3"

# Opcode dictionary based on the PANv0 ISA
OPCODES = {
    "PREP":     0,
    "PUSH.I":   1,
    "PUSH.S":   2,
    "PUSH.R":   3,
    "ADD":      4,
    "JUMP.ABS": 5,
    "JUMP":     6,
}


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input file> [<output file>]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = "output.bin" if len(sys.argv) == 2 else sys.argv[2] 

    # Read input file
    with open(input_file, 'r') as f:
        asm_code = f.readlines()

    # Assemble and write to output file
    binary_code = assemble_program(asm_code)

    # Pretty print it to console
    s = str(bin(int.from_bytes(binary_code, byteorder='little')))[2:]
    s = ("0" * (8 - (len(s) % 8))) + s
    ss = ""
    for i in range(len(s)):
        if i % 4 == 0 and i != 0:
            if i % 8 == 0:
                ss += " "
            else:
                ss += "_"
        ss += s[i]
    ss = ss.split(" ")[::-1]
    print("\nOutput Binary:")
    i = 0
    while i < len(ss):
        hx = str(hex(i))[2:]
        print(("0"*(8-len(hx)))+hx+":", " ".join(ss[i:i+6]))
        i += 6

    with open(output_file, 'wb') as f:
        f.write(binary_code)


def assemble_program(asm_code):
    """Assemble the assembly code into binary code."""
    binary_code = b''
    labels = {}
    lines = [] # (instr, size)


    # First pass: Record labels
    for line in asm_code:
        line = line.split(";")[0].strip()
        args = line.split()
        if len(args) == 1:
            if line.endswith(':'):
                labels[line[:-1]] = -1
    print("Labels:\n", labels)

    # Second pass: Expand pseudo-ops, remove commends, skip blank lines
    for line in asm_code:
        process_line(line, lines, labels)
    print("\nLines:\n", lines)

    # Third pass: Resolve label addresses
    finished = False
    while not finished:
        finished = True
        curr_addr = 0
        for i, (instr, instr_size) in enumerate(lines):
            if instr_size == 0: # it is a label
                if labels[instr] != curr_addr:
                    finished = False
                    labels[instr] = curr_addr
            else:
                args = instr.split(" ")
                if len(args) < 2:
                    print("\n\n", args)
                    raise "Args not len 2"
                opcode, operand = args[0], args[1]
                if opcode == "JUMP":
                    if operand in labels:
                        # update instr size 
                        lines[i] = (lines[i][0], calc_instr_size(curr_addr + labels[operand]))
            curr_addr += instr_size

    # Fourth pass: Resolve jump relative addresses
    curr_addr = 0
    for i, (instr, instr_size) in enumerate(lines):
        if instr_size == 2:
            args = instr.split(" ")
            opcode, operand = args[0], args[1]
            if opcode == "JUMP":
                if operand not in labels:
                    new_addr = curr_addr + int(operand)
                    lines[i] = (opcode + " " + str(new_addr) , calc_instr_size(new_addr))
        curr_addr += instr_size

    instructions = []
    for i, (instr, instr_size) in enumerate(lines):
        if instr_size != 0:
            instructions.append(instr)
    print("\nInstructions:\n", instructions)
    print("\nUpdated Labels\n", labels)


    # Fifth pass: generate binary code
    print("\nGenerating Program:")
    curr_addr = 0
    for line in instructions:
        args = line.split()
        opcode, operand = args[0], args[1]

        # If the operand is a label, resolve it to its address
        if operand in labels:
            operand = labels[operand]

        instr_size = calc_instr_size(operand)
        binary_code += encode_instruction(opcode, operand, instr_size, curr_addr)
        curr_addr += instr_size

    return binary_code


def encode_instruction(opcode, operand, instr_size, curr_addr):
    """Encode an instruction into binary format."""
    encoded = b''
    op = OPCODES[opcode]
    operand = int(operand)

    if instr_size == 1:
        # One-byte Instr, Layout: `xxxx_ooo0`
        suffix = 0b0
        encoded = struct.pack('<i', (operand << 4) | (op << 1) | suffix)[0:1]
        # Debug info
        print(f"CurrAddr: {curr_addr}\tOne-Byte: xxxx_ooo0\n\tsuffix: {bin(suffix)}\n\topcode: {opcode}\t(binary): {bin(op)}\t(decimal): {op}\n\toperand: {operand}\t(binary) {bin(operand)}")
        s = str(bin(int.from_bytes(encoded, byteorder='little')))[2:]
        s = ("0"*(8-len(s))) + s
    elif instr_size == 2:
        # Two-byte Instr, Layout: `xxxx_xxxx oooo_0001`
        suffix = 0b0001
        encoded = struct.pack('<i', (operand << 8) | (op << 4) | suffix)[0:2]
        # Debug info
        print(f"CurrAddr: {curr_addr}\tTwo-Byte: xxxx_xxxx oooo_0001\n\tsuffix: {bin(suffix)}\n\topcode: {opcode}\t(binary): {bin(op)}\t(decimal): {op}\n\toperand: {operand}\t(binary) {bin(operand)}")
        s = str(bin(int.from_bytes(encoded, byteorder='little')))[2:]
        s = ("0"*(16-len(s))) + s
    elif instr_size == 3:
        # Three-byte Instr, Layout: `xxxx_xxxx xxxx_xxoo oooo_0101`
        suffix = 0b0101
        encoded = struct.pack('<i', (operand << 10) | (op << 4) | suffix)[0:3]
        # Debug info
        print(f"CurrAddr: {curr_addr}\tThree-Byte: xxxx_xxxx xxxx_xxoo oooo_0101\n\tsuffix: {bin(suffix)}\n\topcode: {opcode}\t(binary): {bin(op)}\t(decimal): {op}\n\toperand: {operand}\t(binary) {bin(operand)}")
        s = str(bin(int.from_bytes(encoded, byteorder='little')))[2:]
        s = ("0"*(24-len(s))) + s
    elif instr_size == 4:
        # Four-byte Instr, Layout: `xxxx_xxxx xxxx_xxxx xxxx_oooo oooo_1101`
        suffix = 0b1101
        encoded = struct.pack('<i', (operand << 12) | (op << 4) | suffix)
        # Debug info
        print(f"CurrAddr: {curr_addr}\tFour-Byte: xxxx_xxxx xxxx_xxxx xxxx_oooo oooo_0101\n\tsuffix: {bin(suffix)}\n\topcode: {opcode}\t(binary): {bin(op)}\t(decimal): {op}\n\toperand: {operand}\t(binary) {bin(operand)}")
        s = str(bin(int.from_bytes(encoded, byteorder='little')))[2:]
        s = ("0"*(32-len(s))) + s
    else:
        raise "Operand out of range, doesn't fit in 4 byte instruction"

    ss = ""
    for i in range(len(s)):
        if i % 4 == 0 and i != 0:
            if i % 8 == 0:
                ss += " "
            else:
                ss += "_"
        ss += s[i]
    print(f"\tbinary output: {ss}")

    return encoded

def process_line(line, lines, labels):
    line = line.split(";")[0].strip() # remove comments
    if line.startswith(';') or line == '': # skip blank lines
        return

    args = line.split()
    if len(args) == 1:
        if line.endswith(':'):
            lines.append((line[:-1], 0)) # 0 indicates it's a label
            return
        else:
            args.append("0") # add 0 operand
    opcode, operand = args[0], args[1]

    if opcode == "PUSH" and len(args) == 2:
        if operand == "SP":
            lines.append(("PUSH.R 0", 1))
        elif operand == "FP":
            lines.append(("PUSH.R 1", 1))
        elif operand == "PC":
            lines.append(("PUSH.R 2", 1))
        elif operand == "LR":
            lines.append(("PUSH.R 3", 1))
        elif operand == "ANC":
            lines.append(("PUSH.R 4", 1))
        elif operand[0:3] == "SPM":
            lines.append(("PUSH.S " + operand[3:], calc_instr_size(operand[3:])))
        else:
            try:
                numVal = int(operand)
                lines.append(("PUSH.I " + operand, calc_instr_size(operand)))
            except ValueError:
                raise "Invalid PUSH spm/special register:" + line
    elif opcode == "PUSHA" and len(args) == 3:
        if operand == "SP":
            lines.append(("PREP " + args[2], calc_instr_size(args[2])))
            lines.append(("PUSH.R 0", 1))
        elif operand == "FP":
            lines.append(("PREP " + args[2], calc_instr_size(args[2])))
            lines.append(("PUSH.R 1", 1))
        elif operand == "PC":
            lines.append(("PREP " + args[2], calc_instr_size(args[2])))
            lines.append(("PUSH.R 2", 1))
        elif operand == "LR":
            lines.append(("PREP " + args[2], calc_instr_size(args[2])))
            lines.append(("PUSH.R 3", 1))
        elif operand == "ANC":
            lines.append(("PREP " + args[2], calc_instr_size(args[2])))
            lines.append(("PUSH.R 4", 1))
        elif operand[0:3] == "SPM":
            lines.append(("PREP " + args[2], calc_instr_size(args[2])))
            lines.append(("PUSH.S " + operand[3:], calc_instr_size(operand[3:])))
        else:
            raise "Invalid PUSH spm/special register:" + line
    elif opcode == "USA" and len(args) == 2:
        lines.append(("PUSH.S " + operand, calc_instr_size(operand)))
        lines.append(("PUSH.R 4", 1))
        lines.append(("ADD 0", 1))
        lines.append(("PUSH.R 4", 1))
        lines.append(("PUSH.S " + operand, calc_instr_size(operand)))
        lines.append(("ADD 0", 1))
    # Handle normal case
    elif len(args) == 2:
        if operand in labels:
            lines.append((line, 1)) # Handle label
        else:
            lines.append((opcode + " " + operand, calc_instr_size(operand))) # Handle label
    else:
        raise "Invalid instruction:" + line

def calc_instr_size(operand):
    if type(operand) == str:
        operand = int(operand)

    if operand >= -8 and operand <= 7:
        return 1
    elif operand >= -128 and operand <= 127:
        return 2
    elif operand >= -8192 and operand <= 8191:
        return 3
    elif operand >= -524288 and operand <= 524287:
        return 4

if __name__ == "__main__":
    main()
