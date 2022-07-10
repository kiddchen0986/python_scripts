# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 Fingerprint Cards AB <tech@fingerprints.com>
#
# All rights are reserved.
# Proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.
# Any use is subject to an appropriate license granted by Fingerprint Cards AB.
#

import sys

from PyQt5.QtWidgets import QApplication
from MainWindow import *

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    MainWindow = MainWindow()
    MainWindow.show()
    tool_ver = "9.9.9.0999"
    MainWindow.setWindowTitle("MTT_Log_Parser v" + tool_ver)
    sys.exit(app.exec_())
