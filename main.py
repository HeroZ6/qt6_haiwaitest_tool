# ///////////////////////////////////////////////////////////////
#
# BY: WANDERSON M.PIMENTA
# PROJECT MADE WITH: Qt Designer and PySide6
# V: 1.0.0
#
# This project can be used freely for all uses, as long as they maintain the
# respective credits only in the Python scripts, any information in the visual
# interface (GUI) can be modified without any implication.
#
# There are limitations on Qt licenses if you want to use your products
# commercially, I recommend reading them on the official website:
# https://doc.qt.io/qtforpython/licenses.html
#
# ///////////////////////////////////////////////////////////////
import ctypes
import signal
import sys
import os
import platform
import threading

from PySide6.QtUiTools import QUiLoader

# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////
from modules import *
from widgets import *
from PySide6.QtCore import QThread, Signal
import pyqtgraph as pg

os.environ["QT_FONT_DPI"] = "96"  # FIX Problem for High DPI and Scale above 100%

# SET AS GLOBAL WIDGETS
# ///////////////////////////////////////////////////////////////
widgets = None


# 多线程信号创建
# aab转apk线程
class FunctionSignal(QThread):
    getApkSignal = Signal(str)

    def __init__(self):
        super().__init__()
        print('FunctionSignal_run')

    def run(self):
        result = AppFunctions.aabGetapk(self, widgets)
        self.getApkSignal.emit(result)
        widgets.btn_aab.setEnabled(True)


# 监测绘图线程
class PlotSiganl(QThread):
    plot = Signal(list, list)

    def __init__(self):
        super().__init__()
        widgets.plotout.clear()
        self.packagename = str(widgets.packageName.text())
        self.i = 0
        self.x = []
        self.y = []
        print('PlotSiganl_run')

    def run(self):

        def count_occurrences(string, field):
            return string.count(field)

        def get_data():
            cmd_pid = f'adb shell pidof {self.packagename}'
            pid = os.popen(cmd_pid).read().strip()
            print(pid)
            cmd_countpid = f'adb shell ps|findstr {self.packagename}'
            countpid = count_occurrences(os.popen(cmd_countpid).read(), self.packagename)
            print(countpid)
            return pid, countpid

        def update():
            self.x.append(self.i)
            try:
                self.y.append(int(get_data()[0]))
            except ValueError:
                self.y.append(0)

        while True:
            self.i += 1
            update()
            print(self.x)
            print(self.y)
            self.plot.emit(self.x, self.y)
            self.msleep(1000)


# 安装线程
class InstallSignal(QThread):
    debugInstallsignal = Signal(str)
    install = Signal(str)
    uninstall = Signal(str)

    def __init__(self):
        super().__init__()
        print('InstallSignal_run')

    def run(self):
        result = AppFunctions.debug_install(self, widgets.apkPath.text(), widgets.packageName.text(),
                                            widgets.device_serial.currentText())
        self.debugInstallsignal.emit(result)
        widgets.debugInstall.setEnabled(True)


class MainWindow(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)

        # SET AS GLOBAL WIDGETS
        # ///////////////////////////////////////////////////////////////
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        global widgets
        widgets = self.ui
        loader = QUiLoader()
        loader.registerCustomWidget(pg.PlotWidget)
        # USE CUSTOM TITLE BAR | USE AS "False" FOR MAC OR LINUX
        # ///////////////////////////////////////////////////////////////
        Settings.ENABLE_CUSTOM_TITLE_BAR = True

        # APP NAME
        # ///////////////////////////////////////////////////////////////
        title = "OverSeaTool"
        description = "OverSeaTool"
        # APPLY TEXTS
        self.setWindowTitle(title)
        widgets.titleRightInfo.setText(description)

        # TOGGLE MENU
        # ///////////////////////////////////////////////////////////////
        widgets.toggleButton.clicked.connect(lambda: UIFunctions.toggleMenu(self, True))

        # SET UI DEFINITIONS
        # ///////////////////////////////////////////////////////////////
        UIFunctions.uiDefinitions(self)

        # QTableWidget PARAMETERS
        # ///////////////////////////////////////////////////////////////
        widgets.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 事件改写初始化
        widgets.aabfilepath.installEventFilter(QEventHandler(widgets.aabfilepath))
        widgets.jksfilepath.installEventFilter(QEventHandler(widgets.jksfilepath))
        widgets.apkPath.installEventFilter(QEventHandler(widgets.apkPath))
        # BUTTONS CLICK
        # ///////////////////////////////////////////////////////////////

        # LEFT MENUS
        widgets.btn_home.clicked.connect(self.buttonClick)
        widgets.btn_widgets.clicked.connect(self.buttonClick)
        widgets.btn_new.clicked.connect(self.buttonClick)
        widgets.btn_new_2.clicked.connect(self.buttonClick)
        widgets.btn_save.clicked.connect(self.buttonClick)
        widgets.plotBtn.clicked.connect(self.plot_qt)
        widgets.endplotBtn.clicked.connect(self.plot_end)
        # FUNCTION BOTTON CONNECT
        widgets.btn_aab.clicked.connect(self.aabGetapk_qt)
        widgets.c_file1.clicked.connect(lambda: AppFunctions.OpenFileWin(self, widgets, 'zippath'))
        widgets.c_file2.clicked.connect(lambda: AppFunctions.OpenFileWin(self, widgets, 'aabfilepath'))
        widgets.c_file3.clicked.connect(lambda: AppFunctions.OpenFileWin(self, widgets, 'jksfilepath'))
        widgets.refreshBtm.clicked.connect(lambda: AppFunctions.updateSerialData(self, widgets, 'device_serial'))

        widgets.debugInstall.clicked.connect(self.dubugInstall_qt)
        # widgets.install.clicked.connect()
        # widgets.uninstall.clicked.connect()

        # EXTRA LEFT BOX
        def openCloseLeftBox():
            UIFunctions.toggleLeftBox(self, True)

        widgets.toggleLeftBox.clicked.connect(openCloseLeftBox)
        widgets.extraCloseColumnBtn.clicked.connect(openCloseLeftBox)

        # EXTRA RIGHT BOX
        def openCloseRightBox():
            UIFunctions.toggleRightBox(self, True)

        widgets.settingsTopBtn.clicked.connect(openCloseRightBox)

        # SHOW APP
        # ///////////////////////////////////////////////////////////////
        self.show()

        # SET CUSTOM THEME
        # ///////////////////////////////////////////////////////////////
        useCustomTheme = False
        themeFile = "themes\py_dracula_light.qss"

        # SET THEME AND HACKS
        if useCustomTheme:
            # LOAD AND APPLY STYLE
            UIFunctions.theme(self, themeFile, True)

            # SET HACKS
            AppFunctions.setThemeHack(self)

        # SET HOME PAGE AND SELECT MENU
        # ///////////////////////////////////////////////////////////////
        widgets.stackedWidget.setCurrentWidget(widgets.home)
        widgets.btn_home.setStyleSheet(UIFunctions.selectMenu(widgets.btn_home.styleSheet()))

    # BUTTONS CLICK
    # Post here your functions for clicked buttons
    # ///////////////////////////////////////////////////////////////
    def buttonClick(self):
        # GET BUTTON CLICKED
        btn = self.sender()
        btnName = btn.objectName()

        # SHOW HOME PAGE
        if btnName == "btn_home":
            widgets.stackedWidget.setCurrentWidget(widgets.home)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        # SHOW WIDGETS PAGE
        if btnName == "btn_widgets":
            widgets.stackedWidget.setCurrentWidget(widgets.widgets)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        # SHOW NEW PAGE
        if btnName == "btn_new":
            widgets.stackedWidget.setCurrentWidget(widgets.new_page)  # SET PAGE
            UIFunctions.resetStyle(self, btnName)  # RESET ANOTHERS BUTTONS SELECTED
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))  # SELECT MENU
        # SHOW NEW PAGE
        if btnName == "btn_new_2":
            widgets.stackedWidget.setCurrentWidget(widgets.new_page2)  # SET PAGE
            UIFunctions.resetStyle(self, btnName)  # RESET ANOTHERS BUTTONS SELECTED
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))  # SELECT MENU
        if btnName == "btn_save":
            print("Save BTN clicked!")
        # PRINT BTN NAME
        print(f'Button "{btnName}" pressed!')

    # RESIZE EVENTS
    # ///////////////////////////////////////////////////////////////
    def resizeEvent(self, event):
        # Update Size Grips
        UIFunctions.resize_grips(self)

    # MOUSE CLICK EVENTS
    # ///////////////////////////////////////////////////////////////
    def mousePressEvent(self, event):
        # SET DRAG POS WINDOW
        self.dragPos = event.globalPos()

        # PRINT MOUSE EVENTS
        if event.buttons() == Qt.LeftButton:
            print('Mouse click: LEFT CLICK')
        if event.buttons() == Qt.RightButton:
            print('Mouse click: RIGHT CLICK')

    # FUNCTION
    def aabGetapk_qt(self, str1):
        widgets.btn_aab.setEnabled(False)
        self.workthread = FunctionSignal()

        def checkErro(str1):
            if str1 != '':
                AppFunctions.errobox(self, str1)
            elif str1 == '转换完成':
                AppFunctions.errobox(self, str1)

        self.workthread.getApkSignal.connect(checkErro)
        self.workthread.started.connect(lambda: widgets.resultline.setText('开始转换'))
        self.workthread.finished.connect(lambda: widgets.resultline.setText('转换完成'))
        self.workthread.start()

    def plot_qt(self):
        self.plot_qt = PlotSiganl()

        def plot(list1, list2):
            self.curve = widgets.plotout.plot()
            self.curve.setData(list1, list2)

        self.plot_qt.plot.connect(plot)
        self.plot_qt.started.connect(lambda: print('开始绘图'))
        self.plot_qt.finished.connect(lambda: print('结束绘图'))
        self.plot_qt.start()

    def plot_end(self):
        print('点击')
        self.plot_qt.terminate()
        # 停止线程事件循环
        del self.plot_qt  # 手动删除线程对象

    def dubugInstall_qt(self):
        widgets.debugInstall.setEnabled(False)
        self.workthread = InstallSignal()

        def checkErro(str1):
            AppFunctions.errobox(self, str1)

        self.workthread.debugInstallsignal.connect(checkErro)
        self.workthread.started.connect(lambda: widgets.resultLog.setPlainText('开始安装'))
        self.workthread.finished.connect(lambda: widgets.resultLog.setPlainText('安装完成'))
        self.workthread.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.ico"))
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('icon.png')
    window = MainWindow()
    sys.exit(app.exec())
