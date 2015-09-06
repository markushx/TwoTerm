__author__ = 'mab'

import sys

try:
    from PyQt5.QtWidgets import QApplication
except ImportError:
    print("Problems with PyQt5. Falling back to PyQt4.")
    from PyQt4.QtGui import QApplication

from twoterm import TwoTermWidget

def main():
    app = QApplication(sys.argv)
    widget = TwoTermWidget()
    widget.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
