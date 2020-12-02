import sys, os, threading
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import QDateTime, Qt, QSize, QTimer
from playsound import playsound

from translator.kor_to_braille import translate
from translator.tts import text2speech
from translator.Communication import Data_Send

lock = threading.Lock()

baud = 9600
txtEncoding = 'UTF-8'

class historyWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('TTS Player')
        self.fname = 'data/TTS'
        self.isfile = [False] * 11
        self.cb = QComboBox(self)
        for fidx in range(1, 11):
            if os.path.isfile(self.fname + str(fidx) + '.mp3'):
                self.isfile[fidx] = True
                self.cb.addItem('TTS' + str(fidx) + '.mp3')
        self.cb.activated[str].connect(self.onActivated)
        self.lbl_front = QLabel('현재 저장되어 있는 tts 기록: ', self)

        self.lbl_caution = QLabel('※1번이 가장 최근의 TTS 파일입니다.', self)

        self.btn_play = QPushButton('', self)
        self.btn_play.setIcon(QIcon('icon/play.png'))
        self.btn_play.setIconSize(QSize(40, 40))
        self.btn_play.setStyleSheet('QPushButton{border: 0px solid;}')
        self.btn_play.clicked.connect(self.play)

        self.vlay = QVBoxLayout()
        self.hlay = QHBoxLayout()
        self.hlay.addWidget(self.lbl_front)
        self.hlay.addWidget(self.cb)
        self.hlay.addWidget(self.btn_play)

        self.vlay.addLayout(self.hlay)
        self.vlay.addWidget(self.lbl_caution)
        self.setLayout(self.vlay)
        self.setFixedSize(680, 100)  # set window size
        mainWindow.center(self)
        self.show()

    def onActivated(self, text):
        self.fname = text
        print(self.fname)

    def play(self):
        if not 'mp3' in self.fname:
            print('no file error')
            return
        # >>> Thread Setting
        # if thread is daemon thread, when main thread is terminated immediately daemon thread is killed regardless of end of task
        self.t1 = threading.Thread(target=self.play_music)
        self.t1.daemon = True  # make t1 thread daemon thread
        # <<< Thread Setting
        self.t1.start()

    def pause(self):
        pass

    def stop(self):
        pass

    def play_music(self):
        print('thread start')
        lock.acquire()
        playsound('data/' + self.fname)
        lock.release()
        print('thread exit')


class centWidget(QWidget):
    def __init__(self):
        super().__init__()

        # >>> text editor settings
        self.te = QTextEdit()
        self.te.setAcceptRichText(False)
        self.lbl_teCnt = QLabel('0 자', self)
        self.lbl_bteCnt = QLabel('0 자', self)
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
        try:
            self.bte.setText(translate(self.te.toPlainText()))
        except:
            pass
        self.lbl_teCnt.setText(str(len(self.te.toPlainText())) + ' 자')
        self.lbl_bteCnt.setText(str(len(self.bte.toPlainText())) + '자')


class mainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Dot  ::  designed by d2h10s') # set window title
        self.setWindowIcon(QIcon('icon/printer.png')) # set window icon

        # >>> status bar setting
        self.statMsg = 'Ready'
        self.timeMsg = QDateTime.currentDateTime().toString(Qt.DefaultLocaleLongDate)
        self.statusBar().showMessage(self.timeMsg + '                    ' + self.statMsg) # set status bar message
        # <<< status bar setting

        # >>> font object
        self.fsize = 10
        self.font = QFont()
        self.font.setPointSize(self.fsize)
        # <<< font object

        # >>> font size label settings
        self.lbl_fsize = QLabel('10', self)
        self.lbl_fsize.setFont(QFont("consolas", 14, QFont.Bold))
        self.lbl_fsize.setFixedWidth(50)
        self.lbl_fsize.setAlignment(Qt.AlignCenter)
        self.lbl_fsize.setStyleSheet("background-color: #FFFFFF;"
                                     "border-style: solid;"
                                     "order-color: #FFFFFF;"
                                     "border-width: 2px;"
                                     "border-radius: 3px;")
        # <<< font size label settings

        # >>> Timer Settings, interval is 900ms
        self.timer = QTimer(self)
        self.timer.setInterval(900)
        self.timer.timeout.connect(self.showDate)
        self.timer.start()
        # <<< Timer Settings

        # >>> Program exit Action
        exitAction = QAction(QIcon('icon/exit.png'), '종료', self)
        exitAction.setShortcut('Alt+Q')
        exitAction.setStatusTip('프로그램 종료')
        exitAction.triggered.connect(qApp.quit)
        # <<< Program exit Action

        # >>> text open Action
        openAction = QAction(QIcon('icon/open.png'), '열기', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('텍스트 열기(.txt 확장자만 가능합니다.)')
        openAction.triggered.connect(self.text_open)
        # <<< text open Action

        # >>> text Save Action
        saveAction = QAction(QIcon('icon/save.png'), '저장', self)
        saveAction.setShortcut('Ctrl+s')
        saveAction.setStatusTip('텍스트 저장')
        saveAction.triggered.connect(self.text_save)
        # <<< text Save Action

        # >>> TTS Action
        ttsAction = QAction(QIcon('icon/tts.png'), 'TTS', self)
        ttsAction.setShortcut('Ctrl+t')
        ttsAction.setStatusTip('입력한 텍스트를 음성으로 읽습니다.')
        ttsAction.triggered.connect(self.tts_btn)
        # <<< TTS Action

        # >>> TTS History Action
        ttshisAction = QAction(QIcon('icon/history.png'), '기록', self)
        ttshisAction.setShortcut('Ctrl+h')
        ttshisAction.setStatusTip('최근 10개의 TTS 히스토리를 볼 수 있습니다.')
        ttshisAction.triggered.connect(self.history)
        # <<< TTS History Action

        # >>> font size Action
        fdecAction = QAction(QIcon('icon/down.png'), '글자 크기 감소', self)
        fdecAction.setShortcut('Ctrl+1')
        fdecAction.setStatusTip('텍스트 에디터의 폰트 사이즈를 줄입니다.')
        fdecAction.triggered.connect(self.font_dec)

        fincAction = QAction(QIcon('icon/up.png'), '글자 크기 증가', self)
        fincAction.setShortcut('Ctrl+2')
        fincAction.setStatusTip('텍스트 에디터의 폰트 사이즈를 키웁니다.')
        fincAction.triggered.connect(self.font_inc)
        # <<< font size Action

        # >>> print Action
        printAction = QAction(QIcon('icon/printer.png'), '점자 출력', self)
        printAction.setShortcut('Ctrl+p')
        printAction.setStatusTip('점자 프린터로 점자를 출력합니다.')
        printAction.triggered.connect(self.print)
        # <<< print Action

        # >>> BAUD COMB
        # self.bcb = QComboBox(self)
        # self.bcb.addItems(['9600', '19200', '38400', '115200'])
        # self.bcb.activated[str].connect(self.setBaudrate)
        # <<< BAUD COMB Action

        # >>> ENCODING COMB
        # self.ecb = QComboBox(self)
        # self.ecb.addItems(['UTF-8', 'ANSI'])
        # self.ecb.activated[str].connect(self.setEncoding)
        # <<< ENCODING COMB Action

        # >>> menu bar settings
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False) # to present same gui in Mac OS
        filemenu = menubar.addMenu('&File')
        filemenu.addAction(exitAction)
        filemenu.addAction(openAction)
        filemenu.addAction(saveAction)
        filemenu.addAction(printAction)

        editormenu = menubar.addMenu('&Editor') # editor menu
        editormenu.addAction(fincAction) # font size increase
        editormenu.addAction(fdecAction) # font size decrease

        voicemenu = menubar.addMenu('&Voice')
        voicemenu.addAction(ttsAction)
        voicemenu.addAction(ttshisAction)

        # <<< menu bar settings

        # >>> tool bar settings
        self.toolbar = self.addToolBar('home')
        self.toolbar.addAction(openAction)
        self.toolbar.addAction(saveAction)
        self.toolbar.addAction(ttsAction)
        self.toolbar.addAction(ttshisAction)
        self.toolbar.addWidget(QLabel('      ')) # Blank label
        self.toolbar.addAction(fdecAction)
        self.toolbar.addWidget(self.lbl_fsize)
        self.toolbar.addAction(fincAction)
        self.toolbar.addWidget(QLabel('      ')) # Blank label
        self.toolbar.addAction(printAction)
        # self.toolbar.addWidget(self.bcb)
        # self.toolbar.addWidget(self.ecb)
        # self.toolbar.addAction(printStopAction)
        # <<< tool bar settings

        self.centralWidget = centWidget()
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.te.setFont(self.font)
        self.centralWidget.bte.setFont(self.font)
        self.resize(1280, 720) # set window size
        self.center() # make window center
        self.show()

    def center(self):
        qr = self.frameGeometry() # get position and size of window in rect structure
        cp = QDesktopWidget().availableGeometry().center() # get center of monitor in point structure
        qr.moveCenter(cp) # move window to monitor's center
        self.move(qr.topLeft()) # move window to monitor's center

    def showDate(self):
        self.timeMsg = QDateTime.currentDateTime().toString(Qt.DefaultLocaleLongDate)
        self.statusBar().showMessage(self.timeMsg + '                    ' + self.statMsg)

    def text_open(self):
        desktopAddr = os.path.join(os.path.expanduser('~'), 'Desktop')  # get user's destop address regardless of os
        fname, _ = QFileDialog.getOpenFileName(self, caption='Save File', directory=desktopAddr)
        try:
            with open(file=fname, mode='r', encoding='UTF-8') as f:
                text = f.read()
                self.centralWidget.te.setText(text)
            self.msgbox(QMessageBox.Information, '확인', '열기를 성공하였습니다.', QMessageBox.Ok)
            self.statMsg = '열기를 성공하였습니다.'
        except:
            self.msgbox(QMessageBox.Information, '오류', '열기를 실패하였습니다.', QMessageBox.Ok)
            self.statMsg = '열기를 실패하였습니다.'

    def text_save(self, event):
        desktopAddr = os.path.join(os.path.expanduser('~'),'Desktop') # get user's destop address regardless of os
        fname, _ = QFileDialog.getSaveFileName(self, caption='Save File', directory=desktopAddr)
        if not fname.endswith('.txt'):
            fname += '.txt'
        with open(file=fname, mode='w', encoding='UTF-8') as f:
            f.write(self.centralWidget.te.toPlainText())

    def tts_btn(self):
        # >>> Thread Setting
        # if thread is daemon thread, when main thread is terminated immediately daemon thread is killed regardless of end of task
        self.t1 = threading.Thread(target=(self.tts))
        self.t1.daemon = True  # make t1 thread daemon thread
        # <<< Thread Setting
        self.t1.start()

    def tts(self):
        lock.acquire()
        text = self.centralWidget.te.toPlainText()
        if len(text.strip()) < 1:
            lock.release()
            return
        text2speech(text)
        lock.release()

    def history(self):
        self.histWidget = historyWidget()

    def font_dec(self):
        self.fsize -= 2
        self.fsize = 10 if self.fsize < 10 else self.fsize # constraint size range
        self.lbl_fsize.setText(str(self.fsize))
        self.font.setPointSize(self.fsize)
        self.centralWidget.te.setFont(self.font) # setFontPointSize(10)
        self.centralWidget.bte.setFont(self.font)  # setFontPointSize(10)

    def font_inc(self):
        self.fsize += 2
        self.fsize = 40 if self.fsize > 40 else self.fsize # constraint size range
        self.lbl_fsize.setText(str(self.fsize))
        self.font.setPointSize(self.fsize)
        self.centralWidget.te.setFont(self.font)  # setFontPointSize(10)
        self.centralWidget.bte.setFont(self.font)  # setFontPointSize(10)

    def print(self):
        self.t3 = threading.Thread(target=(Data_Send), args=(self.centralWidget.te.toPlainText().strip(),))
        self.t3.daemon = True  # make t1 thread daemon thread
        # <<< Thread Setting
        self.t3.start()

    # def setBaudrate(self, text):
    #     global baud
    #     baud = int(text)
    #     print('baudrate set', )
    #
    # def setEncoding(self, text):
    #     global txtEncoding
    #     txtEncoding = text
    #     print('encoding set', )

    def msgbox(self, seticon, title, text, btn):
        msg = QMessageBox()
        msg.setIcon(seticon)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setStandardButtons(btn)
        return msg.exec_()
        # QMessageBox.NoIcon : 값은 0 이며, 기본값이다. 메시지 박스에 아이콘을 표시
        # QMessageBox.Information : 값은 1 이며, 느낌표 아이콘 표시
        # QMessageBox.Warning : 값은 2 이며, 느낌표 아이콘에 배경이 노란색 삼각형 표시
        # QMessageBox.Critial : 값은 3 이며, 오류를 나타낼 때 표시
        # QMessageBox.Question : 값은 4 이며, 물음표 아이콘 표시

if __name__ == '__main__':
    try:
        os.chdir(sys._MEIPASS)
        print(sys._MEIPASS)
    except:
        os.chdir(os.getcwd())
    app = QApplication(sys.argv)
    ex = mainWindow()
    sys.exit(app.exec_())