from Scanner.Scanner import scan
from Parser.Parser import parse
from Generator.Generator import generate
from Machine.Machine import execute

def run(sourceCode: str) -> None:
    tokenList = scan(sourceCode)
    syntaxTree = parse(tokenList)
    objectCode= generate(syntaxTree)
    execute(objectCode)

run(
R"""
function a(x){
    return x+1;
}

function main(){
    var a=1;
}
"""
)
