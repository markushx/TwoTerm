__author__ = 'mab'

try:
    from PyQt5.QtCore import pyqtSlot, QTimer
    from PyQt5.QtWidgets import QMainWindow
    from PyQt5.uic import loadUi
except:
    print("Problems with PyQt5. Falling back to PyQt4.")
    from PyQt4.QtCore import pyqtSlot, QTimer
    from PyQt4.QtGui import QMainWindow
    from PyQt4.uic import loadUi

from serial.tools.list_ports import comports

import serial.tools.list_ports


ports = list(serial.tools.list_ports.comports())
for p in ports:
    print(p)

import serial
import io

CONNECT_LABEL = "Connect"
DISCONNECT_LABEL = "Disconnect"
TIMEOUT_READLINE = 0.01
TIMEOUT_TIMER = 1


class TwoTermWidget(QMainWindow):
    def __init__(self, *args):
        super(TwoTermWidget, self).__init__(*args)
        self.serL = None
        self.serR = None
        self.sioL = None
        self.sioR = None

        loadUi('TwoTerm.ui', self)

        self.connect_status = False

        iterator = sorted(comports())
        for port, desc, hwid in iterator:
            self.comboBoxL.addItem(str(port))
            self.comboBoxR.addItem(str(port))
            print("Port: " + str(port))

        self.comboBoxLBaudrate.addItems(map(str, serial.Serial.BAUDRATES))
        self.comboBoxRBaudrate.addItems(map(str, serial.Serial.BAUDRATES))

    def timeout(self):
        l = self.sioL.readline()
        r = self.sioR.readline()
        if l != "":
            self.textBrowserL.append(l)
        if r != "":
            self.textBrowserR.append(r)

        if l != "" and r == "":
            self.textBrowserR.append("")
        if l == "" and r != "":
            self.textBrowserL.append("")

    @pyqtSlot()
    def on_connectButton_clicked(self):

        if not self.connect_status:

            portL = self.comboBoxL.currentText()
            portR = self.comboBoxR.currentText()

            if portL == "":
                portL = 'loop://'

            if portR == "":
                portR = 'loop://'

            self.serL = serial.serial_for_url(portL, baudrate=int(self.comboBoxLBaudrate.currentText()),
                                              timeout=TIMEOUT_READLINE)
            self.serR = serial.serial_for_url(portR, baudrate=int(self.comboBoxRBaudrate.currentText()),
                                              timeout=TIMEOUT_READLINE)

            self.sioL = io.TextIOWrapper(io.BufferedRWPair(self.serL, self.serL))
            self.sioR = io.TextIOWrapper(io.BufferedRWPair(self.serR, self.serR))

            # test
            self.sioL.write(u"hello l")
            self.sioL.flush()
            self.sioR.write(u"hello r")
            self.sioR.flush()

            self.connectButton.setText(DISCONNECT_LABEL)
            self.connect_status = True
            self.textBrowserL.append(CONNECT_LABEL + " " + str(self.serL))
            self.textBrowserR.append(CONNECT_LABEL + " " + str(self.serR))

            self.timer = QTimer(self)
            self.timer.timeout.connect(self.timeout)
            self.timer.start(TIMEOUT_TIMER)
        else:

            self.timer.stop()

            self.serL.close()
            self.serR.close()

            self.serL = None
            self.serR = None

            self.sioL = None
            self.sioR = None

            self.connectButton.setText(CONNECT_LABEL)
            self.connect_status = False
            self.textBrowserL.append(DISCONNECT_LABEL)
            self.textBrowserR.append(DISCONNECT_LABEL)
