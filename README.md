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
python event_planner.py
```

## Usage.
1. When the program starts, you will be prompted to install an ODBC driver if you do not have one. Install the driver following the instructions in the window that opens.
2. In the opened “Sign In” window, you need to enter your username and password. When the data is entered, press Enter.

On the "Main" tab you can create a new event. In order to do it: 
1. Write event name.
2. Choose event type.
3. Choose class that will attend the event.
4. Choose event time.
5. Chosee event date.
6. Click on the "Create Event" button.

On the "Events tab you can:
- See all the events in the table.
- Update the table by clicking on the "Update Table" button.

In order to change settings, you need to go to the "Settings" tab. There you can: 
- Change language by selecting it in the dropdown list.
- Change theme of the application to dark or light.



