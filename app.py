import sys
import random
from PySide6 import QtCore, QtWidgets, QtGui


class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.hello = ["Hallo Welt", "Hei maailma", "Hola Mundo", "Привет мир"]



        self.button = QtWidgets.QPushButton("Click me!")
        self.text = QtWidgets.QLabel("Hello World", alignment=QtCore.Qt.AlignCenter)
        self.date = QtWidgets.QDateEdit()
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.date)
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.button)
        self.player_names = [QtWidgets.QLineEdit()]
        self.layout.addWidget(self.player_names[0])


        self.button.clicked.connect(self.magic)

    @QtCore.Slot()
    def magic(self):
        self.text.setText(random.choice(self.hello))
        self.player_names.append(QtWidgets.QLineEdit())
        self.layout.addWidget(self.player_names[-1])
        self.text.setText(str(self.date.date()))


if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    widget = MyWidget()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())
