import sys, os, threading, time
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, qApp, QWidget, QDesktopWidget
from PyQt5.QtWidgets import QLabel, QTextEdit, QVBoxLayout, QHBoxLayout, QFileDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QDateTime, Qt
from libpkg import tts
from translator import kor_to_braille

lock = threading.Lock()

class centWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    def initUI(self):
        # >>> text editor settings
        self.te = QTextEdit()
        self.te.setAcceptRichText(False)
        self.lbl_teCnt = QLabel('0 자')
        self.lbl_bteCnt = QLabel('0 자')
        self.te.textChanged.connect(self.text_changed)

        self.bte = QTextEdit()
        self.bte.setReadOnly(True)

        self.teVBox = QVBoxLayout()
        self.teVBox.addWidget(self.te)
        self.teVBox.addWidget(self.lbl_teCnt, alignment=Qt.AlignLeft)

        self.bteVBox = QVBoxLayout()
        self.bteVBox.addWidget(self.bte)
        self.bteVBox.addWidget(self.lbl_bteCnt, alignment=Qt.AlignRight)

        self.textHBox = QHBoxLayout()
        self.textHBox.addLayout(self.teVBox)
        self.textHBox.addLayout(self.bteVBox)

        self.mainHBox = QHBoxLayout()
        self.mainHBox.addLayout(self.textHBox)
        self.setLayout(self.mainHBox)
        # <<< text editor settings

    def text_changed(self):
        self.lbl_teCnt.setText(str(len(self.te.toPlainText())) + ' 자')
        self.lbl_bteCnt.setText(str(len(self.bte.toPlainText())) + '자')
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

        self.statMsg = 'Ready'
        self.timeMsg = QDateTime.currentDateTime().toString(Qt.DefaultLocaleLongDate)
        self.statusBar().showMessage(self.timeMsg + self.statMsg) # set status bar message

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
        # <<< text Save Action

        # >>> TTS Action
        ttsAction = QAction(QIcon('icon/tts.png'), 'TTS', self)
        ttsAction.setShortcut('Ctrl+t')
        ttsAction.setStatusTip('입력한 텍스트를 음성으로 읽기')
        ttsAction.triggered.connect(self.tts)
        # <<< TTS Action

        # >>> menu bar settings
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        filemenu = menubar.addMenu('&File')
        filemenu.addAction(exitAction)
        filemenu.addAction(saveAction)
        filemenu.addAction(ttsAction)
        # <<< menu bar settings

        # >>> tool bar settings
        self.toolbar = self.addToolBar('종료')
        self.toolbar.addAction(exitAction)
        self.toolbar.addAction(saveAction)
        self.toolbar.addAction(ttsAction)
        # <<< tool bar settings

        # >>> Thread Setting
        # if thread is daemon thread, when main thread is terminated immediately daemon thread is killed regardless of end of task
        t1 = threading.Thread(target=self.showDate)
        t1.daemon = True # make t1 thread daemon thread
        t1.start()
        # <<< Thread Setting

        self.centralWidget = centWidget()
        self.setCentralWidget(self.centralWidget)
        self.resize(1280, 720) # set window size
        self.center() # make window center
        self.show()

    def center(self):
        qr = self.frameGeometry() # get position and size of window in rect structure
        cp = QDesktopWidget().availableGeometry().center() # get center of monitor in point structure
        qr.moveCenter(cp) # move window to monitor's center
        self.move(qr.topLeft()) # move window to monitor's center

    def showDate(self):
        lock.acquire()
        # if you use timer instead of sleep, the app may crash
        while True:
            self.timeMsg = QDateTime.currentDateTime().toString(Qt.DefaultLocaleLongDate)
            self.statusBar().showMessage(self.timeMsg + '\t' + self.statMsg)
            time.sleep(0.9)
        lock.release()

    def text_save(self):
        desktopAddr = os.path.join(os.path.expanduser('~'),'Desktop') # get user's destop address regardless of os
        fname, _ = QFileDialog.getSaveFileName(self, caption='Save File', directory=desktopAddr)
        if not fname:
            self.statMsg = '저장을 실패하였습니다.'
            return
        with open(file=fname, mode='w') as f:
            f.write(self.centralWidget.te.toPlainText())
        self.statMsg = '저장을 성공하였습니다.'

    def tts(self):
        tts.text2speech(self.centralWidget.te.toPlainText())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = mainWindow()
    sys.exit(app.exec_())


text ="애미야 국이짜다 Amy, Soup is so solty"
tts.text2speech(text)