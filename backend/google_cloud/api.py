import sqlite3
import os.path
import pandas as pd
import json



class GoogleCloudAPI():
    ''' Local Mock version of the actual GoogelCloudAPI

    Init the local Database, using sqlite3, 
    and fills the default values, and mimicks
    the functionality of the real version.
    Provides the full capability to run the 
    application locally!
    '''

    def __init__(self):
        self.__db_name = 'my_finance.db'
        self._dataset = 'DATASET-FILLER' # Not used in sqlite
        if not os.path.isfile(self.__db_name): # Create the DB, if not already exists
            self.__init_local_db()


    def sql_to_pandas(self, sql: str) -> pd.DataFrame:
        ''' Run a regular SQL query 
        and return a pandas DataFrame.
        
        Inputs
        ------
        sql : string
            A regular SQL query

        Returns
        -------
        df : DataFrame
        '''
        # Remove the `<dataset>.` part for SQLite
        sql = sql.replace("DATASET-FILLER.", "")
        conn = sqlite3.connect(self.__db_name)
        df = pd.read_sql_query(sql, conn)
        return df
    

    def write_pandas_to_table(self, df: pd.DataFrame, table: str):
        ''' Push a DataFrame to BigQuery.

        A new table will be create, if the destination does not exists,
        however, pyarrows has a bug and it fails for datetime columns,
        thus the schema must be constructed manually from pandas to GBQ format.
        The mode is locked to Append only, to prevent accidental overwrites
        
        Inputs
        ------
        df : pd.DataFram
            A regular DataFrame
        table : str
            The name of destination Table, that is used together with initial project parameters
        '''
        conn = sqlite3.connect(self.__db_name)
        df.to_sql(name=table, con=conn, if_exists='append', index=False)


    def write_rows_to_table(self, rows_to_insert: list, table: str) -> bool:
        ''' Write rows to an existing table.

        Note, writing one row from the list may fail, but others are completed successfully.
        
        Inputs
        ------
        rows_to_insert : list[dict]
            A DataBase row in a dict format
        table: str
            The name of the destination Table, that is used together with initial project parameters

        Returns
        -------
        success: bool
            If the insert operation results any errors, those a printed and False is returned
        '''
        conn = sqlite3.connect(self.__db_name)
        cursor = conn.cursor()

        columns = rows_to_insert[0].keys()
        
        # Create placeholders for the values (e.g., ?, ?, ? for 3 columns)
        placeholders = ", ".join(["?"] * len(columns))
        
        # Prepare the insert query
        query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
        
        # Convert rows (dicts) into a list of tuples for execution
        values = [tuple(row[col] for col in columns) for row in rows_to_insert]
        
        try:
            cursor.executemany(query, values)
            conn.commit()
        except Exception as e:
            conn.close()
            return False
        conn.close()
        return True
    

    def upload_file_to_gcs(self, local_file_path: str):
        ''' Upload Local File to GCS
        
        The Bucker and folder are project specific,
        and only the <local_file_path> is required

        Inputs
        ------
        local_file_path : str
            Name/Dir of the file to be uploaded with the same dir
        '''
        pass # The file is already saved localy to be uploaded


    def download_file_from_gcs(self, local_file_path: str):
        ''' Download a file from GCS to local filesystem.

        The direcotry is the same on the both platforms
        
        Inputs
        ------
        local_file_path : str
            Name/Dir of the file to be downloaded with the same dir
        '''
        pass # The file is already in the local space


    def __init_local_db(self):
        conn = sqlite3.connect(self.__db_name)

        conn.execute('''
                     CREATE TABLE f_transactions (
                     KeyDate DATE,
                     KeyUser CHAR(50),
                     Amount REAL,
                     Receiver CHAR(50),
                     Category CHAR(50),
                     CommitTimestamp TIMESTAMP
                     );''')
        
        conn.execute('''
                     CREATE TABLE d_filetypes (
                     KeyFileName CHAR(50),
                     DateColumn CHAR(50),
                     DateColumnFormat CHAR(50),
                     AmountColumn CHAR(50),
                     ReceiverColumn CHAR(50),
                     ColumnNameString CHAR(200)
                     );''')
        
        conn.execute('''
                     CREATE TABLE f_assets (
                     KeyDate DATE,
                     KeyUser CHAR(50),
                     Category CHAR(50),
                     Explanation CHAR(50),
                     Value REAL,
                     CommitTimestamp TIMESTAMP
                     );''')
        
        conn.execute('''
                     CREATE TABLE d_category (
                     KeyId INT,
                     Type CHAR(50),
                     Name CHAR(50),
                     Explanation CHAR(50)
                     );''')
        
        conn.execute('''
                     INSERT INTO d_category(KeyId, Type, Name, Explanation)
                     VALUES 
                        (1,'asset','CASH','All availeable cash in all accounts'),
                        (2,'asset','APARTMENT','Estimated market value of all apartments'),
                        (3,'asset','CAPITAL-ASSETS-PURCHASE-PRICE','Current Avg. pruchase price of all capital assets'),
                        (4,'asset','UNREALIZED-CAPITAL-GAINS','Unrealized gains of all capital assets'),
                        (5,'asset','CAPITAL-ASSETS-VALUE','Current total market price of all capital assets'),
                        (6,'asset','REALIZED-CAPITAL-GAINS','Realized capital gains in the Quarter'),
                        (7,'asset','REALIZED-CAPITAL-LOSSES','Realized capital losses in the Quarter'),
                        (8,'asset','DIVIDENDS','Received dividends in the Quarter'),
                        (9,'asset','OTHER-ASSETS','Any tangeable assets, such as cars, etc.'),
                        (10,'asset','MORTGAGE','Current total mortgage'),
                        (11,'asset','STUDENT-LOAN','Current student loan'),
                        (12,'asset','OTHER-LOANS','Any other loan, such as car loans'),
                        (13,'transaction','FOOD','Groceries and lunches, etc.'),
                        (14,'transaction','HEALTH','Barber, Hygiene, Medicine, Makeups, etc.'),
                        (15,'transaction','LIVING','All expenditures related to living'),
                        (16,'transaction','SALARY','Money paid from a work'),
                        (17,'transaction','HOBBIES','All expenditures that are related to hobbies'),
                        (18,'transaction','CLOTHING','Clothes, excluding sport gear'),
                        (19,'transaction','COMMUTING','All expenditures related to basic transportation, excluding holiday trips etc.'),
                        (20,'transaction','INVESTMENT','Any negatve cash float that is assumed to generate interest'),
                        (21,'transaction','TECHNOLOGY','Computer, Phone, TV, mobile carriers, etc.'),
                        (22,'transaction','OTHER-INCOME','Any positive cashflow, that is not salary'),
                        (23,'transaction','ENTERTAINMENT','Netflix, movies, restaurant, bars, etc.'),
                        (24,'transaction','UNCATEGORIZED','Typically, not a repeating cashflow...'),
                        (25,'transaction','HOUSEHOLD-ITEMS','Furnitures, Maintenence, Ikea, Cleaning stuff'); 
                     ''')
        
        conn.commit()
        conn.close()