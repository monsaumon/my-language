from dataclasses import dataclass

from Scanner.Kind import Kind

@dataclass(repr=False)
class Token:
    kind: Kind = Kind.Unknown
    string: str = ''

    def __repr__(self) -> str:
        return f"Token[{self.kind}, '{self.string}']"