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
import pypyodbc as odbc
from datetime import datetime

class SchoolDB:
    def __init__(self):
        self.credentials = self.read_DB_credentials()
        self.conn_string = f'''Driver={self.credentials['driver']};Server=tcp:{self.credentials['server']},1433;
                                     Database={self.credentials['database']};Uid={self.credentials['login']};Pwd={self.credentials['password']};
                                     Encrypt=yes;TrustServerCertificate=no;conn Timeout=30;'''

    def read_DB_credentials(self):
        with open('credentials.json', 'r', encoding='utf-8') as file:
            return json.load(file)

    def select_all_events(self):
        conn = odbc.connect(self.conn_string)
        cursor = conn.cursor()

        data = []

        query_1 = f'''
        SELECT classID, eventID
        FROM RegisteredEvents
        '''

        cursor.execute(query_1)
        events_data = cursor.fetchall()

        for event in events_data:
            query_2 = f'''
            SELECT classNumber, classLetter
            FROM Classes
            WHERE classID = {event[0]}
            '''

            cursor.execute(query_2)
            class_data = cursor.fetchall()

            query_3 = f'''
            SELECT eventName, eventDate
            FROM Events
            WHERE eventID = {event[1]}
            '''

            cursor.execute(query_3)
            event_data = cursor.fetchall()

            data.append([str(class_data[0][0]), class_data[0][1], event_data[0][0], event_data[0][1].strftime("%Y-%m-%d %H:%M")])

        conn.commit()
        conn.close()

        return data
    
    # Basic version
    def create_event(self, class_number: int, class_letter: str, event_name: str, event_type_name: str, event_date: str):
        conn = odbc.connect(self.conn_string)
        cursor = conn.cursor()

        # Find class by class_number and class_letter
        query_1 = f'''
        SELECT classID 
        FROM Classes 
        WHERE classNumber = {class_number} 
        AND classLetter = '{class_letter}';
        '''
        
        cursor.execute(query_1)
        class_id = cursor.fetchone()[0]

        # Find index of event type
        query_2 = f'''
        SELECT eventTypeID 
        FROM EventTypes 
        WHERE eventTypeName = '{event_type_name}';
        '''

        cursor.execute(query_2)
        event_type_id = cursor.fetchone()[0]

        # Create event
        query_3 = f'''
        INSERT INTO Events (eventName, eventDate, eventTypeID) VALUES ('{event_name}', '{event_date}', '{event_type_id}');
        '''

        cursor.execute(query_3)
        cursor.execute("SELECT SCOPE_IDENTITY()") # Get index of the created event
        event_id = cursor.fetchone()[0]

        # Add the event to the RegisteredEvents table
        query_4 = f'''
        INSERT INTO RegisteredEvents(classID, eventID) VALUES ({class_id}, {event_id});   
        '''

        cursor.execute(query_4)

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

        cursor.execute(query)

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
        cursor.execute(query)
        data = cursor.fetchall()

        conn.commit()
        conn.close()

        return sorted(data, key=lambda x: x[0])
    
    def select_all_event_types(self):
        query = f'''
        SELECT eventTypeID, eventTypeName 
        FROM EventTypes;
        '''

        conn = odbc.connect(self.conn_string)
        cursor = conn.cursor()
        cursor.execute(query)
        data = cursor.fetchall()

        conn.commit()
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
        cursor.execute(query)
        data = cursor.fetchall()

        conn.commit()
        conn.close()

        return data

if __name__ == "__main__":
    school_DB = SchoolDB()
    #school_DB.create_event(class_number=10, class_letter='a', event_name='New Year concerts', event_type_name='Concert', event_date='2024-03-07 15:30')
    #print(school_DB.select_all_from_table("RegisteredEvents"))

    #print(school_DB.select_all_classes())
    #print(school_DB.select_all_event_types())
    print(school_DB.select_all_events())
