from PyQt5.QtWidgets import *
import sys

class next_page(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Waitting for Next Page')
        self.center()
        self.resize(300, 200)
        self.show()
        self.btn = QPushButton(self)
        self.btn.setText('Next Page')
        self.btn.clicked.connect(qApp.quit)

        self.mlay = QVBoxLayout()
        self.mlay.addWidget(self.btn)
        self.setLayout(self.mlay)

    def center(self):
        qr = self.frameGeometry() # get position and size of window in rect structure
        cp = QDesktopWidget().availableGeometry().center() # get center of monitor in point structure
        qr.moveCenter(cp) # move window to monitor's center
        self.move(qr.topLeft()) # move window to monitor's center


app = QApplication(sys.argv)
a = next_page()
print('hello')
app.exec_()
print('hello')