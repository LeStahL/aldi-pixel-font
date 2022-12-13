from typing import Optional
import construct

class Glyph:
    Width = 5
    Height = 6
    Size = 32

    BinaryFormat = construct.Struct(
        'data' / construct.Array(
            Width * Height,
            construct.Flag,
        ),
        construct.BitsInteger(2),
    )

    def __init__(self,
        ordinal: int = 0,
    ):
        self._pixels = [False] * Glyph.Width * Glyph.Height
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
        return Glyph.BinaryFormat.build({
            'data': self._pixels,
        })

    def fromBytes(self,
        data: bytes,
    ) -> None:
        self._pixels = Glyph.BinaryFormat.parse(data)['data']

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
