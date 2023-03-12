import sys
from datetime import datetime
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtWidgets import QMainWindow
from selenium.webdriver.common.by import By
from data_analysis import read_matches, filter_matches, plot_scores, print_player_stats
from selenium.webdriver.firefox.options import Options
from main import load_data
from selenium import webdriver
import string


def remove_non_ascii(a_str):
    ascii_chars = set(string.printable)

    return ''.join(
        filter(lambda x: x in ascii_chars, a_str)
    )


def get_player_name(url):
    """
    function searches steam's user's profile for its nickname
    :param url: url to steam profile
    :return: player name (string)
    """
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    driver.get(url)
    name = driver.find_element(By.CLASS_NAME, "actual_persona_name").text
    driver.quit()
    return name


class MainUIWindow(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.instruction = QtWidgets.QLabel("To download the data from steam press 'Get data from steam' to produce report from data press 'Process data'"
                                            , alignment=QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.instruction)
        self.get_data_button = QtWidgets.QPushButton("Get data from steam")
        self.layout.addWidget(self.get_data_button)
        self.process_data_button = QtWidgets.QPushButton("Process data")
        self.layout.addWidget(self.process_data_button)


class GetDataWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QtWidgets.QVBoxLayout(self)
        with open('download_help.txt', 'r') as file:
            help_text = ""
            for line in file:
                help_text += line
        self.instruction = QtWidgets.QLabel(help_text, alignment=QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.instruction)
        self.get_data_button = QtWidgets.QPushButton("Get data")
        self.layout.addWidget(self.get_data_button)
        self.get_data_button.clicked.connect(self.get_data_clicked)
        self.return_button = QtWidgets.QPushButton("Return to main menu")
        self.layout.addWidget(self.return_button)

    @QtCore.Slot()
    def get_data_clicked(self):
        load_data()
        self.notification = QtWidgets.QLabel("Data has been downloaded and saved")
        self.layout.addWidget(self.notification)


class ProcessDataWindow(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QtWidgets.QVBoxLayout(self)
        with open('report_help.txt', 'r') as file:
            help_text = ""
            for line in file:
                help_text += line
        self.instruction = QtWidgets.QLabel(help_text, alignment=QtCore.Qt.AlignCenter)
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
        self.players_label = QtWidgets.QLabel("Players whose reports are to be generated (format same as above)")
        self.layout.addWidget(self.players_label)
        self.players = QtWidgets.QTextEdit()
        self.layout.addWidget(self.players)
        self.plots = QtWidgets.QCheckBox("Generate score plot for each map")
        self.layout.addWidget(self.plots)
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
            return
        participants_links = self.participants.toPlainText().strip(' ').strip('\n').split(',')
        if len(participants_links) == 0:
            return
        players_links = self.players.toPlainText().strip(' ').strip('\n').split(',')
        if len(players_links) == 0:
            return
        generate_plots = self.plots.isChecked()

        participants = []
        for participant in participants_links:
            participants.append(get_player_name(participant))
        players = []
        for player in players_links:
            players.append(get_player_name(player))

        matches = read_matches('results')
        filtered_matches = filter_matches(matches, players + participants, begin_date, finish_date)
        for player in players:
            print_player_stats(player, filtered_matches, remove_non_ascii(player))
        if generate_plots:
            plot_scores(players[0], filtered_matches)


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
