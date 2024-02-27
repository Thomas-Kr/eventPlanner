import sys
import json

from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, 
                             QVBoxLayout, QWidget, QTabWidget, QComboBox, 
                             QCheckBox, QCalendarWidget, QLabel)

def read_json(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)
    
def read_qss(file_path: str):
    with open(file_path, 'r') as file:
        return file.read()

class EventPlanner(QMainWindow):
    def __init__(self):
        super(EventPlanner, self).__init__()

        self.settings = read_json('settings.json')
        self.translations = read_json('translations.json')

        self.white_style = read_qss('white_style.qss')
        self.dark_style = read_qss('dark_style.qss')

        self.tab_widget = QTabWidget()

        main_tab = QWidget()
        settings_tab = QWidget()

        # Add 'main' and 'settings' tabs
        self.create_main_tab(main_tab)
        self.create_settings_tab(settings_tab)

        self.tab_widget.addTab(main_tab, self.translations['main'][self.settings['language']])
        self.tab_widget.addTab(settings_tab, self.translations['settings'][self.settings['language']])

        self.setCentralWidget(self.tab_widget)

        # Window's settings
        self.setGeometry(100, 100, 400, 300)
        self.setWindowTitle('Event Planner')
        
        self.apply_theme(self.settings['light_theme'] == True)

    def create_main_tab(self, main_tab: QWidget):
        # Create a button in the Main tab
        self.create_event_button = QPushButton(self.translations['create_event'][self.settings['language']], main_tab)
        self.create_event_button.clicked.connect(self.create_event)

        # Create a label and calendar widget for date selection
        self.date_label = QLabel(self.translations['event_date'][self.settings['language']], main_tab)
        self.calendar_widget = QCalendarWidget(main_tab)
        self.calendar_widget.clicked[QDate].connect(self.show_selected_date)

        # Set layout for the Main tab
        layout = QVBoxLayout()
        layout.addWidget(self.create_event_button)
        layout.addWidget(self.date_label)
        layout.addWidget(self.calendar_widget)
        main_tab.setLayout(layout)

    def create_settings_tab(self, settings_tab: QWidget):
        # Create a dropdown menu in the Settings tab
        self.language_dropdown = QComboBox(settings_tab)
        self.language_dropdown.addItem('latvian')
        self.language_dropdown.addItem('english')

        # Set the first element of the dropdown menu - last used language
        initial_index = self.language_dropdown.findText(self.settings['language'])
        self.language_dropdown.setCurrentIndex(initial_index)

        # Create a checkbox for the theme
        self.light_theme_checkbox = QCheckBox(self.translations['light_theme'][self.settings['language']], settings_tab)
        self.light_theme_checkbox.setChecked(self.settings.get('light_theme', False))
        self.light_theme_checkbox.stateChanged.connect(self.toggle_theme)
        self.language_dropdown.currentTextChanged.connect(self.select_language)

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
            print(self.selected_date)
        except AttributeError:
            pass

    # Write the date that is currently selected on the calendar
    def show_selected_date(self, date: QDate):
        print(type(date))
        self.selected_date = date.toString("yyyy-MM-dd")
        self.date_label.setText(f'{self.translations["event_date"][self.settings["language"]]}: {self.selected_date}')

    def select_language(self, current_lang: str):
        self.settings['language'] = current_lang.lower()

        with open('settings.json', 'w') as file:
            json.dump(self.settings, file, indent=4)

        self.update_language()
        
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

    main_window = EventPlanner()
    main_window.show()
    
    sys.exit(app.exec_())
