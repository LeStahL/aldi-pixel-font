from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6 import uic
from typing import Optional, List
from sys import argv
from glypheditor import GlyphEditor
from font import Font
from glyph import Glyph
from os.path import basename

class FontEditor(QMainWindow):
    def __init__(self,
        parent: Optional[QWidget] = None,
        flags: Qt.WindowType = Qt.WindowType.Window,
    ) -> None:
        super().__init__(parent, flags)

        uic.loadUi('FontEditor.ui', self)

        self.glyphEditor = GlyphEditor()
        self.centralWidget().layout().addWidget(self.glyphEditor)

        self.fileNew()

        self.actionExit.triggered.connect(self.exit)
        self.actionNew.triggered.connect(self.fileNew)
        self.actionOpen.triggered.connect(self.fileOpen)
        self.actionSave.triggered.connect(self.fileSave)
        self.actionSave_As.triggered.connect(self.fileSaveAs)
        self.actionAdd_Glyph.triggered.connect(self.addGlyph)
        self.actionRemove_Glyph.triggered.connect(self.removeCurrentGlyph)
        self.actionExport_GLSL.triggered.connect(self.exportFont)

    def fileNew(self) -> None:
        self._fileName = None
        self._font = Font()

        self._updateGlyphTable()

    def fileSave(self) -> None:
        if not self._fileName:
            self.fileSaveAs()
            return

        with open(self._fileName, "wb") as f:
            f.write(self._font.toBytes())
            f.close()

    def fileSaveAs(self) -> None:
        (self._fileName, _) = QFileDialog.getSaveFileName(
            self,
            "Save font binary...",
            "~",
            "ALDI Pixel Font Files (*.apf)",
        )

        if self._fileName != "":
            self.fileSave()

    def fileOpen(self) -> None:
        (self._fileName, _) = QFileDialog.getOpenFileName(
            self,
            "Open font binary...",
            "~",
            "ALDI Pixel Font Files (*.apf)",
        )

        if self._fileName != "":
            with open(self._fileName, "rb") as f:
                self._font.fromBytes(f.read())
                f.close()

            self._updateGlyphTable()

    def exit(self) -> None:
        exit(0)

    def _updateGlyphTable(self) -> None:
        newModel = QStringListModel(map(
            lambda ordinal: chr(ordinal),
            self._font.ordinals(),
        ))
        newModel.dataChanged.connect(self._glyphTableEdited)
        self.listView.setModel(newModel)

        self.listView.selectionModel().selectionChanged.connect(self._glyphTableSelectionChanged)
        self.listView.selectionModel().select(self.listView.model().index(0), QItemSelectionModel.SelectionFlag.Select)

    def _glyphTableEdited(self,
        topLeft: QModelIndex,
        bottomRight: QModelIndex,
        roles: List[int] = [Qt.ItemDataRole.EditRole],
    ) -> None:
        if self._font.renameGlyph(self._font.ordinals()[topLeft.row()], ord(topLeft.model().data(topLeft, Qt.ItemDataRole.EditRole))):
            self._updateGlyphTable()

    def _glyphTableSelectionChanged(self,
        selected: QItemSelectionRange,
        deselected: QItemSelectionRange,
    ) -> None:
        selectedIndices = selected.indexes()
        
        if len(selectedIndices) == 0:
            return

        self.glyphEditor.setGlyph(self._font.glyphWithOrdinal(ord(selectedIndices[0].model().data(selectedIndices[0]))))

    def addGlyph(self) -> None:
        ordinal = self._font.addNewGlyph()
        
        if ordinal == -1:
            return

        self._updateGlyphTable()
        self.listView.selectionModel().select(self.listView.model().index(self._font.ordinals().index(ordinal)), QItemSelectionModel.SelectionFlag.Select)

    def removeCurrentGlyph(self) -> None:
        selectedIndices = self.listView.selectionModel().selection().indexes()

        if len(selectedIndices) == 0:
            return
        
        self._font.removeGlyph(ord(selectedIndices[0].model().data(selectedIndices[0])))
        self._updateGlyphTable()
        if self._font.glyphCount() > 0:
            self.listView.selectionModel().select(self.listView.model().index(0), QItemSelectionModel.SelectionFlag.Select)

    def _fontId(self, shaderFileName) -> None:
        return basename(shaderFileName).replace(' ', '_').replace('.', '_')

    def exportFont(self) -> None:
        (shaderFileName, _) = QFileDialog.getSaveFileName(
            self,
            "Export Font GLSL...",
            "font",
            "Fragment shaders (*.frag)",
        )

        if shaderFileName == "":
            return

        with open(shaderFileName, "wt") as f:
            f.write('''
uint {uniqueFontId}[{glyphCount}] = uint[{glyphCount}](
    {dataLines}
);

float d{uniqueFontId}(vec2 uv, int ordinal, float pixelSize) {{
    vec2 x = mod(uv, pixelSize) - .5*pixelSize,
        xij = (uv - x)/pixelSize;
        
    if(any(lessThan(xij, vec2(0))) || any(greaterThanEqual(xij, vec2({width},{height}))))
        return 1.;

    if(bool((font_frag[ordinal - {firstOrdinal}] >> ({width}u * (uint(xij.y) + 1u) + 1u - uint(xij.x))) & 1u))
        return -1.;

    return 1.;
}}

void mainImage(out vec4 fragColor, vec2 fragCoord) {{
    vec2 uv = (fragCoord-.5*iResolution.xy)/iResolution.y;
    fragColor = vec4(1);
    fragColor.rgb = mix(fragColor.rgb, vec3(0), step(d{uniqueFontId}(uv, 35, .05), 0.));
}}
'''.format(
    uniqueFontId = self._fontId(shaderFileName),
    glyphCount = self._font.glyphCount(),
    dataLines = ',\n    '.join(map(
        lambda chunk: ', '.join(map(
            lambda glyph: '{}u'.format(glyph.toUnsignedInt()),
            chunk,
        )),
        self._font.chunks(4),
    )),
    width = Glyph.Width,
    height = Glyph.Height,
    firstOrdinal = self._font.ordinals()[0],
))
            f.close()

if __name__ == '__main__':
    app = QApplication(argv)

    fontEditor = FontEditor()
    fontEditor.show()

    app.exec()
