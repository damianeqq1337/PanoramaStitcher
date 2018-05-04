import sys
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog, QMessageBox
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.uic import loadUi
from ShowWindow import ShowWindow
from Stitcher import Stitcher

class StitcherMainWindow(QDialog):
    def __init__(self):
        #self.imagesToStitch = []
        super(StitcherMainWindow, self).__init__()
        #design
        loadUi('StitcherMainWindow.ui', self)
        self.setWindowTitle('Panorama Stitcher')
        self.upButton.setText(u'\u25b2')
        self.downButton.setText(u'\u25bc')
        self.delButton.setText(u'\u2717')
        self.delButton.setStyleSheet('QPushButton {color: red;}')
        self.progressBar.setValue(0)
        self.disableButtons()     
        #actions
        self.loadImagesButton.clicked.connect(self.openFileNamesDialog)
        self.savePathButton.clicked.connect(self.changeSavePath)
        self.mergeButton.clicked.connect(self.runStitcher)
        self.fileListWidget.itemDoubleClicked.connect(self.openImage)
        self.upButton.clicked.connect(self.moveUpItem)
        self.downButton.clicked.connect(self.moveDownItem)
        self.delButton.clicked.connect(self.deleteSelectedItemFromListWidget)
        
    @pyqtSlot()
    def openFileNamesDialog(self):    
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _filter = QFileDialog.getOpenFileNames(self,"Load Images", "./","JPG Files (*.jpg);;PNG Files (*.png);;JPEG Files (*.jpeg)", options=options)
        if files:
            self.addFileToListView(files)

    def addFileToListView(self, files):
        self.fileListWidget.addItems(files)
        self.imageCountLabel.setText(str(self.fileListWidget.count()))
        self.enableButtons()
        
    def openImage(self, path):
        func = ShowWindow(path.text())
        func.showImage()

    def changeSavePath(self):
        fileName = QFileDialog.getExistingDirectory(self, 'Set save directory')
        self.savePathLineEdit.setText(fileName)
    
    def runStitcher(self):
        stitcher = Stitcher()
        items = self.getAllItemsFromListWidget()
        if len(items) < 2:
            self.showMessageBox("Niewystarczająca liczba zdjęć do uruchomienia programu")
        else:
            stitcher.runStitcher(items)

    def moveUpItem(self):
        currentRow = self.fileListWidget.currentRow()
        currentItem = self.fileListWidget.takeItem(currentRow)
        self.fileListWidget.insertItem(currentRow - 1, currentItem)
        self.fileListWidget.setCurrentRow(currentRow - 1)

    def moveDownItem(self):
        currentRow = self.fileListWidget.currentRow()
        currentItem = self.fileListWidget.takeItem(currentRow)
        self.fileListWidget.insertItem(currentRow + 1, currentItem)
        self.fileListWidget.setCurrentRow(currentRow + 1)

    def getAllItemsFromListWidget(self):
        items = []
        for x in range(self.fileListWidget.count()):
            items.append(self.fileListWidget.item(x).text())
        return items

    def deleteSelectedItemFromListWidget(self):
        self.fileListWidget.takeItem(self.fileListWidget.currentRow())
        imagesCount = self.fileListWidget.count()
        self.imageCountLabel.setText(str(imagesCount))
        if imagesCount == 0:
            self.disableButtons()

    def enableButtons(self):
        self.delButton.setEnabled(True)
        self.downButton.setEnabled(True)
        self.upButton.setEnabled(True)
        self.mergeButton.setEnabled(True)
        self.progressBar.setEnabled(True)
        
    def disableButtons(self):
        self.delButton.setEnabled(False)
        self.downButton.setEnabled(False)
        self.upButton.setEnabled(False)
        self.mergeButton.setEnabled(False)
        self.progressBar.setEnabled(False)

    def showMessageBox(self, text):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(text)
        msg.setWindowTitle("Błąd!")
        msg.setStandardButtons(QMessageBox.Ok)
        retval = msg.exec_()

app=QApplication(sys.argv)
widget=StitcherMainWindow()
widget.show()
sys.exit(app.exec_())