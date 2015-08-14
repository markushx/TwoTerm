__author__ = 'Markus Becker'

try:
    from PyQt5.QtCore import pyqtSlot, QTimer, QSize
    from PyQt5.QtWidgets import QMainWindow, QMessageBox
    from PyQt5.uic import loadUi
    from PyQt5.QtCore import QSettings
    from PyQt5.QtGui import QIcon
    
except ImportError:
    print("Problems with PyQt5. Falling back to PyQt4.")
    from PyQt4.QtCore import pyqtSlot, QTimer, QSettings, QSize
    from PyQt4.QtGui import QMainWindow, QIcon
    from PyQt4.uic import loadUi

import serial
import io
from serial.tools.list_ports import comports

CONNECT_LABEL = "Connect"
DISCONNECT_LABEL = "Disconnect"

TIMEOUT_READLINE = 0
TIMEOUT_TIMER = 1

SETTING_COMPORT_L = "COMPORT_L"
DEFAULT_COMPORT_L = ""
SETTING_COMPORT_R = "COMPORT_R"
DEFAULT_COMPORT_R = ""

SETTING_BAUDRATE_L = "BAUDRATE_L"
DEFAULT_BAUDRATE_L = "9600"
SETTING_BAUDRATE_R = "BAUDRATE_R"
DEFAULT_BAUDRATE_R = "9600"

SETTING_BYTESIZE_L = "BYTESIZE_L"
DEFAULT_BYTESIZE_L = "8"
SETTING_BYTESIZE_R = "BYTESIZE_R"
DEFAULT_BYTESIZE_R = "8"

SETTING_PARITY_L = "PARITY_L"
DEFAULT_PARITY_L = "N"
SETTING_PARITY_R = "PARITY_R"
DEFAULT_PARITY_R = "N"

SETTING_STOPBITS_L = "STOPBITS_L"
DEFAULT_STOPBITS_L = "1"
SETTING_STOPBITS_R = "STOPBITS_R"
DEFAULT_STOPBITS_R = "1"

class TwoTermWidget(QMainWindow):
    def __init__(self, *args):
        super(TwoTermWidget, self).__init__(*args)

        self.serL = None
        self.serR = None
        self.sioL = None
        self.sioR = None

        loadUi('TwoTermSingleScrollArea.ui', self)

        app_icon = QIcon('TwoTerm.png')
        self.setWindowIcon(app_icon)

        self.settings = QSettings("twoterm.cfg", QSettings.NativeFormat)

        self.connect_status = False

        iterator = sorted(comports())
        for port, desc, hwid in iterator:
            self.comboBoxL.addItem(str(port))
            self.comboBoxR.addItem(str(port))
            print("Port: " + str(port))
        self.comboBoxL.setCurrentText(self.settings.value(SETTING_COMPORT_L, DEFAULT_COMPORT_L))
        self.comboBoxR.setCurrentText(self.settings.value(SETTING_COMPORT_R, DEFAULT_COMPORT_R))

        self.comboBoxLBaudrate.addItems(map(str, serial.Serial.BAUDRATES))
        self.comboBoxRBaudrate.addItems(map(str, serial.Serial.BAUDRATES))
        self.comboBoxLBaudrate.setCurrentText(self.settings.value(SETTING_BAUDRATE_L, DEFAULT_BAUDRATE_L))
        self.comboBoxRBaudrate.setCurrentText(self.settings.value(SETTING_BAUDRATE_R, DEFAULT_BAUDRATE_R))

        self.comboBoxLBytesizes.addItems(map(str, serial.Serial.BYTESIZES))
        self.comboBoxRBytesizes.addItems(map(str, serial.Serial.BYTESIZES))
        self.comboBoxLBytesizes.setCurrentText(self.settings.value(SETTING_BYTESIZE_L, DEFAULT_BYTESIZE_L))
        self.comboBoxRBytesizes.setCurrentText(self.settings.value(SETTING_BYTESIZE_R, DEFAULT_BYTESIZE_R))

        self.comboBoxLParity.addItems(map(str, serial.Serial.PARITIES))
        self.comboBoxRParity.addItems(map(str, serial.Serial.PARITIES))
        self.comboBoxLBytesizes.setCurrentText(self.settings.value(SETTING_PARITY_L, DEFAULT_PARITY_L))
        self.comboBoxRBytesizes.setCurrentText(self.settings.value(SETTING_PARITY_R, DEFAULT_PARITY_R))

        self.comboBoxLStopbits.addItems(map(str, serial.Serial.STOPBITS))
        self.comboBoxRStopbits.addItems(map(str, serial.Serial.STOPBITS))
        self.comboBoxLBytesizes.setCurrentText(self.settings.value(SETTING_STOPBITS_L, DEFAULT_STOPBITS_L))
        self.comboBoxRBytesizes.setCurrentText(self.settings.value(SETTING_STOPBITS_R, DEFAULT_STOPBITS_R))

        self.textR.verticalScrollBar().valueChanged.connect(self.textL.verticalScrollBar().setValue)
        self.textR.horizontalScrollBar().valueChanged.connect(self.textL.horizontalScrollBar().setValue)
        self.textL.horizontalScrollBar().valueChanged.connect(self.textR.horizontalScrollBar().setValue)

        self.comboBoxL.currentTextChanged.connect(self.update_settings)
        self.comboBoxR.currentTextChanged.connect(self.update_settings)
        self.comboBoxLBaudrate.currentIndexChanged.connect(self.update_settings)
        self.comboBoxRBaudrate.currentIndexChanged.connect(self.update_settings)
        self.comboBoxLBytesizes.currentIndexChanged.connect(self.update_settings)
        self.comboBoxRBytesizes.currentIndexChanged.connect(self.update_settings)
        self.comboBoxLParity.currentIndexChanged.connect(self.update_settings)
        self.comboBoxRParity.currentIndexChanged.connect(self.update_settings)
        self.comboBoxLStopbits.currentIndexChanged.connect(self.update_settings)
        self.comboBoxRStopbits.currentIndexChanged.connect(self.update_settings)

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

    @pyqtSlot()
    def update_settings(self):
        self.settings.setValue(SETTING_COMPORT_L, self.comboBoxL.currentText())
        self.settings.setValue(SETTING_COMPORT_R, self.comboBoxR.currentText())
        self.settings.setValue(SETTING_BAUDRATE_L, self.comboBoxLBaudrate.currentText())
        self.settings.setValue(SETTING_BAUDRATE_R, self.comboBoxRBaudrate.currentText())
        self.settings.setValue(SETTING_BYTESIZE_L, self.comboBoxLBytesizes.currentText())
        self.settings.setValue(SETTING_BYTESIZE_R, self.comboBoxRBytesizes.currentText())
        self.settings.setValue(SETTING_PARITY_L, self.comboBoxLParity.currentText())
        self.settings.setValue(SETTING_PARITY_R, self.comboBoxRParity.currentText())
        self.settings.setValue(SETTING_STOPBITS_L, self.comboBoxLStopbits.currentText())
        self.settings.setValue(SETTING_STOPBITS_R, self.comboBoxRStopbits.currentText())

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

            try:
                self.serL = serial.serial_for_url(portl,
                                                  baudrate=int(self.comboBoxLBaudrate.currentText()),
                                                  bytesize=int(self.comboBoxLBytesizes.currentText()),
                                                  parity=self.comboBoxLParity.currentText(),
                                                  stopbits=float(self.comboBoxLStopbits.currentText()),
                                                  timeout=TIMEOUT_READLINE)
            except serial.serialutil.SerialException as e:
                QMessageBox.warning(None, "", "Unable to open serial port " + portl + ".")
                return

            try:
                self.serR = serial.serial_for_url(portr,
                                                  baudrate=int(self.comboBoxRBaudrate.currentText()),
                                                  bytesize=int(self.comboBoxLBytesizes.currentText()),
                                                  parity=self.comboBoxLParity.currentText(),
                                                  stopbits=float(self.comboBoxLStopbits.currentText()),
                                                  timeout=TIMEOUT_READLINE)
            except serial.serialutil.SerialException as e:
                QMessageBox.warning(None, "", "Unable to open serial port " + portr + ".")
                return

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
