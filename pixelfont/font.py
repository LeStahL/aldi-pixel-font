import construct
from typing import Optional, List
from glyph import *

class Font:
    BinaryFormat = 'glyphs' / construct.PrefixedArray(
        construct.Int32un,
        Glyph.BinaryFormat,
    )

    def __init__(self,
        ordinals: List[int] = [ord('a'), ord('b')],
    ) -> None:
        self._glyphs = list(map(
            lambda ordinal: Glyph(ordinal),
            ordinals,
        ))

    def toBytes(self) -> bytes:
        return Font.BinaryFormat.build({
            "glyphs": self._glyphs,
        })
    
    def fromBytes(self,
        data: bytes,
    ):
        self._glyphs = Font.BinaryFormat.parse(data)['glyphs']

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
