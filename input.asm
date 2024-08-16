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
	PUSH.RL 0   ; dst = r0 = SP
	PUSH.RL 0   ; op1 = r0 = SP
	PUSH.IL -8  ; op2 = -8
	ADD 0       ; Unsized add

	; total = 0
	PUSH.RA 0   ; dst = *r0 = *SP
	ADD 0       ; Unsized add

	; SPM0 = &i
	PUSH.SL 0   ; dst = SPM0
	PUSH.RL 0   ; op1 = r0 = SP
	PUSH.IL 4   ; op2 = 4
	ADD 4       ; 4B Add
	; i = 0
	PUSH.SA 0   ; dst = *SPM0 = i
	ADD 4       ; 4B Add

	; exit loop if i > size
	PUSH.IL 2   ; cond = 2 = LTE
	PUSH.SL -2  ; op1 = SPM-2 = size
	PUSH.SL 0   ; op2 = SPM0 = i
	JUMP 17     ; to .loop_end

.loop_begin:
	; SPM1 = arr+i
	PUSH.SL 1   ; dst = SPM1
	PUSH.SL -1  ; op1 = SPM-1 = arr
	PUSH.SL 0   ; op2 = SPM0 = i
	PUSH.IL 2   ; shift = 2
	ADD 4       ; 4B Add
	; total += *(SPM1)
	PUSH.RA 0   ; dst = *r0 = *SP
	PUSH.RA 0   ; op1 = *r0 = *SP
	PUSH.SA 1   ; op2 = SPM1 = *(arr+i)
	ADD 4       ; 4B Add
	; i ++
	PUSH.SA 0   ; dst = SPM0 = i
	PUSH.SA 0   ; op1 = SPM0 = i
	PUSH.IL 1   ; op2 = 1
	ADD 4
	JUMP -15    ; to .loop_begin
	.loop_end:
	; SP += 8
	PUSH.RL 0   ; dst = r0 = SP
	PUSH.RL 0   ; op1 = r0 = SP
	PUSH.IL 8   ; op2 = 8
	ADD 0       ; Unsized add
	; return
	PUSH.RL 0   ; target = r0 = SP
	JUMP.ABS 3  ; TODO: Is this 3 (LE)?
