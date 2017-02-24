#
# Copyright (c) 2017 Joshua Henderson <digitalpeer@digitalpeer.com>
#
# SPDX-License-Identifier: GPL-3.0
from qt import *

class CustomLineEdit(QT_QLineEdit):
    """Custom line edit class that handles special key events."""

    key_event = QtCore.pyqtSignal(int, name='key_event')

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Up or event.key() == QtCore.Qt.Key_Down:
            self.key_event.emit(event.key())
            event.accept()
        else:
            super(CustomLineEdit, self).keyPressEvent(event)
