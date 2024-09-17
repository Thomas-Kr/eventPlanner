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
import socket
import hashlib

from datetime import datetime

import pyodbc as odbc

# Configure logging
logging.basicConfig(filename='errors.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def hash_password(password):
        salt = b'my_random_salt'
        password = password.encode('utf-8')
        hashed_password = hashlib.sha256(password + salt).hexdigest()

        return hashed_password

class SchoolDB:
    def __init__(self):
        self.server_name = socket.gethostname()
        self.credentials = self.read_DB_credentials()
        self.conn_string = f'''Driver={self.credentials['driver']};
                               Server={self.server_name};
                               Database={self.credentials['database']};'''
        self.role_id = 1
        self.classNumber, self.classLetter = 1, 'a'
        
    def create_sample_db(self):
        '''
        Creates DB with sample data
        '''
        conn_string_1 = f'''Driver={self.credentials['driver']};
                            Server={self.server_name};
                            Database=master;'''
        
        conn = odbc.connect(conn_string_1)
        conn.autocommit = True
        cursor = conn.cursor()

        query_1 = f'''
        IF DB_ID('{self.credentials['database']}') IS NULL 
        CREATE DATABASE [{self.credentials['database']}];
        '''

        try:
            cursor.execute(query_1)
            conn.commit()
        except Exception as err:
            logging.error(f'Error executing query_1 in create_sample_db(): {err}')
            return -1
        finally:
            conn.close()  

        conn_string_2 = f'''Driver={self.credentials['driver']};
                            Server={self.server_name};
                            Database={self.credentials['database']};'''
            
        conn = odbc.connect(conn_string_2)
        cursor = conn.cursor()

        query_2 = f'''
        IF OBJECT_ID('Classes', 'U') IS NULL
        BEGIN
            CREATE TABLE Classes (
                classID INT PRIMARY KEY IDENTITY,
                classNumber TINYINT,
                classLetter CHAR(1)
            )
            
            INSERT INTO Classes (classNumber, classLetter)
            VALUES
                (1, 'a'), (2, 'a'), (3, 'b'), (3, 'a'),
                (4, 'a'), (4, 'b'), (5, 'a'), (5, 'b'),
                (5, 'c'), (6, 'a'), (7, 'a'), (8, 'a'),
                (9, 'a'), (10, 'a'), (10, 'b'), (11, 'a'),
                (11, 'b'), (12, 'a')
        END
        '''

        try:
            cursor.execute(query_2)
        except Exception as err:
            logging.error(f'Error executing query_2 in create_sample_db(): {err}')
            conn.close()
            return -1

        query_3 = f'''
        IF OBJECT_ID('EventTypes', 'U') IS NULL
        BEGIN
            CREATE TABLE EventTypes (
                eventTypeID INT PRIMARY KEY IDENTITY,
                eventTypeName VARCHAR(50),
                isStudyEvent BIT
            )

            INSERT INTO EventTypes (eventTypeName, isStudyEvent)
            VALUES
                ('Examinations', 1),
                ('Trip', 0),
                ('Concert', 0),
                ('Seminars', 1)
        END
        '''

        try:
            cursor.execute(query_3)
        except Exception as err:
            logging.error(f'Error executing query_3 in create_sample_db(): {err}')
            conn.close()
            return -1

        query_4 = f'''
        IF OBJECT_ID('Events', 'U') IS NULL
        CREATE TABLE Events (
            eventID INT PRIMARY KEY IDENTITY,
            eventName VARCHAR(50),
            eventDate DATETIME,
            eventTypeID INT,
            FOREIGN KEY (eventTypeID) REFERENCES EventTypes(eventTypeID) 
        )
        '''

        try:
            cursor.execute(query_4)
        except Exception as err:
            logging.error(f'Error executing query_4 in create_sample_db(): {err}')
            conn.close()
            return -1

        query_5 = f'''
        IF OBJECT_ID('RegisteredEvents', 'U') IS NULL
        CREATE TABLE RegisteredEvents (
            registeredEventID INT PRIMARY KEY IDENTITY,
            classID INT,
            eventID INT,
            FOREIGN KEY (classID) REFERENCES Classes(classID),
            FOREIGN KEY (eventID) REFERENCES Events(eventID)
        )
        '''

        try:
            cursor.execute(query_5)
        except Exception as err:
            logging.error(f'Error executing query_5 in create_sample_db(): {err}')
            conn.close()
            return -1

        query_6 = f'''
        IF OBJECT_ID('Roles', 'U') IS NULL
        BEGIN
            CREATE TABLE Roles (
                roleID INT PRIMARY KEY IDENTITY,
                roleName VARCHAR(20)
            )

            INSERT INTO Roles (roleName)
            VALUES
                ('School Worker'),
                ('Class Teacher'),
                ('School Administrator'),
                ('Superuser')
        END
        '''

        try:
            cursor.execute(query_6)
        except Exception as err:
            logging.error(f'Error executing query_6 in create_sample_db(): {err}')
            conn.close()
            return -1

        query_7 = f'''
        IF OBJECT_ID('Users', 'U') IS NULL
        BEGIN
            CREATE TABLE Users (
                userID INT PRIMARY KEY IDENTITY,
                userLogin VARCHAR(20),
                userPassword VARCHAR(64),
                roleID INT,
                classID INT,
                FOREIGN KEY (roleID) REFERENCES Roles(roleID),
                FOREIGN KEY (classID) REFERENCES Classes(classID)
            )

            INSERT INTO Users (userLogin, userPassword, roleID, classID)
            VALUES
                ('Tomass', '{hash_password('admin123')}', 4, 1),
                ('Konstantins', '{hash_password('admin123')}', 4, 2)
        END
        '''

        try:
            cursor.execute(query_7)
            conn.commit()
        except Exception as err:
            logging.error(f'Error executing query_7 in create_sample_db(): {err}')
            return -1
        finally:
           conn.close() 
        
    def connect_to_db(self) -> bool:
        '''
        Returns True if connected \n
        Returns False if not connected
        '''
        for _ in range(3):
            try:
                conn = odbc.connect(self.conn_string)
                conn.close()
                return True
            except Exception:
                pass
        return False

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

        if event_id is None:
            # If event does not exist - create it
            query_4 = f'''
            INSERT INTO Events (eventName, eventDate, eventTypeID) VALUES ('{event_name}', '{event_date}', '{event_type_id}');
            '''

            try:
                cursor.execute(query_4)
                cursor.execute("SELECT SCOPE_IDENTITY()") # Get index of the created event
                event_id = cursor.fetchone()
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

        input_password = hash_password(input_password)

        query_1 = f'''
        SELECT userPassword, roleID, classID 
        FROM Users 
        WHERE userLogin = '{user_login}';
        '''

        try:
            cursor.execute(query_1)
        except Exception as err:
                logging.error(f'Error executing query_1 in authenticate(): {err}')
                conn.close()
                return -1

        try:
            password, self.role_id, class_id = cursor.fetchone()

            query_2 = f'''
            SELECT classNumber, classLetter 
            FROM Classes 
            WHERE classID = '{class_id}';
            '''

            try:
                cursor.execute(query_2)
                self.classNumber, self.classLetter = cursor.fetchone()
            except Exception as err:
                    logging.error(f'Error executing query_2 in authenticate(): {err}')
                    return -1
             
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
        SELECT userLogin, roleID, classID
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
            WHERE roleID = {users[i][1]}
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
            WHERE classID = {users[i][2]}
            '''

            try:
                cursor.execute(query_3)
                class_data = cursor.fetchone()
            except Exception as err:
                logging.error(f'Error executing query_3 in select_all_users(): {err}')
                conn.close()
                return -1
            
            users[i] = (users[i][0], role, f'{class_data[0]}{class_data[1]}')

        conn.close()
        return users
    
    def delete_class_from_event(self, class_number, class_letter):
        conn = odbc.connect(self.conn_string)
        cursor = conn.cursor()

        # Select class classID from Classes by classNumber and classLetter
        query_1 = f'''
        SELECT classID
        FROM Classes
        WHERE classNumber = {class_number} AND classLetter = '{class_letter}';
        '''

        try:
            cursor.execute(query_1)
            class_id = cursor.fetchone()[0]
            if class_id is None:
                return 0    
        except Exception as err:
                logging.error(f'Error executing query_1 in delete_class_from_event(): {err}')
                conn.close()
                return -1
        
        # Check if class attends the event
        query_2 = f'''
        SELECT registeredEventID
        FROM RegisteredEvents
        WHERE classID = {class_id}
        '''

        try:
            cursor.execute(query_2)
            if cursor.fetchone() is None:
                return 0
        except Exception as err:
                logging.error(f'Error executing query_2 in delete_class_from_event(): {err}')
                conn.close()
                return -1

        # Delete class from event by classID
        query_3 = f'''
        DELETE FROM RegisteredEvents
        WHERE classID = {class_id}
        '''

        try:
            cursor.execute(query_3)
            cursor.commit()
            return True
        except Exception as err:
            logging.error(f'Error executing query_3 in delete_class_from_event(): {err}')
            return -1
        finally:
            conn.close()

    def select_all_roles(self):
        conn = odbc.connect(self.conn_string)
        cursor = conn.cursor()

        # Select all users
        query = f'''
        SELECT roleName
        FROM Roles;
        '''

        try:
            cursor.execute(query)
            data = cursor.fetchall()
        except Exception as err:
            logging.error(f'Error executing query in select_all_roles(): {err}')
            return
        finally:   
            conn.close()

        return data
    
    def change_user_data(self, user_id, new_username, new_password, new_role, new_class_number, new_class_letter):
        conn = odbc.connect(self.conn_string)
        cursor = conn.cursor()

        if new_username != "":
            query_1 = f'''
            UPDATE Users 
            SET userLogin = '{new_username}'
            WHERE userID = {user_id};
            '''

            try:
                cursor.execute(query_1)
            except Exception as err:
                logging.error(f'Error executing query_1 in change_user_data(): {err}')
                conn.close()
                return -1
            
        if new_password != "":
            new_password = hash_password(new_password)

            query_2 = f'''
            UPDATE Users 
            SET userPassword = '{new_password}'
            WHERE userID = {user_id};
            '''

            try:
                cursor.execute(query_2)
            except Exception as err:
                logging.error(f'Error executing query_2 in change_user_data(): {err}')
                conn.close()
                return -1
            
        if new_role != "":
            query_3 = f'''
            SELECT roleID
            FROM Roles
            WHERE roleName = '{new_role}';
            '''

            try:
                cursor.execute(query_3)
                role_id = cursor.fetchone()[0]
            except Exception as err:
                logging.error(f'Error executing query_3 in change_user_data(): {err}')
                conn.close()
                return -1

            query_4 = f'''
            UPDATE Users 
            SET roleID = {role_id}
            WHERE userID = {user_id};
            '''

            try:
                cursor.execute(query_4)
            except Exception as err:
                logging.error(f'Error executing query_4 in change_user_data(): {err}')
                conn.close()
                return -1
            
        if new_class_number is not None:
            query_5 = f'''
            SELECT classID
            FROM Classes
            WHERE classNumber = {new_class_number} AND classLetter = '{new_class_letter}';
            '''

            try:
                cursor.execute(query_5)
                class_id = cursor.fetchone()[0]
            except Exception as err:
                logging.error(f'Error executing query_5 in change_user_data(): {err}')
                conn.close()
                return -1
            
            query_6 = f'''
            UPDATE Users 
            SET classID = {class_id}
            WHERE userID = {user_id};
            '''

            try:
                cursor.execute(query_6)
            except Exception as err:
                logging.error(f'Error executing query_6 in change_user_data(): {err}')
                conn.close()
                return -1
            
        conn.commit()
        conn.close()

    def get_user_id(self, username):
        conn = odbc.connect(self.conn_string)
        cursor = conn.cursor()

        query = f'''
        SELECT userID
        FROM Users
        WHERE userLogin = '{username}';
        '''

        try:
            cursor.execute(query)
            return cursor.fetchone()[0]
        except Exception:
            return False
        finally: 
            conn.close()

    def delete_user(self, user_id):
        conn = odbc.connect(self.conn_string)
        cursor = conn.cursor()

        query = f'''
        DELETE FROM Users
        WHERE userID = {user_id};
        '''

        try:
            cursor.execute(query)
            conn.commit()
        except Exception as err:
            logging.error(f'Error executing query in delete_user(): {err}')
            return False
        finally: 
            conn.close()   

    def add_user(self, username, password, role, class_number, class_letter):
        conn = odbc.connect(self.conn_string)
        cursor = conn.cursor()

        password = hash_password(password)

        query_1 = f'''
        SELECT userID
        FROM Users
        WHERE userLogin = '{username}';
        '''

        try:
            cursor.execute(query_1)
            user_id = cursor.fetchone()
        except Exception as err:
            logging.error(f'Error executing query_1 in add_user(): {err}')
            return -1
        
        if user_id is None:
            query_2 = f'''
            SELECT roleID
            FROM Roles
            WHERE roleName = '{role}';
            '''

            try:
                cursor.execute(query_2)
                role_id = cursor.fetchone()[0]
            except Exception as err:
                logging.error(f'Error executing query_2 in add_user(): {err}')
                return -1

            query_3 = f'''
            SELECT classID
            FROM Classes
            WHERE classNumber = {class_number} AND classLetter = '{class_letter}';
            '''
            try:
                cursor.execute(query_3)
                class_id = cursor.fetchone()[0]
            except Exception as err:
                logging.error(f'Error executing query_3 in add_user(): {err}')
                return -1
            
            query_4 = f'''
            INSERT INTO Users (userLogin, userPassword, roleID, classID)
            VALUES ('{username}', '{password}', {role_id}, {class_id});
            '''

            try:
                cursor.execute(query_4)
                conn.commit()
            except Exception as err:
                logging.error(f'Error executing query_4 in add_user(): {err}')
                return -1
            finally:
                conn.close()
        else:
            return 0
            
if __name__ == "__main__":
    school_DB = SchoolDB()
    school_DB.create_sample_db()
