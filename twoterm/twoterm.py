__author__ = 'Markus Becker'

try:
    from PyQt5.QtCore import pyqtSlot, QTimer
    from PyQt5.QtWidgets import QMainWindow
    from PyQt5.uic import loadUi
except ImportError:
    print("Problems with PyQt5. Falling back to PyQt4.")
    from PyQt4.QtCore import pyqtSlot, QTimer
    from PyQt4.QtGui import QMainWindow
    from PyQt4.uic import loadUi

import serial
import io
from serial.tools.list_ports import comports

CONNECT_LABEL = "Connect"
DISCONNECT_LABEL = "Disconnect"

TIMEOUT_READLINE = 0
TIMEOUT_TIMER = 1


class TwoTermWidget(QMainWindow):
    def __init__(self, *args):
        super(TwoTermWidget, self).__init__(*args)
        self.serL = None
        self.serR = None
        self.sioL = None
        self.sioR = None

        loadUi('TwoTermSingleScrollArea.ui', self)

        self.connect_status = False

        iterator = sorted(comports())
        for port, desc, hwid in iterator:
            self.comboBoxL.addItem(str(port))
            self.comboBoxR.addItem(str(port))
            print("Port: " + str(port))

        self.comboBoxLBaudrate.addItems(map(str, serial.Serial.BAUDRATES))
        self.comboBoxRBaudrate.addItems(map(str, serial.Serial.BAUDRATES))
        self.comboBoxLBaudrate.setCurrentIndex(12)
        self.comboBoxRBaudrate.setCurrentIndex(12)

        self.comboBoxLBytesizes.addItems(map(str, serial.Serial.BYTESIZES))
        self.comboBoxRBytesizes.addItems(map(str, serial.Serial.BYTESIZES))
        self.comboBoxLBytesizes.setCurrentIndex(3)
        self.comboBoxRBytesizes.setCurrentIndex(3)

        self.comboBoxLParity.addItems(map(str, serial.Serial.PARITIES))
        self.comboBoxRParity.addItems(map(str, serial.Serial.PARITIES))

        self.comboBoxLStopbits.addItems(map(str, serial.Serial.STOPBITS))
        self.comboBoxRStopbits.addItems(map(str, serial.Serial.STOPBITS))


        self.textR.verticalScrollBar().valueChanged.connect(self.textL.verticalScrollBar().setValue)
        self.textR.horizontalScrollBar().valueChanged.connect(self.textL.horizontalScrollBar().setValue)
        self.textL.horizontalScrollBar().valueChanged.connect(self.textR.horizontalScrollBar().setValue)

        self.timer = None

    def timeout(self):
        l = self.sioL.readline()
        r = self.sioR.readline()
        if l != "":
            self.textL.append(l)
        if r != "":
            self.textR.append(r)

        if l != "" and r == "":
            self.textR.append("")
        if l == "" and r != "":
            self.textL.append("")

    # noinspection PyPep8Naming
    @pyqtSlot()
    def on_connectButton_clicked(self):

        if not self.connect_status:

            portl = self.comboBoxL.currentText()
            portr = self.comboBoxR.currentText()

            if portl == "":
                portl = 'loop://'

            if portr == "":
                portr = 'loop://'

            self.serL = serial.serial_for_url(portl,
                                              baudrate=int(self.comboBoxLBaudrate.currentText()),
                                              bytesize=int(self.comboBoxLBytesizes.currentText()),
                                              parity=self.comboBoxLParity.currentText(),
                                              stopbits=float(self.comboBoxLStopbits.currentText()),
                                              timeout=TIMEOUT_READLINE)
            self.serR = serial.serial_for_url(portr,
                                              baudrate=int(self.comboBoxRBaudrate.currentText()),
                                              bytesize=int(self.comboBoxLBytesizes.currentText()),
                                              parity=self.comboBoxLParity.currentText(),
                                              stopbits=float(self.comboBoxLStopbits.currentText()),
                                              timeout=TIMEOUT_READLINE)

            self.sioL = io.TextIOWrapper(io.BufferedRWPair(self.serL, self.serL))
            self.sioR = io.TextIOWrapper(io.BufferedRWPair(self.serR, self.serR))

            # test code
            # self.sioL.write(u"hello l")
            # self.sioL.flush()
            # self.sioR.write(u"hello r")
            # self.sioR.flush()

            self.connectButton.setText(DISCONNECT_LABEL)
            self.connect_status = True
            self.textL.append(CONNECT_LABEL + " " + str(self.serL))
            self.textR.append(CONNECT_LABEL + " " + str(self.serR))

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
            self.textL.append(DISCONNECT_LABEL)
            self.textR.append(DISCONNECT_LABEL)
