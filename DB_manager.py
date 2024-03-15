'''
Database's "SchoolEvents" structure

TABLE Classes (
    classID INT PRIMARY KEY IDENTITY,
    classNumber TINYINT,
    classLetter CHAR(1)
);

TABLE Events (
    eventID INT PRIMARY KEY IDENTITY,
    eventName VARCHAR(50),
    eventDate DATETIME
    eventTypeID INT,
    FOREIGN KEY (eventTypeID) REFERENCES EventTypes(eventTypeID) 
);

TABLE RegisteredEvents (
    registeredEventID INT PRIMARY KEY IDENTITY,
    classID INT,
    eventID INT,
    FOREIGN KEY (classID) REFERENCES Classes(classID),
    FOREIGN KEY (eventID) REFERENCES Events(eventID)
);

TABLE EventTypes (
    eventTypeID INT PRIMARY KEY IDENTITY,
    eventTypeName VARCHAR(50),
    isStudyEvent BIT
)

TABLE Roles (
    roleID INT PRIMARY KEY IDENTITY,
    roleName VARCHAR(20)
)

TABLE Users (
    userID INT PRIMARY KEY IDENTITY,
    userLogin VARCHAR(20),
    userPassword VARCHAR(20),
    roleID INT,
    classID INT,
    FOREIGN KEY (roleID) REFERENCES Roles(roleID),
    FOREIGN KEY (classID) REFERENCES Classes(classID),
)
            
self.role_id represents the role of the authenticated user:
1 - School Worker
2 - Class Teacher
3 - School Administrator
4 - Superuser
'''

import json
import logging
from datetime import datetime

import pypyodbc as odbc

from os import system

# Configure logging
logging.basicConfig(filename='errors.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class SchoolDB:
    def __init__(self):
        self.check_driver_installed()
        self.credentials = self.read_DB_credentials()
        self.conn_string = f'''Driver={self.credentials['driver']};Server=tcp:{self.credentials['server']},1433;
                               Database={self.credentials['database']};Uid={self.credentials['login']};Pwd={self.credentials['password']};
                               Encrypt=yes;TrustServerCertificate=no;conn Timeout=90;'''
        
    def connect_to_db(self):
        for attempts in range(3):
            try:
                conn = odbc.connect(self.conn_string)
                conn.close()
                return True
            except Exception:
                pass
        return False
        
    def check_driver_installed(self):
        drivers = [x for x in odbc.drivers()]

        if 'ODBC Driver 18 for SQL Server' not in drivers:
            try:
                system('msiexec /i "msodbcsql.msi"')
            except Exception as err:
                logging.error(f'Error downloading ODBC driver: {err}')

    def read_DB_credentials(self):
        try:
            with open('credentials.json', 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as err:
            logging.error(f'Error reading credentials.json: {err}')

    def select_all_events(self, show_finished_events):
        conn = odbc.connect(self.conn_string)
        cursor = conn.cursor()

        data = []

        # Select all classID and eventID of every event
        query_1 = f'''
        SELECT classID, eventID
        FROM RegisteredEvents
        '''

        try:
            cursor.execute(query_1)
            events_data = cursor.fetchall()
        except Exception as err:
            logging.error(f'Error executing query_1 in select_all_events(): {err}')
            conn.close()
            return -1

        for event in events_data:
            # Select class data by its ID
            query_2 = f'''
            SELECT classNumber, classLetter
            FROM Classes
            WHERE classID = {event[0]}
            '''

            try:
                cursor.execute(query_2)
                class_data = cursor.fetchall()
            except Exception as err:
                logging.error(f'Error executing query_2 in select_all_events(): {err}')
                conn.close()
                return -1

            # Select event data by its ID
            query_3 = f'''
            SELECT eventName, eventDate, eventTypeID
            FROM Events
            WHERE eventID = {event[1]}
            '''

            try:
                cursor.execute(query_3)
                event_data = cursor.fetchall()
            except Exception as err:
                logging.error(f'Error executing query_3 in select_all_events(): {err}')
                conn.close()
                return -1
            
            event_date = event_data[0][1]

            if show_finished_events is False and event_date < datetime.now():
                continue

            # Select event type name by its ID
            query_4 = f'''
            SELECT eventTypeName
            FROM EventTypes
            WHERE eventTypeID = {event_data[0][2]}
            '''

            try:
                cursor.execute(query_4)
                event_name = cursor.fetchall()
            except Exception as err:
                logging.error(f'Error executing query_4 in select_all_events(): {err}')
                conn.close()
                return -1

            data.append([str(class_data[0][0]) + class_data[0][1], event_data[0][0], event_date.strftime("%Y-%m-%d %H:%M"), event_name[0][0]])

        conn.commit()
        conn.close()

        grouped_data = {}

        for subarray in data:
            key = tuple(subarray[1:])
            if key in grouped_data:
                grouped_data[key].append(subarray[0])
            else:
                grouped_data[key] = [subarray[0]]

        return [[[', '.join(subarrays)], *key] for key, subarrays in grouped_data.items()]
    
    # Basic version
    def create_event(self, class_number: int, class_letter: str, event_name: str, event_date: str, event_type_name: str):
        conn = odbc.connect(self.conn_string)
        cursor = conn.cursor()

        # Find ID of class
        query_1 = f'''
        SELECT classID 
        FROM Classes 
        WHERE classNumber = {class_number} 
        AND classLetter = '{class_letter}';
        '''
        
        try:
            cursor.execute(query_1)
            class_id = cursor.fetchone()[0]
        except Exception as err:
                logging.error(f'Error executing query_1 in create_event(): {err}')
                conn.close()
                return -1
            

        # Find ID of event type
        query_2 = f'''
        SELECT eventTypeID 
        FROM EventTypes 
        WHERE eventTypeName = '{event_type_name}';
        '''

        try:
            cursor.execute(query_2)
            event_type_id = cursor.fetchone()[0]
        except Exception as err:
                logging.error(f'Error executing query_2 in create_event(): {err}')
                conn.close()
                return -1

        # Find ID of event
        query_3 = f'''
        SELECT eventID 
        FROM Events 
        WHERE eventName = '{event_name}' AND eventDate = '{event_date}' AND eventTypeID = '{event_type_id}'
        '''

        try:
            cursor.execute(query_3)
            event_id = cursor.fetchone()
        except Exception as err:
                logging.error(f'Error executing query_3 in create_event(): {err}')
                conn.close()
                return -1

        if not event_id:
            # If event does not exist - create it
            query_4 = f'''
            INSERT INTO Events (eventName, eventDate, eventTypeID) VALUES ('{event_name}', '{event_date}', '{event_type_id}');
            '''

            try:
                cursor.execute(query_4)
                cursor.execute("SELECT SCOPE_IDENTITY()") # Get index of the created event
                event_id = cursor.fetchone()[0]
            except Exception as err:
                logging.error(f'Error executing query_4 in create_event(): {err}')
                conn.close()
                return -1
        else:
            # If event already exists - check if the class already attends it
            query_5 = f'''
            SELECT RegisteredEventID
            FROM RegisteredEvents
            WHERE classID = {class_id} AND eventID = {event_id[0]};
            '''

            try:
                cursor.execute(query_5)
                if cursor.fetchone():
                    conn.close()
                    return 0
            except Exception as err:
                logging.error(f'Error executing query_5 in create_event(): {err}')
                conn.close()
                return -1
        
        # Add the event to the RegisteredEvents table
        query_6 = f'''
        INSERT INTO RegisteredEvents(classID, eventID) VALUES ({class_id}, {event_id[0]});   
        '''

        try:
            cursor.execute(query_6)
        except Exception as err:
            logging.error(f'Error executing query_6 in create_event(): {err}')
            return -1
        finally:
            conn.commit()
            conn.close()

    def authenticate(self, user_login: str, input_password: str):
        conn = odbc.connect(self.conn_string)
        cursor = conn.cursor()

        query = f'''
        SELECT userPassword, roleID 
        FROM Users 
        WHERE userLogin = '{user_login}';
        '''

        try:
            cursor.execute(query)
        except Exception as err:
                logging.error(f'Error executing query in authenticate(): {err}')
                conn.close()
                return -1

        try:
            password, self.role_id = cursor.fetchone()
        except TypeError:
            return False
        finally:
            conn.close()

        if input_password == password:
            return True 
        
        return False
    
    def select_all_classes(self):
        query = f'''
        SELECT classNumber, classLetter 
        FROM Classes;
        '''

        conn = odbc.connect(self.conn_string)
        cursor = conn.cursor()

        try:
            cursor.execute(query)
            data = cursor.fetchall()
        except Exception as err:
                logging.error(f'Error executing query in select_all_classes(): {err}')
                return
        finally:   
            conn.close()

        return sorted(data, key=lambda x: x[0])
    
    def select_all_event_types(self):
        query = f'''
        SELECT eventTypeID, eventTypeName 
        FROM EventTypes;
        '''

        conn = odbc.connect(self.conn_string)
        cursor = conn.cursor()

        try:
            cursor.execute(query)
            data = cursor.fetchall()
        except Exception as err:
                logging.error(f'Error executing query in select_all_event_types(): {err}')
                return
        finally:   
            conn.close()

        return data
    
    def select_events_by_type(self, event_type):
        query = f'''
        SELECT eventName, eventDate
        FROM Events
        WHERE eventTypeID = '{event_type}'
        '''
        conn = odbc.connect(self.conn_string)
        cursor = conn.cursor()

        try:
            cursor.execute(query)
            data = cursor.fetchall()
        except Exception as err:
                logging.error(f'Error executing query in select_events_by_type(): {err}')
                return
        finally:
            conn.close()

        return data
    
    def delete_event(self, event_name, event_date):
        conn = odbc.connect(self.conn_string)
        cursor = conn.cursor()

        # Get event id from Events
        query_1 = f'''
        SELECT eventID 
        FROM Events
        WHERE eventName = '{event_name}' AND eventDate = '{event_date}'
        '''

        try:
            cursor.execute(query_1)
            event_id = cursor.fetchone()[0]
        except Exception as err:
            logging.error(f'Error executing query_1 in delete_event(): {err}')
            conn.close()
            return False

        # Delete event from RegisteredEvents table
        query_2 = f'''
        DELETE FROM RegisteredEvents 
        WHERE eventID = {event_id};
        '''

        try:
            cursor.execute(query_2)
        except Exception as err:
            logging.error(f'Error executing query_2 in delete_event(): {err}')
            conn.close()
            return False

        # Delete event from Events table
        query_3 = f'''
        DELETE FROM Events 
        WHERE eventID = {event_id};
        '''

        try:
            cursor.execute(query_3)
            conn.commit()
            return True
        except Exception as err:
            logging.error(f'Error executing query_3 in delete_event(): {err}')
            return False
        finally:
            conn.close()

    def select_all_users(self):
        conn = odbc.connect(self.conn_string)
        cursor = conn.cursor()

        # Select all users
        query_1 = f'''
        SELECT userLogin, userPassword, roleID, classID
        FROM Users;
        '''

        try:
            cursor.execute(query_1)
            users = cursor.fetchall()
        except Exception as err:
            logging.error(f'Error executing query_1 in select_all_users(): {err}')
            conn.close()
            return -1

        for i in range(len(users)):
            # Get roleName by roleID
            query_2 = f'''
            SELECT roleName
            FROM Roles
            WHERE roleID = {users[i][2]}
            '''

            try:
                cursor.execute(query_2)
                role = cursor.fetchone()[0]
            except Exception as err:
                logging.error(f'Error executing query_2 in select_all_users(): {err}')
                conn.close()
                return -1
            
            # Get class and its letter by classID 
            query_3 = f'''
            SELECT classNumber, classLetter
            FROM Classes
            WHERE classID = {users[i][3]}
            '''

            try:
                cursor.execute(query_3)
                class_data = cursor.fetchone()
            except Exception as err:
                logging.error(f'Error executing query_3 in select_all_users(): {err}')
                conn.close()
                return -1
            
            users[i] = (users[i][0], users[i][1], role, f'{class_data[0]}{class_data[1]}')

        conn.close()
        return users

if __name__ == "__main__":
    school_DB = SchoolDB()
    #school_DB.create_event(class_number=10, class_letter='a', event_name='New Year concerts', event_type_name='Concert', event_date='2024-03-07 15:30')
    #print(school_DB.select_all_from_table("RegisteredEvents"))

    #print(school_DB.select_all_classes())
    #print(school_DB.select_all_event_types())
    #print(school_DB.select_all_events(True))
    print(school_DB.select_all_users())