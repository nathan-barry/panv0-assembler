run:
	clear && python3 assembler.py input.asm output.bin && echo "\nxxd -b output.bin" && xxd -b output.bin
