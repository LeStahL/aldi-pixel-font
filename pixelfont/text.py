import construct
from typing import List

class Text:
    BinarySaveFormat = construct.Aligned(
        4,
        construct.GreedyRange(
            construct.PascalString,
        ),
    )
    
    BinaryExporFormat = construct.GreedyRange(
        construct.Int32un,
    )

    def __init__(self) -> None:
        self._lines = []

    def add(self, line: str) -> None:
        self._lines.append(line)
    
    def toBytes(self) -> bytes:
        return Text.BinarySaveFormat.build(self._lines)

    def fromBytes(self, data: bytes) -> None:
        self._lines = Text.BinarySaveFormat.parse(data)

    def toUnsignedIntegerArray(self) -> List[int]:
        return 