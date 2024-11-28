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
	; 0x5: Init SPM0 as *arr
	PUSHA SPM0 4
	PUSH SP
	ADD

	; 0x9: Init SPM1 as our iterator
	PUSHA SPM1 4
	PUSH SPM0
	ADD

	; Fill array
	; arr[0]
	PUSHA SPM1 4
	PUSH 40
	ADD
	PUSH SPM1
	PUSH 4
	ADD
	; arr[1]
	PUSHA SPM1 4
	PUSH 0
	ADD
	PUSH SPM1
	PUSH 4
	ADD
	; arr[2]
	PUSHA SPM1 4
	PUSH 7
	ADD
	PUSH SPM1
	PUSH 4
	ADD
	; arr[3]
	PUSHA SPM1 4
	PUSH -500
	ADD
	PUSH SPM1
	PUSH 4
	ADD
	; arr[4]
	PUSHA SPM1 4
	PUSH 3000
	ADD

	; Set up args for call to sum
	; SPM0 is already the address of the array
	PUSH SPM1
	PUSH 5
	ADD
	PUSH SPM2 ; 0x35: Init SPM2
	ADD 4
	PUSH.R 4
	PUSH 2
	ADD
	; USA 2 ;addr 0x3f

sum:
	; Args in SPM regs
	; SPM-2: int size
	; SPM-1: int arr[]
	; Others:
	; SPM0: return int [aka. total]
	; *SP  = total
	; SPM1: (int*)&i
	; SPM2: (int*)(arr+i)

	; SP -= 8
	PUSH SP   ; dst = r0 = SP
	PUSH SP   ; op1 = r0 = SP
	PUSH -8  ; op2 = -8
	ADD       ; Unsized add

	; total = 0
	PUSHA SP 4  ; dst = *r0 = *SP
	ADD 0       ; Unsized add

	; Init SPM1 as &i
	PUSHA SPM1 4  ; dst = SPM1
	PUSH SP   ; op1 = r0 = SP
	PUSH 4   ; op2 = 4
	ADD
	; i = 0
	PUSHA SPM1 4 ; dst = *SPM1 = i
	ADD

	; exit loop if i > size
	PUSH 2   ; cond = 2 = LTE
	PUSH SPM-2   ; op1 = SPM-2 = size
	PUSHA SPM1 4  ; op2 = SPM1 = i
	JUMP 26     ; to .loop_end. factors size of self.

	PUSHA SPM2 4 ; Init SPM2 (int*)(arr+i) before loop start.
	ADD
.loop_begin:
	; SPM2 = arr+i
	PUSH SPM2  ; dst = SPM2
	PUSH SPM-1  ; op1 = SPM2-1 = arr
	PUSHA SPM1 4  ; op2 = SPM0 = i
	PUSH 2   ; shift = 2
	ADD       ; Unsized Add
	; total += *(SPM1)
	PUSHA SP 4  ; dst = *r0 = *SP = total
	PUSHA SP 4   ; op1 = *r0 = *SP = total
	PUSHA SPM2 4  ; op2 = SPM1 = *(arr+i)
	ADD 4       ; 4B Add
	; i ++
	PUSHA SPM1 4   ; dst = SPM0 = i
	PUSHA SPM1 4   ; op1 = SPM0 = i
	PUSH 1   ; op2 = 1
	ADD 4
	JUMP -19    ; to .loop_begin
.loop_end:
	; Prep for return
	PUSH SPM0
	PUSHA SP 4
	ADD
	; SP += 8
	PUSH SP   ; dst = r0 = SP
	PUSH SP    ; op1 = r0 = SP
	PUSH 8   ; op2 = 8
	ADD 0       ; Unsized add
	; return
	PUSH LR   ; target = r2 = LR
	JUMP.ABS 3  ; TODO: Is this 3 (LE)?
