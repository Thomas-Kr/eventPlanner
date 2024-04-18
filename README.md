# Event Planner.
Events Planner is a program for school workers where they can plan all school activities.
## Installation.

1. Download Python 3.12.1 .
2. Download all the files from this repository and place them in the same directory.
3. Install all the neccessary libraries:
```bash
pip install PyQt5
pip install json
pip install pyodbc
```
4. Open terminal and go to the project's directory.
5. Run the following command:
```bash
python event_planner.py
```

## Usage.
1. When the program is launched, “Sign In” window will be opened, you need to enter your username and password. When the data is entered, press Enter.

On the "Main" tab you can create a new event. In order to do it: 
1. Write event name.
2. Choose event type.
3. Choose class that will attend the event.
4. Choose event time.
5. Chosee event date.
6. Click on the "Create Event" button.

![Main tab guide](https://github.com/Thomas-Kr/eventPlanner/blob/main/Sources/Tutor_1.png)

On the "Events" tab you can:
- See all the events in the table.
- Update the table by clicking on the "Update Table" button.

![Events tab guide](https://github.com/Thomas-Kr/eventPlanner/blob/main/Sources/Tutor_2.png)

In the "Users" tab, you can:
- Change user information.
- Add new users.
- Delete users.

![Users tab guide](https://github.com/Thomas-Kr/eventPlanner/blob/main/Sources/Tutor_3.png)

On the "Settings" tab you can: 
- Change language by selecting it in the dropdown list.
- Change theme of the application to dark or light.

![Settings tab guide](https://github.com/Thomas-Kr/eventPlanner/blob/main/Sources/Tutor_4.png)

## Details
- Database is local. After it is created, it is filled with default data.







