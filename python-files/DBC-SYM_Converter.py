import sys
import os
import cantools

from PySide6 import QtWidgets
from PySide6.QtCore import (
    QFileInfo,
    QUrl
)
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QMessageBox,
    QPushButton,
    QLineEdit,
    QLabel,
    QDialogButtonBox,
    QFileDialog,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox
)


class MyWidget(QtWidgets.QWidget) :
    def __init__(self):
        super().__init__()

        self.file_info = QFileInfo("")

        SearchButton = QPushButton("Parcourir...")
        self.pathFile = QLineEdit(self.file_info.absoluteFilePath())
        self.console = QLabel("")
        button_box = QDialogButtonBox()
        button_box.addButton(QPushButton("Convertir"), QDialogButtonBox.ButtonRole.AcceptRole)
        button_box.addButton(QPushButton("Fermer"), QDialogButtonBox.ButtonRole.RejectRole)
        self.OpenExploButton = QPushButton("Trouver")

        FileGroup = QGroupBox("Fichier")
        FileLayout = QHBoxLayout()
        FileLayout.addWidget(self.pathFile)
        FileLayout.addWidget(SearchButton)
        FileGroup.setLayout(FileLayout)
        WindowLayout = QVBoxLayout(self)
        WindowLayout.addWidget(FileGroup)
        self.ConsoleGrp = QGroupBox("Console")
        OneWidget = QVBoxLayout()
        OneWidget.addWidget(self.console)
        self.ConsoleGrp.setLayout(OneWidget)
        WindowLayout.addWidget(self.ConsoleGrp)
        CmdLayout = QHBoxLayout()
        CmdLayout.addWidget(self.OpenExploButton)
        CmdLayout.addWidget(button_box)
        WindowLayout.addLayout(CmdLayout)

        self.ConsoleGrp.hide()
        SearchButton.clicked.connect(self.FileExplorer)
        self.pathFile.editingFinished.connect(self.PathExplorer)
        button_box.accepted.connect(self.CANConvert)
        button_box.rejected.connect(self.close)
        self.OpenExploButton.clicked.connect(self.findInExplorer)
        self.OpenExploButton.hide()

    def printConsole(self, msg:str) :
        self.ConsoleGrp.show()
        self.console.setText(self.console.text()+msg+"\n")

    def FileExplorer(self) :
        self.OpenExploButton.hide()
        FilePath, Extensions = QFileDialog.getOpenFileName(self, "Ouvrir fichier CAN", "Documents", "CAN Files (*.dbc *.sym)")
        self.file_info = QFileInfo(FilePath)
        self.pathFile.setText(self.file_info.absoluteFilePath())

    def PathExplorer(self) :
        self.OpenExploButton.hide()
        EditedText = self.pathFile.text()
        if os.path.exists(EditedText) :
            self.file_info = QFileInfo(EditedText)
        else :
            QMessageBox.warning(self, "Fichier introuvable",
                                "Le fichier semble introuvable. Vérifiez le chemin d'accès."
                               )
            self.pathFile.redo()
            self.printConsole("Vérifiez le chemin d'accès du fichier.")
    
    def findInExplorer(self) : QDesktopServices.openUrl(QUrl("file:///" + self.file_info.absolutePath()))

    def CANConvert(self) :
        CanFile = cantools.database.Database()

        fileAbsolutePath = self.file_info.absoluteFilePath()
        fileExtension = self.file_info.suffix()

        if fileExtension == "dbc" :
            self.printConsole("Fichier DBC détecté. Conversion vers SYM en cours...")

            CanFile.add_dbc_file(fileAbsolutePath)
            fileOutput = fileAbsolutePath[:-3]+"sym"

            if os.path.isfile(fileOutput) :
                self.printConsole("Fichier déjà existant.")
                rt_wrn = QMessageBox.warning(self, "Fichier existant",
                                            "Un fichier de ce nom existe déjà. Souhaitez-vous l'écraser ?",
                                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                            QMessageBox.StandardButton.No
                                            )
                if rt_wrn == QMessageBox.StandardButton.No :
                    self.printConsole("Opération annulée.")
                    return
                else :
                    self.printConsole("Réécriture du fichier.")
                
            symString = CanFile.as_sym_string()
            anyMatchVal = True
            while anyMatchVal :
                anyMatchVal = False
                signals = []
                for line in symString.split("\n") :
                    matchVal = True
                    for val in ['FormatVersion=', 'Title=', 'Enum=', 'Sig=', 'ID=', 'Type=', 'Len=', 'CycleTime=', '{', '['] :
                        if line.find(val) != -1 or line == "" :
                            signals.append(line)
                            matchVal = False
                            break
                    if matchVal :
                        anyMatchVal = True
                        signals[-1] = " ".join([signals[-1], line])
                symString = "\n".join(signals)

            try :
                with open (fileOutput, 'w') as f :
                    f.write(symString)
            except Exception :
                QMessageBox.critical(self, "Erreur critique", "Erreur durant l'écriture.")
                self.printConsole("Erreur durant l'écriture du fichier \""+fileOutput+"\" :\n" + Exception)
                os.remove(fileOutput)
                return
        else :
            QMessageBox.warning(self, "Erreur", "Format de fichier non pris en charge.")
            self.printConsole("Choisissez un fichier DBC ou SYM à convertir.")
            return
        
        self.printConsole("Conversion terminée du fichier \""+fileOutput+"\".")
        self.OpenExploButton.show()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MyWidget()
    widget.setWindowTitle("Convertisseur DBC-SYM")
    widget.resize(600, 112)
    widget.show()

    sys.exit(app.exec())
