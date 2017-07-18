#!/usr/bin/python
#
# A simple line based GUI serial terminal.
#
# Copyright (c) 2017 Joshua Henderson <digitalpeer@digitalpeer.com>
#
# SPDX-License-Identifier: GPL-3.0

"""TinyCom"""
import sys
import glob
import re
import codecs
import serial
from pkg_resources import parse_version
from qt import *
from version import __version__
import guisave
import tinycom_rc # pylint: disable=unused-import
from lineedit import CustomLineEdit

# By default, a thread is used to process the serial port. If this is set to
# False, a timer will poll the serial port at a fixed interval, which can have
# obvious negative side effects of delayed recv.
USE_THREAD = True

if USE_THREAD:
    import serialthread # pylint: disable=wrong-import-position

def populate_serial_ports():
    """Gather all serial ports found on system."""
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            ser = serial.Serial(port)
            ser.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

def _chunks(text, chunk_size):
    """Chunk text into chunk_size."""
    for i in range(0, len(text), chunk_size):
        yield text[i:i+chunk_size]

def str_to_hex(text):
    """Convert text to hex encoded bytes."""
    return ''.join('{:02x}'.format(ord(c)) for c in text)

def hex_to_raw(hexstr):
    """Convert a hex encoded string to raw bytes."""
    return ''.join(chr(int(x, 16)) for x in _chunks(hexstr, 2))

def human_size(nbytes):
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    if nbytes == 0: return '0 B'
    i = 0
    while nbytes >= 1024 and i < len(suffixes)-1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[i])

def load_ui_widget(filename, this):
    """Abstracts out using custom loadUi(), necessary with pySide, or PYQt's uic.loadUi()."""
    if USE_QT_PY == PYSIDE:
        loadUi(filename, this, dict(CustomLineEdit=CustomLineEdit))
    else:
        uic.loadUi(filename, this)

class SettingsDialog(QT_QDialog):
    """Settings dialog."""
    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)
        load_ui_widget(os.path.join(os.path.dirname(__file__), 'settings.ui'),
                       self)

        try:
            self.port.addItems(populate_serial_ports())
        except EnvironmentError:
            pass

        self.buttonBox.accepted.connect(self.onAccept)

        self.baudrate.setCurrentIndex(self.baudrate.findText("115200"))

        self.bytesize.addItem("5", serial.FIVEBITS)
        self.bytesize.addItem("6", serial.SIXBITS)
        self.bytesize.addItem("7", serial.SEVENBITS)
        self.bytesize.addItem("8", serial.EIGHTBITS)
        self.bytesize.setCurrentIndex(self.bytesize.findText("8"))

        self.parity.addItem("None", serial.PARITY_NONE)
        self.parity.addItem("Even", serial.PARITY_EVEN)
        self.parity.addItem("Odd", serial.PARITY_ODD)
        self.parity.addItem("Mark", serial.PARITY_MARK)
        self.parity.addItem("Space", serial.PARITY_SPACE)
        self.parity.setCurrentIndex(self.parity.findText("None"))

        self.stopbits.addItem("1", serial.STOPBITS_ONE)
        self.stopbits.addItem("1.5", serial.STOPBITS_ONE_POINT_FIVE)
        self.stopbits.addItem("2", serial.STOPBITS_TWO)
        self.stopbits.setCurrentIndex(self.stopbits.findText("1"))

        self.settings = QtCore.QSettings('tinycom', 'tinycom')
        self.settings.beginGroup("settingsDialog")
        guisave.load(self, self.settings)
        self.settings.endGroup()

    def getValues(self):
        """
        Return a dictionary of settings.
        This returns direct attributes of the serial object.
        """
        return {'port':self.port.currentText(),
                'baudrate':int(self.baudrate.currentText()),
                'bytesize':self.bytesize.itemData(self.bytesize.currentIndex()),
                'parity':self.parity.itemData(self.parity.currentIndex()),
                'stopbits':self.stopbits.itemData(self.stopbits.currentIndex()),
                'xonxoff':self.xonxoff.isChecked(),
                'rtscts':self.rtscts.isChecked(),
                'dsrdtr':self.dsrdtr.isChecked()}

    def onAccept(self):
        """Accept changes."""
        self.settings.beginGroup("settingsDialog")
        guisave.save(self, self.settings,
                     ["port", "baudrate", "bytesize", "parity", "stopbits",
                      "xonxoff", "rtscts", "dsrdtr"])
        self.settings.endGroup()

class MainWindow(QT_QMainWindow):
    """The main window."""
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        load_ui_widget(os.path.join(os.path.dirname(__file__), 'tinycom.ui'),
                       self)
        self.serial = None
        self.rx = 0
        self.tx = 0
        self.history_index = 0

        self.statusBar().showMessage("Not connected")

        ports = []
        try:
            ports = populate_serial_ports()
        except EnvironmentError:
            pass

        if not len(ports):
            self.statusBar().showMessage(
                'No serial ports found.  You can try manually entering one.')

        self.btn_open.clicked.connect(self.onBtnOpen)
        self.btn_send.clicked.connect(self.onBtnSend)
        self.input.returnPressed.connect(self.onBtnSend)
        self.input.textChanged.connect(self.onInputChanged)
        self.line_end.currentIndexChanged.connect(self.onInputChanged)
        self.btn_clear.clicked.connect(self.onBtnClear)
        self.btn_open_log.clicked.connect(self.onBtnOpenLog)
        self.actionQuit.triggered.connect(QT_QApplication.quit)
        self.actionAbout.triggered.connect(self.onAbout)
        self.history.itemDoubleClicked.connect(self.onHistoryDoubleClick)

        self.input.setEnabled(False)
        self.btn_send.setEnabled(False)
        self.history.setEnabled(False)

        self.rxtx = QT_QLabel("TX: 0 B  RX: 0 B")
        self.statusBar().addPermanentWidget(self.rxtx)

        self.settings = QtCore.QSettings('tinycom', 'tinycom')
        self.settings.beginGroup("mainWindow")
        guisave.load(self, self.settings)
        self.settings.endGroup()

        self.ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
        if parse_version(serial.VERSION) >= parse_version("3.0"):
            self.serial = serial.Serial(timeout=0.1,
                                        write_timeout=5.0,
                                        inter_byte_timeout=1.0)
        else:
            self.serial = serial.Serial(timeout=0.1,
                                        writeTimeout=5.0,
                                        interCharTimeout=1.0)
        if not USE_THREAD:
            self.timer = QtCore.QTimer()
            self.timer.timeout.connect(self.doReadData)
        else:
            self.thread = serialthread.SerialThread(self.serial)
            self.thread.recv.connect(self.recv)
            self.thread.recv_error.connect(self.onRecvError)

        self.input.key_event.connect(self.onInputKey)

    def uiConnectedEnable(self, connected):
        """Toggle enabled on controls based on connect."""
        if connected:
            self.btn_open.setText("&Close Device")
            self.onInputChanged()
        else:
            self.btn_open.setText("&Open Device")
            self.btn_send.setEnabled(connected)
        self.input.setEnabled(connected)
        self.history.setEnabled(connected)

    def onBtnOpen(self):
        """Open button clicked."""
        if self.serial.isOpen():
            if not USE_THREAD:
                self.timer.stop()
                self.serial.close()
            else:
                self.thread.close()
            self.uiConnectedEnable(False)
            self.statusBar().showMessage("Not connected")
        else:
            dlg = SettingsDialog(self)
            if dlg.exec_():
                settings = dlg.getValues()
                for key in settings:
                    setattr(self.serial, key, settings[key])
            else:
                return

            try:
                self.serial.open()
            except serial.SerialException as exp:
                QtGui.QMessageBox.critical(self, 'Error Opening Serial Port',
                                           str(exp))
            except (IOError, OSError) as exp:
                QtGui.QMessageBox.critical(self, 'IO Error Opening Serial Port',
                                           str(exp))
            else:
                if parse_version(serial.VERSION) >= parse_version("3.0"):
                    self.serial.reset_input_buffer() # pylint: disable=no-member
                    self.serial.reset_output_buffer() # pylint: disable=no-member
                else:
                    self.serial.flushInput() # pylint: disable=no-member
                    self.serial.flushOutput() # pylint: disable=no-member
                self.statusBar().showMessage('Connected to ' + settings['port'] +
                                        ' ' +
                                        str(settings['baudrate']) + ',' +
                                        str(settings['parity']) + ',' +
                                        str(settings['bytesize']) + ',' +
                                        str(settings['stopbits']))
                self.uiConnectedEnable(True)
                if not USE_THREAD:
                    self.timer.start(100)
                else:
                    self.thread.start()

    def doLog(self, text):
        """Write to log file."""
        text = text.decode("utf-8", 'backslashreplace')
        if self.remove_escape.isChecked():
            text = self.ansi_escape.sub('', text)
        if self.output_hex.isChecked():
            text = str_to_hex(text)
            text = ' '.join(a+b for a, b in zip(text[::2], text[1::2]))
            text = text + ' '

        cursor = self.log.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        if not self.lock.isChecked():
            self.log.moveCursor(QtGui.QTextCursor.End)

        if self.enable_log.isChecked() and len(self.log_file.text()):
            with open(self.log_file.text(), "a") as handle:
                handle.write(text)

    def encodeInput(self):
        """
        Interpret the user input text as hex or append appropriate line ending.
        """
        endings = [u"\n", u"\r", u"\r\n", u"\n\r", u"", u""]
        text = self.input.text()

        if self.line_end.currentText() == "Hex":
            text = ''.join(text.split())
            if len(text) % 2:
                raise ValueError('Hex encoded values must be a multiple of 2')
            text = hex_to_raw(text)
        else:
            text = text + endings[self.line_end.currentIndex()]
        return text.encode()

    def onInputChanged(self):
        """Input line edit changed."""
        try:
            self.encodeInput()
        except ValueError:
            self.input.setStyleSheet("color: rgb(255, 0, 0);")
            self.btn_send.setEnabled(False)
            return
        self.input.setStyleSheet("color: rgb(0, 0, 0);")
        if self.serial is not None and self.serial.isOpen():
            self.btn_send.setEnabled(True)

    def onInputKey(self, key):
        """Input line edit key pressed."""
        if key == QtCore.Qt.Key_Up:
            if self.history_index > 0:
                self.history_index -= 1
                item = self.history.item(self.history_index)
                self.input.setText(item.text())
        elif key == QtCore.Qt.Key_Down:
            if self.history_index < self.history.count():
                self.history_index += 1
                if self.history_index == self.history.count():
                    self.input.setText("")
                else:
                    item = self.history.item(self.history_index)
                    self.input.setText(item.text())

    def onBtnSend(self):
        """Send button clicked."""
        if not self.serial.isOpen():
            return
        try:
            raw = self.encodeInput()
            if not USE_THREAD:
                ret = self.serial.write(raw)
            else:
                ret = self.thread.write(raw)
            self.tx = self.tx + ret
            self.rxtx.setText("TX: " + human_size(self.tx) + "  RX: " + human_size(self.rx))
        except serial.SerialException as exp:
            QtGui.QMessageBox.critical(self, 'Serial write error', str(exp))
            return
        except ValueError as exp:
            QtGui.QMessageBox.critical(self, 'Input Error', str(exp))
            return

        if self.echo_input.isChecked():
            self.doLog(raw)

        if len(self.input.text()):
            item = QT_QListWidgetItem(self.input.text())
            self.history.addItem(item)
            self.history.scrollToItem(item)
            self.history_index = self.history.count()

        self.input.clear()

    def onBtnOpenLog(self):
        """Open log file button clicked."""
        dialog = QT_QFileDialog(self)
        dialog.setWindowTitle('Open File')
        dialog.setNameFilter("All files (*.*)")
        dialog.setFileMode(QtGui.QFileDialog.AnyFile)
        if dialog.exec_() == QT_QDialog.Accepted:
            filename = dialog.selectedFiles()[0]
            self.log_file.setText(filename)

    def onHistoryDoubleClick(self, item):
        """Send log item double clicked."""
        self.input.setText(item.text())
        self.onBtnSend()

    def onBtnClear(self):
        """Clear button clicked."""
        self.log.clear()

    def doReadData(self):
        """Read serial port."""
        if self.serial.isOpen:
            try:
                text = self.serial.read(2048)
            except serial.SerialException as exp:
                QtGui.QMessageBox.critical(self, 'Serial read error', str(exp))
            else:
                self.recv(text)

    def recv(self, text):
        """Receive data from the serial port signal."""
        if len(text):
            size = len(text)
            self.rx = self.rx + size
            self.rxtx.setText("TX: " + human_size(self.tx) + "  RX: " + human_size(self.rx))
            self.doLog(text)

    def onRecvError(self, error):
        """Receive error when reading serial port from signal."""
        QtGui.QMessageBox.critical(self, 'Serial read error', error)
        self.onBtnOpen()

    def onAbout(self):
        """About menu clicked."""
        msg = QtGui.QMessageBox(self)
        msg.setIcon(QtGui.QMessageBox.Information)
        msg.setText("TinyCom " + __version__)
        msg.setInformativeText("Copyright (c) 2017 Joshua Henderson")
        msg.setWindowTitle("TinyCom")
        with codecs.open('LICENSE.txt', encoding='utf-8') as f:
            msg.setDetailedText(f.read())
        msg.setStandardButtons(QtGui.QMessageBox.Ok)
        msg.exec_()

    def closeEvent(self, unused_event):
        """Handle window close event."""
        _ = unused_event
        if not USE_THREAD:
            self.timer.stop()
            self.serial.close()
        else:
            self.thread.close()
        self.settings.beginGroup("mainWindow")
        guisave.save(self, self.settings,
                     ["ui", "remove_escape",
                      "echo_input", "log_file", "enable_log", "line_end",
                      "splitter", "output_hex"])
        self.settings.endGroup()

def main():
    """Create main app and window."""
    app = QT_QApplication(sys.argv)
    app.setApplicationName("TinyCom")
    win = MainWindow(None)
    win.setWindowTitle("TinyCom " + __version__)
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
