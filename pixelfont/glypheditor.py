from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6 import uic
from typing import Optional
from glyph import *
from sys import argv

class GlyphEditor(QWidget):
    def __init__(self,
        glyph: Optional[Glyph] = Glyph(),
        parent: Optional[QWidget] = None,
        flags: Qt.WindowType = Qt.WindowType.Window,
    ) -> None:
        super().__init__(parent, flags)

        self._glyph = glyph
        self._holding = False
        self._lastResult = True

        self.resize(Glyph.Width * 50, Glyph.Height * 50)

    def paintEvent(self,
        event: QPaintEvent,
    ) -> None:
        super().paintEvent(event)
    
        painter = QPainter(self)
        painter.save()

        dx = int(self.rect().width() / Glyph.Width)
        dy = int(self.rect().height() / Glyph.Height)

        for x in range(Glyph.Width):
            painter.drawLine(x * dx, 0, x * dx, self.rect().height())
            for y in range(Glyph.Height):
                on = self._glyph.isOn(x,y)
                if on is not None:
                    painter.fillRect(
                        x * dx,
                        y * dy,
                        dx,
                        dy,
                        QBrush(QColor(Qt.GlobalColor.black if on else Qt.GlobalColor.white)),
                    )
        for y in range(Glyph.Height):
            painter.drawLine(0, y * dy, self.rect().width(), y * dy)

        painter.restore()

    def mousePressEvent(self,
        event: QMouseEvent,
    ) -> None:
        super().mousePressEvent(event)

        dx = int(self.rect().width() / Glyph.Width)
        dy = int(self.rect().height() / Glyph.Height)

        x = int(event.pos().x() / dx)
        y = int(event.pos().y() / dy)

        on = self._glyph.isOn(x,y)
        if on is None:
            return

        self._holding = True
        self._lastResult = not on

        self.toggle(x, y)

    def mouseMoveEvent(self,
        event: QMouseEvent,
    ) -> None:
        super().mouseMoveEvent(event)

        dx = int(self.rect().width() / Glyph.Width)
        dy = int(self.rect().height() / Glyph.Height)

        x = int(event.pos().x() / dx)
        y = int(event.pos().y() / dy)

        if self._holding:
            self.toggle(x, y)

    def mouseReleaseEvent(self,
        event: QMouseEvent,
    ) -> None:
        super().mouseReleaseEvent(event)

        self._holding = False
    
    def toggle(self,
        x: int,
        y: int,
    ) -> bool:
        self._glyph.toggle(x, y, self._lastResult)
        self.update()
    
    def setGlyph(self,
        glyph: Glyph,
    ) -> None:
        self._glyph = glyph
        self.update()

    def glyph(self) -> Glyph:
        return self._glyph

if __name__ == '__main__':
    app = QApplication(argv)

    glyphEditor = GlyphEditor()
    glyphEditor.show()

    app.exec()
