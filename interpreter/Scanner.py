from typing import List
from enum import Enum, auto

from Token import Token
from Kind import Kind, toKind

#문자의 종류(CharType)를 나열한 객체(열거체)
class CharType(Enum):
    Unknown = auto()
    WhiteSpace = auto()
    NumberLiteral = auto()
    StringLiteral = auto()
    IdentifierAndKeyword = auto()
    OperatorAndPunctuator = auto()

#코드를 저장하고 한 문자씩 읽기 위한 객체
class Code:
    def __init__(self, code: str):
        self.code = code
        self.current = 0
        self.char = self.code[self.current]
    
    def plus(self):
        self.current += 1
        self.char = self.code[self.current]
    
    def minus(self):
        self.current -= 1
        self.char = self.code[self.current]

#문자를 입력받아 그 문자의 CharType을 반환하는 함수
def getCharType(c: str) -> CharType:
    if c == ' ' or c == '\t' or c == '\r' or c == '\n':
        return CharType.WhiteSpace
    if ord('0') <= ord(c) <= ord('9'):
        return CharType.NumberLiteral
    if c == '\'':
        return CharType.StringLiteral
    if ord('a') <= ord(c) <= ord('z') or ord('A') <= ord(c) <= ord('Z'):
        return CharType.IdentifierAndKeyword
    if 33 <= ord(c) <= 47 and c != '\'' \
    or 58 <= ord(c) <= 64 \
    or 91 <= ord(c) <= 96 \
    or 123 <= ord(c) <= 126:
        return CharType.OperatorAndPunctuator

    return CharType.Unknown

#문자와 CharType을 받아 문자의 종류가 CharType인지 확인하여 bool형으로 반환하는 함수
def isCharType(c: str, ct: CharType) -> bool:
    if ct == CharType.NumberLiteral:
        return ord('0') <= ord(c) <= ord('9')
    if ct == CharType.StringLiteral:
        return 32 <= ord(c) <= 126 and c != '\''
    if ct == CharType.IdentifierAndKeyword:
        return ord('0') <= ord(c) <= ord('9') \
            or ord('a') <= ord(c) <= ord('z') \
            or ord('A') <= ord(c) <= ord('Z')
    if ct == CharType.OperatorAndPunctuator:
        return 33 <= ord(c) <= 47 \
            or 58 <= ord(c) <= 64 \
            or 91 <= ord(c) <= 96 \
            or 123 <= ord(c) <= 126

#숫자를 읽어 Token으로 반환하는 함수
def scanNumberLiteral() -> Token:
    string: str = ''
    while isCharType(current.char, CharType.NumberLiteral):
        string += current.char
        current.plus()
    if current.char == '.':
        string += current.char
        current.plus()
        while isCharType(current.char, CharType.NumberLiteral):
            string += current.char
            current.plus()
    return Token(Kind.NumberLiteral, string)

#문자열을 읽어 Token으로 반환하는 함수
def scanStringLiteral() -> Token:
    string: str = ""
    current.plus()
    while isCharType(current.char, CharType.StringLiteral):
        if current.char == '\\':
            current.plus()
            if current.char == 'n': string += '\n'
            elif current.char == 't': string += '\t'
            elif current.char == 'r': string += '\r'
            elif current.char == 'b': string += '\b'
            elif current.char == '\'': string += '\''
            elif current.char == '\\': string += '\\'
            elif current.char == 'f': string += '\f'
            elif current.char == 'a': string += '\a'
            elif current.char == '0': string += '\000'
            else:
                print("존재하지 않는 이스케이프 시퀀스입니다.")
        else: string += current.char
        current.plus()
    if current.char != '\'':
        raise RuntimeError("문자열의 종료 문자가 없습니다.")
    current.plus()
    return Token(Kind.StringLiteral, string)

#Identifier(이름)과 Keyword(if, for, True 등 지정된 단어)를 읽어 Token으로 반환하는 함수
def scanIdentifierAndKeyword() -> Token:
    string: str = ""
    while isCharType(current.char, CharType.IdentifierAndKeyword):
        string += current.char
        current.plus()
    kind : Kind = toKind(string)
    if kind == Kind.Unknown:
        kind = Kind.Identifier
    return Token(kind, string)

#Operator(연산자)와 Punctuator(구분자)를 읽어 Token으로 반환하는 함수
def scanOperatorAndPunctuator() -> Token:
    string: str = ""
    while isCharType(current.char, CharType.OperatorAndPunctuator):
        string += current.char
        current.plus()
    while string and toKind(string) == Kind.Unknown:
        string = string[:-1]
        current.minus()
    if not string:
        raise RuntimeError(f"{current.char} 사용할 수 없는 문자입니다.")
    return Token(toKind(string), string)

#전체 코드를 받고 읽어 Token의 리스트로 반환하는 함수
def scan(sourceCode: str) -> List[Token]:
    global current
    result: List[Token] = []
    sourceCode += '\000'
    current = Code(sourceCode)
    while current.char != '\000':
        CT: CharType = getCharType(current.char)
        if CT == CharType.WhiteSpace:
            current.plus()
        elif CT == CharType.NumberLiteral:
            result.append(scanNumberLiteral())
        elif CT == CharType.StringLiteral:
            result.append(scanStringLiteral())
        elif CT == CharType.IdentifierAndKeyword:
            result.append(scanIdentifierAndKeyword())
        elif CT == CharType.OperatorAndPunctuator:
            result.append(scanOperatorAndPunctuator())
        else:
            raise RuntimeError("사용할 수 없는 문자입니다.")
    result.append(Kind.EndOfList)
    return result