import numpy as np
import sys

REGISTERS_COUNT = 9
FUNC_START_ADDR_SIZE = 10

INSTRUCTION_SIZE = 3  # количество ячеек, занимаемое одной инструкцией

REGISTERS_DICT = {'ip':0, 'sp':1, 'r1':2, 'r2':3, 'r3':4, 'r4':5, 'r5':6, 'r6':7, 'rf':8}      

def get_reg_name(reg_addr):
    """
    По адресу регистра (числу от 0 до 7) возвращает его строковое имя
    """
    for name, addr in REGISTERS_DICT.items():
        if addr == reg_addr:
            return name
        
class Disassembler:
    
    def __init__(self):
        self.program_code = []
        
        # адрес строки - label этой строки
        self.address_to_label = {}
        
        self.labels_counter = 0
    
    # Как и VirtualMachine умеет считывать программу из bin файла
    def read_program_from_file(self, filename):
        with open(filename) as f:
            program_str = f.readlines()
        program_line = program_str[0]
        program_line = program_line.split()
        self.program_code = [int(num) for num in program_line]

    def convert_code_to_string(self, instruction, arg_first, arg_second, use_labels=True):
        """
        Конфертирует команду состоящую из 3х чисел в ассемблерную инструкцию
        Если выставлен флаг use_labels заменяет в переходах ip на новые адреса эти самые адреса на названия лейблов,
        лейблы при этом запоминает
        """
        if instruction == 0:  # MOV
            string_result = 'MOV ' + get_reg_name(arg_first) + ' ' + get_reg_name(arg_second)
            
        if instruction == 1:  # ADD
            string_result = 'ADD ' + get_reg_name(arg_first) + ' ' + get_reg_name(arg_second)
            
        if instruction == 2:  # JUMP
            if use_labels:
                address = (arg_second - REGISTERS_COUNT - FUNC_START_ADDR_SIZE) / INSTRUCTION_SIZE
                if address in self.address_to_label:
                    string_result = 'JUMP ' + self.address_to_label[address]
                else:
                    self.address_to_label[address] = 'label' + str(self.labels_counter)
                    string_result = 'JUMP ' + 'label' + str(self.labels_counter)
                    self.labels_counter += 1
            else:
                string_result = 'JUMP ' + str(arg_second)
            
        if instruction == 3:  # STOP
            string_result = 'STOP'
            
        if instruction == 4:  # READ    
            string_result = 'READ ' + get_reg_name(arg_second)
            
        if instruction == 5:  # PRINT
            string_result = 'PRINT ' + get_reg_name(arg_second)
            
        if instruction == 6:  # FBEG
            string_result = 'FBEG ' + str(arg_second)
            
        if instruction == 7:  # FEND
            string_result = 'FEND'
            
        if instruction == 8:  # PUSH
            string_result = 'PUSH ' + str(arg_second)
            
        if instruction == 9:  # POP
            string_result = 'POP'
            
        if instruction == 10:  # CALL
            string_result = 'CALL ' + str(arg_second)
            
        if instruction == 11:  # TOP
            string_result = 'TOP ' + get_reg_name(arg_second)
            
        if instruction == 12:  # SUB
            string_result = 'SUB ' + get_reg_name(arg_first) + ' ' + get_reg_name(arg_second)
            
        if instruction == 13:  # ASSIGN
            string_result = 'ASSIGN ' + get_reg_name(arg_first) + ' ' + str(arg_second)
            
        if instruction == 14:  # IFNIL
            if use_labels:
                address = (arg_second - REGISTERS_COUNT - FUNC_START_ADDR_SIZE) / INSTRUCTION_SIZE
                if address in self.address_to_label:
                    string_result = 'IFNIL ' + get_reg_name(arg_first) + ' ' + self.address_to_label[address]
                else:
                    self.address_to_label[address] = 'label' + str(self.labels_counter)
                    string_result = 'IFNIL ' + get_reg_name(arg_first) + ' label' + str(self.labels_counter)
                    self.labels_counter += 1
            else:
                string_result = 'IFNIL ' + get_reg_name(arg_first) + ' ' + str(arg_second)
            
        if instruction == 15:  # PUSHREG
            string_result = 'PUSHREG ' + get_reg_name(arg_second)
            
        if instruction == 16:  # PUTC
            string_result = 'PUTC ' + str(arg_second)
            
        return string_result    
        
            
    def convert_program_code_to_text(self):
        self.program_text = []
        for i in np.arange(0, len(self.program_code) - (INSTRUCTION_SIZE - 1), INSTRUCTION_SIZE):
            self.program_text.append(self.convert_code_to_string(self.program_code[i],
                                              self.program_code[i + 1],
                                              self.program_code[i + 2]))
        
    def insert_labels_in_program_text(self):
        """
        В текст программы вставляет лейблы в начале необходимых строк
        Информацию берёт из self.address_to_label
        """
        for i in range(len(self.program_text)):
            if i in self.address_to_label:
                self.program_text[i] = self.address_to_label[i] + ': ' + self.program_text[i]
                
                
    def convert_putcs_to_putstr(self):
        """
        Последовательности инструкций PUTC, заканчивающиеся переводом строки заменяет одной инструкцией PUTSTR
        Всё во имя человекочитабельности!
        """
        new_program_text = []
        
        begin_putc_index = -1
        end_putc_index = -1
        string_sum = ''
        has_label = False
        
        for i in range(len(self.program_text)):
            
            line = self.program_text[i]
            
            if line.find('PUTC') == -1:  # в строке нет команды PUTC
                # предыдущая команда тоже не PUTC
                if begin_putc_index == end_putc_index:
                    new_program_text.append(line)
                else:
                    for j in range(begin_putc_index, i + 1):
                        new_program_text.append(self.program_text[j])
                begin_putc_index = i
                end_putc_index = i
                has_label = False
                continue
                
            # если в строке есть команда PUTC, а ещё встретился label
            if i in self.address_to_label:
                # оставляем все предыдущие команды в первоначальном виде
                for j in range(begin_putc_index, i):
                    new_program_text.append(self.program_text[j])
                    begin_putc_index = i
                    has_label = True
            
            # первая встреча инструкции PUTC
            if begin_putc_index == end_putc_index:  
                begin_putc_index = i
            
            current_chr = chr(int(line[line.find('PUTC') + 5:]))
            
            if current_chr == '\n':
                end_putc_index = i
                if has_label:
                    new_program_text.append(self.address_to_label[begin_putc_index]+ ': PUTSTR ' + string_sum)
                else:
                    new_program_text.append('PUTSTR ' + string_sum)
                begin_putc_index = i
                string_sum = ''
                continue
            
            string_sum = string_sum + current_chr
        
        self.program_text = new_program_text
            
    
    def write_program_text_into_file(self, disassembly_file):
        with open(disassembly_file, 'w') as outfile:
            for line in self.program_text:
                outfile.write("%s\n" % line)
                
    def disassembly(self, bytecode_file, disassembled_file):
        self.address_to_label = {}
        self.labels_counter = 0
        
        self.read_program_from_file(bytecode_file)
        self.convert_program_code_to_text()
        self.insert_labels_in_program_text()
        self.convert_putcs_to_putstr()
        self.write_program_text_into_file(disassembled_file)
        