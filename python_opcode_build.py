
import opcode
import sys
import time


opcode_map=opcode.opmap


class code_object(object):

    def __init__(self, initial_code) :
        self.co_argcount=initial_code.co_argcount
        self.co_nlocals=initial_code.co_nlocals
        self.co_stacksize=initial_code.co_stacksize
        self.co_flags=initial_code.co_flags
        self.co_code=initial_code.co_code
        self.co_consts=initial_code.co_consts
        self.co_names=initial_code.co_names
        self.co_varnames=initial_code.co_varnames
        self.co_filename=initial_code.co_filename
        self.co_name=initial_code.co_name
        self.co_firstlineno=initial_code.co_firstlineno
        self.co_lnotab=initial_code.co_lnotab
        self.co_freevars=initial_code.co_freevars
        self.co_cellvars=initial_code.co_cellvars

    def get_code(self) :
        return self.co_code
    
    def set_code(self,new_code) :
        self.co_code=new_code

        
def read_file(file_path) :
    file=open(file_path,'r')
    file_data=file.read()
    
    file.close()
    
    return file_data

def format_code(code) :
    code_list=[]
    code=code.replace('\r','')
    newline_flag_offset=code.find('\n')
    
    while not -1==newline_flag_offset :
        line_code=code[:newline_flag_offset]
        line_code=line_code.replace(' ','')
        line_code=line_code.replace('\t','')
        
        if len(line_code) :
            code_list.append(code[:newline_flag_offset])
        
        code=code[newline_flag_offset+1:]
        newline_flag_offset=code.find('\n')
        
    return code_list
    
def compiler_pseudo_opcode(python_pseudo_opcode_stream) :
'''

    Python pseudo-opcode file format :
    
    const_list_start
        'const_name1'=const_value1
        'const_name2'=const_value2
    const_list_end
    name_list_start
        'name_1'
        'name_2'
        'name_3'
    name_list_end


    Instruction_Block1

    Function_Label1:
        Function_Instruction_Block1

    Function_Label2:
        Function_Instruction_Block2
        
    Instruction_Block2


'''

    const_list=[]
    name_list=[]
    compile_state=0
    
    for code_stream in python_pseudo_opcode_stream :
        if 'const_list_start'==code_stream :
            
        elif 'const_list_end'==code_stream :
            
        elif 'name_list_start'==code_stream :
            
        elif 'name_list_end'==code_stream :
            pass

    
if __name__=='__main__' :
    if 2==len(sys.argv) :
        print format_code(read_file(sys.argv[1]))






