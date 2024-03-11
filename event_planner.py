import sys
import json

from datetime import datetime
from PyQt5.QtCore import QDate, QTime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, 
                             QVBoxLayout, QWidget, QTabWidget, QComboBox, 
                             QCheckBox, QCalendarWidget, QLabel, QDialog,
                             QMessageBox, QLineEdit, QTimeEdit, QTableWidget,
                             QTableWidgetItem)

from DB_manager import SchoolDB

def read_json(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)
    
def read_qss(file_path: str):
    with open(file_path, 'r') as file:
        return file.read()
    
school_db = SchoolDB()

class SignInWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Sign In')

        self.username_label = QLabel('Username:', self)
        self.username_input = QLineEdit(self)
        self.password_label = QLabel('Password:', self)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)

        self.sign_in_button = QPushButton('Sign In', self)
        self.sign_in_button.clicked.connect(self.authenticate)

        layout = QVBoxLayout()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.sign_in_button)

        self.setLayout(layout)

    def authenticate(self):
        user_login = self.username_input.text()
        user_password = self.password_input.text()

        if school_db.authenticate(user_login, user_password):
            self.accept()
        else:
            QMessageBox.warning(self, 'Error', 'Invalid username or password')


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.settings = read_json('settings.json')
        self.translations = read_json('translations.json')

        self.white_style = read_qss('white_style.qss')
        self.dark_style = read_qss('dark_style.qss')

        self.tab_widget = QTabWidget()

        main_tab = QWidget()
        settings_tab = QWidget()
        event_list_tab = QWidget()

        # Add 'main' and 'settings' tabs
        self.create_main_tab(main_tab)
        self.create_settings_tab(settings_tab)
        self.create_event_list_tab(event_list_tab)

        self.tab_widget.addTab(main_tab, self.translations['main'][self.settings['language']])
        self.tab_widget.addTab(event_list_tab, "Events")
        self.tab_widget.addTab(settings_tab, self.translations['settings'][self.settings['language']])

        self.setCentralWidget(self.tab_widget)

        # Window's settings
        self.setGeometry(100, 100, 600, 600)
        self.setWindowTitle('Event Planner')
        
        self.apply_theme(self.settings['light_theme'] == True)

    def create_main_tab(self, main_tab: QWidget):
        self.selected_class = f'{school_db.select_all_classes()[0][0]} {school_db.select_all_classes()[0][1]}'
        self.selected_event_time = QTime(9, 0)
        self.selected_date = datetime.now().strftime('%Y-%m-%d')
        self.selected_event_type = school_db.select_all_event_types()[0][1]

        # Create a button in the Main tab
        self.create_event_button = QPushButton(self.translations['create_event'][self.settings['language']], main_tab)
        self.create_event_button.clicked.connect(self.create_event)

        # Create text fields 
        self.event_name_label = QLabel('Event name:', self)
        self.event_name_input = QLineEdit(self)

        # Create a dropdown list with all the classes in the school
        self.classes_dropdown = QComboBox(main_tab)
        classes = school_db.select_all_classes()

        for cl in classes:
            self.classes_dropdown.addItem(f'{cl[0]} {cl[1]}')

        self.classes_dropdown.currentTextChanged.connect(self.select_class)

        # Create a dropdown list with all the event types
        self.event_types_dropdown = QComboBox(main_tab)
        event_types = school_db.select_all_event_types()

        for event_type in event_types:
            self.event_types_dropdown.addItem(event_type[1])

        self.event_types_dropdown.currentTextChanged.connect(self.select_event_type)

        # Create time widget
        self.event_time = QTimeEdit(self)
        self.event_time.setDisplayFormat("HH:mm")

        self.event_time.setTime(self.selected_event_time)

        self.event_time.timeChanged.connect(self.handle_time_changed)

        # Create a label and calendar widget for date selection
        self.date_label = QLabel(self.translations['event_date'][self.settings['language']], main_tab)
        self.calendar_widget = QCalendarWidget(main_tab)
        self.calendar_widget.clicked[QDate].connect(self.show_selected_date)

        # Set layout for the Main tab and add all the widgets
        layout = QVBoxLayout()
        layout.addWidget(self.create_event_button)
        layout.addWidget(self.event_name_label)
        layout.addWidget(self.event_name_input)
        layout.addWidget(self.event_types_dropdown)
        layout.addWidget(self.classes_dropdown)
        layout.addWidget(self.event_time)
        layout.addWidget(self.date_label)
        layout.addWidget(self.calendar_widget)
        main_tab.setLayout(layout)

    def create_event_list_tab(self, event_list_tab: QWidget):
        self.table = QTableWidget(event_list_tab) 

        self.events = school_db.select_all_events()
        print(self.events)
        self.table.setColumnCount(4)  
        self.table.setRowCount(len(self.events))

        self.update_table()

        # Create button for table updating
        self.update_button = QPushButton("Update Table", event_list_tab)
        self.update_button.clicked.connect(self.update_table) # does not work propeprly for now

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addWidget(self.update_button)
        event_list_tab.setLayout(layout)

    def update_table(self):
        # Add data to the table
        for row_index, row_data in enumerate(self.events):
            for col_index, cell_data in enumerate(row_data):
                item = QTableWidgetItem(cell_data)
                self.table.setItem(row_index, col_index, item)

        self.table.resizeColumnsToContents()

    def create_settings_tab(self, settings_tab: QWidget):
        # Create a dropdown menu in the Settings tab
        self.language_dropdown = QComboBox(settings_tab)
        self.language_dropdown.addItem('latvian')
        self.language_dropdown.addItem('english')

        # Set the first element of the dropdown menu - last used language
        initial_index = self.language_dropdown.findText(self.settings['language'])
        self.language_dropdown.setCurrentIndex(initial_index)

        self.language_dropdown.currentTextChanged.connect(self.select_language)

        # Create a checkbox for the theme
        self.light_theme_checkbox = QCheckBox(self.translations['light_theme'][self.settings['language']], settings_tab)
        self.light_theme_checkbox.setChecked(self.settings.get('light_theme', False))
        self.light_theme_checkbox.stateChanged.connect(self.toggle_theme)

        # Set layout for the Settings tab
        layout = QVBoxLayout()
        layout.addWidget(self.language_dropdown)
        layout.addWidget(self.light_theme_checkbox)
        settings_tab.setLayout(layout)

    def update_language(self):
        # Update the text in the main tab
        self.create_event_button.setText(self.translations['create_event'][self.settings['language']])
        self.date_label.setText(self.translations['event_date'][self.settings['language']])

        # Update the tab names
        self.tab_widget.setTabText(0, self.translations['main'][self.settings['language']])
        self.tab_widget.setTabText(1, self.translations['settings'][self.settings['language']])
        
        # Update the checkbox name
        self.light_theme_checkbox.setText(self.translations['light_theme'][self.settings['language']])

    def create_event(self):
        try:
            if self.event_name_input.text() != '':
                school_db.create_event(class_number=self.selected_class.split()[0], class_letter=self.selected_class.split()[1],
                                       event_name=self.event_name_input.text(), event_type_name=self.selected_event_type, 
                                       event_date=f'{self.selected_date} {f'{self.selected_event_time.hour()}:{self.selected_event_time.minute()}'}')
                
                QMessageBox.information(self, 'Event Created', 'Event was succesfully created!')
        except Exception as err:
            print(err)

    # Write the date that is currently selected on the calendar
    def show_selected_date(self, date: QDate):
        self.selected_date = date.toString("yyyy-MM-dd")
        self.date_label.setText(f'{self.translations["event_date"][self.settings["language"]]}: {self.selected_date}')

    def select_language(self, current_lang: str):
        self.settings['language'] = current_lang.lower()

        with open('settings.json', 'w') as file:
            json.dump(self.settings, file, indent=4)

        self.update_language()

    def handle_time_changed(self, selected_event_time):
        self.selected_event_time = selected_event_time

    def select_event_type(self, selected_event_type: str):
        self.selected_event_type = selected_event_type

    def select_class(self, selected_class: str):
        self.selected_class = selected_class
        
    def apply_theme(self, is_white_theme: bool):
        if is_white_theme:
            self.setStyleSheet(self.white_style)
        else:
            self.setStyleSheet(self.dark_style)

    def toggle_theme(self, state: int):
        if state == 2:
            self.settings['light_theme'] = True # 2 corresponds to checked state
        else:
            self.settings['light_theme'] = False

        # Save whether the light theme is selected or not
        with open('settings.json', 'w') as file:
            json.dump(self.settings, file, indent=4)
            
        self.apply_theme(self.settings['light_theme'])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    sign_in_window = SignInWindow()
    if sign_in_window.exec_() == QDialog.Accepted:
        main_window = MainWindow()
        main_window.show()
        sys.exit(app.exec_())