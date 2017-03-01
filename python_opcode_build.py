
import imp
import marshal
import opcode
import struct
import sys
import time


opcode_map=opcode.opmap


class code_object(object):

    def __init__(self) :
        self.co_argcount=0
        self.co_nlocals=0
        self.co_stacksize=1
        self.co_flags=0x40
        self.co_code=b''
        self.co_consts=()
        self.co_names=()
        self.co_varnames=()
        self.co_filename=''
        self.co_name='<module>'
        self.co_firstlineno=2
        self.co_lnotab=''
        self.co_freevars=()
        self.co_cellvars=()

        
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
        line_code=line_code.strip()
        line_code=line_code.replace('\t','')
        
        if len(line_code) :
            code_list.append(code[:newline_flag_offset])
        
        code=code[newline_flag_offset+1:]
        newline_flag_offset=code.find('\n')
        
    return code_list

def get_data(list_object,value) :
    for list_index in range(list_object) :
        if list_object[list_index]==value :
            return list_index
        
    return None

def add_data(list_object,value) :
    if None==get_data(list_object,value) :
        list_object.append(value)
        
    return list_object
    
def compiler_pseudo_opcode(python_pseudo_opcode_stream) :
    '''

    Python pseudo-opcode file format :
    
    config_start
        argcount=%int%
        locals=%int%
        stacksize=%int%
        flags=%int%
    config_end
    const_list_start
        'const_name1'=const_value1
        'const_name2'=const_value2
    const_list_end
    name_list_start
        'name_1'
        'name_2'
        'name_3'
    name_list_end
    variant_name_list_start
        'variant_name_1'
        'variant_name_2'
        'variant_name_3'
    variant_name_list_end

    Instruction_Block1

    function_start
    %function_name% (arg1,arg2,...)
        Function_Instruction_Block1
    function_end

    function_start
    %function_name% (arg1,arg2,...)
        Function_Instruction_Block2
    function_end
        
    Instruction_Block2

    '''
    
    const_list=[None]  #  save const string or function code ,WARNING ! value None is give to return or other using ..
    function_map_in_const_list={}  #  function code index map in const_list ..
    name_list=[]  #  save function or other name ..
    variant_name_list=[]  #  save variant name ..
    global_code_block=b''
    function_name=''
    function_code_block=b''
    compile_state=0
    return_code_object=code_object()
    
    for code_stream_index in range(len(python_pseudo_opcode_stream)) :
        code_stream=python_pseudo_opcode_stream[code_stream_index]
                
        if 'config_start'==code_stream :
            compile_state=1
        elif 'config_end'==code_stream :
            compile_state=0
        elif 'const_list_start'==code_stream :
            compile_state=2
        elif 'const_list_end'==code_stream :
            compile_state=0
        elif 'name_list_start'==code_stream :
            compile_state=3
        elif 'name_list_end'==code_stream :
            compile_state=0
        elif 'variant_name_list_start'==code_stream :
            compile_state=4
        elif 'variant_name_list_end'==code_stream :
            compile_state=0
        elif 'function_start'==code_stream :
            compile_state=5
            
            function_header=python_pseudo_opcode_stream[code_stream_index+1]
            function_argumunt_list=[]
            
            try :
                function_name=function_header[:function_header.find(' ')].strip()
                function_argumunt_string=function_header[function_header.find('(')+1:function_header.rfind(')')].strip()
                function_argument_string_split_flag=function_argumunt_string.find(',')
                
                while not -1==function_argument_string_split_flag :
                    function_argumunt_list.append(function_argumunt_string[:function_argument_string_split_flag].strip())
                    
                    function_argumunt_string=function_argumunt_string[function_argument_string_split_flag+1:]
                    function_argument_string_split_flag=function_argumunt_string.find(',')
            except :
                print 'Syntax Error ! Resolve Function Block Error ..'
                
                raise TypeError
                
            name_list=add_data(name_list,function_name)
            
            for function_argumunt_list_index in function_argumunt_list :
                name_list=add_data(name_list,function_argumunt_list_index)
                
            code_stream_index+=2
        elif 'function_end'==code_stream :
            const_list.append(function_code_block)
            
            function_map_in_const_list[function_name]=len(const_list)-1
            function_code_block=b''
            function_name=''
            compile_state=0
        elif 0==compile_state or 5==compile_state :  #  code and function code block ..
            opcode_instruction=''
            opcode_argument=''
            
            try :
                if '#'==code_stream[0] :  #  noncommenting code ..
                    continue
                if not -1==code_stream.find(' ') :
                    opcode_instruction=code_stream[:code_stream.find(' ')].strip()

                    if 'LOAD_CONST'==opcode_instruction :  #  per-process for special instruction ..
                        opcode_argument=code_stream[code_stream.find(' ')+1:].strip()

                        if 'None'==opcode_argument :  #  LOAD_CONST None
                            opcode_argument=0
                        else :
                            opcode_argument=int(opcode_argument,16)+1
                    else :
                        opcode_argument=int(code_stream[code_stream.find(' ')+1:].strip(),16)
                else :
                    opcode_instruction=code_stream.strip()
            except :
                print 'Can\'t not resolve instruction '+opcode_instruction+'\'s argument ..'
                
                raise TypeError
                
            # print opcode_instruction,opcode_argument  #  debug opcode stream ..
                
            opcode_instruction_to_byte_code=0
            
            try :
                opcode_instruction_to_byte_code=opcode_map[opcode_instruction]
            except :
                print 'Can\'t not conver instruction '+opcode_instruction+' to byte-code ..'
                
                raise TypeError
                
            if opcode_instruction_to_byte_code<opcode.HAVE_ARGUMENT :  #  no-argument instruction
                if 0==compile_state :
                    global_code_block+=chr(opcode_instruction_to_byte_code)
                else :
                    function_code_block+=chr(opcode_instruction_to_byte_code)
            else :  #  take-argument instruction
                opcode_instruction_to_byte_code_=chr(opcode_instruction_to_byte_code)
                opcode_argument_hige_byte=chr((opcode_argument>>8) & 0xFF)
                opcode_argument_low_byte=chr(opcode_argument & 0xFF)
                
                if 0==compile_state :
                    global_code_block+=opcode_instruction_to_byte_code_
                    global_code_block+=opcode_argument_low_byte
                    global_code_block+=opcode_argument_hige_byte
                else :
                    function_code_block+=opcode_instruction_to_byte_code_
                    function_code_block+=opcode_argument_low_byte
                    function_code_block+=opcode_argument_hige_byte
        elif 1==compile_state :  #  config list ..
            try :
                setting_name=code_stream[:code_stream.find('=')].strip()
                setting_value=code_stream[code_stream.find('=')+1:].strip()
                
                if 'argcount'==setting_name :
                    setting_value=int(setting_value,16)
                    return_code_object.co_argcount=setting_value
                elif 'locals'==setting_name :
                    setting_value=int(setting_value,16)
                    return_code_object.co_nlocals=setting_value
                elif 'stacksize'==setting_name :
                    setting_value=int(setting_value,16)
                    return_code_object.co_stacksize=setting_value
                elif 'flags'==setting_name :
                    setting_value=int(setting_value,16)
                    return_code_object.co_flags=setting_value
            except :
                print 'Resolve config block ERROR ..'
                
                raise TypeError
        elif 2==compile_state :  #  const list ..
            const_list.append(code_stream)
        elif 3==compile_state :  #  name list ..
            name_list.append(code_stream)
        elif 4==compile_state :  #  variant name list ..
            variant_name_list.append(code_stream)
            
    return_code_object.co_code=global_code_block
    return_code_object.co_consts=tuple(const_list,)
    return_code_object.co_names=tuple(name_list)
    return_code_object.co_varnames=tuple(variant_name_list)
            
    return return_code_object

def save_to_pyc(file_path,code_object) :
    file=open(file_path, 'wb')
    
    if file :
        file.write(imp.get_magic())
        file.write(struct.pack('L',time.time()))
        file.write('\x63')
        file.write(marshal.dumps(code_object.co_argcount)[1:])
        file.write(marshal.dumps(code_object.co_nlocals)[1:])
        file.write(marshal.dumps(code_object.co_stacksize)[1:])
        file.write(marshal.dumps(code_object.co_flags)[1:])
        file.write(marshal.dumps(code_object.co_code))
        file.write(marshal.dumps(code_object.co_consts))
        file.write(marshal.dumps(code_object.co_names))
        file.write(marshal.dumps(code_object.co_varnames))
        file.write(marshal.dumps(code_object.co_freevars))
        file.write(marshal.dumps(code_object.co_cellvars))
        file.write(marshal.dumps(code_object.co_filename))
        file.write(marshal.dumps(code_object.co_name))
        file.write(struct.pack('L',code_object.co_firstlineno))
        file.write(marshal.dumps(code_object.co_lnotab))
        file.close()
    
    
if __name__=='__main__' :
    if 2==len(sys.argv) :
        compile_code_object=compiler_pseudo_opcode(format_code(read_file(sys.argv[1])))

        save_to_pyc(sys.argv[1]+'.pyc',compile_code_object)

