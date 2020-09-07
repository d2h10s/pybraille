import sys
import threading
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, qApp, QWidget, QDesktopWidget
from PyQt5.QtWidgets import QLabel, QTextEdit, QVBoxLayout, QHBoxLayout, QPlainTextEdit
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QDateTime, Qt
from libpkg import tts
from translator import kor_to_braille



class centWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    def initUI(self):
        # >>> text editor settings
        self.te = QTextEdit()
        self.te.setAcceptRichText(False)
        self.lbl_textCnt = QLabel('0 자')
        self.te.textChanged.connect(self.text_changed)

        self.bte = QTextEdit()
        self.bte.setAcceptRichText(False)

        self.textHBox = QHBoxLayout()
        self.textHBox.addWidget(self.te)
        self.textHBox.addWidget(self.bte)

        self.textVBox = QVBoxLayout()
        self.textVBox.addLayout(self.textHBox)
        self.textVBox.addWidget(self.lbl_textCnt, alignment=Qt.AlignRight)

        self.mainHBox = QHBoxLayout()
        self.mainHBox.addLayout(self.textVBox)
        self.setLayout(self.mainHBox)
        # <<< text editor settings

    def text_changed(self):
        text =  self.te.toPlainText()
        self.lbl_textCnt.setText(str(len(text))+' 자')
        try:
            self.bte.setText(self.braille_str(kor_to_braille.translate(self.te.toPlainText())))
        except:
            pass

    def to_braille(self, json):
        return json["braille"]

    def braille_str(self, json):
       json_format_braille = json
       return "".join(list(map(self.to_braille, json_format_braille)))

class mainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Dot  ::  designed by d2h10s') # set window title
        self.setWindowIcon(QIcon('icon/printer.png')) # set window icon

        self.statusBar().showMessage('Ready') # set status bar message

        # >>> Program exit Action
        exitAction = QAction(QIcon('icon/exit.png'), '종료', self)
        exitAction.setShortcut('Alt+Q')
        exitAction.setStatusTip('프로그램 종료')
        exitAction.triggered.connect(qApp.quit)
        # <<< Program exit Action

        # >>> text Save Action
        saveAction = QAction(QIcon('icon/save.png'), '저장', self)
        saveAction.setShortcut('Ctrl+s')
        saveAction.setShortcut('Alt+s')
        saveAction.setStatusTip('텍스트 저장')
        saveAction.triggered.connect(self.text_save)
        # >>> menu bar settings
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        filemenu = menubar.addMenu('&File')
        filemenu.addAction(exitAction)
        # <<< menu bar settings

        # >>> tool bar settings
        self.toolbar = self.addToolBar('종료')
        self.toolbar.addAction(exitAction)
        # <<< tool bar settings

        # >>> Thread Setting
        # if thread is daemon thread, when main thread is terminated immediately daemon thread is killed regardless of end of task
        t1 = threading.Thread(target=self.showDate)
        t1.daemon = True # make t1 thread daemon thread
        t1.start()
        # <<< Thread Setting

        self.setCentralWidget(centWidget())
        self.resize(1280, 720) # set window size
        self.center() # make window center
        self.show()

    def center(self):
        qr = self.frameGeometry() # get position and size of window in rect structure
        cp = QDesktopWidget().availableGeometry().center() # get center of monitor in point structure
        qr.moveCenter(cp) # move window to monitor's center
        self.move(qr.topLeft()) # move window to monitor's center

    def showDate(self):
        # if you use timer instead of sleep, the app may crash
        while True:
            self.statusBar().showMessage(QDateTime.currentDateTime().toString(Qt.DefaultLocaleLongDate))
            time.sleep(0.9)

    def text_save(self):
        


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = mainWindow()
    sys.exit(app.exec_())


text ="애미야 국이짜다 Amy, Soup is so solty"
tts.text2speech(text)