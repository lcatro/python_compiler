
##Python Compiler

---

`Python Compiler` 用于Python 指令代码编译,和汇编代码转换到字节码的原理一样,用来测试Python 的细节和更多有趣的东西,后续会添加更多与`Python Compiler` 相关的原理与思考..

##How to create

Python Compiler 使用如下的格式进行编译<br/>

    Instruction_Block1  #  代码块1

    function_start  %function_name% (arg1,arg2,...)  #  函数名与参数声名
        Function_Instruction_Block1  #  函数代码
    function_end

    function_start %function_name% (arg1,arg2,...)
        Function_Instruction_Block2
    function_end
        
    Instruction_Block2  #  代码块2

`python_opcode_build_test.py` 是一个输出print 'AAAAAAAA' 的例子,代码如下:<br/>

    LOAD_CONST 'try to load function ..'
    PRINT_ITEM
    PRINT_NEWLINE

    function try_print ()
    LOAD_CONST 'AAA'
    PRINT_ITEM
    PRINT_NEWLINE
    return

    LOAD_CONST 'try to call function ..'
    PRINT_ITEM
    PRINT_NEWLINE

    CALL_FUNCTION 'try_print'

    LOAD_CONST 'call function end ..'
    PRINT_ITEM
    PRINT_NEWLINE

##How to using

`python_disassmble.py` 用于查看Python 代码对应的Python 指令,用法`python_disassmble.py %file_Path%` <br/>
`python_opcode_build.py` 用来编译Python 指令,用法`python_opcode_build.py %file_Path%` <br/>

