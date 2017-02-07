# Copyright (c) 2017 Joshua Henderson <digitalpeer@digitalpeer.com>
#
# SPDX-License-Identifier: GPL-3.0
"""
Wraps a serial port in a thread.
"""
import threading
import serial
from .qt import *

class SerialThread(QtCore.QThread):
    """Serial thread."""

    recv = QtCore.pyqtSignal(bytes, name='recv')
    recv_error = QtCore.pyqtSignal(str, name='recv_error')

    def __init__(self, serial_instance):
        super(SerialThread, self).__init__()

        self.serial = serial_instance
        self.alive = True
        self._lock = threading.Lock()

    #def __del__(self):
    #    self.stop()

    def stop(self):
        """Stop the thread from running."""
        self.alive = False
        if hasattr(self.serial, 'cancel_read'):
            self.serial.cancel_read()
        self.wait()

    def run(self):
        """Thread run loop."""
        error = None
        while self.alive and self.serial.isOpen:
            try:
                data = self.serial.read(1024)
            except serial.SerialException as exp:
                error = str(exp)
                break
            else:
                if data:
                    try:
                        self.recv.emit(data)
                    except Exception as exp: # pylint: disable=broad-except
                        error = str(exp)
                        break
        if error != None:
            self.recv_error.emit(error)
        self.alive = True

    def write(self, data):
        """Write to the port with lock held."""
        with self._lock:
            return self.serial.write(data)

    def close(self):
        """Stop the thread and close the serial port with lock held."""
        with self._lock:
            self.stop()
            self.serial.close()
