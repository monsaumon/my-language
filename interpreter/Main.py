from typing import List

from Parser import parse
from Node import Program
from Token import Token
from Scanner import scan
from Interpreter import interpret

def run(sourceCode: str) -> None:
    tokenList: List[Token] = scan(sourceCode)
    syntaxTree: Program = parse(tokenList)
    interpret(syntaxTree)

run(
R"""
function main(){
    var a=1;
    b=2;
    if(a != b) {printLine(a);}
}
"""
)