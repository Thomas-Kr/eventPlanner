import pypyodbc as odbc
import pandas as pd
import json

class SchoolDB:
    def __init__(self):
        self.credentials = self.read_DB_credentials()
        self.connection_string = f'''Driver={self.credentials['driver']};Server=tcp:{self.credentials['server']},1433;
                                     Database={self.credentials['database']};Uid={self.credentials['login']};Pwd={self.credentials['password']};
                                     Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'''
        
        self.connect_to_DB(self.connection_string)

    def connect_to_DB(self, connection_string):
        pass

    def read_DB_credentials(self):
        with open('credentials.json', 'r', encoding='utf-8') as file:
            return json.load(file)
        
SchoolDB()