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
import os
import subprocess
import time
from typing import re

from PySide6 import QtCore

# MAIN FILE
# ///////////////////////////////////////////////////////////////
from main import *
from modules import Settings
import sys, re
import zipfile


# WITH ACCESS TO MAIN WINDOW WIDGETS
# ///////////////////////////////////////////////////////////////
class AppFunctions(MainWindow):
    def setThemeHack(self):
        Settings.BTN_LEFT_BOX_COLOR = "background-color: #495474;"
        Settings.BTN_RIGHT_BOX_COLOR = "background-color: #495474;"
        Settings.MENU_SELECTED_STYLESHEET = MENU_SELECTED_STYLESHEET = """
        border-left: 22px solid qlineargradient(spread:pad, x1:0.034, y1:0, x2:0.216, y2:0, stop:0.499 rgba(255, 121, 198, 255), stop:0.5 rgba(85, 170, 255, 0));
        background-color: #566388;
        """

        # SET MANUAL STYLES
        self.ui.lineEdit.setStyleSheet("background-color: #6272a4;")
        self.ui.pushButton.setStyleSheet("background-color: #6272a4;")
        self.ui.plainTextEdit.setStyleSheet("background-color: #6272a4;")
        self.ui.tableWidget.setStyleSheet(
            "QScrollBar:vertical { background: #6272a4; } QScrollBar:horizontal { background: #6272a4; }")
        self.ui.scrollArea.setStyleSheet(
            "QScrollBar:vertical { background: #6272a4; } QScrollBar:horizontal { background: #6272a4; }")
        self.ui.comboBox.setStyleSheet("background-color: #6272a4;")
        self.ui.horizontalScrollBar.setStyleSheet("background-color: #6272a4;")
        self.ui.verticalScrollBar.setStyleSheet("background-color: #6272a4;")
        self.ui.commandLinkButton.setStyleSheet("color: #ff79c6;")

    def resource_path(self, relative_path):
        """获取程序中所需文件资源的绝对路径"""
        try:
            # PyInstaller创建临时文件夹,将路径存储于_MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    # aab转apk
    def aabGetapk(self, ui):
        work_path = r'.\bundle'
        aabfilepath = ui.aabfilepath.text()
        apkfilepath = ui.apkfilepath.text()
        jksfilepath = ui.jksfilepath.text()
        keypass = ui.keypass.currentText()
        ailas = ui.ailas.currentText()
        bundletool = AppFunctions.resource_path(self, r'bundle\bundletool-all-1.15.1.jar')
        print(apkfilepath, aabfilepath, keypass, ailas)
        content = subprocess.Popen(
            f'java -jar {bundletool} build-apks --mode=universal --bundle={aabfilepath} --output=test.apks --ks={jksfilepath} --ks-pass=pass:{keypass} --ks-key-alias={ailas} --key-pass=pass:{keypass}',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, cwd=work_path)
        print(work_path)
        out = content.communicate()[0].decode('gbk')
        erro = content.communicate()[1].decode('gbk')
        print(f'输出结果：{out}')
        print(f'出现的错误：{erro}')
        if erro != '':
            return str(erro)

        def check_file_existence(filename):
            i = 0
            while not os.path.exists(filename):
                i += 1
                time.sleep(1)  # 等待1秒
                print(i)
            print("文件已生成！")

        filename_front = AppFunctions.resource_path(self, r'bundle') + r'\test.apks'
        check_file_existence(filename_front)
        filename = AppFunctions.resource_path(self, r'bundle\test.apks')
        destionname = os.path.dirname(aabfilepath)
        with zipfile.ZipFile(filename, 'r') as apk:
            apk.extractall(destionname)
        destionfile = os.path.dirname(aabfilepath) + r'\universal.apk'
        print(destionfile)
        check_file_existence(destionfile)
        os.remove(AppFunctions.resource_path(self, filename))
        os.remove(AppFunctions.resource_path(self, rf'{destionname}\toc.pb'))
        return '转换完成'

    def errobox(self, erro):
        QMessageBox.information(widgets, 'erro', str(erro))
        return

    def OpenFileWin(self, obj1, obj2):
        getattr(obj1, obj2).setText(
            str(QFileDialog.getOpenFileName(self, '选择文件', '.', 'All Files (*);;py文件(*.py *.pyd))')[0]))

    def plot(self, packagename):
        subprocess.Popen(f'adb shell ps|findstr {packagename}', stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)

    # 获取包名
    def get_appPackagename(self, path):
        """
        :param path: 包的绝对路径，反编译包得到包的包名
        :return:
        """
        cmd = "aapt dump badging %s" % path
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             stdin=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()
        match = re.compile("package: name='(\S+)' versionCode='(\d+)' versionName='(\S+)'").match(output.decode())
        if not match:
            return "获取不到包名,请检查apk路径是否有中文"
        appPackage = match.group(1)
        return appPackage

    def updateSerialData(self, obj1, obj2):
        adb_serial_cmd = 'adb devices'
        serial = subprocess.run(adb_serial_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # 检查命令是否成功执行
        if serial.returncode == 0:
            # 获取标准输出并解码成字符串
            output = serial.stdout
            print("Command output:")
            print(output)
        else:
            # 获取标准错误并解码成字符串
            error_output = serial.stderr
            print("Error occurred:")
            print(error_output)
        pattern = re.compile(r'^([A-Za-z0-9]+)\s+device$', re.MULTILINE)
        matches = pattern.findall(output)
        getattr(obj1, obj2).clear()
        getattr(obj1, obj2).addItems(matches)
        print('列表已更新')

    def debug_install(self, apk_path, package_name, device_serial):
        # 替换为你的 APK 文件路径、应用包名和设备的序列号（可以通过 adb devices 命令获取）
        # apk_path = r"D:\PRODUCT\fileManager\file2\0828\2\test.apk"
        # package_name = "com.fullmemory.scan"
        # device_serial = "ZY22CQH692"

        # 安装应用并传送 .debug 文件
        adb_install_cmd = f"adb -s {device_serial} install -r {apk_path}"
        adb_push_cmd = f"adb -s {device_serial} push D:\protect\sit\cache /sdcard/android/data/{package_name}"

        # 运行 ADB 命令
        try:
            subprocess.run(adb_install_cmd, shell=True, check=True)
            for i in range(2):
                subprocess.run(adb_push_cmd, shell=True, check=True)
                print(f'第{i + 1}次')
            print("App安装成功且debug已打开.")
            return "App安装成功且debug已打开."
        except subprocess.CalledProcessError:
            print("安装失败/debug失败.")
            return "安装失败/debug失败."

class QEventHandler(QtCore.QObject):
    def eventFilter(self, obj, event):
        """
        目前已经实现将拖到控件上文件的路径设置为控件的显示文本；
        """
        if event.type() == QtCore.QEvent.DragEnter:
            event.accept()
        if event.type() == QtCore.QEvent.Drop:
            md = event.mimeData()
            if md.hasUrls():
                # 此处md.urls()的返回值为拖入文件的file路径列表，支持多文件同时拖入；默认读取第一个文件的路径进行处理
                url = md.urls()[0]
                obj.setText(url.toLocalFile())
                # print(str(url.toLocalFile()))
                # print(type(url))
                return True
        return super().eventFilter(obj, event)
# if __name__ == '__main__':
#     AppFunctions.updateSerialData()
