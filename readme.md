
##Python Compiler

---

`Python Compiler` 用于Python 指令代码编译,和汇编代码转换到字节码的原理一样,用来测试Python 的细节和更多有趣的东西,后续会添加更多与`Python Compiler` 相关的原理与思考..

##How to create

Python Compiler 使用如下的格式进行编译<br/>

    config_start  #  全局配置字段(配置PYC 代码字段部分)
        argcount=%int%  #  默认为0
        locals=%int%  #  默认为0
        stacksize=%int%  #  栈大小
        flags=%int%  #  默认为0x40
    config_end
    const_list_start  #  全局常量字段
        const_value1  #  常量值1
        const_value2  #  常量值2
    const_list_end
    name_list_start  #  代码名字列表
        name_1  #  名字1
        name_2
        name_3
    name_list_end
    variant_name_list_start  #  变量名列表
        variant_name_1  #  变量名1
        variant_name_2
        variant_name_3
    variant_name_list_end

    Instruction_Block1  #  代码块1

    function_start  #  函数声名
    %function_name% (arg1,arg2,...)  #  函数名与参数声名
        Function_Instruction_Block1  #  函数代码
    function_end

    function_start
    %function_name% (arg1,arg2,...)
        Function_Instruction_Block2
    function_end
        
    Instruction_Block2  #  代码块2

`python_opcode_build_test.py` 是一个输出print 'AAAAAAAA' 的例子<br/>

##How to using

`python_disassmble.py` 用于查看Python 代码对应的Python 指令,用法`python_disassmble.py %file_Path%` <br/>
`python_opcode_build.py` 用来编译Python 指令,用法`python_opcode_build.py %file_Path%` <br/>

