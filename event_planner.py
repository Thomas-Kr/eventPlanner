import sys
import json
import logging

from datetime import datetime
from PyQt5.QtCore import QDate, QTime, Qt, QLocale
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

try:
    settings = read_json('settings.json')
    translations = read_json('translations.json')
except Exception as err:
    logging.error(f'Error reading *.json files: {err}')

class SignInWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(translations['sign_in'][settings['language']])

        self.username_label = QLabel(translations['username'][settings['language']], self)
        self.username_input = QLineEdit(self)
        self.password_label = QLabel(translations['password'][settings['language']], self)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)

        self.sign_in_button = QPushButton(translations['sign_in'][settings['language']], self)
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
        
        is_authenticated = school_db.authenticate(user_login, user_password)

        if is_authenticated:
            self.accept()
        elif is_authenticated == -1:
            QMessageBox.warning(self, translations['error'][settings['language']], translations['auth_error'][settings['language']])
        else:
            QMessageBox.warning(self, translations['error'][settings['language']], translations['invalid_usrn_or_psw'][settings['language']])


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        try:
            self.white_style = read_qss('white_style.qss')
            self.dark_style = read_qss('dark_style.qss')
        except Exception as err:
            logging.error(f'Error reading *.qss files: {err}')

        self.tab_widget = QTabWidget()

        main_tab = QWidget()
        settings_tab = QWidget()
        event_list_tab = QWidget()

        # Add 'main' and 'settings' tabs
        self.create_main_tab(main_tab)
        self.create_settings_tab(settings_tab)
        self.create_event_list_tab(event_list_tab)

        self.tab_widget.addTab(main_tab, translations['main'][settings['language']])
        self.tab_widget.addTab(event_list_tab, translations['events'][settings['language']])
        self.tab_widget.addTab(settings_tab, translations['settings'][settings['language']])

        self.setCentralWidget(self.tab_widget)

        # Window's settings
        self.setGeometry(100, 100, 600, 600)
        self.setWindowTitle(translations['event_planner'][settings['language']])
        
        self.apply_theme(settings['light_theme'] == True)

    def create_main_tab(self, main_tab: QWidget):
        # Default values
        self.selected_class = f'{school_db.select_all_classes()[0][0]} {school_db.select_all_classes()[0][1]}'
        self.selected_event_time = QTime(9, 0)
        self.selected_date = datetime.now().strftime('%Y-%m-%d')
        self.selected_event_type = school_db.select_all_event_types()[0][1]

        # Create a button in the Main tab
        self.create_event_button = QPushButton(translations['create_event'][settings['language']]+':', main_tab)
        self.create_event_button.clicked.connect(self.create_event)

        # Create label
        self.event_name_label = QLabel(translations['event_name'][settings['language']]+':', main_tab)
        self.event_name_input = QLineEdit(main_tab)

        # Create a label and dropdown list with all the classes in the school
        self.classes_dropdown_label = QLabel(translations['class_label'][settings['language']]+':', main_tab)
        self.classes_dropdown = QComboBox(main_tab)
        classes = school_db.select_all_classes()

        for cl in classes:
            self.classes_dropdown.addItem(f'{cl[0]} {cl[1]}')

        self.classes_dropdown.currentTextChanged.connect(self.select_class)

        # Create a label and dropdown list with all the event types
        self.event_type_label = QLabel(translations['event_type_label'][settings['language']]+':', self)
        self.event_types_dropdown = QComboBox(main_tab)
        event_types = school_db.select_all_event_types()

        for event_type in event_types:
            self.event_types_dropdown.addItem(event_type[1])

        self.event_types_dropdown.currentTextChanged.connect(self.select_event_type)

        # Create a label and time widget
        self.event_time_label = QLabel(translations['event_time_label'][settings['language']]+':', self)
        self.event_time = QTimeEdit(self)
        self.event_time.setDisplayFormat("HH:mm")

        self.event_time.setTime(self.selected_event_time)

        self.event_time.timeChanged.connect(self.handle_time_changed)

        # Create a label and calendar widget for date selection
        self.date_label = QLabel(translations['event_date'][settings['language']]+':', main_tab)
        self.calendar_widget = QCalendarWidget(main_tab)
        self.calendar_widget.clicked[QDate].connect(self.show_selected_date)

        if settings['language'] == "latvian":
            self.calendar_widget.setLocale(QLocale(QLocale.Latvian))
        else:
            self.calendar_widget.setLocale(QLocale(QLocale.English))

        # Set layout for the Main tab and add all the widgets
        layout = QVBoxLayout()
        layout.addWidget(self.create_event_button)

        layout.addWidget(self.event_name_label)
        layout.addWidget(self.event_name_input)

        layout.addWidget(self.event_type_label)
        layout.addWidget(self.event_types_dropdown)

        layout.addWidget(self.classes_dropdown_label)
        layout.addWidget(self.classes_dropdown)

        layout.addWidget(self.event_time_label)
        layout.addWidget(self.event_time)

        layout.addWidget(self.date_label)
        layout.addWidget(self.calendar_widget)
        main_tab.setLayout(layout)

    def create_event_list_tab(self, event_list_tab: QWidget):
        self.table = QTableWidget(event_list_tab) 

        self.table.setColumnCount(4)  
        self.table.setHorizontalHeaderLabels([translations['class'][settings['language']], translations['event_name_column'][settings['language']], 
                                              translations['event_date'][settings['language']], translations['event_type'][settings['language']]])
        self.table.itemClicked.connect(self.on_table_item_clicked)
        self.row_data = []

        self.update_table()

        self.classes_dropdown_label_2 = QLabel(translations['class_label'][settings['language']], event_list_tab)
        self.classes_dropdown_2 = QComboBox(event_list_tab)
        classes = school_db.select_all_classes()
        
        for cl in classes:
            self.classes_dropdown_2.addItem(f'{cl[0]} {cl[1]}')

        self.classes_dropdown_2.currentTextChanged.connect(self.select_class_2)

        # Create a button for adding a class to some event
        self.add_class_button = QPushButton(translations['add_class'][settings['language']], event_list_tab)
        self.add_class_button.clicked.connect(self.add_class)

        # Create a button for table updating
        self.update_button = QPushButton(translations['update_table'][settings['language']], event_list_tab)
        self.update_button.clicked.connect(self.update_table) 

        # Set layout for event_list_tab and all the widgets 
        layout = QVBoxLayout()
        layout.addWidget(self.table)

        layout.addWidget(self.classes_dropdown_label_2)
        layout.addWidget(self.classes_dropdown_2)

        layout.addWidget(self.add_class_button)
        layout.addWidget(self.update_button)
        event_list_tab.setLayout(layout)

    def update_table(self):
        self.events = school_db.select_all_events()

        if self.events == -1:
            QMessageBox.warning(self, translations['error'][settings['language']], translations['error_updating_table'][settings['language']])
            return
        
        self.table.setRowCount(len(self.events))

        # Add data to the table
        for row_index, row_data in enumerate(self.events):
            for col_index, cell_data in enumerate(row_data):
                # If its an array of classes
                if isinstance(cell_data, list):
                    cell_data = ', '.join(cell_data)

                item = QTableWidgetItem(cell_data)
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_index, col_index, item)

        self.table.resizeColumnsToContents()

    def on_table_item_clicked(self, item):
        row = item.row()
        for column in range(self.table.columnCount()):
            cell_data = self.table.item(row, column).text()
            self.row_data.append(cell_data)

    def select_class_2(self, item):
        self.selected_class_2 = item

    def add_class(self):
        if self.row_data:
            # Check if its senior class (10c, 11b, 12a) or primary - middle class (1b, 5a, 9c)
            if len(self.selected_class_2) == 4:
                class_number = self.selected_class_2[:2]
                class_letter = self.selected_class_2[3]
            else:
                class_number = self.selected_class_2[0]
                class_letter = self.selected_class_2[2]
            
            school_db.create_event(class_number, class_letter, event_name=self.row_data[1], event_date=self.row_data[2], event_type_name=self.row_data[3])
            self.update_table()
        else:
            QMessageBox.warning(self, translations['error'][settings['language']], translations['event_not_selected'][settings['language']])

    def create_settings_tab(self, settings_tab: QWidget):
        # Create a dropdown menu in the Settings tab
        self.language_dropdown = QComboBox(settings_tab)
        self.language_dropdown.addItem('latvian')
        self.language_dropdown.addItem('english')

        # Set the first element of the dropdown menu - last used language
        initial_index = self.language_dropdown.findText(settings['language'])
        self.language_dropdown.setCurrentIndex(initial_index)

        self.language_dropdown.currentTextChanged.connect(self.select_language)

        # Create a checkbox for the theme
        self.light_theme_checkbox = QCheckBox(translations['light_theme'][settings['language']], settings_tab)
        self.light_theme_checkbox.setChecked(settings.get('light_theme', False))
        self.light_theme_checkbox.stateChanged.connect(self.toggle_theme)

        # Set layout for the Settings tab
        layout = QVBoxLayout()
        layout.addWidget(self.language_dropdown)
        layout.addWidget(self.light_theme_checkbox)
        settings_tab.setLayout(layout)

    def update_language(self):
        # Update language in the main tab
        self.event_name_label.setText(translations['event_name'][settings['language']])
        self.create_event_button.setText(translations['create_event'][settings['language']])
        self.date_label.setText(translations['event_date'][settings['language']]+':')
        self.classes_dropdown_label.setText(translations['class_label'][settings['language']])
        self.event_type_label.setText(translations['event_type_label'][settings['language']])
        self.event_time_label.setText(translations['event_time_label'][settings['language']])

        if settings['language'] == "latvian":
            self.calendar_widget.setLocale(QLocale(QLocale.Latvian))
        else:
            self.calendar_widget.setLocale(QLocale(QLocale.English))

        # Update language in the events tab 
        self.table.setHorizontalHeaderLabels([translations['class'][settings['language']],translations['event_name_column'][settings['language']], 
                                              translations['event_date'][settings['language']], translations['event_type'][settings['language']]])
        self.update_button.setText(translations['update_table'][settings['language']])

        # Update language in the settings tab
        self.light_theme_checkbox.setText(translations['light_theme'][settings['language']])

        # Update the tabs' language
        self.tab_widget.setTabText(0, translations['main'][settings['language']])
        self.tab_widget.setTabText(1, translations['events'][settings['language']])
        self.tab_widget.setTabText(2, translations['settings'][settings['language']])

    def create_event(self):
        try:
            if len(self.event_name_input.text()) > 0 and len(self.event_name_input.text()) <= 50:
                if school_db.create_event(class_number=self.selected_class.split()[0], class_letter=self.selected_class.split()[1],
                                       event_name=self.event_name_input.text(), event_type_name=self.selected_event_type, 
                                       event_date=f'{self.selected_date} {f'{self.selected_event_time.hour()}:{self.selected_event_time.minute()}'}') == -1:
                    QMessageBox.warning(self, translations['error'][settings['language']], translations['error_creating_event'][settings['language']])
                
                QMessageBox.information(self, translations['event_created'][settings['language']], 
                                        translations['event_created_successfully'][settings['language']])
            else:
                QMessageBox.warning(self, translations['error'][settings['language']], translations['text_len_is_incorrect'][settings['language']])
        except Exception:
            pass

    # Write the date that is currently selected on the calendar
    def show_selected_date(self, date: QDate):
        self.selected_date = date.toString("yyyy-MM-dd")
        self.date_label.setText(f'{translations["event_date"][settings["language"]]}: {self.selected_date}')

    def select_language(self, current_lang: str):
        settings['language'] = current_lang.lower()

        with open('settings.json', 'w') as file:
            json.dump(settings, file, indent=4)

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
            settings['light_theme'] = True # 2 corresponds to checked state
        else:
            settings['light_theme'] = False

        # Save whether the light theme is selected or not
        with open('settings.json', 'w') as file:
            json.dump(settings, file, indent=4)
            
        self.apply_theme(settings['light_theme'])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    sign_in_window = SignInWindow()
    if sign_in_window.exec_() == QDialog.Accepted:
        main_window = MainWindow()
        main_window.show()
        sys.exit(app.exec_())