from dataclasses import dataclass

from Kind import Kind

#토큰 객체
@dataclass
class Token:
    kind: Kind = Kind.Unknown   #토큰 종류
    string: str = ''            #토큰의 데이터