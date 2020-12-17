import sys, os, threading
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QFont, QImage, QPixmap
from PyQt5.QtCore import QDateTime, Qt, QSize, QTimer, QThread
from playsound import playsound
import cv2, pytesseract
import numpy as np

from lib.kor_to_braille import translate
from lib.tts import text2speech
from lib.Communication import Data_Send
from lib.preprocess_img import process

lock = threading.Lock()

baud = 9600
txtEncoding = 'UTF-8'


class ocrWidget(QWidget):
    def __init__(self, main):
        super(ocrWidget, self).__init__()
        self.main = main

        self.setWindowTitle('ocr')

        # >>> Flag Setting
        self.isCamRun = False
        self.lbl_pic = QLabel('', self)
        self.img = np.array([])
        self.camEnd = True
        # >>> camAction
        self.camAction = QAction(QIcon('icon/cam.png'), '카메라 켜기/끄기', self)
        self.camAction.triggered.connect(self.cam)

        # >>> text open Action
        self.openAction = QAction(QIcon('icon/open.png'), '불러오기', self)
        self.openAction.triggered.connect(self.img_open)

        # >>> ocr Action
        self.ocrAction = QAction(QIcon('icon/ocr.png'), 'OCR 실행', self)
        self.ocrAction.triggered.connect(self.ocrRun)

        # >>> ccw Action
        self.ccwAction = QAction(QIcon('icon/ccw.png'), '반시계 방향 회전', self)
        self.ccwAction.triggered.connect(self.ccwRotate)

        # >>> cw Action
        self.cwAction = QAction(QIcon('icon/cw.png'), '반시계 방향 회전', self)
        self.cwAction.triggered.connect(self.cwRotate)

        # >>> Layout Settings
        self.toolbar = QToolBar()
        self.toolbar.addAction(self.camAction)
        self.toolbar.addAction(self.openAction)
        self.toolbar.addWidget(QLabel('      '))  # Blank label
        self.toolbar.addAction(self.ccwAction)
        self.toolbar.addAction(self.cwAction)
        self.toolbar.addWidget(QLabel('      '))  # Blank label
        self.toolbar.addAction(self.ocrAction)

        self.vlay = QVBoxLayout()
        self.vlay.addWidget(self.toolbar)
        self.vlay.addWidget(self.lbl_pic)

        self.setLayout(self.vlay)

        # environment variable settings
        if not 'Tesseract' in os.environ.get('path'):
            os.environ['path'].append(r'C:\Program Files\Tesseract-OCR\tesseract')
            print('tesseract environment variable appended')

        if not os.environ.get('TESSDATA_PREFIX'):
            os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tesseract\tessdata'
            print('tessdata environment variable appended')
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'

        # >>> Window Setting
        width, height = 640, 480
        self.resize(width, height+34) # set window size
        main.center()
        self.show()
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        self.cap.release()

    def __del__(self):
        if self.cap.isOpened():
           self.cap.release()
           del self.cap
    def img_open(self):
        self.isCamRun = False
        desktopAddr = os.path.join(os.path.expanduser('~'), 'Desktop')  # get user's destop address regardless of os
        fname, _ = QFileDialog.getOpenFileName(self, caption='Save File', directory=desktopAddr)
        try:
            if not fname:
                return
            self.img = cv2.imread(fname)
            mainWindow.msgbox(self, QMessageBox.Information, '확인', '열기를 성공하였습니다.', QMessageBox.Ok)
            img = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, (640, 640 * self.img.shape[0] // self.img.shape[1]))
            h, w, c = img.shape
            qImg = QImage(img.data, w, h, w * c, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qImg)
            self.lbl_pic.setPixmap(pixmap)
        except:
            mainWindow.msgbox(self,QMessageBox.Information, '오류', '열기를 실패하였습니다.', QMessageBox.Ok)

    def cam(self):
        if self.isCamRun or not self.camEnd:
            self.isCamRun = False
            self.camAction.setIcon(QIcon('icon/cam.png'))
            return False
        self.t1 = threading.Thread(target=self.camRun)
        self.t1.daemon = True
        self.t1.start()
        return True

    def camRun(self):
        lock.acquire()
        self.isCamRun = True
        self.camEnd = False
        self.camAction.setIcon(QIcon('icon/cam_green.png'))
        try:
            self.cap.open(0)
            width, height = 640, 480
            self.resize(width, height + 34)  # set window size
            self.lbl_pic.resize(width, height)
            while self.isCamRun:
                ret, self.img = self.cap.read()
                if not ret:
                    mainWindow.msgbox(self, seticon=QMessageBox.Critical, title='오류', text='카메라를 작동할 수 없습니다.', btn=QMessageBox.Ok)
                    print('can\'t open camera')
                    self.isCamRun = False
                    break

                img = cv2.resize(self.img, (640, 640 * self.img.shape[0] // self.img.shape[1]))
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                h, w, c = img.shape
                qImg = QImage(img.data, w, h, w * c, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qImg)
                self.lbl_pic.setPixmap(pixmap)
        except:
            mainWindow.msgbox(self, QMessageBox.Information, '오류', '카메라 오류가 발생하였습니다.', QMessageBox.Ok)
            print('cam error occured')
        self.cap.release()
        self.camAction.setIcon(QIcon('icon/cam.png'))
        print('cam end')
        self.camEnd = True
        lock.release()

    def ocrRun(self):
        if self.img.size == 0:
            mainWindow.msgbox(self, QMessageBox.Information, '오류', '이미지를 먼저 지정해주세요.', QMessageBox.Ok)
            return
        if self.isCamRun:
            self.isCamRun = False
        self.camAction.setIcon(QIcon('icon/cam.png'))
        self.img = process(self.img)
        text = pytesseract.image_to_string(self.img, lang='kor', config='--psm 1 -c preserve_interword_spaces=1')
        self.main.centralWidget.te.setText(text)

    def ccwRotate(self):
        if self.img.size == 0:
            mainWindow.msgbox(self, QMessageBox.Information, '오류', '이미지를 먼저 지정해주세요.', QMessageBox.Ok)
            return
        h,w, *_ = self.img.shape
        self.img = cv2.rotate(self.img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        img = cv2.resize(self.img, (640, 640 * self.img.shape[0] // self.img.shape[1]))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, c = img.shape
        qImg = QImage(img.data, w, h, w * c, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qImg)
        self.lbl_pic.setPixmap(pixmap)

    def cwRotate(self):
        if self.img.size == 0:
            mainWindow.msgbox(self, QMessageBox.Information, '오류', '이미지를 먼저 지정해주세요.', QMessageBox.Ok)
            return
        h,w, *_ = self.img.shape
        self.img = cv2.rotate(self.img, cv2.ROTATE_90_CLOCKWISE)
        img = cv2.resize(self.img, (640, 640 * self.img.shape[0] // self.img.shape[1]))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, c = img.shape
        qImg = QImage(img.data, w, h, w * c, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qImg)
        self.lbl_pic.setPixmap(pixmap)

class historyWidget(QWidget):
    def __init__(self):
        super(historyWidget, self).__init__()

        self.setWindowTitle('TTS Player')
        self.fname = 'data_tts/TTS'
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
        playsound('data_tts/' + self.fname)
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
    def __call__(self):
        return self
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

        self.isOnOcrWidget = False

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
        self.lbl_fsize.setStyleSheet("border-style: solid;"
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

        # >>> OCR Action
        ocrAction = QAction(QIcon('icon/ocr.png'), '문서 인식', self)
        ocrAction.setShortcut('Ctrl+r')
        ocrAction.setStatusTip('문서 이미지를 텍스트로 변환합니다.')
        ocrAction.triggered.connect(self.ocrw)
        # <<< OCR Action


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
        editormenu.addAction(ocrAction)

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
        self.toolbar.addAction(ocrAction)
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

    def ocrw(self):
        self.ocr = ocrWidget(self)
        self.isOnOcrWidget = not self.isOnOcrWidget


if __name__ == '__main__':
    try:
        os.chdir(sys._MEIPASS)
        print(sys._MEIPASS)
    except:
        os.chdir(os.getcwd())
    app = QApplication(sys.argv)
    ex = mainWindow()
    sys.exit(app.exec_())