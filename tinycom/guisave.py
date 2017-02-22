#
# Module for saving and restoring UI control values.
#
# Copyright (c) 2017 Joshua Henderson <digitalpeer@digitalpeer.com>
#
# SPDX-License-Identifier: GPL-3.0
"""Saves and loads Qt GUI Control Settings"""
import sys
import inspect
from .qt import *

def save(ui, settings, controls):
    """Save the state of controls to settings."""

    if "ui" in controls:
        settings.setValue('geometry', ui.saveGeometry())

    for name, obj in inspect.getmembers(ui):

        if name not in controls:
            continue

        if isinstance(obj, QT_QComboBox):
            name = obj.objectName()
            index = obj.currentIndex()
            text = obj.itemText(index)
            settings.setValue(name, text)

        if isinstance(obj, QT_QLineEdit):
            name = obj.objectName()
            value = obj.text()
            settings.setValue(name, value)

        if isinstance(obj, QT_QCheckBox):
            name = obj.objectName()
            state = obj.isChecked()
            settings.setValue(name, state)

        if isinstance(obj, QT_QRadioButton):
            name = obj.objectName()
            value = obj.isChecked()
            settings.setValue(name, value)

        if isinstance(obj, QT_QSpinBox):
            name = obj.objectName()
            value = obj.value()
            settings.setValue(name, value)

        if isinstance(obj, QT_QSlider):
            name = obj.objectName()
            value = obj.value()
            settings.setValue(name, value)

        if isinstance(obj, QT_QSplitter):
            name = obj.objectName()
            settings.setValue(name, obj.saveState())

def load(ui, settings):
    """
    Configure UI controls from settings.

    With PyQt's QSettings.value(), you can get a QVariant and use the toBool(),
    toPoint() to convert back to the right type.  With Version 2 API, you
    can pass a third parameter to value() like so to convert to the right
    Python type:

        ui.resize(settings.value('size', QSize(500, 500), type=QSize))
        value = settings.value(name, None, type=bool)

    See http://pyqt.sourceforge.net/Docs/PyQt4/pyqt_qsettings.html

    Then comes in PySide, where neither of those work in all cases and you have
    to do the conversion from a string to the right type yourself. And then,
    this works across all APIs (on compatible versions).
    """

    if settings.contains('geometry'):
        ui.restoreGeometry(settings.value('geometry'))

    for name, obj in inspect.getmembers(ui):
        if isinstance(obj, QT_QComboBox):
            name = obj.objectName()
            value = settings.value(name, None)
            if value is None:
                continue

            index = obj.findText(value)
            if index == -1:
                obj.insertItem(0, value)
                index = obj.findText(value)
                obj.setCurrentIndex(index)
            else:
                obj.setCurrentIndex(index)

        if isinstance(obj, QT_QLineEdit):
            name = obj.objectName()
            value = settings.value(name, None)
            if value is None:
                continue
            obj.setText(value)

        if isinstance(obj, QT_QCheckBox):
            name = obj.objectName()
            value = settings.value(name, None)
            if value is None:
                continue
            obj.setChecked(value.lower() in ["true", "1", "yes", "y"])

        if isinstance(obj, QT_QRadioButton):
            name = obj.objectName()
            value = settings.value(name, None)
            if value is None:
                continue
            obj.setChecked(value.lower() in ["true", "1", "yes", "y"])

        if isinstance(obj, QT_QSlider):
            name = obj.objectName()
            value = settings.value(name, None)
            if value is None:
                continue
            obj.setValue(int(value))

        if isinstance(obj, QT_QSpinBox):
            name = obj.objectName()
            value = settings.value(name, None)
            if value is None:
                continue
            obj.setValue(int(value))

        if isinstance(obj, QT_QSplitter):
            name = obj.objectName()
            value = settings.value(name, None)
            if value is None:
                continue
            obj.restoreState(value)

if __name__ == "__main__":
    sys.exit()
