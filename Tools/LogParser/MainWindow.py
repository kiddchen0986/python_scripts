# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 Fingerprint Cards AB <tech@fingerprints.com>
#
# All rights are reserved.
# Proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.
# Any use is subject to an appropriate license granted by Fingerprint Cards AB.
#


from PyQt5.QtWidgets import QMainWindow, QFileDialog
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from MainWindow_ui import *
from generate_report import parser_default_set, generate_all_report
import threading
from enum import Enum
import logging
import sys
import os
from collections import OrderedDict

class EmittingStr(QtCore.QObject):
    textWritten = pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))


class UiStatus(Enum):
    START = 0
    STOP = 1


class MainWindow(QMainWindow):
    __ui = Ui_MainWindow()
    __ui_status_signal = pyqtSignal(UiStatus)
    __combo_parsers = {}

    def __init__(self):
        super().__init__()
        self.__ui.setupUi(self)
        index = 0
        for item, val in parser_default_set.items():
            label = QtWidgets.QLabel(self.__ui.groupBox_Parsers)
            label.setObjectName("label_"+item)
            label.setText(item)
            self.__combo_parsers[item] = QtWidgets.QComboBox(self.__ui.groupBox_Parsers)
            self.__combo_parsers[item].addItems(['*.json', '*.txt', '*.html', 'None'])
            self.__combo_parsers[item].setObjectName("comboBox_" + item)
            self.__combo_parsers[item].setCurrentText(val['default_pattern'])
            self.__ui.groupBox_Parsers.layout().addWidget(label, index/2, (2*index) % 4)
            self.__ui.groupBox_Parsers.layout().addWidget(self.__combo_parsers[item], index/2, (2*index) % 4 + 1)
            index += 1
        self.on_checkBox_Option_clicked()
        sys.stdout = EmittingStr(textWritten=self.outputWritten)
        sys.stderr = EmittingStr(textWritten=self.outputWritten)
        console = logging.StreamHandler(sys.stdout)
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(name)s : %(levelname)s : %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)

        self.__ui_status_signal.connect(self.on_ui_status)

    @pyqtSlot(str)
    def outputWritten(self, text):
        cursor = self.__ui.textBrowser_Consol.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.__ui.textBrowser_Consol.setTextCursor(cursor)
        self.__ui.textBrowser_Consol.ensureCursorVisible()
        pass

    @pyqtSlot(UiStatus)
    def on_ui_status(self, status):
        if status == UiStatus.START:
            self.__ui.pushButton_Gen.setEnabled(False)
        elif status == UiStatus.STOP:
            self.__ui.pushButton_Gen.setEnabled(True)

    def closeEvent(self, event):
        """Shuts down application on close."""
        # Return stdout to defaults.
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        super().closeEvent(event)

    def run_generate(self, str_path, str_prefix, merged, parser_filters):
        try:
            print('start!')
            self.__ui_status_signal.emit(UiStatus.START)
            generate_all_report(str_path, str_prefix, merged, parser_filters)
            print('Complete!')
            self.__ui_status_signal.emit(UiStatus.STOP)
            os.startfile(str_path)
        except Exception as e:
            print('Error:' + str(e))
            self.__ui_status_signal.emit(UiStatus.STOP)

    @pyqtSlot(name='on_pushButton_Folder_clicked')
    def on_button_folder_clicked(self):
        str_path = QFileDialog.getExistingDirectory(self, "Select Folder", ".")
        if str_path != '':
            self.__ui.lineEdit_Folder.setText(str_path)

    @pyqtSlot(name='on_checkBox_Option_clicked')
    def on_checkBox_Option_clicked(self):
        self.__ui.groupBox_Parsers.setHidden(not self.__ui.checkBox_Option.isChecked())

    @pyqtSlot(name='on_pushButton_Gen_clicked')
    def on_button_gen_clicked(self):
        str_path = self.__ui.lineEdit_Folder.text()
        str_prefix = self.__ui.lineEdit_Prefix.text()
        merged = self.__ui.checkBox_Merged.isChecked()
        parser_filter = OrderedDict()
        for key, value in self.__combo_parsers.items():
            if value.currentText() != 'None':
                parser_filter[key] = value.currentText()
        if os.path.exists(str_path) and str_prefix != '':
            try:
                t1 = threading.Thread(target=self.run_generate, args=(str_path, str_prefix, merged, parser_filter))
                t1.start()
                pass
            except Exception as e:
                print(e)
