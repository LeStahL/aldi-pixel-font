import construct
from typing import Optional, List
from glyph import *
from random import choice

class Font:
    BinarySaveFormat = construct.GreedyRange(
        Glyph.BinarySaveFormat,
    )

    def __init__(self,
        ordinals: List[int] = range(32, 126),
    ) -> None:
        self._glyphs = list(map(
            lambda ordinal: Glyph(ordinal),
            ordinals,
        ))

    def toBytes(self) -> bytes:
        return Font.BinarySaveFormat.build(list(map(
            lambda glyph: glyph.toObject(),
            self._glyphs,
        )))
    
    def fromBytes(self,
        data: bytes,
    ):
        self._glyphs = list(map(
            lambda glyphConstruct: Glyph(glyphConstruct['ordinal'], glyphConstruct['pixels']),
            Font.BinarySaveFormat.parse(data),
        ))

    def ordinals(self) -> List[int]:
        return sorted(list(map(
            lambda glyph: glyph._ordinal,  
            self._glyphs,
        )))

    def glyphWithOrdinal(self,
        ordinal: int,
    ) -> Glyph:
        result = list(filter(
            lambda glyph: glyph._ordinal == ordinal,
            self._glyphs,
        ))

        if result == []:
            return None
        
        return result[0]

    def renameGlyph(self,
        fromOrdinal: int,
        toOrdinal: int,
    ) -> bool:
        if fromOrdinal not in self.ordinals():
            return False

        if toOrdinal in self.ordinals():
            return False

        self.glyphWithOrdinal(fromOrdinal)._ordinal = toOrdinal
        
        return True

    def addNewGlyph(self) -> int:
        choices = list(filter(
            lambda glyph: glyph not in self.ordinals(),
            range(127),
        ))

        if len(choices) == 0:
            return -1

        ordinal = choice(choices)
        self._glyphs.append(Glyph(ordinal))
        
        return ordinal

    def removeGlyph(self, ordinal: int) -> bool:
        self._glyphs = list(filter(
            lambda glyph: glyph._ordinal != ordinal,
            self._glyphs,
        ))

    def glyphCount(self) -> int:
        return len(self._glyphs)

    def chunks(self, width: int) -> List[List[Glyph]]:
        sortedGlyphs = list(map(
            lambda ordinal: self.glyphWithOrdinal(ordinal),
            self.ordinals(),
        ))
        return [sortedGlyphs[i:i + width] for i in range(0, len(sortedGlyphs), width)]

if __name__ == '__main__':
    font = Font()
    font.glyphWithOrdinal(ord('a')).toggle(1, 1, True)
    serialized = font.toBytes()

    font = Font()
    font.fromBytes(serialized)
    assert font.glyphWithOrdinal(ord('a')).isOn(1,1)
