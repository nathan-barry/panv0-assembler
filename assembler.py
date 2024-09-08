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
    instructions = []
    current_address = 0

    # First pass: resolve labels
    for line in asm_code:
        line = line.split(";")[0].strip() # remove comments
        if line.startswith(';') or line == '': # skip blank lines
            continue

        if line.endswith(':'):
            labels[line[:-1]] = current_address
        else:
            opcode = line.split()[0]
            instruction_length = 1  # Default length is 1 byte

            # Adjust length based on opcode
            if opcode in {"PUSH.IL", "PUSH.IA"}:
                instruction_length = 2
            elif opcode == "JUMP":
                instruction_length = 3

            instructions.append(line)
            current_address += instruction_length

    print("Instructions:\n", instructions)

    # Second pass: generate binary code
    print("\nGenerating Program:")
    for line in instructions:
        args = line.split()
        if len(args) == 1:
            args.append("0")
        opcode, operand = args[0], args[1]
        # If the operand is a label, resolve it to its address
        if operand in labels:
            operand = labels[operand]

        # Handle pseudo-opcodes 
        if opcode == "PUSH" and len(args) == 2:
            if operand == "SP":
                encoded_instruction = encode_instruction("PUSH.R", "0", current_address)
            elif operand == "FP":
                encoded_instruction = encode_instruction("PUSH.R", "1", current_address)
            elif operand == "PC":
                encoded_instruction = encode_instruction("PUSH.R", "2", current_address)
            elif operand == "LR":
                encoded_instruction = encode_instruction("PUSH.R", "3", current_address)
            elif operand == "ANC":
                encoded_instruction = encode_instruction("PUSH.R", "4", current_address)
            elif operand[0:3] == "SPM":
                encoded_instruction = encode_instruction("PUSH.S", operand[3:], current_address)
            else:
                try:
                    numVal = int(operand)
                    encoded_instruction = encode_instruction("PUSH.I", operand, current_address)
                except ValueError:
                    raise "Invalid PUSH spm/special register:" + line
        elif opcode == "PUSHA" and len(args) == 3:
            if operand == "SP":
                encoded_instruction = encode_instruction("PREP", args[2], current_address)
                binary_code += encoded_instruction
                current_address += len(encoded_instruction)

                encoded_instruction = encode_instruction("PUSH.R", "0", current_address)
            elif operand == "FP":
                encoded_instruction = encode_instruction("PREP", args[2], current_address)
                binary_code += encoded_instruction
                current_address += len(encoded_instruction)

                encoded_instruction = encode_instruction("PUSH.R", "1", current_address)
            elif operand == "PC":
                encoded_instruction = encode_instruction("PREP", args[2], current_address)
                binary_code += encoded_instruction
                current_address += len(encoded_instruction)

                encoded_instruction = encode_instruction("PUSH.R", "2", current_address)
            elif operand == "LR":
                encoded_instruction = encode_instruction("PREP", args[2], current_address)
                binary_code += encoded_instruction
                current_address += len(encoded_instruction)

                encoded_instruction = encode_instruction("PUSH.R", "3", current_address)
            elif operand[0:3] == "SPM":
                encoded_instruction = encode_instruction("PREP", args[2], current_address)
                binary_code += encoded_instruction
                current_address += len(encoded_instruction)

                encoded_instruction = encode_instruction("PUSH.S", operand[3:], current_address)
            else:
                raise "Invalid PUSH spm/special register:" + line
        elif opcode == "USA" and len(args) == 2:
            encoded_instruction = encode_instruction("PUSH.S", operand, current_address)
            binary_code += encoded_instruction
            current_address += len(encoded_instruction)
            encoded_instruction = encode_instruction("PUSH.R", "4", current_address) # ANC
            binary_code += encoded_instruction
            current_address += len(encoded_instruction)
            encoded_instruction = encode_instruction("ADD", "0", current_address)
            binary_code += encoded_instruction
            current_address += len(encoded_instruction)
            encoded_instruction = encode_instruction("PUSH.R", "4", current_address)
            binary_code += encoded_instruction
            current_address += len(encoded_instruction)
            encoded_instruction = encode_instruction("PUSH.S", operand, current_address) # ANC
            binary_code += encoded_instruction
            current_address += len(encoded_instruction)
            encoded_instruction = encode_instruction("ADD", "0", current_address)
            binary_code += encoded_instruction
            current_address += len(encoded_instruction)

        elif len(args) == 2:
            # Handle normal case
            encoded_instruction = encode_instruction(opcode, operand, current_address)
        else:
            raise "Invalid instruction:" + line

        binary_code += encoded_instruction
        current_address += len(encoded_instruction)

    return binary_code


def encode_instruction(opcode, operand, current_address):
    """Encode an instruction into binary format."""
    encoded = b''
    op = OPCODES[opcode]
    operand = int(operand)


    if operand >= -8 and operand <= 7:
        # One-byte Instr, Layout: `xxxx_ooo0`
        suffix = 0b0
        encoded = struct.pack('<i', (operand << 4) | (op << 1) | suffix)[0:1]
        # Debug info
        print(f"One-Byte: xxxx_ooo0\n\tsuffix: {bin(suffix)}\n\topcode: {opcode}\t(binary): {bin(op)}\t(decimal): {op}\n\toperand: {operand}\t(binary) {bin(operand)}")
        s = str(bin(int.from_bytes(encoded, byteorder='little')))[2:]
        s = ("0"*(8-len(s))) + s
    elif operand >= -128 and operand <= 127:
        # Two-byte Instr, Layout: `xxxx_xxxx oooo_0001`
        suffix = 0b0001
        encoded = struct.pack('<i', (operand << 8) | (op << 4) | suffix)[0:2]
        # Debug info
        print(f"Two-Byte: xxxx_xxxx oooo_0001\n\tsuffix: {bin(suffix)}\n\topcode: {opcode}\t(binary): {bin(op)}\t(decimal): {op}\n\toperand: {operand}\t(binary) {bin(operand)}")
        s = str(bin(int.from_bytes(encoded, byteorder='little')))[2:]
        s = ("0"*(16-len(s))) + s
    elif operand >= -8192 and operand <= 8191:
        # Three-byte Instr, Layout: `xxxx_xxxx xxxx_xxoo oooo_0101`
        suffix = 0b0101
        offset = current_address + operand
        encoded = struct.pack('<i', (offset << 10) | (op << 4) | suffix)[0:3]
        # Debug info
        print(f"Three-Byte: xxxx_xxxx xxxx_xxoo oooo_0101\n\tsuffix: {bin(suffix)}\n\topcode: {opcode}\t(binary): {bin(op)}\t(decimal): {op}\n\toperand: {operand}\t(binary) {bin(operand)}")
        s = str(bin(int.from_bytes(encoded, byteorder='little')))[2:]
        s = ("0"*(24-len(s))) + s
    elif operand >= -524288 and operand <= 524287:
        # Four-byte Instr, Layout: `xxxx_xxxx xxxx_xxxx xxxx_oooo oooo_1101`
        suffix = 0b1101
        offset = current_address + operand
        encoded = struct.pack('<i', (offset << 12) | (op << 4) | suffix)
        # Debug info
        print(f"Four-Byte: xxxx_xxxx xxxx_xxxx xxxx_oooo oooo_0101\n\tsuffix: {bin(suffix)}\n\topcode: {opcode}\t(binary): {bin(op)}\t(decimal): {op}\n\toperand: {operand}\t(binary) {bin(operand)}")
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


if __name__ == "__main__":
    main()
