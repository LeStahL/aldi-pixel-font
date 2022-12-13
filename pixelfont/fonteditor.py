from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6 import uic
from typing import Optional, List
from sys import argv
from glypheditor import GlyphEditor
from font import Font

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

    def fileNew(self) -> None:
        self._fileName = None
        self._font = Font()

        self._updateGlyphTable()

    def fileSave(self) -> None:
        if not self._fileName:
            self.fileSaveAs()

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
        self._updateGlyphTable()
        self.listView.selectionModel().select(self.listView.model().index(self._font.ordinals().index(ordinal)), QItemSelectionModel.SelectionFlag.Select)

    def removeCurrentGlyph(self) -> None:
        pass

if __name__ == '__main__':
    app = QApplication(argv)

    fontEditor = FontEditor()
    fontEditor.show()

    app.exec()
