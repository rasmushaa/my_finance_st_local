import re
from .user import User
from backend.google_cloud.api import GoogleCloudAPI


class CredentialsAPI():
    def __init__(self):
        self.__client = GoogleCloudAPI()

    def username_and_password_match(self, username, password_hash) -> bool:
        if not self.__is_valid_username(username):
            return False
        sql = f"""
        SELECT 
            COUNT(*) AS ct
        FROM 
            {self.__client._dataset}.d_credentials     
        WHERE 
            UserName = '{username}' AND PasswordHash = '{password_hash}'     
        """
        df = self.__client.sql_to_pandas(sql)
        if df['ct'][0] == 1:
            return True
        else:
            return False
        
    
    def init_user(self, username, password_hash) -> User:
        if not self.__is_valid_username(username):
            return User(-1, '', '', False)
        sql = f"""
        SELECT
            KeyUserId,
            UserName,
            Role,
            PasswordHash
        FROM 
            {self.__client._dataset}.d_credentials  
        WHERE 
            UserName = '{username}' AND PasswordHash = '{password_hash}'
        """
        df = self.__client.sql_to_pandas(sql)
        if df.shape[0] == 1:
            return User(id=df['KeyUserId'][0] ,name=df['UserName'][0], role=df['Role'][0], is_logged_in=True)
        else:
            return User(-1, '', '', False)
        
    
    def __is_valid_username(user_input: str):
        # Allow only alphanumeric characters and underscores
        return re.match(r"^[a-zA-Z0-9_]+$", user_input) is not None
        
    


    

    