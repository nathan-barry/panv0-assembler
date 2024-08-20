run:
	clear && python3 assembler.py input.asm output.bin

check:
	xxd -b output.bin

