import sys
from datetime import datetime
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtWidgets import QMainWindow
from main import main


class MainUIWindow(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.instruction = QtWidgets.QLabel("Main Screen", alignment=QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.instruction)
        self.get_data_button = QtWidgets.QPushButton("Get data from steam")
        self.layout.addWidget(self.get_data_button)
        self.process_data_button = QtWidgets.QPushButton("Process data")
        self.layout.addWidget(self.process_data_button)


class GetDataWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.instruction = QtWidgets.QLabel("Get data from steam", alignment=QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.instruction)
        self.get_data_button = QtWidgets.QPushButton("Get data")
        self.layout.addWidget(self.get_data_button)
        self.get_data_button.clicked.connect(self.get_data_clicked)
        self.return_button = QtWidgets.QPushButton("Return to main menu")
        self.layout.addWidget(self.return_button)

    @QtCore.Slot()
    def get_data_clicked(self):
        main()


class ProcessDataWindow(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.instruction = QtWidgets.QLabel("Test text")
        self.layout.addWidget(self.instruction)
        self.begin_date_label = QtWidgets.QLabel("Begin date")
        self.layout.addWidget(self.begin_date_label)
        self.begin_date = QtWidgets.QDateEdit()
        self.layout.addWidget(self.begin_date)
        self.finish_date_label = QtWidgets.QLabel("Finish date")
        self.layout.addWidget(self.finish_date_label)
        today = datetime.now()
        self.finish_date = QtWidgets.QDateEdit(QtCore.QDate(today.year, today.month, today.day))
        self.layout.addWidget(self.finish_date)
        self.participants_label = QtWidgets.QLabel("Players participating in game (profile links separated by commas ',' )")
        self.layout.addWidget(self.participants_label)
        self.participants = QtWidgets.QTextEdit()
        self.layout.addWidget(self.participants)
        self.players_label = QtWidgets.QLabel("Players whose reports are to be generated (format save as above)")
        self.layout.addWidget(self.players_label)
        self.players = QtWidgets.QTextEdit()
        self.layout.addWidget(self.players)
        self.plots = QtWidgets.QCheckBox("Generate score plot for each map")
        self.layout.addWidget(self.plots)
        self.directory_name_label = QtWidgets.QLabel("Name of the directory where report will be saved (if empty name will be current date)")
        self.layout.addWidget(self.directory_name_label)
        self.directory_name = QtWidgets.QLineEdit()
        self.layout.addWidget(self.directory_name)
        self.generate_report_button = QtWidgets.QPushButton("Generate Report")
        self.layout.addWidget(self.generate_report_button)
        self.return_button = QtWidgets.QPushButton("Return to main menu")
        self.layout.addWidget(self.return_button)

        self.generate_report_button.clicked.connect(self.generate_report_clicked)

    @QtCore.Slot()
    def generate_report_clicked(self):
        begin_date = self.begin_date.date()
        begin_date = datetime(begin_date.year(), begin_date.month(), begin_date.day())
        finish_date = self.finish_date.date()
        finish_date = datetime(finish_date.year(), finish_date.month(), finish_date.day())
        if begin_date > finish_date:
            # TODO (mystyk): make better exception
            return
        participants_links = self.participants.toPlainText().strip(' ').strip('\n').split(',')
        if len(participants_links) == 0:
            # TODO (mystyk): make better exception
            return
        players_links = self.players.toPlainText().strip(' ').strip('\n').split(',')
        if len(players_links) == 0:
            # TODO (mystyk): make better exception
            return
        generate_plots = self.plots.isChecked()
        directory_name = self.directory_name.text()
        if len(directory_name) == 0:
            directory_name = str(datetime.now()).split()[0]


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_main_ui()

    def set_main_ui(self):
        self.setGeometry(50, 50, 600, 600)
        self.setFixedSize(800, 600)
        self.main_ui = MainUIWindow(self)
        self.setWindowTitle("Main menu")
        self.setCentralWidget(self.main_ui)
        self.main_ui.get_data_button.clicked.connect(self.get_button_clicked)
        self.main_ui.process_data_button.clicked.connect(self.process_button_clicked)
        self.show()
        # self.player_names = [QtWidgets.QLineEdit()]
        # self.layout.addWidget(self.player_names[0])

    @QtCore.Slot()
    def get_button_clicked(self):
        self.get_data_window = GetDataWindow(self)
        self.setWindowTitle("Get Data from Steam")
        self.setCentralWidget(self.get_data_window)
        self.get_data_window.return_button.clicked.connect(self.return_button_clicked)
        self.show()

    @QtCore.Slot()
    def process_button_clicked(self):
        self.process_data_window = ProcessDataWindow(self)
        self.setWindowTitle("Process data")
        self.setCentralWidget(self.process_data_window)
        self.process_data_window.return_button.clicked.connect(self.return_button_clicked)
        self.show()

    @QtCore.Slot()
    def return_button_clicked(self):
        self.set_main_ui()


if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    widget = MainWindow()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())
