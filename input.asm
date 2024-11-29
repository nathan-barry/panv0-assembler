;
;  int sum(int size, int* arr) {
;    int total = 0;
;    for(int i = 0; i < size; i++) {
;      total += arr[i];
;    }
;    return total;`
;  }
;
;  int main() {
;    int arr[5] = {40, 0, 7, -500, 3000};
;    sum(arr, 5);
;  }
;

_start:
	; Make space for arr
	PUSH SP
	PUSH SP
	PUSH -20
	ADD

	; Init SPM0 as *arr
	PUSH SPM0
	PUSH SP
	ADD
	; Init SPM1 as our iterator
	PUSH SPM1
	PUSH SPM0
	ADD

	; Fill array
	; arr[0]
	PUSHA SPM1 4 ; dst is 4 B
	PUSH 40
	ADD          ; write is auto
	PUSH SPM1
	PUSH SPM1
	PUSH 4
	ADD
	; arr[1]
	PUSHA SPM1 4
	PUSH 0
	ADD
	PUSH SPM1
	PUSH SPM1
	PUSH 4
	ADD
	; arr[2]
	PUSHA SPM1 4
	PUSH 7
	ADD
	PUSH SPM1
	PUSH SPM1
	PUSH 4
	ADD
	; arr[3]
	PUSHA SPM1 4
	PUSH -500
	ADD
	PUSH SPM1
	PUSH SPM1
	PUSH 4
	ADD
	; arr[4]
	PUSHA SPM1 4
	PUSH 3000
	ADD

	; Pre call preparation (insn 47)
	PUSH SPM1
	PUSH SPM0
	ADD ; SPM1 = arr
	PUSH SPM0
	PUSH 5
	ADD ; SPM0 = size
	PUSH ANC
	PUSH 2
	ADD

sum:
	; Args in SPM regs
	; SPM-2: int size
	; SPM-1: int arr[]

	; SP -= 8 (insn 56)
	PUSH SP   ; dst = r0 = SP
	PUSH SP   ; op1 = r0 = SP
	PUSH -8  ; op2 = -8
	ADD       ; Unsized add

	; total = 0 (referenced via sp) (insn 60)
	PUSHA SP 4  ; dst = *r0 = *SP
	ADD         ; writes 0s

	; Init SPM0 as &i (sp + 4) (insn 63)
	PUSH SPM0 ; dst = SPM0
	PUSH SP   ; op1 = r0 = SP
	PUSH 4    ; op2 = 4
	ADD       ;  Add
	; i = 0 (cycle 67)
	PUSHA SPM0 4 ; dst = *SPM0 = i
	ADD 0       ; 4B Add


.loop_begin:

	; The guard - exit loop if i > size (cycle 70)
	PUSH 2   ; cond = 2 = LTE
	PUSH.S -2   ; op1 = SPM-2 = size
	PUSHA SPM0 4  ; op2 = SPM0 = i
	JUMP .loop_end     ; offset factors size of self.

	; SPM1 = arr+i
	PUSH SPM1   ; dst = SPM1
	PUSH SPM-1  ; op1 = SPM-1 = arr
	PUSHA SPM0 4 ; op2 = SPM0 = i
	PUSH 2      ; shift = 2
	ADD         ; 4B Add
	; total += *(SPM1)
	PUSHA SP 4  ; dst = *r0 = *SP
	PUSHA SP 4  ; op1 = *r0 = *SP
	PUSHA SPM1 4 ; op2 = SPM1 = *(arr+i)`
	ADD 4       ; 4B Add
	; i ++
	PUSHA SPM0 4 ; dst = SPM0 = i
	PUSHA SPM0 4 ; op1 = SPM0 = i
	PUSH 1   ; op2 = 1
	ADD
	JUMP .loop_begin    ; to .loop_begin

.loop_end:
	; SP += 8
	; PUSH.R 0   ; dst = r0 = SP
	; PUSH.R 0   ; op1 = r0 = SP
	; PUSH.I 8   ; op2 = 8
	; ADD 0       ; Unsized add

	; return
	PUSH.R 2   ; target = r2 = LR
	JUMP.ABS 3  ; TODO: Is this 3 (LE)?
