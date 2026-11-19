from Node import *

def interpret(program: Program) -> None:
    global C
    C.clear()
    for node in program.functions:
        C.functionTable[node.name] = node
    
    if "main" not in C.functionTable:
        return None
    try:
        C.localv.append([{}])
        C.functionTable["main"].visit()
    except ReturnException:
        C.localv.pop()