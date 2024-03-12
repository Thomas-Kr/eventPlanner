# Event Planner.
Events Planner is a program for school workers where they can plan all school activities.
## Installation.

1. Download Python 3.12.1 .
2. Download all the files from this repository and place them in the same directory.
3. Install all the neccessary libraries:
```bash
pip install PyQt5
pip install json
pip install pypyodbc
```
4. Open terminal and go to the project's directory.
5. Run the following command:
```bash
python event_planner.py'
```

## Usage.
1. When the program starts, you will be prompted to install an ODBC driver if you do not have one. Install the driver following the instructions in the window that opens.
2. In the opened “Sign In” window, you need to enter your username and password. When the data is entered, press Enter.

In order to create a new event, you need to: 
1. Open the "Main" tab.
2. Write event name.
3. Choose event type.
4. Choose class that will attend the event.
5. Choose event time.
6. Chosee event date.
7. Click on the "Create Event" button.

In order to see all the events, you need to open the "Events" tab. Moreover, you can update the table if you click on the "Update Table" button.

In order to change settings, you need to go to the "Settings" tab. There you can: 
- Change language by selecting it in the dropdown list.
- Change theme of the application to dark or light.



