FBEG 42
IFNIL r1 ret1
ASSIGN r2 1
SUB r1 r2
IFNIL r1 ret1
PUSHREG r1
CALL 42
TOP r1
POP
ASSIGN r2 1
SUB r1 r2
PUSHREG r6
CALL 42
TOP r5
POP
ADD r6 r5
JUMP finish
ret1: ASSIGN r6 1
finish: FEND
PUTSTR Эта программа возвращает n-й элемент последовательности Фибоначчи!
PUTSTR Введите число n:
READ r1
CALL 42
PUTSTR Результат:
PRINT r6
STOP