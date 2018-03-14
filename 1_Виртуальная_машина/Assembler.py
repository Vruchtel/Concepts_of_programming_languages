import numpy as np
import sys

REGISTERS_COUNT = 8
IP_ADDRESS = 0  # instructions pointer
SP_ADDRESS = 1  # stack pointer

INSTRUCTION_SIZE = 3  # количество ячеек, занимаемое одной инструкцией

INSTRUCTIONS_DICT = {'MOV':0, 'ADD':1, 'JUMP':2, 'STOP':3, 'READ':4, 'PRINT':5, 'FBEG':6, 'FEND':7, 'PUSH':8, 'POP':9, 'CALL':10, 'TOP':11, 'SUB':12, 'ASSIGN':13, 'IFNIL':14, 'PUSHREG':15, 'PUTC':16}

REGISTERS_DICT = {'ip':0, 'sp':1, 'r1':2, 'r2':3, 'r3':4, 'r4':5, 'r5':6, 'r6':7}    

class Assembler:
    
    def __init__(self):
        self.program_text = []  # Каждый элемент массива будет соответствовать одной строке кода
    
    def read_file(self, filename):
        with open(filename) as f:
            self.program_text = f.readlines()
            self.program_text = [line.strip() for line in self.program_text]
            
    def create_putcs_for_putstr(self, putstr_instruction):
        """
        Для инструкции, содержащей PUTSTR возвращает список инструкций, содержащий PUTC
        """
        # Обработка лейблов
        has_label = False
        # Проверить, есть ли в строке label
        if putstr_instruction.find(':') != -1 and putstr_instruction.find(':') < putstr_instruction.find('PUTSTR'):
            label = putstr_instruction[:putstr_instruction.find(':') + 1]
            has_label = True
        
        # Список символов, которые необходимо вывести
        chars = list(putstr_instruction[putstr_instruction.find('PUTSTR') + len('PUTSTR '):])
        
        chars.append('\n')  
        
        result_instructions = []
        for char in chars:
            if has_label:
                # Добавляем инструкцию [label: PUTC номер_символа]
                result_instructions.append(label + ' PUTC ' + str(ord(char)))
                has_label = False
            # Добавляем инструкцию [PUTC номер_символа]
            result_instructions.append('PUTC ' + str(ord(char)))
            
        return result_instructions
            
    def replace_all_putstr_with_putcs(self):
        """
        В массиве program_text все вхождения инструкций с PUTSTR 
        заменяет на вхождение последовательности команд PUTC
        """
        
        new_program_text = []
        
        for i, line in enumerate(self.program_text):
            
            if line.find('PUTSTR') != -1:  # в строке есть инструкция PUTSTR
                new_instructions = self.create_putcs_for_putstr(line)
                for instruction in new_instructions:
                    new_program_text.append(instruction)
                continue
                
            new_program_text.append(line)
                
        self.program_text = new_program_text
    
            
    def replace_labels_with_cell_numbers(self):
        """
        В массиве program_text заменяет лейблы на соответствующие номера ячеек 
        (каким они будут соответствовать в байт-коде)
        """
        label_to_num = {}
        
        result = []
        
        for i, line in enumerate(self.program_text):
            if line.find(':') != -1:  # в строке есть : -> в строке уканан лейбл
                label = line[:line.find(':')]
                label_to_num[label] = i  # соответствие label -> номер строки, в которой встретился
                line = line[line.find(':') + 1:]
            line = line.strip()
            result.append(line)
            
        lines = result
        result = []
        
        for line in lines:
            for label, num in label_to_num.items():
                line = line.replace(label, str(num * INSTRUCTION_SIZE + REGISTERS_COUNT))
            result.append(line)
        self.program_text = result
        
        
    def convert_to_static(self, string_parameter):
        """
        Возвращает либо адрес регистра, которому соответствует переданная строка,
        либо статическое число
        """
        if string_parameter in REGISTERS_DICT:
            return REGISTERS_DICT[string_parameter]
        return int(string_parameter)
        
    def convert_string_to_code(self, string):
        """
        По входной строке генерирует соответствующий ей байт-код.
        - заменяет название инструкции на соответствующий id;
        - делает все инструкции трёхсложными (дополняет нулями)
        - заменяет названия регистров на соответствующие им адреса в памяти
        
        Возвращает массив из 3х чисел.
        """
        
        # Массив параметров, содержащихся в строке
        string_params = string.split()
        
        # первый параметр заменяем на соответствующий id инструкции
        string_params[0] = INSTRUCTIONS_DICT[string_params[0]]
        
        # делаем все инструкции трехсложными
        if len(string_params) < 3:
            if len(string_params) == 2:
                string_params.append(self.convert_to_static(string_params[1]))
                string_params[1] = 0
            if len(string_params) == 1:
                string_params.append(0)
                string_params.append(0)
        else:
            string_params[1] = self.convert_to_static(string_params[1])
            string_params[2] = self.convert_to_static(string_params[2])
        
        return string_params
    
    
    def generate_bytecode(self):
        """
        Считанный текст программы преобразует в байт-код, возвращает соответствующий массив
        """
        self.replace_all_putstr_with_putcs()
        self.replace_labels_with_cell_numbers()
        
        byte_code = []
        
        for instruction in self.program_text:
            instr_byte_code = self.convert_string_to_code(instruction)
            for code in instr_byte_code:
                byte_code.append(code)
        
        return byte_code
    
    
    def assembly(self, program_file, bytecode_file):
        """
        Принимает 
        - путь до файла с программой, написанной вспомогательным языком,
        - путь до файла, в который будет записан полученный бинарный файл с программой
        """
        
        self.read_file(program_file)
        bytecode = self.generate_bytecode()
        # записать bytecode в файл
        with open(bytecode_file, 'w') as outfile:
            for code in bytecode:
                outfile.write("%d " % code)
    