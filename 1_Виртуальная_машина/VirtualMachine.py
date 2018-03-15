import numpy as np
import sys

REGISTERS_COUNT = 9 
IP_ADDRESS = 0  # instructions pointer
SP_ADDRESS = 1  # stack pointer

# количество ячеек, выделенных для хранения информации об адресах первых инструкций функций
# [имя, адрес, имя, адрес,...]
FUNC_START_ADDR_SIZE = 10

INSTRUCTION_SIZE = 3  # количество ячеек, занимаемое одной инструкцией

INSTRUCTIONS_DICT = {'MOV':0, 'ADD':1, 'JUMP':2, 'STOP':3, 'READ':4, 'PRINT':5, 'FBEG':6, 'FEND':7, 'PUSH':8, 'POP':9, 'CALL':10, 'TOP':11, 'SUB':12, 'ASSIGN':13, 'IFNIL':14, 'PUSHREG':15, 'PUTC':16}

class VirtualMachine:
    
    def __init__(self, size):
        self.memory = np.zeros(size, dtype=np.int)
        # первые ячейки памяти выделены для регистров и адресов первых инструкций функций
        self.memory[IP_ADDRESS] = REGISTERS_COUNT + FUNC_START_ADDR_SIZE
        # стек начинается в последней ячейке памяти и растёт к началу выделенного участка
        self.memory[SP_ADDRESS] = size - 1 
        
        # Для поддержки функций 
        
        # Хранит адрес первой инструкции функции с числовым названием (ключ)
        #self.func_start_address = {}
        # флаг, отвечающий за считывание объявления функции
        #self.func_prototype_reading = False 
        # в последнем регистре - флаг, отвечющй за считывание объявления функции func_prototype_reading
        self.memory[REGISTERS_COUNT - 1] = 0  
    
    
    # Работа с отдельными ячейками памяти
    
    def read_from_address(self, address):
        return self.memory[address]
    
    def write_value_to_address(self, address, value):
        self.memory[address] = value
        
    
    # Считывание программы из входного numpy массива / обычного массива
    # программа содержит только инструкции - записываются прямо за регистрами
    
    def read_program_from_array(self, program):
        self.func_start_address = {}
        self.func_prototype_reading = False 
        
        for code_idx in range(len(program)):
            self.memory[REGISTERS_COUNT + FUNC_START_ADDR_SIZE + code_idx] = program[code_idx]
    
    def read_program_from_file(self, filename):
        with open(filename) as f:
            program_str = f.readlines()
        program_line = program_str[0]
        program_line = program_line.split()
        program = [int(num) for num in program_line]
        
        self.read_program_from_array(program)
            
    
    # Работа с инструкциями
    
    # переход к следующей инструкции
    def move_to_next_instruction(self):
        self.write_value_to_address(IP_ADDRESS, self.read_from_address(IP_ADDRESS) + INSTRUCTION_SIZE)
        
    def get_instruction_value(self, address):
        return self.memory[address:address + INSTRUCTION_SIZE]
    
    def get_instruction_id(self, instruction_name):
        return INSTRUCTIONS_DICT[instruction_name]
    
    
    def mov(self, dest_addr, src_addr):
        """
        копирование данных из регистра номер src_addr в регистр номер dest_addr
        Инструкция записывается: [1, dest_addr, src_addr]
        """
        data = self.read_from_address(src_addr)
        self.write_value_to_address(dest_addr, data)
        self.move_to_next_instruction()
        
    def add(self, dest_addr, addition_addr):
        """
        добавление данных из регистра номер addition_addr к данным из регистра dest_addr
        Инструкция записывается: [1, dest_addr, addition_addr]
        """
        addition_value = self.read_from_address(addition_addr)
        dest_value = self.read_from_address(dest_addr)
        
        self.write_value_to_address(dest_addr, dest_value + addition_value)
        self.move_to_next_instruction()
        
    def jump(self, dest_addr):
        """
        instruction_pointer перемещается на адрес dest_addr
        Инструкция записывается: [2, 0, dest_addr]
        """
        self.write_value_to_address(IP_ADDRESS, dest_addr)
        
    def read(self, dest_addr):
        """
        dest_addr - номер регистра, в который будет записано считанное число
        Инструкция записывается: [4, 0, dest_addr]
        """
        value = int(input())
        self.write_value_to_address(dest_addr, value)
        self.move_to_next_instruction() 
        
    def print_reg(self, reg_addr):
        """
        reg_addr - номер регистра, содержимое которого необходимо вывести на экран
        Инструкция записывается: [5, 0, reg_addr]
        """
        print(self.read_from_address(reg_addr))
        self.move_to_next_instruction()
        
    def function_begin(self, name_num):
        """
        принимает числовое "имя" функции
        Инструкция записывается: [6, 0, name_num]
        """
        self.write_value_to_address(REGISTERS_COUNT - 1, 1)
        
        # индекс, начиная с которого ещё нет записей об именах функций
        index_to_write = list(self.memory[REGISTERS_COUNT : REGISTERS_COUNT + FUNC_START_ADDR_SIZE]).index(0)
        index_to_write = index_to_write + REGISTERS_COUNT
        self.write_value_to_address(index_to_write, name_num)
        self.write_value_to_address(index_to_write + 1, self.read_from_address(IP_ADDRESS) + INSTRUCTION_SIZE)
        
        self.move_to_next_instruction()
        
    def function_end(self):
        """
        Определяет окончание определеня функции
        Инструкция записывается: [7, 0, 0]
        """
        if self.read_from_address(REGISTERS_COUNT - 1) == 1:
            self.write_value_to_address(REGISTERS_COUNT - 1, 0)
            self.move_to_next_instruction()
        else:  # это было не определение функции, а вызов
            # Выходим из функции - переход на следующую инструкцию, адрес которой лежит в стеке
            self.write_value_to_address(IP_ADDRESS, self.read_from_address(self.read_from_address(SP_ADDRESS) + 1))
            self.pop()
        
    def push(self, value, is_move_to_next_instruction=False):
        """
        Кладёт на стек число value
        Инструкция записывается: [8, 0, value]
        """
        self.write_value_to_address(self.read_from_address(SP_ADDRESS), value)
        self.write_value_to_address(SP_ADDRESS, self.read_from_address(SP_ADDRESS) - 1)
        if is_move_to_next_instruction:
            self.move_to_next_instruction()
    
    def pop(self, is_move_to_next_instruction=False):
        """
        "Удаляет" верхнее значение со стека (увеличивает stack pointer)
        Инструкция записывается: [9, 0, 0]
        """
        self.write_value_to_address(SP_ADDRESS, self.read_from_address(SP_ADDRESS) + 1)
        if is_move_to_next_instruction:
            self.move_to_next_instruction()
        
    def call(self, name_num):
        """
        Вызывает функцию с числовым именем name_num
        Инструкция записывается: [10, 0, name_num]
        """
        # Кладём в стек адрес следующей за вызовом функции инструкции
        self.push(self.read_from_address(IP_ADDRESS) + INSTRUCTION_SIZE)
        
        # Нужно найти адрес, с которого начинается вызов функции
        func_start_addresses = self.memory[REGISTERS_COUNT : REGISTERS_COUNT + FUNC_START_ADDR_SIZE]
        
        for i in range(len(func_start_addresses)):
            if i % 2 == 0:
                # сравниваем значение в ячейке с требуемым именем
                if self.read_from_address(i + REGISTERS_COUNT) == name_num:
                    self.write_value_to_address(IP_ADDRESS, func_start_addresses[i + 1])
        
    def top(self, reg_addr):
        """
        Копирует информацию, записанную в верхушке стека, в регистр reg_addr
        Инструкция записывается: [11, 0, reg_addr]
        """
        self.write_value_to_address(reg_addr, self.read_from_address(self.read_from_address(SP_ADDRESS) + 1))
        self.move_to_next_instruction()
        
    def sub(self, dest_addr, subtract_addr):
        """
        Вычитает значение, лежащее в subtract_addr из dest_addr
        Инструкция записывается: [12, dest_addr, subtract_addr]
        """
        subtract_value = self.read_from_address(subtract_addr)
        dest_value = self.read_from_address(dest_addr)
        
        self.write_value_to_address(dest_addr, dest_value - subtract_value)
        self.move_to_next_instruction()
        
    def assign(self, dest_addr, value):
        """
        Записывает в ячейку с адресом dest_addr значение value
        Инструкция записывается: [13, dest_addr, value]
        """
        self.write_value_to_address(dest_addr, value)
        self.move_to_next_instruction()
        
    def ifnil(self, reg_addr, jump_addr):
        """
        Если значение, лежащее по адресу reg_addr равно нулю, переносит IP на адрес jump_addr
        Иначе - просто переходит на следующую инструкцию
        Инструкция записывается: [14, reg_addr, jump_addr]
        """
        reg_value = self.read_from_address(reg_addr)
        if reg_value == 0:
            self.jump(jump_addr)
        else:
            self.move_to_next_instruction()
            
    def push_reg(self, reg_addr):
        """
        Кладёт на стек значение, лежащее по адресу reg_addr
        Инструкция записывается: [15, 0, reg_addr]
        """
        reg_value = self.read_from_address(reg_addr)
        self.push(reg_value, is_move_to_next_instruction=True)
        
    def put_char(self, char_num):
        """
        Выводит на экран символ, соответствующий числу char_num
        Инструкция записывается: [16, 0, char_num]
        """
        print(chr(char_num), end='')
        self.move_to_next_instruction()
        
        
    # Интерпретация команд
    
    def interpret_current_comand(self):
        """
        интерпретирует команду, на которую указывает IP
        returns: True, если нужно продолжать выполнение
                 False, если выполнение программы необходимо прекратить
        """
        instruction_value = self.get_instruction_value(self.read_from_address(IP_ADDRESS))
        #print(instruction_value)
        
        instruction_id = instruction_value[0]
        arg_first = instruction_value[1]
        arg_second = instruction_value[2]
        
        # Если сейчас считываем определение функции, ничего выполнять не нужно, просто переходим дальше
        func_prototype_reading = self.read_from_address(REGISTERS_COUNT - 1)
        if func_prototype_reading and not instruction_id == INSTRUCTIONS_DICT['FEND']:
            self.move_to_next_instruction()
            return True
        
        if instruction_id == INSTRUCTIONS_DICT['MOV']:  # 0
            self.mov(arg_first, arg_second)
            return True
        
        if instruction_id == INSTRUCTIONS_DICT['ADD']:  # 1
            self.add(arg_first, arg_second)
            return True
        
        if instruction_id == INSTRUCTIONS_DICT['JUMP']:  # 2
            self.jump(arg_second)
            return True
        
        if instruction_id == INSTRUCTIONS_DICT['STOP']:  # 3
            return False
        
        if instruction_id == INSTRUCTIONS_DICT['READ']:  # 4
            self.read(arg_second)
            return True
        
        if instruction_id == INSTRUCTIONS_DICT['PRINT']:  # 5
            self.print_reg(arg_second)
            return True
        
        if instruction_id == INSTRUCTIONS_DICT['FBEG']:  # 6
            self.function_begin(arg_second)
            return True
        
        if instruction_id == INSTRUCTIONS_DICT['FEND']:  # 7
            self.function_end()
            return True 
        
        if instruction_id == INSTRUCTIONS_DICT['PUSH']:  # 8
            self.push(arg_second, is_move_to_next_instruction=True)
            return True
        
        if instruction_id == INSTRUCTIONS_DICT['POP']:  # 9
            self.pop(is_move_to_next_instruction=True)
            return True
        
        if instruction_id == INSTRUCTIONS_DICT['CALL']:  # 10
            self.call(arg_second)
            return True
        
        if instruction_id == INSTRUCTIONS_DICT['TOP']:  # 11
            self.top(arg_second)
            return True
        
        if instruction_id == INSTRUCTIONS_DICT['SUB']:  # 12
            self.sub(arg_first, arg_second)
            return True
        
        if instruction_id == INSTRUCTIONS_DICT['ASSIGN']:  # 13
            self.assign(arg_first, arg_second)
            return True
        
        if instruction_id == INSTRUCTIONS_DICT['IFNIL']:  # 14
            self.ifnil(arg_first, arg_second)
            return True
        
        if instruction_id == INSTRUCTIONS_DICT['PUSHREG']:  # 15
            self.push_reg(arg_second)
            return True
        
        if instruction_id == INSTRUCTIONS_DICT['PUTC']:  # 16
            self.put_char(arg_second)
            return True
        
    def run(self):
        """
        Запускается работа машины.
        Машина работает с выделенным участком памяти, пока не будет прочитана инструкция STOP
        """
        self.memory[IP_ADDRESS] = REGISTERS_COUNT + FUNC_START_ADDR_SIZE
        self.memory[SP_ADDRESS] = len(self.memory) - 1
        self.memory[REGISTERS_COUNT] = 0
        
        while self.interpret_current_comand():
            continue