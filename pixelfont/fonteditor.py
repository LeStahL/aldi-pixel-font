from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6 import uic
from typing import Optional, List
from sys import argv
from glypheditor import GlyphEditor
from font import Font
from glyph import Glyph
from text import Text
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
        self.actionAdd_Line.triggered.connect(self.addLine)
        self.actionSave_Text_As.triggered.connect(self.saveTextAs)
        self.actionLoad_Text.triggered.connect(self.loadText)

    def fileNew(self) -> None:
        self._fileName = None
        self._font = Font()
        self._text = Text()

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
        if self.listView.hasFocus():
            selectedIndices = self.listView.selectionModel().selection().indexes()

            if len(selectedIndices) == 0:
                return

            self._font.removeGlyph(ord(selectedIndices[0].model().data(selectedIndices[0])))
            self._updateGlyphTable()
            if self._font.glyphCount() > 0:
                self.listView.selectionModel().select(self.listView.model().index(0), QItemSelectionModel.SelectionFlag.Deselect)
                self.listView.selectionModel().select(self.listView.model().index(max(selectedIndices[0].row() - 1, 0)), QItemSelectionModel.SelectionFlag.Select)
        elif self.listView_2.hasFocus():
            selectedIndices = self.listView_2.selectionModel().selection().indexes()

            if len(selectedIndices) == 0:
                return

            del self._text._lines[selectedIndices[0].row()]

            self.updateTextTable()

            if self._text.lineCount() > 0:
                self.listView_2.selectionModel().select(self.listView_2.model().index(0), QItemSelectionModel.SelectionFlag.Deselect)
                self.listView_2.selectionModel().select(self.listView_2.model().index(max(selectedIndices[0].row() - 1, 0)), QItemSelectionModel.SelectionFlag.Select)

    def _fontId(self, shaderFileName) -> None:
        return basename(shaderFileName).replace(' ', '_').replace('.', '_')

    def _alignWidth(self, numberString: str) -> str:
        return ' '*(11-len(numberString)) + numberString

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
            f.write('''// Generated by the ALDI Pixel Font Editor (c) 2022 Alexander Kraus <nr4@z10.info>.
// Find a convenient font and text database editor at: https://github.com/LeStahL/aldi-pixel-font.
uint {uniqueFontId}[{glyphCount}] = uint[{glyphCount}](
    {dataLines}
);

uint {uniqueFontId}_text_offsets[{textCount}] = uint[{textCount}](
    {textOffsetLines}
);

uint {uniqueFontId}_text_strings[{textDataSize}] = uint[{textDataSize}](
    {textDataLines}
);

float d{uniqueFontId}(vec2 uv, uint ordinal, float pixelSize) {{
    vec2 xij = (uv - mod(uv, pixelSize) + .5*pixelSize)/pixelSize;
    return !(any(lessThan(xij, vec2(0))) || any(greaterThanEqual(xij, vec2({width},{height})))) && bool(({uniqueFontId}[ordinal - {firstOrdinal}u] >> ({width}u * (uint(xij.y) + 1u) + 1u - uint(xij.x))) & 1u) ? -1. : 1.;
}}

uint decode_single(uint byteIndex, uint data) {{
    return (data >> (8u * byteIndex)) & 0xffu;
}}

uvec2 localIndices(uint globalByteIndex) {{
    uint localByteIndex = globalByteIndex % 4u,
        globalIntegerIndex = (globalByteIndex - localByteIndex) / 4u;
    return uvec2(globalIntegerIndex, localByteIndex);
}}

float d{uniqueFontId}_text(vec2 uv, uint index, float pixelSize) {{
    float glyphSize = {widthPlusOne}.*pixelSize,
        x = mod(uv.x, glyphSize),
        xi = (uv.x - x)/glyphSize;
       
    uvec2 localTextIndices = localIndices({uniqueFontId}_text_offsets[index]);
    uint textSize = decode_single(localTextIndices.y, {uniqueFontId}_text_strings[localTextIndices.x]);
    localTextIndices = localIndices({uniqueFontId}_text_offsets[index] + uint(xi) + 1u);
    return (xi < 0. || xi >= float(textSize) || abs(uv.y-.5*{height}.*pixelSize) > {height}.*pixelSize) ? 1. : d{uniqueFontId}(vec2(x, uv.y), decode_single(localTextIndices.y, {uniqueFontId}_text_strings[localTextIndices.x]), pixelSize);
}}

uint log10(uint v) {{
    return v < 10u ? 1u
        : v < 100u ? 2u
        : v < 1000u ? 3u
        : v < 10000u ? 4u
        : v < 100000u ? 5u
        : v < 1000000u ? 6u
        : v < 10000000u ? 7u
        : v < 100000000u ? 8u
        : 9u;
}}

uint pow10(uint v) {{
    return v == 0u ? 1u
        : v == 1u ? 10u
        : v == 2u ? 100u
        : v == 3u ? 1000u
        : v == 4u ? 10000u
        : v == 5u ? 100000u
        : v == 6u ? 1000000u
        : v == 7u ? 10000000u
        : v == 8u ? 100000000u
        : 1000000000u;
}}

float d{uniqueFontId}_uint(vec2 uv, uint number, float pixelSize) {{
    uint numberWidth = max(log10(number), 1u);

    float glyphSize = {widthPlusOne}. * pixelSize,
        x = mod(uv.x, glyphSize),
        xi = (uv.x - x) / glyphSize + float(10u - numberWidth);

    uint digitIndex = uint(xi),
        digit = number / pow10(9u - digitIndex);
        
    return xi < 0. || xi > 9. || abs(uv.y-.5*glyphSize) > 6.*pixelSize || digitIndex < 10u - numberWidth
        ? 1.
        : d{uniqueFontId}(vec2(x, uv.y), 48u + digit % 10u, pixelSize);
}}

float d{uniqueFontId}_int(vec2 uv, int number, float pixelSize) {{
    float glyphSize = {widthPlusOne}. * pixelSize,
        x = mod(uv.x, glyphSize),
        xi = (uv.x - x) / glyphSize;

    return uint(xi) == 0u && number < 0
        ? d{uniqueFontId}(uv, 45u, pixelSize)
        : d{uniqueFontId}_uint(uv - vec2(glyphSize*float(number < 0),0.), uint(abs(number)), pixelSize);
}}

float d{uniqueFontId}_float(vec2 uv, float number, uint _precision, float pixelSize) {{
    float glyphSize = {widthPlusOne}. * pixelSize,
        x = mod(uv.x, glyphSize),
        xi = (uv.x - x) / glyphSize;

    if(uint(xi) == 0u && number < 0.)
        return d{uniqueFontId}(uv, 45u, pixelSize);

    uv.x -= glyphSize * float(number < 0.);
    number = abs(number);

    int exponent = number == 0. ? 0 : int(floor(log(number)/log(10.)));

    x = mod(uv.x, glyphSize);
    xi = (uv.x - x) / glyphSize;

    return uint(xi) == 0u
        ? d{uniqueFontId}(vec2(x, uv.y), 48u + uint(floor(number/pow(10., float(exponent)))) % 10u, pixelSize)
        : uint(xi) == 1u
            ? d{uniqueFontId}(vec2(x, uv.y), 46u, pixelSize)
            : uint(xi) < _precision + 1u
                ? d{uniqueFontId}(vec2(x, uv.y), 48u + uint(floor(number/pow(10., float(exponent)-xi+1.))) % 10u, pixelSize)
                : uint(xi) == _precision + 1u
                    ? d{uniqueFontId}(vec2(x, uv.y), 69u, pixelSize)
                    : d{uniqueFontId}_int(vec2(uv.x - float(_precision + 2u) * glyphSize, uv.y), exponent, pixelSize);
}}

void mainImage(out vec4 fragColor, vec2 fragCoord) {{
    vec2 uv = (fragCoord-.5*iResolution.xy)/iResolution.y;
    fragColor = vec4(1);
    fragColor.rgb = mix(fragColor.rgb, vec3(0), step(d{uniqueFontId}(uv+vec2(.5*iResolution.x/iResolution.y,0.)-7.*.01*vec2(0.,1.), 66u, .01), 0.));
    fragColor.rgb = mix(fragColor.rgb, vec3(0), step(d{uniqueFontId}_text(uv+vec2(.5*iResolution.x/iResolution.y,0.), 0u, .005), 0.));
    fragColor.rgb = mix(fragColor.rgb, vec3(0), step(d{uniqueFontId}_uint(uv+vec2(.5*iResolution.x/iResolution.y,0.)+7.*.01*vec2(0.,1.), uint(iFrame), .01), 0.));
    fragColor.rgb = mix(fragColor.rgb, vec3(0), step(d{uniqueFontId}_int(uv+vec2(.5*iResolution.x/iResolution.y,0.)+7.*.01*vec2(0.,2.), int(-iFrame), .01), 0.));
    fragColor.rgb = mix(fragColor.rgb, vec3(0), step(dfont_frag_float(uv+vec2(.5*iResolution.x/iResolution.y,0.)+7.*.01*vec2(0.,3.), iTime, 5u, .01), 0.));
}}

'''.format(
    uniqueFontId = self._fontId(shaderFileName),
    glyphCount = self._font.glyphCount(),
    dataLines = ',\n    '.join(map(
        lambda chunk:  '/** {:4} **/ '.format(''.join(map(
            lambda glyph: chr(glyph._ordinal),
            chunk,
        ))) + ', '.join(map(
            lambda glyph: self._alignWidth('{}u'.format(glyph.toUnsignedInt())),
            chunk,
        )),
        self._font.chunks(4),
    )),
    width = Glyph.Width,
    widthPlusOne = Glyph.Width + 1,
    height = Glyph.Height,
    firstOrdinal = self._font.ordinals()[0],
    textCount = self._text.lineCount(),
    textOffsetLines = ',\n    '.join(map(
        lambda chunk:  ', '.join(map(
            lambda num: self._alignWidth('{}u'.format(num)),
            chunk,
        )),
        self._text.offsetChunks(4),
    )),
    textDataSize = len(self._text.toUnsignedIntegerArray()),
    textDataLines = ',\n    '.join(map(
        lambda chunk:  '/** {:16} **/ '.format(''.join(map(
            lambda num: ''.join(map(chr, Text.BinaryDecodeFormat.parse(Text.BinaryExportFormat.build([num])))),
            chunk,
        ))).replace('\n', ' ').replace('\t', ' ').replace('\r', ' ').replace('\0', ' ') + ', '.join(map(
            lambda num: self._alignWidth('{}u'.format(num)),
            chunk,
        )),
        self._text.chunks(4),
    )),
))
            f.close()

    def addLine(self):
        if self.lineEdit.text() != "":
            self._text.add(self.lineEdit.text())
            self.lineEdit.setText("")

        self.updateTextTable()

    def updateTextTable(self):
        newModel = QStringListModel(self._text._lines)
        newModel.dataChanged.connect(self._textTableChanged)
        self.listView_2.setModel(newModel)

    def _textTableChanged(self,
        topLeft: QModelIndex,
        bottomRight: QModelIndex,
        roles: List[int] = [Qt.ItemDataRole.EditRole],
    ) -> None:
        self._text._lines[topLeft.row()] = topLeft.model().data(topLeft, Qt.ItemDataRole.EditRole)

    def saveTextAs(self):
        (textFileName, _) = QFileDialog.getSaveFileName(
            self,
            "Export Text Table...",
            "table",
            "ALDI Text Tables (*.att)",
        )

        if textFileName == "":
            return

        with open(textFileName, "wb") as f:
            f.write(self._text.toBytes())
            f.close()

    def loadText(self):
        (textFileName, _) = QFileDialog.getOpenFileName(
            self,
            "Export Text Table...",
            "table",
            "ALDI Text Tables (*.att)",
        )

        if textFileName == "":
            return

        with open(textFileName, "rb") as f:
            self._text.fromBytes(f.read())
            f.close()

        self.updateTextTable()

if __name__ == '__main__':
    app = QApplication(argv)

    fontEditor = FontEditor()
    fontEditor.show()

    app.exec()
