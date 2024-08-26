;
;  int sum(int size, int* arr) {
;    int total = 0;
;    for(int i = 0; i < size; i++) {
;      total += arr[i];
;    }
;    return total;`
;  }
;

sum:
	; Args in SPM regs
	; SPM-2: int size
	; SPM-1: int arr[]

	; SP -= 8
	PUSH SP   ; dst = r0 = SP
	PUSH SP   ; op1 = r0 = SP
	PUSH.I -8  ; op2 = -8
	ADD 0       ; Unsized add

	; total = 0
	PUSHA SP 1  ; dst = *r0 = *SP
	ADD 0       ; Unsized add

	; SPM0 = &i
	PUSH SPM0   ; dst = SPM0
	PUSH SP   ; op1 = r0 = SP
	PUSH.I 4   ; op2 = 4
	ADD 4       ; 4B Add
	; i = 0
	PREP 1
	PUSH.S 0   ; dst = *SPM0 = i
	ADD 4       ; 4B Add

	; exit loop if i > size
	PUSH.I 2   ; cond = 2 = LTE
	PUSH.S -2  ; op1 = SPM-2 = size
	PUSH.S 0   ; op2 = SPM0 = i
	JUMP 17     ; to .loop_end

.loop_begin:
	; SPM1 = arr+i
	PUSH.S 1   ; dst = SPM1
	PUSH.S -1  ; op1 = SPM-1 = arr
	PUSH.S 0   ; op2 = SPM0 = i
	PUSH.I 2   ; shift = 2
	ADD 4       ; 4B Add
	; total += *(SPM1)
	PREP 1
	PUSH.R 0   ; dst = *r0 = *SP
	PREP 1
	PUSH.R 0   ; op1 = *r0 = *SP
	PREP 1
	PUSH.S 1   ; op2 = SPM1 = *(arr+i)
	ADD 4       ; 4B Add
	; i ++
	PREP 1
	PUSH.S 0   ; dst = SPM0 = i
	PREP 1
	PUSH.S 0   ; op1 = SPM0 = i
	PUSH.I 1   ; op2 = 1
	ADD 4
	JUMP -15    ; to .loop_begin
	.loop_end:
	; SP += 8
	PUSH.R 0   ; dst = r0 = SP
	PUSH.R 0   ; op1 = r0 = SP
	PUSH.I 8   ; op2 = 8
	ADD 0       ; Unsized add
	; return
	PUSH.R 0   ; target = r0 = SP
	JUMP.ABS 3  ; TODO: Is this 3 (LE)?
