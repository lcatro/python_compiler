
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
        self.co_firstlineno=1
        self.co_lnotab=b'\x00\x01'
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

def conver_string_encode(input_string) :
    try :
        flag_index=input_string.find('\\')

        while not -1==flag_index :
            if 'x'==input_string[flag_index+1] :  #  hex to bin
                before_string=input_string[:flag_index]
                conver_bit_data=b''
                
                try :
                    conver_bit_data=chr(int(input_string[flag_index+2:flag_index+4],16))  #  fkldfklgj\xAAgasukh
                    input_string=before_string+conver_bit_data+input_string[flag_index+4:]
                except :
                    try :
                        conver_bit_data=chr(int(input_string[flag_index+2:flag_index+3],16))  #  gfg\xAhfweq
                        input_string=before_string+input_string[flag_index+3:]
                    except :
                        input_string=before_string+input_string[flag_index+1:]

            flag_index=input_string.find('\\')
    except :
        pass
        
    return input_string
    

def compiler_pseudo_opcode(python_pseudo_opcode_stream,argument_number=0,sub_function=False) :
    '''

    Python pseudo-opcode file format :
    
    Instruction_Block1

    function %function_name% (arg1,arg2,...)
        Function_Instruction_Block1
    return

    function %function_name% (arg1,arg2,...)
        Function_Instruction_Block2
    return
        
    Instruction_Block2

    '''
    
    const_list=[None]      #  save const string or function code ,WARNING ! value None is give to return or other using ..
    name_list=[]           #  save function or other name ..
    variant_name_list=[]   #  save variant name ..
    function_map_in_const_list={}  #  function code index in const_list ..
    global_code_block=b''  #  code segument __main__
    compile_state=0        #  compile_state
    compile_code_object=code_object()
    code_stream_index=0
    python_pseudo_opcode_stream_length=len(python_pseudo_opcode_stream)
    
    while code_stream_index<python_pseudo_opcode_stream_length :
        code_line=python_pseudo_opcode_stream[code_stream_index]
        
#        print code_line  #  debug compile code stream ..
        
        if code_line.startswith('function') :
            code_line=code_line[code_line.find(' ')+1:].strip()
            function_name=code_line[:code_line.find('(')].strip()
            code_line=code_line[code_line.find('(')+1:].strip()
            function_argument_list=[]
            split_flag_index=code_line.find(',')
            
            while not -1==split_flag_index :  #  init function header ..
                function_argument_name=code_line[:split_flag_index].strip()
                code_line=code_line[split_flag_index+1:].strip()
                split_flag_index=code_line.find(',')
                
                if len(function_argument_name) :  #  argument name is empty ..
                    function_argument_list.append(function_argument_name)
                
            function_argument_name=code_line[:code_line.find(')')].strip()
            
            if len(function_argument_name) :  #  argument name is empty ..
                function_argument_list.append(function_argument_name)
            
            find_function_index=code_stream_index+1
            
            while not 'return'==python_pseudo_opcode_stream[find_function_index] :  #  found function end ..
                find_function_index+=1
                
                if find_function_index>len(python_pseudo_opcode_stream) :
                    raise TypeError,'can\' not found function end flag'
            
            function_code_object=compiler_pseudo_opcode(python_pseudo_opcode_stream[code_stream_index+1:find_function_index],len(function_argument_list),True)  #  compile inside function code ..
            function_code_object.co_name=function_name
            function_code_bytecode=deserialize_code_object(serialize_code_object(function_code_object))  #  TIPS : Python function code will save in segument const ,function code must save as code_object ..
            
            if function_map_in_const_list.has_key(function_name) :
                raise TypeError,'this function has been declare'
            
            const_list.append(function_code_bytecode)  #  Python function code is save in segment const ..      
            
            function_map_in_const_list[function_name]=len(const_list)-1
            function_code_index=function_map_in_const_list[function_name]
            
            if not name_list.count(function_name) :
                name_list.append(function_name)
            
            function_name_index=name_list.index(function_name)
            
            make_function_opcode=b''+chr(opcode.opmap['LOAD_CONST'])+chr(function_code_index & 0xFF)+chr((function_code_index>>8) & 0xFF)
            make_function_opcode+=chr(opcode.opmap['MAKE_FUNCTION'])+chr(0x00)+chr(0x00)
            make_function_opcode+=chr(opcode.opmap['STORE_NAME'])+chr(function_name_index & 0xFF)+chr((function_name_index>>8) & 0xFF)
            global_code_block+=make_function_opcode  #  Python don't like C / JAVA / JavaScript ,using function must need to make it first ..
            
            code_stream_index=find_function_index
        else :
            instruction_name=None
            instruction_argument=None  #[]
            
            if -1==code_line.find(' ') :  #  pre-process instruction struct ..
                instruction_name=code_line
            else :
                instruction_name=code_line[:code_line.find(' ')]
                instruction_argument=code_line[code_line.find(' ')+1:].strip()
                
                if not -1==instruction_argument.find('\'') :
                    if 'o'==instruction_argument[0] :  #  o'\x23\xdc\a1'  ,object build ..
                        instruction_argument=conver_string_encode(instruction_argument[instruction_argument.find('\'')+1:instruction_argument.rfind('\'')])
                        instruction_argument=marshal.loads(instruction_argument)
                    else :  #  'ABCD\x11' ,string argument ..
                        instruction_argument=conver_string_encode(instruction_argument[instruction_argument.find('\'')+1:instruction_argument.rfind('\'')])
                elif 'None'==instruction_argument :
                    instruction_argument='None'
                else :
                    instruction_argument=int(instruction_argument)
                
            if opcode.opmap.has_key(instruction_name) :  #  conver instruction to opcode ..
                opcode_instruction_to_byte_code=opcode.opmap[instruction_name]
            else :
                raise TypeError,'this instruction:'+instruction_name+' is not exise'
                
            opcode_argument=0
                
            #  some special instruction need pre-process ..
            if 'LOAD_CONST'==instruction_name :  #  load string or function code into const_list ..
                if 'None'==instruction_argument :
                    opcode_argument=0
                else :
                    if not const_list.count(instruction_argument) :
                        const_list.append(instruction_argument)
                    
                    opcode_argument=const_list.index(instruction_argument)
            elif 'LOAD_NAME'==instruction_name or 'LOAD_ATTR'==instruction_name or 'LOAD_GLOBAL'==instruction_name :  #  load function name into name_list ..
                if not name_list.count(instruction_argument) :
                    name_list.append(instruction_argument)
                    
                opcode_argument=name_list.index(instruction_argument)
            elif 'LOAD_FAST'==instruction_name :  #  load variant name into variant_name_list ..
                if not variant_name_list.count(instruction_argument) :
                    variant_name_list.append(instruction_argument)
                    
                opcode_argument=variant_name_list.index(instruction_argument)
            elif 'CALL_FUNCTION'==instruction_name :  #  load function name into name_list ..
                '''
                    CALL_FUNCTION => LOAD_NAME %function_name_index% + CALL_FUNCTION + POP_TOP
                '''
                if name_list.count(instruction_argument) :
                    opcode_argument=name_list.index(instruction_argument)
                    global_code_block+=chr(opcode.opmap['LOAD_NAME'])+chr(opcode_argument & 0xFF)+chr((opcode_argument>>8) & 0xFF)
                    global_code_block+=chr(opcode.opmap['CALL_FUNCTION'])+chr(0x00)+chr(0x00)
                    opcode_instruction_to_byte_code=opcode.opmap['POP_TOP']
                else :
                    raise TypeError,'instruction CALL_FUNCTION can\' found function name '
            
            global_code_block+=chr(opcode_instruction_to_byte_code)
            
            if opcode_instruction_to_byte_code>opcode.HAVE_ARGUMENT :  #  take-argument instruction
                opcode_argument_hige_byte=chr((opcode_argument>>8) & 0xFF)
                opcode_argument_low_byte=chr(opcode_argument & 0xFF)
                
                global_code_block+=opcode_argument_low_byte
                global_code_block+=opcode_argument_hige_byte
                
        code_stream_index+=1
    
    global_code_block+=chr(opcode.opmap['LOAD_CONST'])+chr(0x00)+chr(0x00)  #  build Python exit instruction ..
    global_code_block+=chr(opcode.opmap['RETURN_VALUE'])
    
    if sub_function :
        compile_code_object.co_flags=0x43
    
    compile_code_object.co_argcount=argument_number
    compile_code_object.co_code=global_code_block
    compile_code_object.co_consts=tuple(const_list,)
    compile_code_object.co_names=tuple(name_list)
    compile_code_object.co_varnames=tuple(variant_name_list)
    
    return compile_code_object

def serialize_code_object(code_object) :
    code_buffer=b'\x63'
    code_buffer+=marshal.dumps(code_object.co_argcount)[1:]
    code_buffer+=marshal.dumps(code_object.co_nlocals)[1:]
    code_buffer+=marshal.dumps(code_object.co_stacksize)[1:]
    code_buffer+=marshal.dumps(code_object.co_flags)[1:]
    code_buffer+=marshal.dumps(code_object.co_code)
    code_buffer+=marshal.dumps(code_object.co_consts)
    code_buffer+=marshal.dumps(code_object.co_names)
    code_buffer+=marshal.dumps(code_object.co_varnames)
    code_buffer+=marshal.dumps(code_object.co_freevars)
    code_buffer+=marshal.dumps(code_object.co_cellvars)
    code_buffer+=marshal.dumps(code_object.co_filename)
    code_buffer+=marshal.dumps(code_object.co_name)
    code_buffer+=struct.pack('L',code_object.co_firstlineno)
    code_buffer+=marshal.dumps(code_object.co_lnotab)

    return code_buffer

def deserialize_code_object(input_string) :
    return marshal.loads(input_string)

def save_to_pyc(file_path,code_object) :
    file=open(file_path, 'wb')
    
    if file :
        file.write(imp.get_magic())
        file.write(struct.pack('L',time.time()))
        file.write(serialize_code_object(code_object))
        file.close()
    
    
if __name__=='__main__' :
    if 2==len(sys.argv) :
        compile_code_object=compiler_pseudo_opcode(format_code(read_file(sys.argv[1])))

        save_to_pyc(sys.argv[1]+'.pyc',compile_code_object)
    else :  #  test_case
        compile_code_object=compiler_pseudo_opcode(format_code(read_file('./python_opcode_build_test.py')))
        
        save_to_pyc('./python_opcode_build_test.pyc',compile_code_object)
