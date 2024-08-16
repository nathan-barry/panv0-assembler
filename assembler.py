import struct
import sys

# Opcode dictionary based on the PANv0 ISA
OPCODES = {
    # One-byte instructions (3-bit opcode)
    "PUSH.RL":  0b001,
    "PUSH.RA":  0b010,
    "PUSH.SL":  0b011,
    "PUSH.SA":  0b100,
    "ADD":      0b101,
    "JUMP.ABS": 0b111,

    # Two-byte instructions (4-bit opcode)
    "PUSH.IL":  0b0001,
    "PUSH.IA":  0b0010,

    # Three-byte instructions (4-bit opcode)
    "JUMP":     0b0011,
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
    print(binary_code)
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

    print(instructions)

    # Second pass: generate binary code
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
        print("One-Byte:", operand, "(", opcode,":", bin(op), ")", bin(suffix))
        encoded = struct.pack('b', (operand << 4) | (op << 1) | suffix)

    # Two-byte instructions
    elif opcode in {"PUSH.IL", "PUSH.IA"}:
        # Layout: `xxxx_xxxx oooo_0001`
        suffix = 0b0001
        print("Two-Byte:", operand, "(", opcode,":", bin(op), ")", bin(suffix))
        encoded = struct.pack('<h', (operand << 8) | (op << 4) | suffix)

    # Three-byte instructions
    elif opcode == "JUMP":
        # Layout: `xxxx_xxxx xxxx_oooo oooo_0101`
        suffix = 0b0101
        offset = current_address + operand
        print("Three-Byte:", operand, "(", opcode,":", bin(op), ")", bin(suffix))
        encoded = struct.pack('<i', (offset << 12) | (op << 4) | suffix)

    print("\t", bin(int.from_bytes(encoded, byteorder='little')))

    return encoded



if __name__ == "__main__":
    main()
