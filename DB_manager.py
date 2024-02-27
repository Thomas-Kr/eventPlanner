'''
Database's "SchoolEvents" structure

TABLE Classes (
    classID INT PRIMARY KEY IDENTITY,
    classNumber TINYINT,
    classLetter CHAR(1)
);

TABLE ClassEvents (
    eventID INT PRIMARY KEY IDENTITY,
    eventName VARCHAR(50),
    eventDate DATETIME
);

TABLE RegisteredEvents (
    registeredEventID INT PRIMARY KEY IDENTITY,
    classID INT,
    eventID INT,
    FOREIGN KEY (classID) REFERENCES Classes(classID),
    FOREIGN KEY (eventID) REFERENCES ClassEvents(eventID)
);

'''

import pypyodbc as odbc
import pandas as pd
import json

class SchoolDB:
    def __init__(self):
        self.credentials = self.read_DB_credentials()
        self.conn_string = f'''Driver={self.credentials['driver']};Server=tcp:{self.credentials['server']},1433;
                                     Database={self.credentials['database']};Uid={self.credentials['login']};Pwd={self.credentials['password']};
                                     Encrypt=yes;TrustServerCertificate=no;conn Timeout=30;'''

    def read_DB_credentials(self):
        with open('credentials.json', 'r', encoding='utf-8') as file:
            return json.load(file)

    def select_all_from_table(self, table_name):
        query = f'''
        SELECT *
        FROM {table_name}
        '''

        conn = odbc.connect(self.conn_string)
        cursor = conn.cursor()
        cursor.execute(query)
        data = cursor.fetchall()

        conn.commit()
        conn.close()

        return data
    
    # Basic version
    def create_event(self, class_number, class_letter, event_name: str, event_date: str):
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

        # Create event
        query_2 = f'''
        INSERT INTO ClassEvents (eventName, eventDate) VALUES ('{event_name}', '{event_date}');
        '''

        cursor.execute(query_2)
        cursor.execute("SELECT SCOPE_IDENTITY()") # Get index of the created event
        event_id = cursor.fetchone()[0]

        # Add the event to the RegisteredEvents table
        query_3 = f'''
        INSERT INTO RegisteredEvents(classID, eventID) VALUES ({class_id}, {event_id});   
        '''

        cursor.execute(query_3)

        conn.commit()
        conn.close()
    
        
school_DB = SchoolDB()
school_DB.create_event(10, 'a', 'Ekskursija', '2024-02-29 17:00:00')
print(school_DB.select_all_from_table("RegisteredEvents"))
