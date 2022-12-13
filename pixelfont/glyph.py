from typing import Optional, List
import construct

class Glyph:
    Width = 5
    Height = 6

    BinaryFormat = construct.Bitwise(construct.Aligned(
        8,
        "data" / construct.Array(
            Width * Height,
            construct.Flag,
        ),
    ))

    BinarySaveFormat = construct.Struct(
        'ordinal' / construct.Int8un,
        'pixels' / BinaryFormat,
    )

    def __init__(self,
        ordinal: int = 0,
        pixels: Optional[List[bool]] = None,
    ):
        self._pixels = pixels if pixels is not None else [False] * Glyph.Width * Glyph.Height
        self._ordinal = ordinal

    def toggle(self,
        x: int,
        y: int,
        on: Optional[bool] = None,
    ) -> bool:
        if not self.isValidPixelCoordinate(x, y):
            return False

        self._pixels[y * Glyph.Width + x] = on if on is not None else not self._pixels[y * Glyph.Width + x]
        
        return True

    def toBytes(self) -> bytes:
        return Glyph.BinarySaveFormat.build(self.toObject())

    def toObject(self) -> object:
        return {
            'ordinal': self._ordinal,
            'pixels': self._pixels,
        }

    def fromBytes(self,
        data: bytes,
    ) -> None:
        parsed = Glyph.BinarySaveFormat.parse(data)
        self._pixels = parsed['pixels']
        self._ordinal = parsed['ordinal']

    def toInt(self) -> int:
        return int.from_bytes(self.serialize(), 'big')

    def fromInt(self,
        data: int,
    ) -> None:
        self.fromBytes(data.to_bytes('big'))

    def isOn(self,
        x: int,
        y: int,
    ) -> Optional[bool]:
        if self.isValidPixelCoordinate(x, y):
            return self._pixels[y * Glyph.Width + x]
        return None

    def isValidPixelCoordinate(self,
        x: int,
        y: int,
    ) -> bool:
        return x >= 0 and x < Glyph.Width and y >= 0 and y < Glyph.Height

if __name__ == '__main__':
    glyph = Glyph(ord('a'))
    glyph.toggle(1, 1, True)

    serialized = glyph.toBytes()

    glyph = Glyph()

    glyph.fromBytes(serialized)

    assert glyph.isOn(1, 1)
