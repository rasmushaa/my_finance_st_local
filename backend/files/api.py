import pandas as pd
import chardet
import csv
from backend.google_cloud.api import GoogleCloudAPI
from backend.categories.api import CategoriesAPI
from .data_collector import DataCollector

class FilesAPI(GoogleCloudAPI):
    def __init__(self):
        self.__client = GoogleCloudAPI()


    def open_binary_as_pandas(self, input_file) -> pd.DataFrame:
        ''' Open provided unkown CSV safely.
        
        The text encoding, and seperator characters are unkown,
        and must be determined manaully using external libraries.

        Inputs
        ------
        input_file : Streamlit BytesIO
            User provided file, that is validate to be a csv
        '''
        encoding, separator = self.__autodetect_file_coding(input_file)
        df = pd.read_csv(input_file, encoding=encoding, sep=separator)
        return df
    

    def add_filetype_to_databases(self, **kwargs) -> bool:
        ''' Add a new supported filetype row to database.
        
        The ColumnNameString is a common string that contains all of the column names,
        that is used to identify different file.
        The table contains required information to select correct columns to run analysis.

        Inputs
        ------
        Keyvalue-pairs
            The key is going to be the column name, and value is the row value
        '''
        kwargs['ColumnNameString'] = ','.join(kwargs['ColumnNameString'])
        self.__client.write_rows_to_table([kwargs], 'd_filetypes')


    def add_transactions_to_database(self, df: pd.DataFrame, user_name: str) -> bool:
        ''' Push one Banking file to database.
        
        The table is created, if not already exist.
        Ether the whoele df is uploaded, or it fails completely.

        Inputs
        ------
        df: pd.DataFrame
            The Banking File
        user_name: str
            The current active user
        '''
        df['Category'] = df['Category'].fillna('N/A') # Different missing values can have multiple values: Nan, Empty, etc. Which is a challenge for reporting, thus, 'N/A' is selected to handle this
        df['KeyUser'] = user_name
        df['CommitTimestamp'] = pd.Timestamp('now', tz='Europe/Helsinki')
        df = df[['KeyDate', 'KeyUser', 'Amount', 'Receiver', 'Category', 'CommitTimestamp']]
        try:
            self.__client.write_pandas_to_table(df, 'f_transactions')
        except:
            return False
        return True
    

    def add_assets_to_database(self, date, user_name, collector) -> bool:
        ''' Insert new Quarter for a user
        
        Inputs
        ------
        date : Date object
            The insertation date selected by a user. The qurter level is used on the reporting level
        user_name : str
            User name key for table aggregation
        collector
            DataCollector object with filled values from GUI

        Returns
        -------
        Inseration success
        '''
        if not collector.no_nones(): # User must have inputted something to all possible entries
            return False
        
        df_collection = collector.to_dataframe()

        df = pd.DataFrame(columns=['KeyDate', 'KeyUser', 'Category', 'Explanation', 'Value'])
        df['Category'] = df_collection['key'].str.upper().str.replace('_', '-') # Keys back to BigQuery format
        df['Value'] = df_collection['value']
        df['KeyDate'] = date
        df['KeyUser'] = user_name
        df['CommitTimestamp'] = pd.Timestamp('now', tz='Europe/Helsinki')

        try:
            self.__client.write_pandas_to_table(df, 'f_assets')
        except:
            return False
        return True
    

    def get_asset_data_collector(self):
        ''' Init a class that has possble data entrys
        as member variables.

        Returns
        -------
        DataCollector() with Asset-categories
        '''
        assets = CategoriesAPI().get_asset_categories()
        assets = [asset.replace('-', '_').lower() for asset in assets] # ASSETS-ARE-IN-THIS-FORMAT, and must_formatted_for_python
        collector = DataCollector()
        collector.add_from_list(assets)
        return collector


    def date_not_in_transactions_table(self, date, user_name: str):
        ''' Prevent from adding multiple same banking files to the database.
        The date validation is user specific.
        
        Inputs
        ------
        date: datetime
            The minimum date in the Banking File
        user_name: str
            The current active user
        '''
        sql = f'''
        SELECT
            MAX(KeyDate) AS date
        FROM
            {self.__client._dataset}.f_transactions
        WHERE
            KeyUser = '{user_name}'
        '''
        latest_date = self.__client.sql_to_pandas(sql)['date'][0]
        return (latest_date is None) or (date > pd.to_datetime(latest_date, format='%Y-%m-%d').date()) # If there is data, validate
    

    def date_not_in_assets_table(self, date, user_name: str):
        ''' Prevent from adding multiple same assets files to the database.
        The date validation is user specific.
        
        Inputs
        ------
        date: datetime
            The asset File date
        user_name: str
            The current active user
        '''
        sql = f'''
        SELECT
            MAX(KeyDate) AS date
        FROM
            {self.__client._dataset}.f_assets
        WHERE
            KeyUser = '{user_name}'
        '''
        latest_date = self.__client.sql_to_pandas(sql)['date'][0]
        return (latest_date is None) or (date > pd.to_datetime(latest_date, format='%Y-%m-%d').date()) # If there is data, validate

    
    def transform_input_file(self, df: pd.DataFrame):
        ''' The Raw CSV input file is transformed into the required format
        
        The file is assumed to be known in this part, and its recorded column
        format is quered to transform it into the expected format.
        Floats and Dates are also handled.

        Inputs
        ------
        df: pd.DataFrame
            The user input csv file 
        '''
        cols = df.columns.to_list()
        col_str = ','.join(cols)
        sql=f"""
        SELECT
            *
        FROM
            `{self.__client._dataset}.d_filetypes`
        WHERE
            ColumnNameString = '{col_str}'
        """
        filetype = self.__client.sql_to_pandas(sql).iloc[0].to_dict()

        df.rename(columns={filetype['DateColumn']: 'KeyDate', filetype['ReceiverColumn']: 'Receiver', filetype['AmountColumn']: 'Amount'}, inplace=True)

        df['KeyDate'] = pd.to_datetime(df['KeyDate'], format=filetype['DateColumnFormat']).dt.date
        if df['Amount'].dtype != 'float64':
            df['Amount'] = df['Amount'].str.replace(',', '.').astype(float) # Decimael ',' to '.' float
        df['Category'] = None

        df = df[['KeyDate', 'Amount', 'Receiver', 'Category']].copy()
        df.sort_values(by='KeyDate', ascending=True, inplace=True)
        return df


    def filetype_is_in_database(self, df: pd.DataFrame) -> bool:
        ''' Checks whether the file type is known
        
        Inputs
        ------
        df: pd.DataFrame
            The user input csv file 
        '''
        cols = df.columns.to_list()
        col_str = ','.join(cols)
        sql = f"""
        SELECT
            COUNT(*) AS count
        FROM
            `{self.__client._dataset}.d_filetypes`
        WHERE
            ColumnNameString = '{col_str}'
        """
        df = self.__client.sql_to_pandas(sql)
        return df['count'].all() > 0


    def __autodetect_file_coding(self, file_binary) -> str:
        ''' 
        Auto detects used encoding and separator in csv file.

        If file parameters are unkwown, it has to be first opened in binary
        to avoid any parsing errors.

        Parameters
        ----------
        file_binary : A subclass of BytesIO
            The raw input file from Streamlit File Uploader

        Returns
        -------
        encoding : str
            Detected encoding. Note, chardet works well, but its not perfect!
        separator : str
            Detected separator in [',', ';', '', '\t', '|']
        '''
        encoding_dict = chardet.detect(file_binary.getvalue())
        encoding = encoding_dict['encoding']

        dialect = csv.Sniffer().sniff(file_binary.getvalue().decode(encoding), delimiters=[',', ';', '', '\t', '|'])
        separator = dialect.delimiter

        return encoding, separator
    
