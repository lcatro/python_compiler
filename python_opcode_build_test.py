
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
