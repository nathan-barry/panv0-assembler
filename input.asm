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
;    int arr[5] = {1, 2, 3, 4, 5};
;    sum(arr, 5);
;  }
;

main:
	; Make space for arr
	PUSH SP
	PUSH SP
	PUSH -20
	ADD
	;Init SPM0 as *arr
	PUSHA SPM-1 4
	PUSH SP
	ADD
	

sum:
	; Args in SPM regs
	; SPM-2: int size
	; SPM-1: int arr[]

	; SP -= 8
	PUSH SP   ; dst = r0 = SP
	PUSH SP   ; op1 = r0 = SP
	PUSH -8  ; op2 = -8
	ADD 0       ; Unsized add

	; total = 0
	PUSHA SP 4  ; dst = *r0 = *SP
	ADD 0       ; Unsized add

	; Init SPM0 as &i
	PUSHA SPM0 4  ; dst = SPM0
	PUSH SP   ; op1 = r0 = SP
	PUSH 4   ; op2 = 4
	ADD 0       ; 4B Add
	; i = 0
	PUSHA SPM0 4 ; dst = *SPM0 = i
	ADD 0       ; 4B Add

	; exit loop if i > size
	PUSH 2   ; cond = 2 = LTE
	PUSH.S -2   ; op1 = SPM-2 = size
	PUSHA SPM0 4  ; op2 = SPM0 = i
	JUMP 22     ; to .loop_end. factors size of self.

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
	PUSH.R 2   ; target = r2 = LR
	JUMP.ABS 3  ; TODO: Is this 3 (LE)?
