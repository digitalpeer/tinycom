# Copyright (c) 2017 Joshua Henderson <digitalpeer@digitalpeer.com>
#
# Based on
#    https://github.com/mfitzp/pyqtconfig/blob/master/pyqtconfig/qt.py
#
# Copyright (c) 2013, Martin Fitzpatrick
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the software nor the
#      names of its contributors may be used to endorse or promote products
#      derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
This tries to abstract out PyQt4, PyQt5, and PySide importing such that it can
be determined at runtime either forcefully with a QT_API environment variable,
or automatically, depending on what it can successfully import.

Then, anywhere Qt is needed, just:

    from qt import *

"""
from __future__ import unicode_literals
import sys
import os

PYSIDE = 0
PYQT4 = 1
PYQT5 = 2

USE_QT_PY = None

QT_API_ENV = os.environ.get('QT_API')
ETS = dict(pyqt=PYQT4, pyqt4=PYQT4, pyqt5=PYQT5, pyside=PYSIDE)

if QT_API_ENV and QT_API_ENV in ETS:
    USE_QT_PY = ETS[QT_API_ENV]
elif 'PyQt4' in sys.modules:
    USE_QT_PY = PYQT4
elif 'PyQt5' in sys.modules:
    USE_QT_PY = PYQT5
else:
    try:
        import PyQt4
        USE_QT_PY = PYQT4
    except:
        try:
            import PyQt5
            USE_QT_PY = PYQT5
        except ImportError:
            try:
                import PySide
                USE_QT_PY = PYSIDE
            except:
                pass

if USE_QT_PY == PYQT5:
    from PyQt5 import QtGui, QtCore, QtWidgets, uic
    QT_QDialog=QtWidgets.QDialog
    QT_QFileDialog=QtWidgets.QFileDialog
    QT_QMainWindow=QtWidgets.QMainWindow
    QT_QApplication=QtWidgets.QApplication
    QT_QComboBox=QtWidgets.QComboBox
    QT_QLineEdit=QtWidgets.QLineEdit
    QT_QCheckBox=QtWidgets.QCheckBox
    QT_QRadioButton=QtWidgets.QRadioButton
    QT_QSpinBox=QtWidgets.QSpinBox
    QT_QSlider=QtWidgets.QSlider
    QT_QSplitter=QtWidgets.QSplitter
    QT_QListWidgetItem=QtWidgets.QListWidgetItem

elif USE_QT_PY == PYSIDE:
    from PySide import QtCore, QtGui, QtUiTools
    QtCore.pyqtSignal = QtCore.Signal
    QT_QDialog=QtGui.QDialog
    QT_QFileDialog=QtGui.QFileDialog
    QT_QMainWindow=QtGui.QMainWindow
    QT_QApplication=QtGui.QApplication
    QT_QComboBox=QtGui.QComboBox
    QT_QLineEdit=QtGui.QLineEdit
    QT_QCheckBox=QtGui.QCheckBox
    QT_QRadioButton=QtGui.QRadioButton
    QT_QSpinBox=QtGui.QSpinBox
    QT_QSlider=QtGui.QSlider
    QT_QSplitter=QtGui.QSplitter
    QT_QListWidgetItem=QtGui.QListWidgetItem
    from .pyside_dynamic import *

elif USE_QT_PY == PYQT4:
    import sip
    sip.setapi('QString', 2)
    sip.setapi('QVariant', 2)
    from PyQt4 import QtCore, QtGui, uic
    QT_QDialog=QtGui.QDialog
    QT_QFileDialog=QtGui.QFileDialog
    QT_QMainWindow=QtGui.QMainWindow
    QT_QApplication=QtGui.QApplication
    QT_QComboBox=QtGui.QComboBox
    QT_QLineEdit=QtGui.QLineEdit
    QT_QCheckBox=QtGui.QCheckBox
    QT_QRadioButton=QtGui.QRadioButton
    QT_QSpinBox=QtGui.QSpinBox
    QT_QSlider=QtGui.QSlider
    QT_QSplitter=QtGui.QSplitter
    QT_QListWidgetItem=QtGui.QListWidgetItem
