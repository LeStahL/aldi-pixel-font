import construct
from typing import List

class Text:
    BinarySaveFormat = construct.Aligned(
        4,
        construct.GreedyRange(
            construct.PascalString(
                construct.Int8un,
                'ascii',
            ),
        ),
    )

    BinaryExportFormat = construct.GreedyRange(
        construct.Int32un,
    )

    BinaryDecodeFormat = construct.Array(
        4,
        construct.Int8un,
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
        return Text.BinaryExportFormat.parse(
            Text.BinarySaveFormat.build(self._lines),
        )

    def offsets(self):
        result = []
        offset = 0
        for line in self._lines:
            result.append(offset),
            offset += len(line) + 1
        return result

    def lineCount(self):
        return len(self._lines)

    def chunks(self, width: int) -> List[List[int]]:
        entireList = self.toUnsignedIntegerArray()
        return [entireList[i:i + width] for i in range(0, len(entireList), width)]

    def offsetChunks(self, width: int):
        entireList = self.offsets()
        return [entireList[i:i + width] for i in range(0, len(entireList), width)]

if __name__ == '__main__':
    text = Text()
    text.add("Hello, World!")
    text.add("Foobar.")
    
    serialized = text.toBytes()
    
    print(serialized)
    print(text.toUnsignedIntegerArray())
    print(text.offsets())

    text1 = Text()
    text1.fromBytes(serialized)

    for text in text1._lines:
        print(text)
