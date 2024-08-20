import struct
import sys

# Opcode dictionary based on the PANv0 ISA
OPCODES = {
    # One-byte instructions (3-bit opcode)
    "PUSH.RL":  0b_001,
    "PUSH.RA":  0b_010,
    "PUSH.SL":  0b_011,
    "PUSH.SA":  0b_100,
    "ADD":      0b_101,
    "JUMP.ABS": 0b_111,

    # Two-byte instructions (4-bit opcode)
    "PUSH.IL":  0b_0001,
    "PUSH.IA":  0b_0010,

    # Three-byte instructions (8-bit opcode)
    "JUMP":     0b_0000_0011,
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
    print(f"\nOutput Binary:\n{ss}")
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
        opcode, operand = line.split()
        # If the operand is a label, resolve it to its address
        if operand in labels:
            operand = labels[operand]

        encoded_instruction = encode_instruction(opcode, operand, current_address)
        binary_code += encoded_instruction
        current_address += len(encoded_instruction)

    return binary_code


def encode_instruction(opcode, operand, current_address):
    """Encode an instruction into binary format."""
    encoded = b''
    op = OPCODES[opcode]
    operand = int(operand)

    # One-byte instructions
    if opcode in {"PUSH.RL", "PUSH.RA", "PUSH.SL", "PUSH.SA", "ADD", "JUMP.ABS"}:
        # Layout: `xxxx_ooo0`
        suffix = 0b0
        encoded = struct.pack('b', (operand << 4) | (op << 1) | suffix)
        # Debug info
        print(f"One-Byte: xxxx_ooo0\n\tsuffix: {bin(suffix)}\n\topcode: {opcode}\t(binary): {bin(op)}\n\toperand: {operand}\t(binary) {bin(operand)}")
        s = str(bin(int.from_bytes(encoded, byteorder='little')))[2:]
        s = ("0"*(8-len(s))) + s

    # Two-byte instructions
    elif opcode in {"PUSH.IL", "PUSH.IA"}:
        # Layout: `xxxx_xxxx oooo_0001`
        suffix = 0b0001
        encoded = struct.pack('<h', (operand << 8) | (op << 4) | suffix)
        # Debug info
        print(f"Two-Byte: xxxx_xxxx oooo_0001\n\tsuffix: {bin(suffix)}\n\topcode: {opcode}\t(binary): {bin(op)}\n\toperand: {operand}\t(binary) {bin(operand)}")
        s = str(bin(int.from_bytes(encoded, byteorder='little')))[2:]
        s = ("0"*(16-len(s))) + s

    # Three-byte instructions
    elif opcode == "JUMP":
        # Layout: `xxxx_xxxx xxxx_oooo oooo_0101`
        suffix = 0b0101
        offset = current_address + operand
        encoded = struct.pack('<i', (offset << 12) | (op << 4) | suffix)[0:3]
        # Debug info
        print(f"Three-Byte: xxxx_xxxx xxxx_oooo oooo_0101\n\tsuffix: {bin(suffix)}\n\topcode: {opcode}\t(binary): {bin(op)}\n\toperand: {operand}\t(binary) {bin(operand)}")
        s = str(bin(int.from_bytes(encoded, byteorder='little')))[2:]
        s = ("0"*(24-len(s))) + s

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
